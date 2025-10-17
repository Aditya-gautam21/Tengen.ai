"""
Tengen.ai Production Backend
FastAPI application for AI inference and research assistance
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from services.inference import InferenceService
from services.health import HealthService
from utils.logger import setup_logging, get_logger
from utils.middleware import LoggingMiddleware
from api.routes import inference, health, logs

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Tengen.ai backend...")
    
    # Initialize services
    try:
        app.state.inference_service = InferenceService()
        app.state.health_service = HealthService()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    logger.info("Shutting down Tengen.ai backend...")

# Create FastAPI app
app = FastAPI(
    title="Tengen.ai API",
    description="Production-ready AI inference and research assistant API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[host.strip() for host in allowed_hosts] + ["*"] if os.getenv("ENVIRONMENT") == "development" else [host.strip() for host in allowed_hosts]
)

# Rate limiting middleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware with security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-ID"],
)

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(inference.router, prefix="/api/v1", tags=["inference"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(logs.router, prefix="/api/v1", tags=["logs"])

@app.get("/")
@limiter.limit("30/minute")
async def root(request):
    """Root endpoint with rate limiting"""
    from utils.security import SecurityHeaders
    
    response_data = {
        "message": "Tengen.ai API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
    
    response = JSONResponse(content=response_data)
    
    # Add security headers
    for header, value in SecurityHeaders.get_security_headers().items():
        response.headers[header] = value
    
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    # Production configuration
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False  # Disable reload in production
    )
