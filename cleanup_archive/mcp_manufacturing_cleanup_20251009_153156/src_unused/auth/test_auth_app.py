#!/usr/bin/env python3
"""
Simple Authentication Test App for DcisionAI Platform

This app demonstrates API key authentication with a clean, simple interface.
It shows how to:
- Protect endpoints with API key authentication
- Handle different permission levels
- Provide clear error messages for authentication failures
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import our authentication middleware
from middleware import AuthenticationMiddleware, get_auth_context, require_permission, require_tenant_access
from config import get_minimal_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DcisionAI Platform - Authentication Test",
    description="Simple test application for API key authentication",
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


# ============================================================================
# PUBLIC ENDPOINTS (No Authentication Required)
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - no authentication required."""
    return {
        "message": "DcisionAI Platform Authentication Test",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "running",
        "endpoints": {
            "public": ["/", "/health", "/docs", "/openapi.json"],
            "protected": ["/protected", "/admin", "/tenant/{tenant_id}"],
            "authentication": "Use X-API-Key header with your API key"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint - no authentication required."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dcisionai-auth-test",
        "authentication": "enabled",
        "middleware": "active"
    }


# ============================================================================
# PROTECTED ENDPOINTS (API Key Authentication Required)
# ============================================================================

@app.get("/protected")
async def protected_endpoint(auth_context = Depends(get_auth_context)):
    """Protected endpoint - requires valid API key."""
    return {
        "message": "✅ Access granted to protected endpoint",
        "authentication": {
            "method": auth_context.auth_method,
            "tenant_id": auth_context.tenant_id,
            "user_id": auth_context.user_id,
            "permissions": auth_context.permissions,
            "ip_address": auth_context.ip_address
        },
        "timestamp": datetime.utcnow().isoformat(),
        "note": "This endpoint requires a valid API key in X-API-Key header"
    }


@app.get("/admin")
async def admin_endpoint(auth_context = Depends(get_auth_context)):
    """Admin endpoint - requires admin permission."""
    # Check admin permission manually
    if "admin" not in auth_context.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Admin permission required",
                "required_permissions": ["admin"],
                "current_permissions": auth_context.permissions,
                "suggestion": "Use an admin key or contact your administrator"
            }
        )
    
    return {
        "message": "🔐 Access granted to admin endpoint",
        "authentication": {
            "method": auth_context.auth_method,
            "tenant_id": auth_context.tenant_id,
            "user_id": auth_context.user_id,
            "permissions": auth_context.permissions,
            "ip_address": auth_context.ip_address
        },
        "admin_features": [
            "User management",
            "API key management", 
            "Tenant configuration",
            "System monitoring"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/tenant/{tenant_id}")
async def tenant_endpoint(tenant_id: str, auth_context = Depends(get_auth_context)):
    """Tenant-specific endpoint - requires access to specific tenant."""
    # Check if user has access to this tenant
    if auth_context.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied to tenant",
                "requested_tenant": tenant_id,
                "authenticated_tenant": auth_context.tenant_id,
                "suggestion": "Use an API key for the correct tenant"
            }
        )
    
    return {
        "message": f"🏢 Access granted to tenant {tenant_id}",
        "tenant_info": {
            "tenant_id": tenant_id,
            "authenticated_user": auth_context.user_id,
            "permissions": auth_context.permissions
        },
        "tenant_endpoints": [
            f"/tenant/{tenant_id}/users",
            f"/tenant/{tenant_id}/settings",
            f"/tenant/{tenant_id}/analytics"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# API KEY MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/auth/validate-key")
async def validate_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Validate an API key and return its information."""
    try:
        # Import the manager here to avoid circular imports
        from manage_api_keys import APIKeyManager
        
        manager = APIKeyManager()
        result = await manager.validate_api_key(x_api_key)
        
        if result['valid']:
            return {
                "valid": True,
                "message": "API key is valid",
                "key_info": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "valid": False,
                "error": result['error'],
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"API key validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Validation service error",
                "message": str(e)
            }
        )


@app.get("/auth/keys")
async def list_api_keys(auth_context = Depends(get_auth_context)):
    """List API keys for the authenticated tenant (admin only)."""
    # Check admin permission
    if "admin" not in auth_context.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Admin permission required",
                "required_permissions": ["admin"],
                "current_permissions": auth_context.permissions
            }
        )
    
    try:
        from manage_api_keys import APIKeyManager
        
        manager = APIKeyManager()
        keys = await manager.list_api_keys(auth_context.tenant_id)
        
        return {
            "message": f"API keys for tenant {auth_context.tenant_id}",
            "tenant_id": auth_context.tenant_id,
            "keys": keys,
            "count": len(keys),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve API keys",
                "message": str(e)
            }
        )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler for better error messages."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "method": request.method,
            "help": {
                "authentication": "Include X-API-Key header with valid API key",
                "permissions": "Ensure your API key has required permissions",
                "documentation": "See /docs for API documentation"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "method": request.method,
            "help": "Contact support if this error persists"
        }
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_auth_headers(api_key: str) -> Dict[str, str]:
    """Helper function to get authentication headers for testing."""
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }


# ============================================================================
# MAIN FUNCTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting DcisionAI Authentication Test App...")
    print("📚 API Documentation: http://localhost:8003/docs")
    print("🔐 Test endpoints:")
    print("   - GET  /                    (public)")
    print("   - GET  /health              (public)")
    print("   - GET  /protected           (requires API key)")
    print("   - GET  /admin               (requires admin permission)")
    print("   - GET  /tenant/{tenant_id}  (requires tenant access)")
    print("   - POST /auth/validate-key   (validate API key)")
    print("   - GET  /auth/keys           (list keys, admin only)")
    print()
    print("💡 To test authentication:")
    print("   1. Create an API key using manage_api_keys.py")
    print("   2. Include it in X-API-Key header")
    print("   3. Test protected endpoints")
    
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)
