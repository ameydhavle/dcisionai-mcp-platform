"""
DcisionAI Platform API Test Application

This application includes the full API endpoints for testing the complete functionality
"""

import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from middleware import AuthenticationMiddleware
from config import get_minimal_config
from api_endpoints import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="DcisionAI Platform API",
    description="Enterprise-grade AI platform API for tool invocation, job management, and tenant administration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get configuration
config = get_minimal_config()

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware, config=config)

# Include API endpoints
app.include_router(api_router)

# Add root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DcisionAI Platform API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Add health endpoint (public)
@app.get("/health")
async def health():
    """Public health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dcisionai-platform-api"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting DcisionAI Platform API Test Application...")
    logger.info(f"📋 Configuration: {config}")
    
    uvicorn.run(
        "test_api_app:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
