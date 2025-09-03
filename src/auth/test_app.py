"""
Test FastAPI application for DcisionAI Authentication Middleware

This app demonstrates the authentication middleware functionality
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import our authentication middleware
from middleware import AuthenticationMiddleware, get_auth_context, require_permission, require_tenant_access
from config import get_minimal_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DcisionAI Platform - Authentication Test",
    description="Test application for authentication middleware",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
auth_config = get_minimal_config()
app.add_middleware(AuthenticationMiddleware, config=auth_config)

# Test endpoints
@app.get("/")
async def root():
    """Root endpoint - no authentication required."""
    return {
        "message": "DcisionAI Platform Authentication Test",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint - no authentication required."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dcisionai-auth-test"
    }

@app.get("/protected")
async def protected_endpoint(auth_context = Depends(get_auth_context)):
    """Protected endpoint - requires authentication."""
    return {
        "message": "Access granted to protected endpoint",
        "user": {
            "tenant_id": auth_context.tenant_id,
            "user_id": auth_context.user_id,
            "auth_method": auth_context.auth_method,
            "permissions": auth_context.permissions
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/admin")
async def admin_endpoint(auth_context = Depends(get_auth_context)):
    """Admin endpoint - requires admin permission."""
    # Check admin permission manually
    if "admin" not in auth_context.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    
    return {
        "message": "Access granted to admin endpoint",
        "user": {
            "tenant_id": auth_context.tenant_id,
            "user_id": auth_context.user_id,
            "auth_method": auth_context.auth_method,
            "permissions": auth_context.permissions
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/tenant/{tenant_id}")
async def tenant_endpoint(tenant_id: str, auth_context = Depends(get_auth_context)):
    """Tenant-specific endpoint - requires access to specific tenant."""
    # Check tenant access manually
    if auth_context.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    return {
        "message": f"Access granted to tenant {tenant_id}",
        "user": {
            "tenant_id": auth_context.tenant_id,
            "user_id": auth_context.user_id,
            "auth_method": auth_context.auth_method,
            "permissions": auth_context.permissions
        },
        "requested_tenant": tenant_id,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/test-api-key")
async def test_api_key(request: Request):
    """Test endpoint for API key authentication."""
    # This endpoint will be processed by the middleware
    # We can access the auth context from request.state
    auth_context = getattr(request.state, 'auth_context', None)
    
    if not auth_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return {
        "message": "API key authentication successful",
        "user": {
            "tenant_id": auth_context.tenant_id,
            "user_id": auth_context.user_id,
            "auth_method": auth_context.auth_method,
            "permissions": auth_context.permissions
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/rate-limit-test")
async def rate_limit_test(request: Request):
    """Test endpoint for rate limiting."""
    # This endpoint will be processed by the middleware
    # We can access the rate limit info from request.state
    rate_limit_info = getattr(request.state, 'rate_limit_info', None)
    
    return {
        "message": "Rate limit test endpoint",
        "rate_limit": {
            "current": rate_limit_info.current if rate_limit_info else 0,
            "limit": rate_limit_info.limit if rate_limit_info else 0,
            "remaining": rate_limit_info.remaining if rate_limit_info else 0,
            "reset_time": rate_limit_info.reset_time.isoformat() if rate_limit_info else None
        } if rate_limit_info else None,
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("🚀 DcisionAI Authentication Test App starting up...")
    logger.info(f"📋 Configuration: {auth_config}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("🛑 DcisionAI Authentication Test App shutting down...")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting test application...")
    uvicorn.run(
        "test_app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
