"""
Health Service
Handles health checks and system monitoring
"""

import os
import psutil
from typing import Dict, Any
from datetime import datetime

from utils.logger import get_logger
from .base_service import BaseService

logger = get_logger(__name__)

class HealthService(BaseService):
    """Service for health monitoring and system status"""
    
    def __init__(self):
        super().__init__()
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            # Check API key configuration
            api_key_status = self._check_api_key()
            
            # Check system resources
            system_resources = self._get_system_resources()
            
            # Check service dependencies
            dependencies = await self._check_dependencies()
            
            # Overall health status
            overall_status = "healthy"
            if not api_key_status["configured"] or not dependencies["all_healthy"]:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "api_key": api_key_status,
                "system_resources": system_resources,
                "dependencies": dependencies,
                "uptime": self.get_service_info()["uptime"]
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_api_key(self) -> Dict[str, Any]:
        """Check API key configuration"""
        api_key = os.getenv("GOOGLE_API_KEY")
        
        return {
            "configured": bool(api_key and api_key != "your_google_api_key_here"),
            "has_value": bool(api_key),
            "is_placeholder": api_key == "your_google_api_key_here" if api_key else True
        }
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                    "used": disk.used
                }
            }
        except Exception as e:
            logger.warning(f"Failed to get system resources: {e}")
            return {
                "error": str(e),
                "cpu_percent": None,
                "memory": None,
                "disk": None
            }
    
    async def _check_dependencies(self) -> Dict[str, Any]:
        """Check service dependencies"""
        dependencies = {
            "google_genai": False,
            "langchain": False,
            "vector_db": False,
            "all_healthy": False
        }
        
        try:
            # Check Google Generative AI
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                dependencies["google_genai"] = True
            except ImportError:
                pass
            
            # Check LangChain
            try:
                import langchain
                dependencies["langchain"] = True
            except ImportError:
                pass
            
            # Check vector database
            try:
                import faiss
                dependencies["vector_db"] = True
            except ImportError:
                pass
            
            # Overall health
            dependencies["all_healthy"] = all([
                dependencies["google_genai"],
                dependencies["langchain"],
                dependencies["vector_db"]
            ])
            
        except Exception as e:
            logger.warning(f"Failed to check dependencies: {e}")
        
        return dependencies
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for health service itself"""
        return {
            "status": "healthy",
            "service": "health",
            "timestamp": datetime.now().isoformat(),
            "uptime": self.get_service_info()["uptime"]
        }
