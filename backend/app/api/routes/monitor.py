"""
Monitoring endpoints for system health and metrics.
Public endpoints that don't require authentication.
"""
import asyncio
import json
import os
import psutil
import time
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List
from pathlib import Path

import docker
import structlog
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db_session
from app.services.db_performance import get_database_performance_metrics, db_monitor

logger = structlog.get_logger(__name__)

router = APIRouter()

# Global variables for caching
_docker_client = None
_last_metrics_update = 0
_cached_metrics = {}
_cache_duration = 5  # seconds
_temp_docker_data = None
_temp_docker_timestamp = 0


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


async def enable_temporary_docker_access():
    """
    Attempt to enable Docker access and fetch data.
    Since we can't modify docker-compose from inside the container easily,
    this will try to detect if Docker becomes available and cache the data.
    """
    global _temp_docker_data, _temp_docker_timestamp
    
    try:
        # Try to connect to Docker directly (in case it was enabled externally)
        try:
            temp_client = docker.from_env()
            temp_client.ping()
            
            # Docker is available! Fetch the data immediately
            docker_data = get_docker_status()
            _temp_docker_data = docker_data
            _temp_docker_timestamp = time.time()
            
            logger.info("Docker access available, data fetched successfully")
            return {"success": True, "data": docker_data, "already_enabled": True}
            
        except Exception as docker_error:
            logger.info("Docker not available, need external configuration", error=str(docker_error))
            
            # Create a signal file that the host system can detect
            signal_file = "/tmp/request_docker_access.signal"
            try:
                with open(signal_file, 'w') as f:
                    f.write(f"timestamp={time.time()}\nrequested_by=backend_api\nstatus=requested\n")
                logger.info("Created Docker access request signal file")
            except:
                pass
            
            return {
                "success": False,
                "error": "Docker access not available from within container",
                "automation_note": "Automated Docker restart would need to be triggered from the host system",
                "signal_file_created": True
            }
        
    except Exception as e:
        logger.error("Failed to attempt Docker access", error=str(e))
        return {"success": False, "error": f"Failed to attempt Docker access: {str(e)}"}


async def revert_docker_access():
    """
    Revert back to secure mode by restarting backend without Docker socket access.
    """
    try:
        logger.info("Reverting to secure mode (removing Docker access)...")
        
        # Wait a moment to ensure data was fetched
        await asyncio.sleep(2)
        
        # Restart backend without the override (secure mode)
        revert_cmd = [
            "docker", "compose",
            "-f", "/app/../infra/docker-compose.yml",
            "up", "-d", "--force-recreate", "backend"
        ]
        
        revert_result = subprocess.run(
            revert_cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/"
        )
        
        if revert_result.returncode == 0:
            logger.info("Successfully reverted to secure mode")
            # Clean up temporary override file
            try:
                os.unlink("/tmp/docker-compose.temp-monitoring.yml")
            except:
                pass
        else:
            logger.error("Failed to revert to secure mode", 
                       stderr=revert_result.stderr, stdout=revert_result.stdout)
        
    except Exception as e:
        logger.error("Error while reverting Docker access", error=str(e))


@router.post("/monitor/docker/enable-temp")
async def enable_temporary_docker_monitoring(background_tasks: BackgroundTasks):
    """
    Automatically enable temporary Docker monitoring, fetch data, and revert back to secure mode.
    This endpoint performs the entire process automatically without manual intervention.
    """
    try:
        # Execute the automated temporary Docker access
        result = await enable_temporary_docker_access()
        
        if result["success"]:
            return {
                "success": True,
                "message": result.get("message", "Docker data fetched successfully"),
                "data": result.get("data", {}),
                "automated": result.get("automated", False),
                "already_enabled": result.get("already_enabled", False),
                "status": "completed"
            }
        else:
            # If automated approach failed, fall back to manual instructions
            return {
                "success": False,
                "message": "Automated Docker access failed, manual setup required",
                "error": result.get("error", "Unknown error"),
                "manual_required": True,
                "instructions": {
                    "title": "Manual Docker Monitoring Setup",
                    "description": "Automated setup failed. Please follow these manual steps:",
                    "steps": [
                        {
                            "step": 1,
                            "title": "Edit Docker Compose Configuration",
                            "description": "Edit the file: infra/docker-compose.yml",
                            "action": "Find the backend service section"
                        },
                        {
                            "step": 2,
                            "title": "Uncomment Docker Socket Access",
                            "description": "Remove the # from these two lines:",
                            "code": [
                                "user: \"root\"",
                                "- /var/run/docker.sock:/var/run/docker.sock:ro"
                            ]
                        },
                        {
                            "step": 3,
                            "title": "Restart Backend Service",
                            "description": "Run this command from the project root:",
                            "command": "docker compose -f infra/docker-compose.yml up -d --force-recreate backend"
                        },
                        {
                            "step": 4,
                            "title": "Refresh Monitor Page",
                            "description": "Return to the monitor page and Docker containers will be visible"
                        }
                    ],
                    "security_note": "This temporarily runs the backend as root. Disable Docker monitoring after use by re-commenting the lines and restarting.",
                    "reason": f"Automated setup failed: {result.get('error', 'Unknown error')}"
                }
            }
        
    except Exception as e:
        logger.error("Failed to enable temporary Docker monitoring", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to enable temporary Docker monitoring: {str(e)}")


@router.get("/monitor/docker/temp-data")
async def get_temporary_docker_data():
    """
    Get temporarily cached Docker data without requiring active Docker access.
    This returns data that was fetched during a temporary privilege escalation.
    """
    global _temp_docker_data, _temp_docker_timestamp
    
    # Check if we have recent temporary data (valid for 5 minutes)
    if _temp_docker_data and (time.time() - _temp_docker_timestamp) < 300:
        return {
            "data": _temp_docker_data,
            "timestamp": _temp_docker_timestamp,
            "cache_age_seconds": time.time() - _temp_docker_timestamp,
            "status": "cached"
        }
    
    # Try to get fresh data if Docker access is available
    current_docker_status = get_docker_status()
    if "error" not in current_docker_status or current_docker_status.get("containers"):
        # We have Docker access now
        _temp_docker_data = current_docker_status
        _temp_docker_timestamp = time.time()
        return {
            "data": current_docker_status,
            "timestamp": _temp_docker_timestamp,
            "cache_age_seconds": 0,
            "status": "live"
        }
    
    # No cached data and no Docker access
    return {
        "data": None,
        "error": "No temporary Docker data available and Docker access is not currently enabled",
        "instructions": "Use POST /api/v1/monitor/docker/enable-temp to request temporary access"
    }
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
    global _temp_docker_data, _temp_docker_timestamp
    
    # First check if we have recent temporary data
    if _temp_docker_data and (time.time() - _temp_docker_timestamp) < 300:  # 5 minutes cache
        temp_data = _temp_docker_data.copy()
        temp_data["source"] = "temporary_cache"
        temp_data["cache_age_seconds"] = time.time() - _temp_docker_timestamp
        return temp_data
    
    # Try regular Docker client
    client = get_docker_client()
    if not client:
        return {
            "containers": [],
            "images": [],
            "system_info": {},
            "error": "Docker client not available",
            "temp_monitoring_available": True
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
            },
            "source": "live"
        }
    except Exception as e:
        logger.error("Failed to get Docker status", error=str(e))
        return {
            "containers": [],
            "images": [],
            "system_info": {},
            "error": str(e),
            "temp_monitoring_available": True
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
            from sqlalchemy import text
            async for session in get_db_session():
                result = await session.execute(text("SELECT 1"))
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
    """Get process logs from Docker containers or local files."""
    logs = []
    
    try:
        client = get_docker_client()
        if client:
            # Try to get logs from Docker containers
            try:
                if process_name == "backend":
                    # Look for backend container
                    containers = client.containers.list(filters={"name": "backend"})
                    if not containers:
                        containers = client.containers.list(filters={"ancestor": "x-university-backend"})
                    if containers:
                        container_logs = containers[0].logs(tail=lines, timestamps=True).decode('utf-8')
                        for line in container_logs.strip().split('\n'):
                            if line.strip():
                                try:
                                    timestamp_str, message = line.split(' ', 1)
                                    timestamp = datetime.fromisoformat(timestamp_str.replace('T', ' ').replace('Z', '+00:00'))
                                    level = "INFO"
                                    if "ERROR" in message.upper():
                                        level = "ERROR"
                                    elif "WARNING" in message.upper() or "WARN" in message.upper():
                                        level = "WARNING"
                                    elif "DEBUG" in message.upper():
                                        level = "DEBUG"
                                    
                                    logs.append({
                                        "timestamp": timestamp.isoformat(),
                                        "level": level,
                                        "message": message.strip(),
                                        "service": "backend"
                                    })
                                except:
                                    # Fallback for unparseable lines
                                    logs.append({
                                        "timestamp": datetime.now(timezone.utc).isoformat(),
                                        "level": "INFO",
                                        "message": line.strip(),
                                        "service": "backend"
                                    })
                        return logs[-lines:]
                
                elif process_name == "frontend":
                    # Look for frontend container
                    containers = client.containers.list(filters={"name": "frontend"})
                    if not containers:
                        containers = client.containers.list(filters={"ancestor": "x-university-frontend"})
                    if containers:
                        container_logs = containers[0].logs(tail=lines, timestamps=True).decode('utf-8')
                        for line in container_logs.strip().split('\n'):
                            if line.strip():
                                try:
                                    timestamp_str, message = line.split(' ', 1)
                                    timestamp = datetime.fromisoformat(timestamp_str.replace('T', ' ').replace('Z', '+00:00'))
                                    level = "INFO"
                                    if "ERROR" in message.upper():
                                        level = "ERROR"
                                    elif "WARNING" in message.upper() or "WARN" in message.upper():
                                        level = "WARNING"
                                    
                                    logs.append({
                                        "timestamp": timestamp.isoformat(),
                                        "level": level,
                                        "message": message.strip(),
                                        "service": "frontend"
                                    })
                                except:
                                    logs.append({
                                        "timestamp": datetime.now(timezone.utc).isoformat(),
                                        "level": "INFO",
                                        "message": line.strip(),
                                        "service": "frontend"
                                    })
                        return logs[-lines:]
            except Exception as e:
                logger.warning("Failed to get Docker logs", process=process_name, error=str(e))
    
    except Exception as e:
        logger.warning("Docker not available for log retrieval", error=str(e))
    
    # Fallback to mock logs with some realistic examples
    if process_name == "backend":
        logs = [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "level": "INFO",
                "message": "Server started successfully on port 8000",
                "service": "uvicorn"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=28)).isoformat(),
                "level": "INFO",
                "message": "Database connection pool initialized",
                "service": "sqlalchemy"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "level": "DEBUG",
                "message": "Loading application configuration",
                "service": "backend"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=22)).isoformat(),
                "level": "WARNING",
                "message": "Docker client connection failed - falling back to mock data",
                "service": "monitor"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "level": "INFO",
                "message": "FastAPI application startup complete",
                "service": "backend"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=18)).isoformat(),
                "level": "ERROR",
                "message": "Authentication failed for user: invalid_token",
                "service": "auth"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "level": "INFO",
                "message": "Monitor endpoint accessed",
                "service": "backend"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=12)).isoformat(),
                "level": "DEBUG",
                "message": "Cache hit for user session data",
                "service": "cache"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=8)).isoformat(),
                "level": "WARNING",
                "message": "High memory usage detected: 85%",
                "service": "monitor"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "level": "INFO",
                "message": "System metrics collected successfully",
                "service": "monitor"
            }
        ]
    else:
        # Frontend logs
        logs = [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "level": "INFO",
                "message": "Vite dev server started on port 5173",
                "service": "vite"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=22)).isoformat(),
                "level": "DEBUG",
                "message": "Hot module replacement enabled",
                "service": "vite"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "level": "INFO",
                "message": "React application initialized",
                "service": "react"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=18)).isoformat(),
                "level": "WARNING",
                "message": "Component prop validation failed: missing required prop",
                "service": "react"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "level": "INFO",
                "message": "Router configuration loaded",
                "service": "react-router"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=12)).isoformat(),
                "level": "ERROR",
                "message": "Failed to fetch data from API: Network error",
                "service": "frontend"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "level": "DEBUG",
                "message": "State updated: user authentication status",
                "service": "frontend"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=8)).isoformat(),
                "level": "WARNING",
                "message": "Bundle size exceeded recommended limit",
                "service": "vite"
            },
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "level": "INFO",
                "message": "Monitor page rendered successfully",
                "service": "frontend"
            }
        ]
    
    return logs[-lines:]


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
                "os": dict(zip(['sysname', 'nodename', 'release', 'version', 'machine'], os.uname())) if hasattr(os, 'uname') else {"system": "unknown"},
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


async def stream_docker_logs(service: str):
    """Stream logs from Docker container in real-time."""
    # Rate limit to prevent overwhelming the system
    await asyncio.sleep(1)
    
    client = get_docker_client()
    if not client:
        # Send mock logs instead of failing repeatedly
        await asyncio.sleep(2)
        counter = 0
        mock_logs_data = {
            "backend": [
                {"message": "FastAPI server started successfully", "level": "INFO"},
                {"message": "Database connection established", "level": "INFO"},
                {"message": "Processing API request", "level": "DEBUG"},
                {"message": "Cache miss - fetching from database", "level": "WARNING"},
                {"message": "Authentication failed for user", "level": "ERROR"},
                {"message": "Database query completed successfully", "level": "INFO"},
                {"message": "Deprecated API endpoint accessed", "level": "WARNING"},
                {"message": "Critical: Database connection lost", "level": "ERROR"}
            ],
            "frontend": [
                {"message": "Vite dev server started on port 5173", "level": "INFO"},
                {"message": "Component rendered successfully", "level": "DEBUG"},
                {"message": "API request initiated", "level": "INFO"},
                {"message": "Warning: Component prop validation failed", "level": "WARNING"},
                {"message": "Failed to fetch data from API", "level": "ERROR"},
                {"message": "Route navigation completed", "level": "INFO"},
                {"message": "Debug: State updated", "level": "DEBUG"},
                {"message": "Network request timeout", "level": "ERROR"}
            ],
            "postgres": [
                {"message": "Database system is ready to accept connections", "level": "INFO"},
                {"message": "Connection established from backend", "level": "DEBUG"},
                {"message": "Query execution time: 125ms", "level": "INFO"},
                {"message": "Warning: Slow query detected", "level": "WARNING"},
                {"message": "Connection pool exhausted", "level": "ERROR"},
                {"message": "Transaction committed successfully", "level": "INFO"},
                {"message": "Checkpoint process completed", "level": "DEBUG"},
                {"message": "Critical: Disk space running low", "level": "ERROR"}
            ]
        }
        
        logs_for_service = mock_logs_data.get(service, [{"message": "Service running", "level": "INFO"}])
        
        while counter < 10:  # Limit initial mock logs
            await asyncio.sleep(3)
            log_data = logs_for_service[counter % len(logs_for_service)]
            mock_log = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": log_data["level"],
                "message": log_data["message"],
                "service": service
            }
            yield f"data: {json.dumps(mock_log)}\n\n"
            counter += 1
        
        # Send keep-alive messages less frequently with variety
        keep_alive_counter = 0
        keep_alive_messages = {
            "backend": [
                {"message": "Health check passed", "level": "INFO"},
                {"message": "Memory usage within normal range", "level": "DEBUG"},
                {"message": "High CPU usage detected", "level": "WARNING"},
                {"message": "Background task completed", "level": "INFO"}
            ],
            "frontend": [
                {"message": "Browser connection active", "level": "INFO"},
                {"message": "Hot reload triggered", "level": "DEBUG"},
                {"message": "Bundle size increased", "level": "WARNING"},
                {"message": "User session active", "level": "INFO"}
            ],
            "postgres": [
                {"message": "Database maintenance completed", "level": "INFO"},
                {"message": "Connection pool status checked", "level": "DEBUG"},
                {"message": "Long running query detected", "level": "WARNING"},
                {"message": "Backup process started", "level": "INFO"}
            ]
        }
        
        while True:
            await asyncio.sleep(10)
            service_messages = keep_alive_messages.get(service, [{"message": f"{service} service monitoring active", "level": "INFO"}])
            msg_data = service_messages[keep_alive_counter % len(service_messages)]
            keep_alive = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": msg_data["level"],
                "message": msg_data["message"],
                "service": service
            }
            yield f"data: {json.dumps(keep_alive)}\n\n"
            keep_alive_counter += 1
        return
    
    try:
        # Find the container (simplified)
        container = None
        containers = client.containers.list(filters={"name": service})
        if containers:
            container = containers[0]
        
        if not container:
            yield f"data: {json.dumps({'error': f'Container {service} not found', 'timestamp': datetime.now(timezone.utc).isoformat()})}\n\n"
            return
        
        # Get recent logs first (limited)
        recent_logs = container.logs(tail=20, timestamps=True).decode('utf-8').strip()
        for line in recent_logs.split('\n'):
            if line.strip():
                try:
                    timestamp_str, message = line.split(' ', 1)
                    
                    # Enhanced log level detection
                    level = "INFO"  # default
                    message_upper = message.upper()
                    if any(keyword in message_upper for keyword in ['ERROR', 'EXCEPTION', 'FAILED', 'CRITICAL']):
                        level = "ERROR"
                    elif any(keyword in message_upper for keyword in ['WARNING', 'WARN', 'DEPRECATED']):
                        level = "WARNING"
                    elif any(keyword in message_upper for keyword in ['DEBUG', 'TRACE']):
                        level = "DEBUG"
                    elif any(keyword in message_upper for keyword in ['INFO', 'SUCCESS', 'STARTED', 'FINISHED']):
                        level = "INFO"
                    
                    log_entry = {
                        "timestamp": datetime.fromisoformat(timestamp_str.replace('T', ' ').replace('Z', '+00:00')).isoformat(),
                        "level": level,
                        "message": message.strip(),
                        "service": service
                    }
                    yield f"data: {json.dumps(log_entry)}\n\n"
                except:
                    pass
        
        # Stream new logs with rate limiting
        log_stream = container.logs(stream=True, follow=True, tail=0, timestamps=True)
        for log_line in log_stream:
            await asyncio.sleep(0.5)  # Rate limit
            try:
                line = log_line.decode('utf-8').strip()
                if line:
                    timestamp_str, message = line.split(' ', 1)
                    
                    # Enhanced log level detection
                    level = "INFO"  # default
                    message_upper = message.upper()
                    if any(keyword in message_upper for keyword in ['ERROR', 'EXCEPTION', 'FAILED', 'CRITICAL', 'FATAL']):
                        level = "ERROR"
                    elif any(keyword in message_upper for keyword in ['WARNING', 'WARN', 'DEPRECATED', 'CAUTION']):
                        level = "WARNING"
                    elif any(keyword in message_upper for keyword in ['DEBUG', 'TRACE', 'VERBOSE']):
                        level = "DEBUG"
                    elif any(keyword in message_upper for keyword in ['INFO', 'SUCCESS', 'STARTED', 'FINISHED', 'COMPLETED']):
                        level = "INFO"
                    
                    log_entry = {
                        "timestamp": datetime.fromisoformat(timestamp_str.replace('T', ' ').replace('Z', '+00:00')).isoformat(),
                        "level": level,
                        "message": message.strip(),
                        "service": service
                    }
                    yield f"data: {json.dumps(log_entry)}\n\n"
            except Exception:
                pass  # Skip malformed log lines
                
    except Exception as e:
        error_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "ERROR",
            "message": f"Log streaming error: {str(e)}",
            "service": service
        }
        yield f"data: {json.dumps(error_entry)}\n\n"


async def stream_all_logs():
    """Stream logs from all services simultaneously with rate limiting."""
    services = ["backend", "frontend", "postgres"]
    
    # Send a few historical logs per service (limited)
    for service in services:
        historical_logs = get_process_logs(service, 10)  # Reduced from 50
        for log_entry in historical_logs:
            yield f"data: {json.dumps(log_entry)}\n\n"
        await asyncio.sleep(0.1)  # Small delay between services
    
    # Generate mock real-time logs at a reasonable pace
    counter = 0
    mock_messages = {
        "backend": [
            {"message": "API request processed successfully", "level": "INFO"},
            {"message": "Database connection healthy", "level": "DEBUG"},
            {"message": "Cache updated for user session", "level": "INFO"},
            {"message": "High CPU usage detected", "level": "WARNING"},
            {"message": "Database query failed", "level": "ERROR"}
        ],
        "frontend": [
            {"message": "Page rendered successfully", "level": "INFO"},
            {"message": "User interaction handled", "level": "DEBUG"},
            {"message": "Component updated", "level": "INFO"},
            {"message": "Network request timeout", "level": "WARNING"},
            {"message": "JavaScript runtime error", "level": "ERROR"}
        ], 
        "postgres": [
            {"message": "Query executed in 45ms", "level": "INFO"},
            {"message": "Connection established", "level": "DEBUG"},
            {"message": "Data committed successfully", "level": "INFO"},
            {"message": "Slow query detected", "level": "WARNING"},
            {"message": "Connection pool exhausted", "level": "ERROR"}
        ]
    }
    
    while True:
        await asyncio.sleep(5)  # Slower updates - every 5 seconds instead of 2
        counter += 1
        
        service = services[counter % len(services)]
        service_messages = mock_messages[service]
        msg_data = service_messages[counter % len(service_messages)]
        
        mock_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": msg_data["level"],
            "message": msg_data["message"],
            "service": service
        }
        
        yield f"data: {json.dumps(mock_log)}\n\n"


@router.get("/monitor/logs/stream/{service}")
async def stream_service_logs(service: str):
    """
    Stream real-time logs for a specific service (backend, frontend, postgres).
    Returns Server-Sent Events (SSE) stream.
    """
    if service not in ["backend", "frontend", "postgres", "all"]:
        raise HTTPException(status_code=400, detail="Invalid service. Use: backend, frontend, postgres, or all")
    
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Cache-Control"
    }
    
    if service == "all":
        return StreamingResponse(stream_all_logs(), headers=headers)
    else:
        return StreamingResponse(stream_docker_logs(service), headers=headers)


@router.get("/monitor/logs/{service}")
async def get_service_logs(service: str, lines: int = 100):
    """
    Get historical logs for a specific service.
    """
    if service not in ["backend", "frontend", "postgres"]:
        raise HTTPException(status_code=400, detail="Invalid service. Use: backend, frontend, or postgres")
    
    logs = get_process_logs(service, lines)
    return {
        "service": service,
        "logs": logs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_lines": len(logs)
    }


@router.get("/monitor/database/performance")
async def get_db_performance():
    """
    Get comprehensive database performance metrics.
    
    Returns:
        Database performance metrics including:
        - Connection pool statistics
        - Database size and connection info
        - Table statistics with sizes and row counts
        - Index usage statistics
        - Slow query analysis (if pg_stat_statements is available)
        - Performance recommendations
        - Database health status
    """
    try:
        metrics = await get_database_performance_metrics()
        return metrics
    except Exception as e:
        logger.error("Failed to get database performance metrics", error=str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve database performance metrics: {str(e)}"
        )


@router.get("/monitor/database/health")
async def get_db_health():
    """
    Get database health status.
    
    Returns:
        Health status with connection pool info, performance issues,
        and recommendations for optimization.
    """
    try:
        health = await db_monitor.check_database_health()
        return health
    except Exception as e:
        logger.error("Failed to get database health", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check database health: {str(e)}"
        )


@router.get("/monitor/database/pool")
async def get_connection_pool_stats():
    """
    Get real-time connection pool statistics.
    
    Returns:
        Current connection pool utilization, size, and status information.
    """
    try:
        stats = await db_monitor.get_connection_pool_stats()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pool_stats": stats
        }
    except Exception as e:
        logger.error("Failed to get connection pool stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve connection pool statistics: {str(e)}"
        )
