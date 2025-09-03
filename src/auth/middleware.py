"""
Authentication Middleware for DcisionAI Platform

This module provides comprehensive authentication middleware for:
- API Key validation
- OAuth 2.0 integration
- JWT token validation
- Rate limiting
- IP restrictions
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from functools import wraps

import boto3
import jwt
from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    """Authentication context for requests."""
    tenant_id: str
    user_id: Optional[str] = None
    permissions: List[str] = None
    api_key_id: Optional[str] = None
    auth_method: str = "unknown"
    ip_address: Optional[str] = None
    rate_limit_key: Optional[str] = None


@dataclass
class RateLimitInfo:
    """Rate limiting information."""
    current: int
    limit: int
    reset_time: datetime
    remaining: int


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Main authentication middleware for DcisionAI Platform."""
    
    def __init__(self, app, config: Dict[str, Any]):
        super().__init__(app)
        self.config = config
        self.dynamodb = boto3.resource('dynamodb')
        self.redis_client = self._setup_redis()
        
        # Initialize tables
        self.api_keys_table = self.dynamodb.Table(config['api_keys_table'])
        self.admin_keys_table = self.dynamodb.Table(config['admin_keys_table'])
        self.tenants_table = self.dynamodb.Table(config['tenants_table'])
        
        # Rate limiting configuration
        self.rate_limit_config = config.get('rate_limiting', {})
        
        # OAuth configuration
        self.oauth_config = config.get('oauth', {})
        
        # JWT configuration
        self.jwt_config = config.get('jwt', {})
    
    async def dispatch(self, request: Request, call_next):
        """Process request through authentication middleware."""
        start_time = time.time()
        
        try:
            # Extract client IP
            client_ip = self._get_client_ip(request)
            
            # Check if endpoint requires authentication
            if self._requires_auth(request.url.path):
                # Authenticate request
                auth_context = await self._authenticate_request(request, client_ip)
                
                # Apply rate limiting
                rate_limit_info = await self._check_rate_limit(auth_context, client_ip)
                
                # Add authentication context to request state
                request.state.auth_context = auth_context
                request.state.rate_limit_info = rate_limit_info
                
                # Add rate limit headers
                response = await call_next(request)
                self._add_rate_limit_headers(response, rate_limit_info)
                
            else:
                # No authentication required
                response = await call_next(request)
            
            # Log request
            execution_time = time.time() - start_time
            await self._log_request(request, response, execution_time, client_ip)
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Authentication middleware error: {e}", exc_info=True)
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
        
        return True
    
    async def _authenticate_request(self, request: Request, client_ip: str) -> AuthContext:
        """Authenticate the request using available methods."""
        
        # Try admin key authentication first
        admin_key = self._extract_admin_key(request)
        if admin_key:
            return await self._validate_admin_key(admin_key, client_ip)
        
        # Try API key authentication
        api_key = self._extract_api_key(request)
        if api_key:
            return await self._validate_api_key(api_key, client_ip)
        
        # Try OAuth Bearer token
        bearer_token = self._extract_bearer_token(request)
        if bearer_token:
            return await self._validate_oauth_token(bearer_token, client_ip)
        
        # Try JWT token
        jwt_token = self._extract_jwt_token(request)
        if jwt_token:
            return await self._validate_jwt_token(jwt_token, client_ip)
        
        # No valid authentication found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide API key, admin key, OAuth token, or JWT token."
        )
    
    def _extract_admin_key(self, request: Request) -> Optional[str]:
        """Extract admin key from request headers."""
        return request.headers.get('X-Admin-Key')
    
    def _extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request headers."""
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            # Try Authorization header with Bearer prefix
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        return api_key
    
    def _extract_bearer_token(self, request: Request) -> Optional[str]:
        """Extract OAuth Bearer token from request."""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer ') and len(auth_header) > 7:
            return auth_header[7:]
        return None
    
    def _extract_jwt_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request."""
        # Check Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('JWT '):
            return auth_header[4:]  # Remove 'JWT ' prefix
        
        # Check X-JWT-Token header
        return request.headers.get('X-JWT-Token')
    
    async def _validate_api_key(self, api_key: str, client_ip: str) -> AuthContext:
        """Validate API key and return authentication context."""
        try:
            # Query DynamoDB for API key
            response = await asyncio.to_thread(
                self.api_keys_table.get_item,
                Key={'api_key': api_key}
            )
            
            if 'Item' not in response:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )
            
            api_key_data = response['Item']
            
            # Check if API key is active
            if api_key_data.get('status') != 'active':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key is inactive"
                )
            
            # Check expiration
            if api_key_data.get('expires_at'):
                expires_at = datetime.fromisoformat(api_key_data['expires_at'])
                if datetime.utcnow() > expires_at:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key has expired"
                    )
            
            # Check IP restrictions
            if api_key_data.get('ip_restrictions'):
                if not self._is_ip_allowed(client_ip, api_key_data['ip_restrictions']):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="IP address not allowed"
                    )
            
            # Get tenant information
            tenant_id = api_key_data['tenant_id']
            tenant_info = await self._get_tenant_info(tenant_id)
            
            return AuthContext(
                tenant_id=tenant_id,
                user_id=api_key_data.get('user_id'),
                permissions=api_key_data.get('permissions', []),
                api_key_id=api_key_data.get('api_key_id'),
                auth_method="api_key",
                ip_address=client_ip,
                rate_limit_key=f"rate_limit:{tenant_id}:{api_key}"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    async def _validate_admin_key(self, admin_key: str, client_ip: str) -> AuthContext:
        """Validate admin key and return authentication context."""
        try:
            logger.info(f"🔍 Validating admin key: {admin_key[:20]}...")
            
            # Query DynamoDB for admin key
            response = await asyncio.to_thread(
                self.admin_keys_table.get_item,
                Key={'admin_key': admin_key}
            )
            
            logger.info(f"📊 DynamoDB response: {response}")
            
            if 'Item' not in response:
                logger.warning("❌ Admin key not found in DynamoDB")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid admin key"
                )
            
            admin_key_data = response['Item']
            logger.info(f"✅ Admin key data retrieved: {list(admin_key_data.keys())}")
            
            # Check if admin key is active
            if admin_key_data.get('status') != 'active':
                logger.warning(f"❌ Admin key status: {admin_key_data.get('status')}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Admin key is inactive"
                )
            
            # Get tenant information
            tenant_id = admin_key_data['tenant_id']
            logger.info(f"🏢 Tenant ID: {tenant_id}")
            
            tenant_info = await self._get_tenant_info(tenant_id)
            logger.info(f"✅ Tenant info retrieved: {tenant_info}")
            
            logger.info("🔐 Creating AuthContext for admin key")
            return AuthContext(
                tenant_id=tenant_id,
                user_id=admin_key_data.get('user_id'),
                permissions=admin_key_data.get('permissions', []),
                api_key_id=admin_key_data.get('admin_key'),
                auth_method="admin_key",
                ip_address=client_ip,
                rate_limit_key=f"rate_limit:{tenant_id}:admin"
            )
            
        except HTTPException:
            logger.info("🔄 Re-raising HTTPException")
            raise
        except Exception as e:
            logger.error(f"❌ Admin key validation error: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Admin key validation error"
            )
    
    async def _validate_oauth_token(self, token: str, client_ip: str) -> AuthContext:
        """Validate OAuth token and return authentication context."""
        try:
            # Validate OAuth token with provider
            token_info = await self._validate_oauth_with_provider(token)
            
            # Extract user and tenant information
            user_id = token_info.get('user_id')
            tenant_id = token_info.get('tenant_id')
            
            if not tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid OAuth token: missing tenant information"
                )
            
            # Get tenant information
            tenant_info = await self._get_tenant_info(tenant_id)
            
            return AuthContext(
                tenant_id=tenant_id,
                user_id=user_id,
                permissions=token_info.get('permissions', []),
                auth_method="oauth",
                ip_address=client_ip,
                rate_limit_key=f"rate_limit:{tenant_id}:{user_id}"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OAuth validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth validation error"
            )
    
    async def _validate_jwt_token(self, token: str, client_ip: str) -> AuthContext:
        """Validate JWT token and return authentication context."""
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_config['secret_key'],
                algorithms=[self.jwt_config['algorithm']],
                audience=self.jwt_config.get('audience'),
                issuer=self.jwt_config.get('issuer')
            )
            
            # Check token expiration
            exp = payload.get('exp')
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT token has expired"
                )
            
            # Extract user and tenant information
            user_id = payload.get('sub')
            tenant_id = payload.get('tenant_id')
            
            if not tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid JWT token: missing tenant information"
                )
            
            # Get tenant information
            tenant_info = await self._get_tenant_info(tenant_id)
            
            return AuthContext(
                tenant_id=tenant_id,
                user_id=user_id,
                permissions=payload.get('permissions', []),
                auth_method="jwt",
                ip_address=client_ip,
                rate_limit_key=f"rate_limit:{tenant_id}:{user_id}"
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid JWT token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT validation error"
            )
    
    async def _validate_oauth_with_provider(self, token: str) -> Dict[str, Any]:
        """Validate OAuth token with the configured provider."""
        # This is a simplified implementation
        # In production, you would integrate with actual OAuth providers
        
        provider_url = self.oauth_config.get('provider_url')
        if not provider_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth provider not configured"
            )
        
        # Make request to OAuth provider to validate token
        # This is a placeholder - implement actual OAuth validation
        return {
            'user_id': 'oauth_user_123',
            'tenant_id': 'default_tenant',
            'permissions': ['read', 'write']
        }
    
    async def _get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information from DynamoDB."""
        try:
            response = await asyncio.to_thread(
                self.tenants_table.get_item,
                Key={'tenant_id': tenant_id}
            )
            
            if 'Item' not in response:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid tenant"
                )
            
            tenant_info = response['Item']
            
            # Check if tenant is active
            if tenant_info.get('status') != 'active':
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tenant account is inactive"
                )
            
            return tenant_info
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting tenant info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving tenant information"
            )
    
    async def _check_rate_limit(self, auth_context: AuthContext, client_ip: str) -> RateLimitInfo:
        """Check rate limiting for the request."""
        if not self.rate_limit_config.get('enabled', True):
            return RateLimitInfo(current=0, limit=0, reset_time=datetime.utcnow(), remaining=0)
        
        rate_limit_key = auth_context.rate_limit_key
        
        try:
            # Get current usage from Redis
            current_usage = await self._get_current_usage(rate_limit_key)
            
            # Get tenant rate limit
            tenant_limit = await self._get_tenant_rate_limit(auth_context.tenant_id)
            
            # Check if limit exceeded
            if current_usage >= tenant_limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # Increment usage
            await self._increment_usage(rate_limit_key)
            
            # Calculate reset time and remaining requests
            reset_time = await self._get_reset_time(rate_limit_key)
            remaining = tenant_limit - current_usage - 1
            
            return RateLimitInfo(
                current=current_usage + 1,
                limit=tenant_limit,
                reset_time=reset_time,
                remaining=remaining
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Don't fail the request due to rate limiting errors
            return RateLimitInfo(current=0, limit=0, reset_time=datetime.utcnow(), remaining=0)
    
    async def _get_current_usage(self, rate_limit_key: str) -> int:
        """Get current usage count from Redis."""
        if not self.redis_client:
            return 0
        
        try:
            usage = await asyncio.to_thread(
                self.redis_client.get,
                rate_limit_key
            )
            return int(usage) if usage else 0
        except Exception as e:
            logger.error(f"Error getting usage from Redis: {e}")
            return 0
    
    async def _increment_usage(self, rate_limit_key: str):
        """Increment usage count in Redis."""
        if not self.redis_client:
            return
        
        try:
            # Use Redis pipeline for atomic increment
            pipe = self.redis_client.pipeline()
            pipe.incr(rate_limit_key)
            pipe.expire(rate_limit_key, 3600)  # 1 hour TTL
            pipe.execute()
        except Exception as e:
            logger.error(f"Error incrementing usage in Redis: {e}")
    
    async def _get_reset_time(self, rate_limit_key: str) -> datetime:
        """Get reset time for rate limit window."""
        if not self.redis_client:
            return datetime.utcnow() + timedelta(hours=1)
        
        try:
            ttl = await asyncio.to_thread(
                self.redis_client.ttl,
                rate_limit_key
            )
            return datetime.utcnow() + timedelta(seconds=ttl)
        except Exception as e:
            logger.error(f"Error getting TTL from Redis: {e}")
            return datetime.utcnow() + timedelta(hours=1)
    
    async def _get_tenant_rate_limit(self, tenant_id: str) -> int:
        """Get rate limit for tenant."""
        try:
            response = await asyncio.to_thread(
                self.tenants_table.get_item,
                Key={'tenant_id': tenant_id}
            )
            
            if 'Item' in response:
                tenant_info = response['Item']
                settings = tenant_info.get('settings', {})
                rate_limit = settings.get('rate_limit', '1000/hour')
                
                # Parse rate limit string (e.g., "1000/hour")
                if '/' in rate_limit:
                    limit, period = rate_limit.split('/')
                    if period == 'hour':
                        return int(limit)
                    elif period == 'minute':
                        return int(limit) * 60
                    elif period == 'second':
                        return int(limit) * 3600
                
                return int(rate_limit)
            
            return 1000  # Default rate limit
            
        except Exception as e:
            logger.error(f"Error getting tenant rate limit: {e}")
            return 1000  # Default rate limit
    
    def _is_ip_allowed(self, client_ip: str, allowed_ips: List[str]) -> bool:
        """Check if client IP is allowed."""
        # Simple IP validation - in production, use proper CIDR validation
        return client_ip in allowed_ips
    
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
    
    def _add_rate_limit_headers(self, response: Response, rate_limit_info: RateLimitInfo):
        """Add rate limit headers to response."""
        response.headers['X-RateLimit-Limit'] = str(rate_limit_info.limit)
        response.headers['X-RateLimit-Remaining'] = str(rate_limit_info.remaining)
        response.headers['X-RateLimit-Reset'] = rate_limit_info.reset_time.isoformat()
    
    async def _log_request(self, request: Request, response: Response, execution_time: float, client_ip: str):
        """Log request details for audit purposes."""
        try:
            auth_context = getattr(request.state, 'auth_context', None)
            
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'method': request.method,
                'path': str(request.url.path),
                'status_code': response.status_code,
                'execution_time': execution_time,
                'client_ip': client_ip,
                'user_agent': request.headers.get('User-Agent'),
                'tenant_id': auth_context.tenant_id if auth_context else None,
                'user_id': auth_context.user_id if auth_context else None,
                'auth_method': auth_context.auth_method if auth_context else None
            }
            
            logger.info(f"Request: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Error logging request: {e}")
    
    def _setup_redis(self):
        """Setup Redis client for rate limiting."""
        try:
            import redis
            redis_config = self.config.get('redis', {})
            
            if redis_config.get('enabled', False):
                return redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    password=redis_config.get('password'),
                    decode_responses=True
                )
        except ImportError:
            logger.warning("Redis not available, rate limiting will be disabled")
        except Exception as e:
            logger.error(f"Error setting up Redis: {e}")
        
        return None


# Dependency functions for FastAPI
async def get_auth_context(request: Request) -> AuthContext:
    """Get authentication context from request."""
    auth_context = getattr(request.state, 'auth_context', None)
    if not auth_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return auth_context


async def require_permission(permission: str):
    """Dependency to require specific permission."""
    async def permission_checker(auth_context: AuthContext = Depends(get_auth_context)):
        if permission not in auth_context.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return auth_context
    
    return permission_checker


async def require_tenant_access(tenant_id: str):
    """Dependency to require access to specific tenant."""
    async def tenant_checker(auth_context: AuthContext = Depends(get_auth_context)):
        if auth_context.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )
        return auth_context
    
    return tenant_checker


# Utility functions
def generate_api_key(prefix: str = "dcisionai") -> str:
    """Generate a secure API key."""
    import secrets
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(16)
    return f"{prefix}_{timestamp}_{random_part}"


def hash_secret(secret: str, salt: Optional[str] = None) -> str:
    """Hash a secret with salt."""
    if not salt:
        salt = secrets.token_hex(16)
    
    hash_obj = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt.encode(), 100000)
    return f"{salt}:{hash_obj.hex()}"


def verify_secret(secret: str, hashed_secret: str) -> bool:
    """Verify a secret against its hash."""
    try:
        salt, hash_value = hashed_secret.split(':', 1)
        expected_hash = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt.encode(), 100000)
        return hmac.compare_digest(expected_hash.hex(), hash_value)
    except Exception:
        return False
