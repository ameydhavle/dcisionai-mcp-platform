#!/usr/bin/env python3
"""
DcisionAI MCP Server - FastMCP Implementation for AWS AgentCore
==============================================================

FastMCP implementation for AWS AgentCore compatibility.
Based on AWS AgentCore MCP documentation.
"""

import asyncio
import json
from typing import Dict, Any, Optional

# Import FastMCP for AWS AgentCore compatibility
try:
    from mcp.server.fastmcp import FastMCP
    from starlette.responses import JSONResponse
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("Error: FastMCP not available. Please install with: pip install mcp")

from .config.settings import settings
from .utils.logging import get_logger
from .tools.intent_tool import IntentClassificationTool


class DcisionAIFastMCPServer:
    """FastMCP server for DcisionAI manufacturing tools."""
    
    def __init__(self):
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP is required for AWS AgentCore deployment")
        
        self.mcp = FastMCP(host="0.0.0.0", stateless_http=True)
        self.logger = get_logger(__name__)
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools."""
        try:
            # Register intent classification tool
            @self.mcp.tool()
            def manufacturing_intent_classification(query: str, include_confidence: bool = True, include_reasoning: bool = True) -> str:
                """
                Classify manufacturing optimization queries using 6-agent swarm system
                
                Args:
                    query: Manufacturing optimization query to classify
                    include_confidence: Include confidence scores in response
                    include_reasoning: Include reasoning in response
                
                Returns:
                    Classification result with intent analysis
                """
                try:
                    self.logger.info(f"Processing intent classification for query: {query[:100]}...")
                    
                    # Create and execute the intent tool
                    intent_tool = IntentClassificationTool()
                    result = intent_tool.execute({
                        "query": query,
                        "include_confidence": include_confidence,
                        "include_reasoning": include_reasoning
                    })
                    
                    if result.success:
                        return result.content[0]["text"] if result.content else "No classification result"
                    else:
                        return f"Classification failed: {result.error}"
                        
                except Exception as e:
                    self.logger.exception(f"Intent classification error: {e}")
                    return f"Error during classification: {str(e)}"
            
            self.logger.info("Registered manufacturing_intent_classification tool")
            
        except Exception as e:
            self.logger.exception(f"Failed to register tools: {e}")
            raise
    
    def run(self):
        """Run the FastMCP server."""
        try:
            self.logger.info("Starting DcisionAI FastMCP server for AWS AgentCore")
            self.mcp.run(transport="streamable-http")
        except Exception as e:
            self.logger.exception(f"FastMCP server error: {e}")
            raise


def create_fastmcp_server():
    """Create and return a FastMCP server instance."""
    return DcisionAIFastMCPServer()


if __name__ == "__main__":
    # Create and run the server
    server = create_fastmcp_server()
    server.run()
