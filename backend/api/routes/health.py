"""
Health Routes
API endpoints for health checks and system monitoring
"""

from fastapi import APIRouter, Depends, Request
from services.health import HealthService

router = APIRouter()

def get_health_service(request: Request) -> HealthService:
    """Dependency to get health service"""
    return request.app.state.health_service

@router.get("/health")
async def health_check(
    health_service: HealthService = Depends(get_health_service)
):
    """
    Basic health check endpoint
    
    Returns:
        Basic health status
    """
    return await health_service.health_check()

@router.get("/health/detailed")
async def detailed_health_check(
    health_service: HealthService = Depends(get_health_service)
):
    """
    Detailed health check endpoint
    
    Returns:
        Comprehensive system health status
    """
    return await health_service.get_system_health()

@router.get("/health/ready")
async def readiness_check(
    health_service: HealthService = Depends(get_health_service)
):
    """
    Readiness check endpoint for Kubernetes/Docker
    
    Returns:
        Ready status
    """
    health_status = await health_service.get_system_health()
    
    if health_status.get("status") == "healthy":
        return {"status": "ready"}
    else:
        return {"status": "not_ready", "details": health_status}

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes/Docker
    
    Returns:
        Live status
    """
    return {"status": "alive"}
