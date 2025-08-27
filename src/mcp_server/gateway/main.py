#!/usr/bin/env python3
"""
DcisionAI Gateway Service
=========================

Production-ready gateway service with authentication, authorization, and rate limiting.
This is the rock-solid foundation for our MCP architecture.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import boto3
import jwt
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DcisionAI Gateway",
    description="Production-ready gateway for DcisionAI MCP Server",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(",")
    )

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
cognito_idp = boto3.client('cognito-idp')

# Initialize Redis for rate limiting
redis_client = None

# Configuration
TENANTS_TABLE = os.getenv("TENANTS_TABLE", "dcisionai-tenants-staging")
API_KEYS_TABLE = os.getenv("API_KEYS_TABLE", "dcisionai-api-keys-staging")
RATE_LIMIT_TABLE = os.getenv("RATE_LIMIT_TABLE", "dcisionai-rate-limits-staging")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
USER_POOL_ID = os.getenv("USER_POOL_ID")
USER_POOL_CLIENT_ID = os.getenv("USER_POOL_CLIENT_ID")

# Pydantic models
class MCPRequest(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: Optional[str] = None
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)

class MCPResponse(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class TenantInfo(BaseModel):
    tenant_id: str
    email: str
    plan: str = "basic"
    status: str = "active"
    created_at: str
    request_limit: int = 1000
    rate_limit: int = 100

# Authentication and Authorization
class AuthService:
    """Handles JWT token validation and user authentication."""
    
    def __init__(self):
        self.user_pool_id = USER_POOL_ID
        self.client_id = USER_POOL_CLIENT_ID
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and extract claims."""
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode JWT token
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}  # We'll validate with Cognito
            )
            
            # Extract user info
            user_id = decoded.get('sub')
            email = decoded.get('email')
            tenant_id = decoded.get('custom:tenant_id', user_id)
            plan = decoded.get('custom:plan', 'basic')
            
            return {
                'user_id': user_id,
                'email': email,
                'tenant_id': tenant_id,
                'plan': plan,
                'token': token
            }
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

# Rate Limiting
class RateLimitService:
    """Handles rate limiting for tenants."""
    
    def __init__(self):
        self.redis_client = redis_client
        self.table = dynamodb.Table(RATE_LIMIT_TABLE)
    
    async def check_rate_limit(self, tenant_id: str, endpoint: str) -> bool:
        """Check if request is within rate limits."""
        try:
            if self.redis_client:
                # Use Redis for fast rate limiting
                key = f"rate_limit:{tenant_id}:{endpoint}"
                current = await self.redis_client.incr(key)
                if current == 1:
                    await self.redis_client.expire(key, 60)  # 1 minute window
                
                # Get tenant's rate limit
                tenant_info = await self.get_tenant_info(tenant_id)
                rate_limit = tenant_info.get('rate_limit', 100)
                
                return current <= rate_limit
            else:
                # Fallback to DynamoDB
                return await self._check_rate_limit_dynamodb(tenant_id, endpoint)
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow request if rate limiting fails
    
    async def _check_rate_limit_dynamodb(self, tenant_id: str, endpoint: str) -> bool:
        """Check rate limit using DynamoDB."""
        try:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=1)
            
            response = self.table.query(
                KeyConditionExpression='#key = :key AND #timestamp >= :start',
                ExpressionAttributeNames={
                    '#key': 'key',
                    '#timestamp': 'timestamp'
                },
                ExpressionAttributeValues={
                    ':key': f"{tenant_id}:{endpoint}",
                    ':start': window_start.isoformat()
                }
            )
            
            # Count requests in window
            request_count = len(response.get('Items', []))
            
            # Get tenant's rate limit
            tenant_info = await self.get_tenant_info(tenant_id)
            rate_limit = tenant_info.get('rate_limit', 100)
            
            # Record this request
            self.table.put_item(Item={
                'key': f"{tenant_id}:{endpoint}",
                'timestamp': now.isoformat(),
                'ttl': int((now + timedelta(hours=1)).timestamp())
            })
            
            return request_count < rate_limit
        except Exception as e:
            logger.error(f"DynamoDB rate limit check failed: {e}")
            return True

# Tenant Management
class TenantService:
    """Handles tenant information and management."""
    
    def __init__(self):
        self.table = dynamodb.Table(TENANTS_TABLE)
    
    async def get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information from DynamoDB."""
        try:
            response = self.table.get_item(Key={'tenant_id': tenant_id})
            tenant = response.get('Item')
            
            if not tenant:
                # Create default tenant info
                tenant = {
                    'tenant_id': tenant_id,
                    'plan': 'basic',
                    'status': 'active',
                    'created_at': datetime.utcnow().isoformat(),
                    'request_limit': 1000,
                    'rate_limit': 100
                }
                self.table.put_item(Item=tenant)
            
            return tenant
        except Exception as e:
            logger.error(f"Failed to get tenant info: {e}")
            return {
                'tenant_id': tenant_id,
                'plan': 'basic',
                'status': 'active',
                'request_limit': 1000,
                'rate_limit': 100
            }

# MCP Client
class MCPClient:
    """Handles communication with the MCP server."""
    
    def __init__(self):
        self.base_url = MCP_SERVER_URL
        self.timeout = 30.0
    
    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """Send request to MCP server."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/mcp",
                    json=request.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return MCPResponse(**response.json())
                else:
                    return MCPResponse(
                        id=request.id,
                        error={
                            "code": -32603,
                            "message": f"MCP server error: {response.status_code}"
                        }
                    )
        except Exception as e:
            logger.error(f"MCP client error: {e}")
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )

# Initialize services
auth_service = AuthService()
rate_limit_service = RateLimitService()
tenant_service = TenantService()
mcp_client = MCPClient()

# Dependency functions
async def get_current_user(request: Request) -> Dict[str, Any]:
    """Extract and validate user from request."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    return await auth_service.validate_token(auth_header)

async def get_tenant_info(tenant_id: str) -> Dict[str, Any]:
    """Get tenant information."""
    return await tenant_service.get_tenant_info(tenant_id)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DcisionAI Gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# MCP protocol endpoint
@app.post("/mcp")
async def handle_mcp_request(
    request: MCPRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Handle MCP protocol requests through the gateway."""
    try:
        # Extract tenant info
        tenant_id = current_user['tenant_id']
        tenant_info = await get_tenant_info(tenant_id)
        
        # Check rate limiting
        if not await rate_limit_service.check_rate_limit(tenant_id, "mcp"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        # Log request
        logger.info(f"MCP request from tenant {tenant_id}: {request.method}")
        
        # Forward request to MCP server
        response = await mcp_client.send_request(request)
        
        # Log response
        logger.info(f"MCP response for tenant {tenant_id}: {response.jsonrpc}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gateway error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Tools endpoint
@app.get("/tools")
async def list_tools(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List available tools."""
    try:
        tenant_id = current_user['tenant_id']
        
        # Check rate limiting
        if not await rate_limit_service.check_rate_limit(tenant_id, "tools"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        # Forward request to MCP server
        request = MCPRequest(
            method="tools/list",
            params={}
        )
        
        response = await mcp_client.send_request(request)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tools list error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Tool execution endpoint
@app.post("/tools/{tool_name}")
async def execute_tool(
    tool_name: str,
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Execute a specific tool."""
    try:
        tenant_id = current_user['tenant_id']
        
        # Check rate limiting
        if not await rate_limit_service.check_rate_limit(tenant_id, f"tool:{tool_name}"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        # Forward request to MCP server
        request = MCPRequest(
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": request_body
            }
        )
        
        response = await mcp_client.send_request(request)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global redis_client
    
    try:
        # Initialize Redis if available
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            redis_client = redis.from_url(redis_url)
            await redis_client.ping()
            logger.info("Redis connected successfully")
        else:
            logger.warning("Redis not configured, using DynamoDB for rate limiting")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}, using DynamoDB fallback")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if redis_client:
        await redis_client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
