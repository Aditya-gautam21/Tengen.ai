"""
Custom Middleware
Production-ready middleware for logging, security, and monitoring
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from utils.logger import get_structured_logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_structured_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Start timing
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            processing_time = time.time() - start_time
            self.logger.log_request(
                method=request.method,
                path=str(request.url.path),
                status_code=500,
                response_time=processing_time,
                user_agent=user_agent,
                client_ip=client_ip
            )
            raise
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log request
        self.logger.log_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            response_time=processing_time,
            user_agent=user_agent,
            client_ip=client_ip
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(processing_time)
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if any(t > current_time - 60 for t in times)
        }
        
        # Check rate limit
        if client_ip in self.requests:
            recent_requests = [t for t in self.requests[client_ip] if t > current_time - 60]
            if len(recent_requests) >= self.requests_per_minute:
                return StarletteResponse(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": "60"}
                )
            self.requests[client_ip] = recent_requests + [current_time]
        else:
            self.requests[client_ip] = [current_time]
        
        response = await call_next(request)
        return response
