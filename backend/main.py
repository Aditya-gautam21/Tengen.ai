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
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(inference.router, prefix="/api/v1", tags=["inference"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(logs.router, prefix="/api/v1", tags=["logs"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tengen.ai API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

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
