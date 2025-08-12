"""
Monitoring endpoints for system health and metrics.
Public endpoints that don't require authentication.
"""
import asyncio
import json
import os
import psutil
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

import docker
import structlog
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db_session

logger = structlog.get_logger(__name__)

router = APIRouter()

# Global variables for caching
_docker_client = None
_last_metrics_update = 0
_cached_metrics = {}
_cache_duration = 5  # seconds


def get_docker_client():
    """Get Docker client with error handling."""
    global _docker_client
    if _docker_client is None:
        try:
            _docker_client = docker.from_env()
            # Test connection
            _docker_client.ping()
        except Exception as e:
            logger.warning("Docker client connection failed", error=str(e))
            _docker_client = None
    return _docker_client


def get_system_metrics() -> Dict[str, Any]:
    """Get system resource metrics."""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        network_io = psutil.net_io_counters()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "load_average": {
                    "1min": load_avg[0],
                    "5min": load_avg[1],
                    "15min": load_avg[2]
                }
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "usage_percent": memory.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "usage_percent": (disk.used / disk.total) * 100,
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0,
                "read_count": disk_io.read_count if disk_io else 0,
                "write_count": disk_io.write_count if disk_io else 0
            },
            "network": {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
                "errin": network_io.errin,
                "errout": network_io.errout,
                "dropin": network_io.dropin,
                "dropout": network_io.dropout
            }
        }
    except Exception as e:
        logger.error("Failed to get system metrics", error=str(e))
        return {
            "cpu": {"usage_percent": 0, "count": 0, "load_average": {"1min": 0, "5min": 0, "15min": 0}},
            "memory": {"total": 0, "available": 0, "used": 0, "usage_percent": 0, "swap_total": 0, "swap_used": 0, "swap_percent": 0},
            "disk": {"total": 0, "used": 0, "free": 0, "usage_percent": 0, "read_bytes": 0, "write_bytes": 0, "read_count": 0, "write_count": 0},
            "network": {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0, "errin": 0, "errout": 0, "dropin": 0, "dropout": 0}
        }


def get_docker_status() -> Dict[str, Any]:
    """Get Docker containers and images status."""
    client = get_docker_client()
    if not client:
        return {
            "containers": [],
            "images": [],
            "system_info": {},
            "error": "Docker client not available"
        }
    
    try:
        # Get containers
        containers = []
        for container in client.containers.list(all=True):
            try:
                stats = container.stats(stream=False)
                containers.append({
                    "id": container.id[:12],
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "status": container.status,
                    "state": container.attrs['State'],
                    "created": container.attrs['Created'],
                    "ports": container.attrs.get('NetworkSettings', {}).get('Ports', {}),
                    "stats": {
                        "cpu_percent": 0,  # We'll calculate this on frontend
                        "memory_usage": stats.get('memory_stats', {}).get('usage', 0),
                        "memory_limit": stats.get('memory_stats', {}).get('limit', 0),
                        "network_rx": stats.get('networks', {}).get('eth0', {}).get('rx_bytes', 0),
                        "network_tx": stats.get('networks', {}).get('eth0', {}).get('tx_bytes', 0)
                    }
                })
            except Exception as e:
                logger.warning("Failed to get container stats", container_name=container.name, error=str(e))
                containers.append({
                    "id": container.id[:12],
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "status": container.status,
                    "state": container.attrs['State'],
                    "created": container.attrs['Created'],
                    "ports": container.attrs.get('NetworkSettings', {}).get('Ports', {}),
                    "stats": {
                        "cpu_percent": 0,
                        "memory_usage": 0,
                        "memory_limit": 0,
                        "network_rx": 0,
                        "network_tx": 0
                    }
                })
        
        # Get images
        images = []
        for image in client.images.list():
            images.append({
                "id": image.id[:12],
                "tags": image.tags,
                "size": image.attrs['Size'],
                "created": image.attrs['Created']
            })
        
        # Get system info
        system_info = client.info()
        
        return {
            "containers": containers,
            "images": images,
            "system_info": {
                "containers_running": system_info.get('ContainersRunning', 0),
                "containers_paused": system_info.get('ContainersPaused', 0),
                "containers_stopped": system_info.get('ContainersStopped', 0),
                "images_count": system_info.get('Images', 0),
                "docker_version": system_info.get('ServerVersion', 'unknown'),
                "architecture": system_info.get('Architecture', 'unknown'),
                "os_type": system_info.get('OSType', 'unknown'),
                "total_memory": system_info.get('MemTotal', 0)
            }
        }
    except Exception as e:
        logger.error("Failed to get Docker status", error=str(e))
        return {
            "containers": [],
            "images": [],
            "system_info": {},
            "error": str(e)
        }


async def get_backend_health() -> Dict[str, Any]:
    """Get backend service health status."""
    try:
        # Test database connection
        db_healthy = False
        db_error = None
        try:
            # Get a database session and test it
            from app.db.base import get_db_session
            async for session in get_db_session():
                result = await session.execute("SELECT 1")
                if result.scalar() == 1:
                    db_healthy = True
                break
        except Exception as e:
            db_error = str(e)
        
        return {
            "service": "healthy",
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "error": db_error
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime": time.time() - psutil.boot_time()
        }
    except Exception as e:
        return {
            "service": "unhealthy",
            "database": {
                "status": "unknown",
                "error": str(e)
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime": 0
        }


def get_process_logs(process_name: str, lines: int = 100) -> List[Dict[str, Any]]:
    """Get process logs (mock implementation for now)."""
    # This is a simplified version - in production you'd read from actual log files
    # or use Docker logs API
    try:
        if process_name == "backend":
            # Mock backend logs
            logs = [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "INFO",
                    "message": "Server started successfully",
                    "service": "uvicorn"
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "INFO",
                    "message": "Database connection established",
                    "service": "sqlalchemy"
                }
            ]
        else:
            # Mock frontend logs
            logs = [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "INFO",
                    "message": "Vite dev server started",
                    "service": "vite"
                }
            ]
        
        return logs[-lines:]
    except Exception as e:
        logger.error("Failed to get process logs", process=process_name, error=str(e))
        return []


@router.get("/monitor")
async def get_monitor_data() -> Dict[str, Any]:
    """
    Get comprehensive system monitoring data.
    This endpoint is public and doesn't require authentication.
    """
    global _last_metrics_update, _cached_metrics
    
    current_time = time.time()
    
    # Use cached metrics if they're still fresh
    if current_time - _last_metrics_update < _cache_duration and _cached_metrics:
        return _cached_metrics
    
    try:
        # Gather all monitoring data
        system_metrics = get_system_metrics()
        docker_status = get_docker_status()
        backend_health = await get_backend_health()
        backend_logs = get_process_logs("backend", 50)
        frontend_logs = get_process_logs("frontend", 50)
        
        monitor_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": {
                "os": os.uname()._asdict() if hasattr(os, 'uname') else {"system": "unknown"},
                "python_version": os.sys.version,
                "metrics": system_metrics
            },
            "docker": docker_status,
            "services": {
                "backend": backend_health
            },
            "logs": {
                "backend": backend_logs,
                "frontend": frontend_logs
            }
        }
        
        # Cache the results
        _cached_metrics = monitor_data
        _last_metrics_update = current_time
        
        return monitor_data
        
    except Exception as e:
        logger.error("Failed to get monitor data", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring data: {str(e)}")


@router.get("/monitor/health")
async def get_health_status() -> Dict[str, Any]:
    """Get quick health status - lighter endpoint for frequent polling."""
    try:
        backend_health = await get_backend_health()
        
        # Get basic container status
        client = get_docker_client()
        containers_status = "unknown"
        if client:
            try:
                containers = client.containers.list()
                running_count = len([c for c in containers if c.status == 'running'])
                total_count = len(client.containers.list(all=True))
                containers_status = f"{running_count}/{total_count} running"
            except:
                containers_status = "error"
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "backend": backend_health,
            "containers": containers_status,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }
    except Exception as e:
        logger.error("Failed to get health status", error=str(e))
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "backend": {"service": "unhealthy"},
            "containers": "error",
            "system": {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0}
        }
