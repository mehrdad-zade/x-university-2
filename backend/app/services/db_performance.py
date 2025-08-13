"""
Database Performance Monitoring and Optimization Service

This module provides tools to monitor database performance, connection pool health,
and query analytics to help optimize the X University database operations.

Features:
- Connection pool monitoring
- Slow query analysis
- Database performance metrics
- Index usage statistics
- Table size and bloat monitoring
- Connection health checks
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import engine, AsyncSessionLocal

logger = logging.getLogger(__name__)


class DatabasePerformanceMonitor:
    """Monitor database performance and connection pool health."""
    
    def __init__(self):
        self.metrics_cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    async def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        pool = engine.pool
        
        try:
            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "total_connections": pool.size() + pool.overflow(),
                "utilization_percent": round(
                    (pool.checkedout() / (pool.size() + pool.overflow())) * 100, 2
                ) if (pool.size() + pool.overflow()) > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting connection pool stats: {e}")
            return {
                "pool_size": 0,
                "checked_in": 0,
                "checked_out": 0,
                "overflow": 0,
                "total_connections": 0,
                "utilization_percent": 0,
                "error": str(e)
            }
    
    async def get_database_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        
        stats = {}
        
        try:
            # Basic database size and connection info
            result = await session.execute(text("""
                SELECT 
                    pg_database_size(current_database()) as db_size,
                    (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()) as active_connections,
                    (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() AND state = 'active') as running_queries,
                    current_setting('max_connections')::int as max_connections;
            """))
            db_info = result.fetchone()
            
            if db_info:
                stats.update({
                    "database_size_bytes": db_info.db_size,
                    "database_size_mb": round(db_info.db_size / (1024 * 1024), 2),
                    "active_connections": db_info.active_connections,
                    "running_queries": db_info.running_queries,
                    "max_connections": db_info.max_connections,
                    "connection_usage_percent": round(
                        (db_info.active_connections / db_info.max_connections) * 100, 2
                    )
                })
            
            # Table sizes and row counts
            result = await session.execute(text("""
                SELECT 
                    schemaname,
                    relname as tablename,
                    pg_total_relation_size(schemaname||'.'||relname) as total_size,
                    pg_relation_size(schemaname||'.'||relname) as table_size,
                    n_tup_ins + n_tup_upd + n_tup_del as total_changes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY total_size DESC;
            """))
            
            tables = []
            for row in result.fetchall():
                tables.append({
                    "schema": row.schemaname,
                    "table": row.tablename,
                    "total_size_bytes": row.total_size,
                    "total_size_mb": round(row.total_size / (1024 * 1024), 2),
                    "table_size_bytes": row.table_size,
                    "table_size_mb": round(row.table_size / (1024 * 1024), 2),
                    "total_changes": row.total_changes,
                    "live_rows": row.live_rows,
                    "dead_rows": row.dead_rows,
                    "dead_row_percent": round(
                        (row.dead_rows / max(row.live_rows, 1)) * 100, 2
                    ),
                    "last_vacuum": row.last_vacuum,
                    "last_autovacuum": row.last_autovacuum,
                    "last_analyze": row.last_analyze,
                    "last_autoanalyze": row.last_autoanalyze,
                })
            
            stats["tables"] = tables
            
            # Index usage statistics
            result = await session.execute(text("""
                SELECT 
                    t.schemaname,
                    t.relname as tablename,
                    i.indexrelname as indexname,
                    i.idx_scan as index_scans,
                    i.idx_tup_read as tuples_read,
                    i.idx_tup_fetch as tuples_fetched,
                    pg_size_pretty(pg_relation_size(i.indexrelid)) as size
                FROM pg_stat_user_indexes i
                JOIN pg_stat_user_tables t ON i.relid = t.relid
                WHERE t.schemaname = 'public'
                ORDER BY i.idx_scan DESC;
            """))
            
            indexes = []
            for row in result.fetchall():
                indexes.append({
                    "schema": row.schemaname,
                    "table": row.tablename,
                    "index": row.indexname,
                    "scans": row.index_scans,
                    "tuples_read": row.tuples_read,
                    "tuples_fetched": row.tuples_fetched,
                    "size": row.size
                })
            
            stats["indexes"] = indexes
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            stats["error"] = str(e)
        
        return stats
    
    async def get_slow_queries(self, session: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slow query statistics from pg_stat_statements."""
        
        try:
            # Check if pg_stat_statements extension is available
            result = await session.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                );
            """))
            
            if not result.scalar():
                return [{"error": "pg_stat_statements extension not available"}]
            
            # Get slow queries
            result = await session.execute(text(f"""
                SELECT 
                    query,
                    calls,
                    total_exec_time,
                    mean_exec_time,
                    max_exec_time,
                    min_exec_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements 
                WHERE query NOT LIKE '%pg_stat_statements%'
                ORDER BY mean_exec_time DESC 
                LIMIT {limit};
            """))
            
            slow_queries = []
            for row in result.fetchall():
                slow_queries.append({
                    "query": row.query[:200] + "..." if len(row.query) > 200 else row.query,
                    "calls": row.calls,
                    "total_time_ms": round(row.total_exec_time, 2),
                    "avg_time_ms": round(row.mean_exec_time, 2),
                    "max_time_ms": round(row.max_exec_time, 2),
                    "min_time_ms": round(row.min_exec_time, 2),
                    "rows_processed": row.rows,
                    "cache_hit_percent": round(row.hit_percent or 0, 2)
                })
            
            return slow_queries
            
        except Exception as e:
            logger.error(f"Error getting slow queries: {e}")
            return [{"error": str(e)}]
    
    async def get_performance_recommendations(self, session: AsyncSession) -> List[str]:
        """Get database performance recommendations."""
        
        recommendations = []
        
        try:
            # Check for missing indexes
            result = await session.execute(text("""
                SELECT 
                    schemaname,
                    relname as tablename,
                    seq_scan,
                    seq_tup_read,
                    idx_scan,
                    seq_tup_read / GREATEST(seq_scan, 1) as avg_seq_read
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                AND seq_scan > 0
                AND (idx_scan = 0 OR seq_scan / GREATEST(idx_scan, 1) > 10)
                ORDER BY seq_tup_read DESC;
            """))
            
            for row in result.fetchall():
                if row.seq_scan > 100:  # More than 100 sequential scans
                    recommendations.append(
                        f"Consider adding indexes to {row.tablename} - "
                        f"{row.seq_scan} sequential scans, avg {row.avg_seq_read:.0f} rows per scan"
                    )
            
            # Check for tables needing VACUUM
            result = await session.execute(text("""
                SELECT 
                    relname as tablename,
                    n_dead_tup,
                    n_live_tup,
                    100 * n_dead_tup / GREATEST(n_live_tup + n_dead_tup, 1) as dead_percent
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                AND n_dead_tup > 1000
                AND 100 * n_dead_tup / GREATEST(n_live_tup + n_dead_tup, 1) > 20
                ORDER BY dead_percent DESC;
            """))
            
            for row in result.fetchall():
                recommendations.append(
                    f"Consider VACUUM on {row.tablename} - "
                    f"{row.dead_percent:.1f}% dead rows ({row.n_dead_tup} dead tuples)"
                )
            
            # Check connection usage
            pool_stats = await self.get_connection_pool_stats()
            if pool_stats["utilization_percent"] > 80:
                recommendations.append(
                    f"High connection pool utilization ({pool_stats['utilization_percent']}%) - "
                    "consider increasing pool size or optimizing query performance"
                )
            
            # Check for unused indexes
            result = await session.execute(text("""
                SELECT 
                    schemaname,
                    relname as tablename,
                    indexrelname as indexname,
                    idx_scan
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public'
                AND idx_scan < 10
                ORDER BY idx_scan;
            """))
            
            unused_indexes = result.fetchall()
            if unused_indexes:
                recommendations.append(
                    f"Found {len(unused_indexes)} potentially unused indexes - "
                    "consider reviewing and dropping if not needed"
                )
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append(f"Error analyzing database: {str(e)}")
        
        return recommendations
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Comprehensive database health check."""
        
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "issues": [],
            "warnings": []
        }
        
        try:
            # Test connection
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
                
                # Get basic stats
                pool_stats = await self.get_connection_pool_stats()
                db_stats = await self.get_database_stats(session)
                
                health.update({
                    "connection_pool": pool_stats,
                    "database": {
                        "size_mb": db_stats.get("database_size_mb", 0),
                        "active_connections": db_stats.get("active_connections", 0),
                        "max_connections": db_stats.get("max_connections", 0),
                        "connection_usage_percent": db_stats.get("connection_usage_percent", 0)
                    }
                })
                
                # Check for issues
                if pool_stats["utilization_percent"] > 90:
                    health["issues"].append("Connection pool near capacity")
                    health["status"] = "degraded"
                elif pool_stats["utilization_percent"] > 70:
                    health["warnings"].append("High connection pool usage")
                
                if db_stats.get("connection_usage_percent", 0) > 80:
                    health["warnings"].append("High database connection usage")
                
                # Check table health
                for table in db_stats.get("tables", []):
                    if table["dead_row_percent"] > 25:
                        health["warnings"].append(
                            f"Table {table['table']} has {table['dead_row_percent']}% dead rows"
                        )
                
        except Exception as e:
            health["status"] = "unhealthy"
            health["issues"].append(f"Database connection failed: {str(e)}")
        
        return health


# Global performance monitor instance
db_monitor = DatabasePerformanceMonitor()


async def get_database_performance_metrics() -> Dict[str, Any]:
    """Get comprehensive database performance metrics."""
    
    try:
        async with AsyncSessionLocal() as session:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "connection_pool": await db_monitor.get_connection_pool_stats(),
                "database_stats": await db_monitor.get_database_stats(session),
                "slow_queries": await db_monitor.get_slow_queries(session),
                "recommendations": await db_monitor.get_performance_recommendations(session),
                "health": await db_monitor.check_database_health()
            }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
