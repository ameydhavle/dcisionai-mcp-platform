#!/usr/bin/env python3
"""
DcisionAI MCP Server - AgentCore Entry Point
============================================

Proper entry point for AWS Bedrock AgentCore deployment.
Uses BedrockAgentCoreApp as required by AWS AgentCore.

Based on AWS documentation:
https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/

Usage:
    agentcore configure -e agentcore_entry_point.py --protocol MCP
    agentcore launch
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# Import the AgentCore SDK
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Create the AgentCore app
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """Handler for agent invocation - follows AWS AgentCore pattern"""
    try:
        # Get the user message from payload
        user_message = payload.get("prompt", "No prompt found in input")
        logger.info(f"Received user message: {user_message}")
        
        # Import our FastMCP server
        from mcp_server.fastmcp_server import create_fastmcp_server
        
        # Create our MCP server
        mcp_server = create_fastmcp_server()
        
        logger.info("DcisionAI MCP Server initialized successfully")
        
        # For now, return a simple response indicating the server is ready
        # In a full implementation, this would route the message through the MCP server
        response = {
            "status": "success",
            "message": f"DcisionAI MCP Server received: {user_message}",
            "tools_available": [
                "classify_manufacturing_intent",
                "analyze_data_requirements", 
                "build_optimization_model",
                "solve_optimization_problem",
                "manufacturing_optimization_workflow",
                "manufacturing_tools_status"
            ],
            "server_ready": True
        }
        
        logger.info("AgentCore entry point responding successfully")
        return response
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return {
            "status": "error",
            "message": f"Import error: {e}",
            "error_type": "import_error"
        }
    except Exception as e:
        logger.error(f"Failed to process request: {e}")
        return {
            "status": "error", 
            "message": f"Processing error: {e}",
            "error_type": "processing_error"
        }

@app.ping
async def health_check():
    """Health check endpoint for AgentCore."""
    try:
        # Import our FastMCP server to check if it's working
        from mcp_server.fastmcp_server import create_fastmcp_server
        mcp_server = create_fastmcp_server()
        
        return {
            "status": "healthy",
            "message": "DcisionAI MCP Server is running",
            "tools_available": 6,
            "manufacturing_tools": [
                "classify_manufacturing_intent",
                "analyze_data_requirements", 
                "build_optimization_model",
                "solve_optimization_problem",
                "manufacturing_optimization_workflow",
                "manufacturing_tools_status"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {e}"
        }

if __name__ == "__main__":
    # This will be called by AgentCore
    logger.info("AgentCore entry point loaded")
    logger.info("DcisionAI MCP Server ready for deployment")
