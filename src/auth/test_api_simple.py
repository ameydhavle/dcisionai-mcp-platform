"""
Simple DcisionAI Platform API Test (No Authentication)

This is a simplified version for testing the API endpoints without authentication
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="DcisionAI Platform API (Test)",
    description="Test version without authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class ToolInvocationRequest(BaseModel):
    """Request model for tool invocation."""
    tool_name: str
    parameters: Dict[str, Any]
    tenant_id: Optional[str] = None
    async_execution: bool = False

class ToolInvocationResponse(BaseModel):
    """Response model for tool invocation."""
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    timestamp: datetime

class ToolInfo(BaseModel):
    """Model for tool information."""
    name: str
    description: str
    version: str
    category: str
    parameters_schema: Dict[str, Any]
    permissions_required: List[str]

# ============================================================================
# Root and Health Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DcisionAI Platform API (Test)",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "dcisionai-platform-api-test"
    }

# ============================================================================
# API Endpoints (No Authentication)
# ============================================================================

@app.post("/api/v1/invoke", response_model=ToolInvocationResponse)
async def invoke_tool(request: ToolInvocationRequest):
    """Invoke a DcisionAI tool synchronously."""
    logger.info(f"Tool invocation request: {request.tool_name}")
    
    try:
        # Generate job ID
        job_id = str(uuid4())
        
        # Simulate tool execution
        start_time = datetime.utcnow()
        
        # Mock tool execution
        if request.tool_name == "test_tool":
            result = {
                "message": f"Tool {request.tool_name} executed successfully",
                "parameters": request.parameters,
                "tenant_id": request.tenant_id or "test_tenant",
                "user_id": "test_user"
            }
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        else:
            # Simulate processing time
            await asyncio.sleep(0.1)
            result = {
                "message": f"Tool {request.tool_name} executed with parameters",
                "parameters": request.parameters,
                "tenant_id": request.tenant_id or "test_tenant",
                "user_id": "test_user",
                "timestamp": datetime.utcnow().isoformat()
            }
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return ToolInvocationResponse(
            job_id=job_id,
            status="completed",
            result=result,
            execution_time_ms=execution_time,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Tool invocation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution failed: {str(e)}"
        )

@app.get("/api/v1/tools", response_model=List[ToolInfo])
async def list_tools(category: Optional[str] = None):
    """List available tools."""
    logger.info(f"Tool list request, category filter: {category}")
    
    # Mock tool list
    mock_tools = [
        ToolInfo(
            name="test_tool",
            description="A test tool for development and testing",
            version="1.0.0",
            category="testing",
            parameters_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Test message"}
                }
            },
            permissions_required=["read"]
        ),
        ToolInfo(
            name="data_processor",
            description="Process and analyze data",
            version="2.1.0",
            category="data",
            parameters_schema={
                "type": "object",
                "properties": {
                    "data_source": {"type": "string", "description": "Data source identifier"},
                    "operation": {"type": "string", "enum": ["analyze", "transform", "validate"]}
                }
            },
            permissions_required=["read", "write"]
        )
    ]
    
    if category:
        mock_tools = [tool for tool in mock_tools if tool.category == category]
    
    return mock_tools

@app.get("/api/v1/tools/{tool_name}", response_model=ToolInfo)
async def get_tool_info(tool_name: str):
    """Get detailed information about a specific tool."""
    logger.info(f"Tool info request: {tool_name}")
    
    # Mock tool info
    if tool_name == "test_tool":
        return ToolInfo(
            name="test_tool",
            description="A test tool for development and testing",
            version="1.0.0",
            category="testing",
            parameters_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Test message"}
                },
                "required": ["message"]
            },
            permissions_required=["read"]
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found"
        )

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get platform metrics."""
    logger.info("Metrics request")
    
    # Mock metrics
    return {
        "tenant_id": "test_tenant",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "total_jobs": 42,
            "completed_jobs": 38,
            "failed_jobs": 2,
            "pending_jobs": 2,
            "active_tools": 5,
            "api_requests_today": 156,
            "average_response_time_ms": 245.7
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting DcisionAI Platform API Test (No Authentication)...")
    
    uvicorn.run(
        "test_api_simple:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
