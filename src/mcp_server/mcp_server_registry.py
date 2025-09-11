#!/usr/bin/env python3
"""
DcisionAI MCP Server Registry
============================

Public registry for MCP server discovery and connection information.
Enables customers to easily discover and connect to DcisionAI MCP servers.

Features:
- MCP server discovery and metadata
- Health status monitoring
- Tool catalog and capabilities
- Connection information and authentication
- Version management and compatibility

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

logger = logging.getLogger(__name__)

class ServerStatus(Enum):
    """MCP server status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class AuthenticationType(Enum):
    """Authentication type enumeration."""
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    NONE = "none"

@dataclass
class MCPTool:
    """MCP tool information."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    category: str
    version: str = "1.0.0"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class MCPServer:
    """MCP server information."""
    server_id: str
    name: str
    version: str
    description: str
    endpoint: str
    authentication: AuthenticationType
    status: ServerStatus
    tools: List[MCPTool]
    capabilities: List[str]
    region: str
    last_updated: datetime
    health_check_url: Optional[str] = None
    documentation_url: Optional[str] = None
    support_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['authentication'] = self.authentication.value
        data['status'] = self.status.value
        data['last_updated'] = self.last_updated.isoformat()
        return data

class MCPRegistry:
    """MCP server registry for discovery and management."""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.health_check_interval = 60  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Initialize with DcisionAI Manufacturing MCP Server
        self._initialize_default_servers()
        
        logger.info("🔍 MCP Server Registry initialized")
    
    def _initialize_default_servers(self):
        """Initialize registry with default DcisionAI servers."""
        
        # DcisionAI Manufacturing MCP Server
        manufacturing_tools = [
            MCPTool(
                name="manufacturing_intent_classification",
                description="Classify manufacturing intent using 5-agent peer-to-peer swarm collaboration",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Manufacturing query to classify"},
                        "context": {"type": "object", "description": "Optional context information"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "intent": {"type": "string"},
                        "confidence": {"type": "number"},
                        "entities": {"type": "array"},
                        "objectives": {"type": "array"},
                        "reasoning": {"type": "string"}
                    }
                },
                category="intent_classification",
                tags=["manufacturing", "intent", "classification", "swarm"]
            ),
            MCPTool(
                name="manufacturing_data_analysis",
                description="Analyze manufacturing data using 3-agent peer-to-peer swarm collaboration",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "object", "description": "Manufacturing data to analyze"},
                        "intent_result": {"type": "object", "description": "Intent classification result"}
                    },
                    "required": ["data", "intent_result"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "entities": {"type": "array"},
                        "data_requirements": {"type": "array"},
                        "insights": {"type": "array"},
                        "optimization_readiness_score": {"type": "number"}
                    }
                },
                category="data_analysis",
                tags=["manufacturing", "data", "analysis", "swarm"]
            ),
            MCPTool(
                name="manufacturing_model_builder",
                description="Build mathematical optimization models using 4-agent peer-to-peer swarm collaboration",
                input_schema={
                    "type": "object",
                    "properties": {
                        "intent_result": {"type": "object", "description": "Intent classification result"},
                        "data_result": {"type": "object", "description": "Data analysis result"}
                    },
                    "required": ["intent_result", "data_result"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "model_type": {"type": "string"},
                        "variables": {"type": "array"},
                        "constraints": {"type": "array"},
                        "objectives": {"type": "array"},
                        "model_insights": {"type": "array"}
                    }
                },
                category="model_building",
                tags=["manufacturing", "model", "optimization", "swarm"]
            ),
            MCPTool(
                name="manufacturing_optimization_solver",
                description="Solve optimization problems using 6-agent peer-to-peer swarm collaboration",
                input_schema={
                    "type": "object",
                    "properties": {
                        "model_result": {"type": "object", "description": "Model building result"}
                    },
                    "required": ["model_result"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "solution": {"type": "object"},
                        "optimal_value": {"type": "number"},
                        "status": {"type": "string"},
                        "performance_metrics": {"type": "object"}
                    }
                },
                category="optimization",
                tags=["manufacturing", "solver", "optimization", "swarm"]
            )
        ]
        
        manufacturing_server = MCPServer(
            server_id="dcisionai-manufacturing-v4",
            name="DcisionAI Manufacturing MCP Server",
            version="4.0.0",
            description="Advanced manufacturing optimization with 18-agent peer-to-peer swarm architecture",
            endpoint="https://agentcore.dcisionai.com/mcp",
            authentication=AuthenticationType.API_KEY,
            status=ServerStatus.HEALTHY,
            tools=manufacturing_tools,
            capabilities=[
                "intent_classification",
                "data_analysis", 
                "model_building",
                "optimization_solving",
                "swarm_intelligence",
                "cross_region_optimization",
                "real_time_processing"
            ],
            region="us-east-1",
            last_updated=datetime.now(timezone.utc),
            health_check_url="https://agentcore.dcisionai.com/health",
            documentation_url="https://docs.dcisionai.com/manufacturing",
            support_url="https://support.dcisionai.com"
        )
        
        self.servers[manufacturing_server.server_id] = manufacturing_server
        logger.info(f"✅ Registered MCP server: {manufacturing_server.name}")
    
    async def start_health_monitoring(self):
        """Start health monitoring for all registered servers."""
        if self.health_check_task is None:
            self.health_check_task = asyncio.create_task(self._health_monitoring_loop())
            logger.info("🏥 Started MCP server health monitoring")
    
    async def stop_health_monitoring(self):
        """Stop health monitoring."""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None
            logger.info("🛑 Stopped MCP server health monitoring")
    
    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop."""
        while True:
            try:
                await self._check_all_server_health()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _check_all_server_health(self):
        """Check health of all registered servers."""
        for server_id, server in self.servers.items():
            try:
                await self._check_server_health(server)
            except Exception as e:
                logger.error(f"❌ Health check failed for {server_id}: {e}")
                server.status = ServerStatus.OFFLINE
    
    async def _check_server_health(self, server: MCPServer):
        """Check health of a specific server."""
        if not server.health_check_url:
            return
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(server.health_check_url)
                
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("status") == "healthy":
                        server.status = ServerStatus.HEALTHY
                    else:
                        server.status = ServerStatus.DEGRADED
                else:
                    server.status = ServerStatus.DEGRADED
                    
        except httpx.TimeoutException:
            server.status = ServerStatus.DEGRADED
        except Exception:
            server.status = ServerStatus.OFFLINE
        
        server.last_updated = datetime.now(timezone.utc)
    
    def get_server(self, server_id: str) -> Optional[MCPServer]:
        """Get a specific MCP server by ID."""
        return self.servers.get(server_id)
    
    def list_servers(self, status_filter: Optional[ServerStatus] = None) -> List[MCPServer]:
        """List all MCP servers, optionally filtered by status."""
        servers = list(self.servers.values())
        
        if status_filter:
            servers = [s for s in servers if s.status == status_filter]
        
        return servers
    
    def search_servers(self, query: str) -> List[MCPServer]:
        """Search MCP servers by name, description, or tags."""
        query_lower = query.lower()
        matching_servers = []
        
        for server in self.servers.values():
            # Search in name and description
            if (query_lower in server.name.lower() or 
                query_lower in server.description.lower()):
                matching_servers.append(server)
                continue
            
            # Search in tool names and descriptions
            for tool in server.tools:
                if (query_lower in tool.name.lower() or 
                    query_lower in tool.description.lower() or
                    any(query_lower in tag.lower() for tag in tool.tags)):
                    matching_servers.append(server)
                    break
        
        return matching_servers
    
    def get_server_tools(self, server_id: str) -> List[MCPTool]:
        """Get tools for a specific MCP server."""
        server = self.get_server(server_id)
        return server.tools if server else []
    
    def register_server(self, server: MCPServer) -> bool:
        """Register a new MCP server."""
        try:
            self.servers[server.server_id] = server
            logger.info(f"✅ Registered new MCP server: {server.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register MCP server: {e}")
            return False
    
    def unregister_server(self, server_id: str) -> bool:
        """Unregister an MCP server."""
        if server_id in self.servers:
            del self.servers[server_id]
            logger.info(f"✅ Unregistered MCP server: {server_id}")
            return True
        return False

# Global registry instance
mcp_registry = MCPRegistry()

# FastAPI application for the registry
app = FastAPI(
    title="DcisionAI MCP Server Registry",
    description="Public registry for discovering and connecting to DcisionAI MCP servers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ServerListResponse(BaseModel):
    """Response model for server list."""
    servers: List[Dict[str, Any]]
    total: int
    timestamp: str

class ServerDetailResponse(BaseModel):
    """Response model for server details."""
    server: Dict[str, Any]
    timestamp: str

class ToolListResponse(BaseModel):
    """Response model for tool list."""
    tools: List[Dict[str, Any]]
    server_id: str
    total: int
    timestamp: str

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    servers_healthy: int
    servers_total: int
    timestamp: str

# API Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with registry information."""
    return {
        "name": "DcisionAI MCP Server Registry",
        "version": "1.0.0",
        "description": "Public registry for discovering and connecting to DcisionAI MCP servers",
        "endpoints": {
            "servers": "/registry/servers",
            "server_details": "/registry/servers/{server_id}",
            "server_tools": "/registry/servers/{server_id}/tools",
            "search": "/registry/search",
            "health": "/registry/health"
        },
        "documentation": "https://docs.dcisionai.com/registry",
        "support": "https://support.dcisionai.com"
    }

@app.get("/registry/servers", response_model=ServerListResponse)
async def list_servers(status: Optional[str] = None):
    """List all available MCP servers."""
    try:
        status_filter = None
        if status:
            try:
                status_filter = ServerStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}. Valid values: {[s.value for s in ServerStatus]}"
                )
        
        servers = mcp_registry.list_servers(status_filter)
        
        return ServerListResponse(
            servers=[server.to_dict() for server in servers],
            total=len(servers),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error listing servers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/registry/servers/{server_id}", response_model=ServerDetailResponse)
async def get_server_details(server_id: str):
    """Get detailed information about a specific MCP server."""
    try:
        server = mcp_registry.get_server(server_id)
        
        if not server:
            raise HTTPException(
                status_code=404,
                detail=f"MCP server '{server_id}' not found"
            )
        
        return ServerDetailResponse(
            server=server.to_dict(),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting server details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/registry/servers/{server_id}/tools", response_model=ToolListResponse)
async def list_server_tools(server_id: str):
    """List all tools available on a specific MCP server."""
    try:
        server = mcp_registry.get_server(server_id)
        
        if not server:
            raise HTTPException(
                status_code=404,
                detail=f"MCP server '{server_id}' not found"
            )
        
        tools = [asdict(tool) for tool in server.tools]
        
        return ToolListResponse(
            tools=tools,
            server_id=server_id,
            total=len(tools),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listing server tools: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/registry/search", response_model=ServerListResponse)
async def search_servers(q: str):
    """Search MCP servers by name, description, or tool capabilities."""
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Search query must be at least 2 characters long"
            )
        
        servers = mcp_registry.search_servers(q.strip())
        
        return ServerListResponse(
            servers=[server.to_dict() for server in servers],
            total=len(servers),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error searching servers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/registry/health", response_model=HealthResponse)
async def registry_health():
    """Get registry health status."""
    try:
        servers = mcp_registry.list_servers()
        healthy_servers = len([s for s in servers if s.status == ServerStatus.HEALTHY])
        
        return HealthResponse(
            status="healthy" if healthy_servers > 0 else "degraded",
            servers_healthy=healthy_servers,
            servers_total=len(servers),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error checking registry health: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    await mcp_registry.start_health_monitoring()
    logger.info("🚀 MCP Server Registry started")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    await mcp_registry.stop_health_monitoring()
    logger.info("🛑 MCP Server Registry stopped")

if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | MCP Registry | %(message)s"
    )
    
    # Run the registry server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
