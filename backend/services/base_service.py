"""
Base Service Class
Common functionality for all services
"""

from abc import ABC
from typing import Dict, Any
from datetime import datetime

class BaseService(ABC):
    """Base service class with common functionality"""
    
    def __init__(self):
        self.service_name = self.__class__.__name__
        self.start_time = datetime.now()
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            "service_name": self.service_name,
            "start_time": self.start_time.isoformat(),
            "uptime": (datetime.now() - self.start_time).total_seconds()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Base health check implementation"""
        return {
            "status": "healthy",
            "service": self.service_name,
            "timestamp": datetime.now().isoformat()
        }
