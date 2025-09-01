#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent - Intent + Data (AgentCore Entry Point)
===================================================================

FastAPI agent for AWS Bedrock AgentCore deployment.
Incremental testing version with Intent and Data tools enabled.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

# Import the FastMCP server
from .fastmcp_server_intent_data import get_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DcisionAI Manufacturing Agent - Intent + Data",
    description="Manufacturing optimization agent with intent classification and data analysis",
    version="1.0.0"
)

# Initialize MCP server
mcp_server = get_server()

# Request/Response models
class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    response: Dict[str, Any]

@app.post("/invocations")
async def invoke_agent(request: InvocationRequest):
    """
    Main AgentCore invocation endpoint.
    Processes manufacturing optimization queries with intent and data analysis.
    """
    try:
        start_time = time.time()
        
        # Extract prompt from request
        prompt = request.input.get("prompt", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="No prompt provided")
        
        logger.info(f"Received AgentCore invocation: {prompt[:100]}...")
        
        # Process message through MCP server
        workflow_result = await mcp_server.process_message(prompt)
        
        execution_time = time.time() - start_time
        logger.info(f"AgentCore invocation completed in {execution_time:.2f}s")
        
        # Extract results
        intent_result = workflow_result.get("stages", {}).get("intent", {}).get("result", {})
        data_result = workflow_result.get("stages", {}).get("data", {}).get("result", {})
        
        # Format response for AgentCore
        response_data = {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{
                        "text": f"Intent and data analysis completed successfully. Primary intent: {intent_result.get('primary_intent', 'UNKNOWN')} with confidence {intent_result.get('confidence', 0.0)}. Data analysis ID: {data_result.get('analysis_id', 'N/A')}"
                    }]
                },
                "timestamp": datetime.now().isoformat(),
                "model": "dcisionai-intent-data",
                "intent_analysis": intent_result,
                "data_analysis": data_result,
                "workflow_type": "intent_data",
                "tools_used": ["intent_classification", "data_analysis"],
                "execution_time": execution_time
            }
        }
        
        return InvocationResponse(response=response_data)
        
    except Exception as e:
        logger.exception(f"AgentCore invocation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/invoke")
async def invoke_agent_legacy(request: Request):
    """
    Legacy endpoint for backward compatibility.
    """
    try:
        body = await request.json()
        return await invoke_agent(InvocationRequest(input=body))
    except Exception as e:
        logger.exception(f"Legacy invocation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model": "dcisionai-intent-data",
        "tools": ["intent_classification", "data_analysis"],
        "workflow_type": "intent_data"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
