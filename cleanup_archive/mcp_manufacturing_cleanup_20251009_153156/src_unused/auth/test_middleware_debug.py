"""
Debug version of the authentication middleware
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

class DebugAuthenticationMiddleware(BaseHTTPMiddleware):
    """Debug version of authentication middleware."""
    
    def __init__(self, app, config: Dict[str, Any]):
        super().__init__(app)
        self.config = config
        logger.info(f"🔧 Debug middleware initialized with config: {config}")
    
    async def dispatch(self, request: Request, call_next):
        """Process request through debug middleware."""
        start_time = datetime.utcnow()
        
        logger.info(f"🔍 Debug middleware processing: {request.method} {request.url.path}")
        
        try:
            # Extract client IP
            client_ip = self._get_client_ip(request)
            logger.info(f"📍 Client IP: {client_ip}")
            
            # Check if endpoint requires authentication
            requires_auth = self._requires_auth(request.url.path)
            logger.info(f"🔐 Endpoint requires auth: {requires_auth}")
            
            if requires_auth:
                logger.info("🔑 Attempting authentication...")
                
                # Extract API key
                api_key = self._extract_api_key(request)
                logger.info(f"🔑 API key extracted: {api_key[:20] if api_key else 'None'}...")
                
                if api_key:
                    logger.info("🔑 API key found, attempting validation...")
                    try:
                        # For now, just log that we would validate
                        logger.info("🔑 Would validate API key here")
                        # In real implementation, this would validate against DynamoDB
                    except Exception as e:
                        logger.error(f"❌ API key validation error: {e}")
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"API key validation failed: {str(e)}"
                        )
                else:
                    logger.warning("⚠️  No API key found in request")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required. Please provide API key."
                    )
            
            # Process request
            response = await call_next(request)
            
            # Log response
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"✅ Request processed: {request.method} {request.url.path} -> {response.status_code} ({execution_time:.3f}s)")
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions
            logger.info(f"🚫 HTTP exception raised: {request.method} {request.url.path}")
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"❌ Debug middleware error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal authentication error"
            )
    
    def _requires_auth(self, path: str) -> bool:
        """Check if endpoint requires authentication."""
        # Public endpoints that don't require authentication
        public_endpoints = {
            '/',
            '/health',
            '/health/detailed',
            '/docs',
            '/openapi.json'
        }
        
        # Check for exact matches first, then prefix matches
        if path in public_endpoints:
            return False
        
        # For prefix matches, only match exact path segments
        for endpoint in public_endpoints:
            if endpoint != '/' and path.startswith(endpoint + '/'):
                return False
        
        requires = True
        logger.info(f"🔐 Path {path} requires auth: {requires}")
        return requires
    
    def _extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request headers."""
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            # Try Authorization header with Bearer prefix
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        logger.info(f"🔑 API key extracted: {api_key[:20] if api_key else 'None'}...")
        return api_key
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else 'unknown'

# Test the middleware
async def test_middleware():
    """Test the debug middleware."""
    print("🧪 Testing Debug Middleware...")
    
    # Create a mock config
    config = {
        'environment': 'test',
        'api_keys_table': 'dcisionai-api-keys-dev',
        'admin_keys_table': 'dcisionai-admin-keys-dev',
        'tenants_table': 'dcisionai-tenants-dev'
    }
    
    # Create middleware instance
    middleware = DebugAuthenticationMiddleware(None, config)
    print("✅ Debug middleware created successfully")
    
    # Test path authentication logic
    test_paths = ['/', '/health', '/protected', '/admin']
    for path in test_paths:
        requires = middleware._requires_auth(path)
        print(f"   {path}: requires auth = {requires}")

if __name__ == "__main__":
    asyncio.run(test_middleware())
