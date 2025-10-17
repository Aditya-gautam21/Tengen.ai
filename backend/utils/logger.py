"""
Logging Configuration
Production-ready logging setup with rotation and structured logging
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional
import json

def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """
    Setup production-ready logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    """
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "tengen.log"),
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "tengen_errors.log"),
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # API access log handler
    access_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "tengen_access.log"),
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(detailed_formatter)
    
    # Create access logger
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    access_logger.propagate = False
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class StructuredLogger:
    """Structured logging for JSON-formatted logs"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, status_code: int, 
                   response_time: float, user_agent: Optional[str] = None,
                   client_ip: Optional[str] = None):
        """Log HTTP request in structured format"""
        log_data = {
            "type": "http_request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
            "user_agent": user_agent,
            "client_ip": client_ip
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_inference(self, request_type: str, processing_time: float, 
                     status: str, error: Optional[str] = None):
        """Log inference request in structured format"""
        log_data = {
            "type": "inference",
            "request_type": request_type,
            "processing_time": processing_time,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            log_data["error"] = error
        
        if status == "success":
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.error(json.dumps(log_data))
    
    def log_health_check(self, service: str, status: str, details: Optional[Dict] = None):
        """Log health check in structured format"""
        log_data = {
            "type": "health_check",
            "service": service,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            log_data["details"] = details
        
        self.logger.info(json.dumps(log_data))

def get_structured_logger(name: str = "structured") -> StructuredLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name
    
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(get_logger(name))
