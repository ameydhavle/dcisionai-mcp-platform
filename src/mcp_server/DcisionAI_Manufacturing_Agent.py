#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - FastAPI Agent for AgentCore
===============================================================

DcisionAI Manufacturing Agent implementation following AWS AgentCore requirements.
This agent provides manufacturing optimization and decision intelligence capabilities.

Domain: Manufacturing Optimization & Decision Intelligence
Brand: DcisionAI
Platform: AWS Bedrock AgentCore

Requirements:
- /invocations POST endpoint for agent interactions (REQUIRED)
- /ping GET endpoint for health checks (REQUIRED)
- ARM64 containerized deployment package

Based on AWS documentation:
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from dataclasses import asdict

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(title="DcisionAI Manufacturing MCP Server", version="1.0.0")

# Pydantic models for request/response
class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    """POST endpoint for agent interactions (REQUIRED)"""
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(
                status_code=400, 
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )

        logger.info(f"Received user message: {user_message}")

        # Import our FastMCP server
        from mcp_server.fastmcp_server import create_fastmcp_server
        
        # Create our MCP server
        mcp_server = create_fastmcp_server()
        
        logger.info("DcisionAI Manufacturing MCP Server initialized successfully")
        
        # Route the message through the FastMCP workflow
        try:
            logger.info("Processing through FastMCP manufacturing workflow...")
            
            # Use the FastMCP server's built-in workflow
            workflow_result = await mcp_server.process_message(user_message)
            
            # FastMCP workflow returns a different structure
            if "error" not in workflow_result:
                logger.info(f"✅ FastMCP workflow completed successfully")
                
                response = {
                    "message": workflow_result.get("message", "Manufacturing optimization workflow completed"),
                    "tools_used": workflow_result.get("tools_used", []),
                    "tool_results": workflow_result.get("tool_results", {}),
                    "processing_summary": workflow_result.get("processing_summary", {}),
                    "tools_available": [
                        "classify_manufacturing_intent",
                        "analyze_data_requirements", 
                        "build_optimization_model",
                        "solve_optimization_problem"
                    ],
                    "workflow_type": "fastmcp_sequential",
                    "server_ready": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "model": "dcisionai-manufacturing-mcp-server"
                }
            else:
                logger.error(f"❌ FastMCP workflow failed: {workflow_result.get('error', 'Unknown error')}")
                
                response = {
                    "message": workflow_result.get("message", "Manufacturing optimization workflow failed"),
                    "error": workflow_result.get("error", "Unknown error"),
                    "tools_used": workflow_result.get("tools_used", []),
                    "tool_results": workflow_result.get("tool_results", {}),
                    "tools_available": [
                        "classify_manufacturing_intent",
                        "analyze_data_requirements", 
                        "build_optimization_model",
                        "solve_optimization_problem"
                    ],
                    "workflow_type": "fastmcp_sequential",
                    "server_ready": False,
                    "timestamp": datetime.utcnow().isoformat(),
                    "model": "dcisionai-manufacturing-mcp-server"
                }
            
            logger.info(f"FastMCP workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing message through FastMCP workflow: {e}")
            # Return error response instead of hardcoded message
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process manufacturing request through FastMCP workflow: {e}"
            )

        logger.info("DcisionAI Manufacturing Agent responding successfully")
        return InvocationResponse(output=response)

    except ImportError as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Import error: {e}"
        )
    except Exception as e:
        logger.error(f"Failed to process request: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Processing error: {e}"
        )

@app.get("/ping")
async def ping():
    """GET endpoint for health checks (REQUIRED)"""
    try:
        # Import our FastMCP server to check if it's working
        from mcp_server.fastmcp_server import create_fastmcp_server
        mcp_server = create_fastmcp_server()
        
        return {
            "status": "healthy",
            "message": "DcisionAI Manufacturing MCP Server is running",
            "tools_available": 6,
            "manufacturing_tools": [
                "classify_manufacturing_intent",
                "analyze_data_requirements", 
                "build_optimization_model",
                "solve_optimization_problem",
                "manufacturing_optimization_workflow",
                "manufacturing_tools_status"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {e}"
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting DcisionAI Manufacturing MCP Server on port 8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
