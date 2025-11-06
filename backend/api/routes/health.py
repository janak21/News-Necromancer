"""
Health check and system monitoring endpoints
"""

from fastapi import APIRouter, Request
from datetime import datetime
import psutil
import os
import logging

from ...models.data_models import HealthStatus

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=dict)
async def health_check(request: Request):
    """
    Comprehensive system health check
    
    Returns:
        System health status with component details
    """
    try:
        # Calculate uptime
        start_time = getattr(request.app.state, 'start_time', datetime.now())
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        
        # Check system resources
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=1)
        disk_usage = psutil.disk_usage('/').percent
        
        # Component health checks
        components = {
            "fetcher_module": "healthy",  # Would check actual fetcher health
            "remixer_module": "healthy",  # Would check LLM API connectivity
            "api_gateway": "healthy",
            "memory_usage": f"{memory_usage:.1f}%",
            "cpu_usage": f"{cpu_usage:.1f}%",
            "disk_usage": f"{disk_usage:.1f}%"
        }
        
        # Determine overall status
        overall_status = "healthy"
        if memory_usage > 90 or cpu_usage > 90 or disk_usage > 90:
            overall_status = "degraded"
        if memory_usage > 95 or cpu_usage > 95 or disk_usage > 95:
            overall_status = "unhealthy"
        
        # Get request statistics
        request_count = getattr(request.app.state, 'request_count', 0)
        error_count = getattr(request.app.state, 'error_count', 0)
        
        health_status = HealthStatus(
            status=overall_status,
            timestamp=datetime.now(),
            components=components,
            uptime_seconds=uptime_seconds,
            version="1.0.0"
        )
        
        response = health_status.to_dict()
        response.update({
            "statistics": {
                "total_requests": request_count,
                "total_errors": error_count,
                "error_rate": (error_count / max(request_count, 1)) * 100,
                "requests_per_second": round(request_count / max(uptime_seconds, 1), 2),
                "uptime_human": f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m {int(uptime_seconds % 60)}s"
            },
            "performance_metrics": {
                "memory_usage_percent": memory_usage,
                "cpu_usage_percent": cpu_usage,
                "disk_usage_percent": disk_usage,
                "system_load": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "components": {"health_check": "failed"},
            "uptime_seconds": 0,
            "version": "1.0.0"
        }

@router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check for load balancers
    
    Returns:
        Basic health status
    """
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@router.get("/performance")
async def get_performance_statistics(request: Request):
    """
    Get detailed performance statistics and metrics
    
    Returns:
        Performance metrics and system statistics
    """
    try:
        start_time = getattr(request.app.state, 'start_time', datetime.now())
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        request_count = getattr(request.app.state, 'request_count', 0)
        error_count = getattr(request.app.state, 'error_count', 0)
        
        # Performance metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        # Calculate rates and averages
        requests_per_second = round(request_count / max(uptime_seconds, 1), 2)
        errors_per_second = round(error_count / max(uptime_seconds, 1), 4)
        success_rate = round(((request_count - error_count) / max(request_count, 1)) * 100, 2)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds,
            "performance_metrics": {
                "requests_per_second": requests_per_second,
                "errors_per_second": errors_per_second,
                "success_rate_percent": success_rate,
                "total_requests": request_count,
                "total_errors": error_count
            },
            "system_resources": {
                "memory_usage_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "cpu_usage_percent": cpu_percent,
                "disk_usage_percent": round((disk.used / disk.total) * 100, 1),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "process_info": {
                "process_id": os.getpid(),
                "threads": psutil.Process().num_threads(),
                "memory_rss_mb": round(psutil.Process().memory_info().rss / (1024**2), 2),
                "cpu_percent": psutil.Process().cpu_percent()
            }
        }
        
    except Exception as e:
        logger.error(f"Performance statistics failed: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health/detailed")
async def detailed_health_check(request: Request):
    """
    Detailed health check with extended system information
    
    Returns:
        Detailed system health and performance metrics
    """
    try:
        # System information
        system_info = {
            "platform": os.name,
            "python_version": f"{psutil.PYTHON_VERSION[0]}.{psutil.PYTHON_VERSION[1]}.{psutil.PYTHON_VERSION[2]}",
            "process_id": os.getpid(),
            "working_directory": os.getcwd()
        }
        
        # Memory details
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percentage": memory.percent
        }
        
        # CPU details
        cpu_info = {
            "count": psutil.cpu_count(),
            "usage_per_core": psutil.cpu_percent(percpu=True, interval=1),
            "average_usage": psutil.cpu_percent(interval=1)
        }
        
        # Disk details
        disk = psutil.disk_usage('/')
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percentage": round((disk.used / disk.total) * 100, 1)
        }
        
        # Application statistics
        start_time = getattr(request.app.state, 'start_time', datetime.now())
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        request_count = getattr(request.app.state, 'request_count', 0)
        error_count = getattr(request.app.state, 'error_count', 0)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds,
            "uptime_human": f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m {int(uptime_seconds % 60)}s",
            "system_info": system_info,
            "memory": memory_info,
            "cpu": cpu_info,
            "disk": disk_info,
            "application_stats": {
                "total_requests": request_count,
                "total_errors": error_count,
                "error_rate_percent": round((error_count / max(request_count, 1)) * 100, 2),
                "requests_per_second": round(request_count / max(uptime_seconds, 1), 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/monitoring")
async def get_monitoring_data(request: Request):
    """
    Get real-time monitoring data for system observability
    
    Returns:
        Real-time monitoring metrics and alerts
    """
    try:
        # System metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        disk = psutil.disk_usage('/')
        
        # Application metrics
        start_time = getattr(request.app.state, 'start_time', datetime.now())
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        request_count = getattr(request.app.state, 'request_count', 0)
        error_count = getattr(request.app.state, 'error_count', 0)
        
        # Health thresholds and alerts
        alerts = []
        if memory.percent > 85:
            alerts.append({"level": "warning", "message": f"High memory usage: {memory.percent:.1f}%"})
        if memory.percent > 95:
            alerts.append({"level": "critical", "message": f"Critical memory usage: {memory.percent:.1f}%"})
        
        if cpu_percent > 80:
            alerts.append({"level": "warning", "message": f"High CPU usage: {cpu_percent:.1f}%"})
        if cpu_percent > 95:
            alerts.append({"level": "critical", "message": f"Critical CPU usage: {cpu_percent:.1f}%"})
        
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 85:
            alerts.append({"level": "warning", "message": f"High disk usage: {disk_percent:.1f}%"})
        if disk_percent > 95:
            alerts.append({"level": "critical", "message": f"Critical disk usage: {disk_percent:.1f}%"})
        
        error_rate = (error_count / max(request_count, 1)) * 100
        if error_rate > 5:
            alerts.append({"level": "warning", "message": f"High error rate: {error_rate:.1f}%"})
        if error_rate > 10:
            alerts.append({"level": "critical", "message": f"Critical error rate: {error_rate:.1f}%"})
        
        # Component status
        components_status = {
            "api_gateway": "healthy",
            "fetcher_module": "healthy",  # Would check actual module health
            "remixer_module": "healthy",  # Would check LLM API connectivity
            "memory": "healthy" if memory.percent < 85 else ("warning" if memory.percent < 95 else "critical"),
            "cpu": "healthy" if cpu_percent < 80 else ("warning" if cpu_percent < 95 else "critical"),
            "disk": "healthy" if disk_percent < 85 else ("warning" if disk_percent < 95 else "critical")
        }
        
        # Overall system status
        critical_alerts = [a for a in alerts if a["level"] == "critical"]
        warning_alerts = [a for a in alerts if a["level"] == "warning"]
        
        if critical_alerts:
            overall_status = "critical"
        elif warning_alerts:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": overall_status,
            "uptime_seconds": uptime_seconds,
            "alerts": alerts,
            "components": components_status,
            "metrics": {
                "memory_percent": round(memory.percent, 1),
                "cpu_percent": round(cpu_percent, 1),
                "disk_percent": round(disk_percent, 1),
                "requests_total": request_count,
                "errors_total": error_count,
                "error_rate_percent": round(error_rate, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Monitoring data collection failed: {str(e)}")
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "alerts": [{"level": "critical", "message": f"Monitoring system failure: {str(e)}"}]
        }

@router.get("/logs")
async def get_recent_logs(lines: int = 100):
    """
    Get recent log entries for monitoring and debugging
    
    Args:
        lines: Number of recent log lines to retrieve (default: 100)
        
    Returns:
        Recent log entries
    """
    try:
        log_files = {
            "application": "logs/spooky_rss_system.log",
            "errors": "logs/errors.log"
        }
        
        logs = {}
        for log_type, log_file in log_files.items():
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        all_lines = f.readlines()
                        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                        logs[log_type] = [line.strip() for line in recent_lines]
                else:
                    logs[log_type] = []
            except Exception as e:
                logs[log_type] = [f"Error reading log file: {str(e)}"]
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "lines_requested": lines,
            "logs": logs
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/errors")
async def get_recent_errors(lines: int = 50):
    """
    Get recent error entries for monitoring
    
    Args:
        lines: Number of recent error lines to retrieve (default: 50)
        
    Returns:
        Recent error entries
    """
    try:
        error_file = "logs/errors.log"
        
        if os.path.exists(error_file):
            with open(error_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_errors = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "total_errors": len(recent_errors),
                "errors": [line.strip() for line in recent_errors]
            }
        else:
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "total_errors": 0,
                "errors": [],
                "message": "No error log file found"
            }
            
    except Exception as e:
        logger.error(f"Failed to retrieve error logs: {str(e)}")
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }