#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent - Intent Only (AgentCore Entry Point)
==================================================================

FastAPI agent for AWS Bedrock AgentCore deployment.
Incremental testing version with only Intent tool enabled.

This agent serves as the entry point for AgentCore and handles
HTTP requests from the AgentCore runtime.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import the intent-only FastMCP server
from .fastmcp_server_intent_only import get_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DcisionAI Manufacturing Agent - Intent Only",
    description="Manufacturing optimization agent with intent analysis only",
    version="1.0.0"
)

# Initialize FastMCP server
try:
    mcp_server = get_server()
    logger.info("✅ FastMCP server (Intent Only) initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize FastMCP server: {e}")
    raise

# Pydantic models for request/response
class InvocationRequest(BaseModel):
    """Request model for AgentCore invocation."""
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    """Response model for AgentCore invocation."""
    output: Dict[str, Any]

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "DcisionAI Manufacturing Agent - Intent Only",
        "status": "healthy",
        "version": "1.0.0",
        "tools_enabled": ["intent_classification"]
    }

@app.get("/ping")
async def ping():
    """Health check endpoint for AgentCore."""
    return {"status": "healthy", "message": "pong"}

@app.post("/invocations")
async def invoke_agent(request: InvocationRequest):
    """
    Main invocation endpoint for AgentCore.
    
    This endpoint receives requests from AgentCore and processes them
    using the intent-only workflow.
    """
    try:
        logger.info("🚀 AgentCore invocation received")
        
        # Extract user message from request
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="No prompt provided in request")
        
        logger.info(f"📝 User message: {user_message[:100]}...")
        
        # Process message using intent-only workflow
        logger.info("🧠 Processing with intent-only workflow...")
        workflow_result = await mcp_server.process_message(user_message)
        
        # Check if workflow was successful
        if not workflow_result.get("overall_success", False):
            error_msg = workflow_result.get("error", "Unknown error")
            logger.error(f"❌ Workflow failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Workflow failed: {error_msg}")
        
        # Extract intent result
        intent_stage = workflow_result.get("stages", {}).get("intent", {})
        if not intent_stage.get("success", False):
            logger.error("❌ Intent analysis failed")
            raise HTTPException(status_code=500, detail="Intent analysis failed")
        
        intent_result = intent_stage.get("result", {})
        
        # Create response in AgentCore expected format
        response_data = {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "text": f"Intent analysis completed successfully. Primary intent: {intent_result.get('primary_intent', 'UNKNOWN')} with confidence {intent_result.get('confidence', 0.0)}"
                        }
                    ]
                },
                "timestamp": datetime.now().isoformat(),
                "model": "dcisionai-intent-only",
                "intent_analysis": {
                    "primary_intent": intent_result.get("primary_intent", "UNKNOWN"),
                    "confidence": intent_result.get("confidence", 0.0),
                    "objectives": intent_result.get("objectives", []),
                    "entities": intent_result.get("entities", [])
                },
                "workflow_type": "intent_only",
                "tools_used": ["intent_classification"]
            }
        }
        
        logger.info(f"✅ Intent analysis completed: {intent_result.get('primary_intent', 'UNKNOWN')}")
        
        return InvocationResponse(output=response_data["output"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Unexpected error in agent invocation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/invoke")
async def invoke_agent_legacy(request: Request):
    """
    Legacy invocation endpoint for backward compatibility.
    """
    try:
        # Parse request body
        body = await request.json()
        user_message = body.get("input", {}).get("prompt", "")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No prompt provided")
        
        # Use the main invoke endpoint
        invocation_request = InvocationRequest(input={"prompt": user_message})
        return await invoke_agent(invocation_request)
        
    except Exception as e:
        logger.exception(f"❌ Error in legacy invoke endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_tools():
    """List available tools."""
    return {
        "tools": [
            {
                "name": "classify_manufacturing_intent",
                "description": "Classify manufacturing optimization intent from natural language query",
                "enabled": True
            }
        ],
        "workflow_type": "intent_only"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    try:
        # Check if MCP server is working
        test_result = await mcp_server.process_message("test")
        
        return {
            "status": "healthy",
            "mcp_server": "operational",
            "tools_enabled": ["intent_classification"],
            "workflow_type": "intent_only",
            "test_result": test_result.get("overall_success", False)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status": "error",
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status": "error",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
