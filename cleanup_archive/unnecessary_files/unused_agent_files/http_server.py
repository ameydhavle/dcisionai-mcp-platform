#!/usr/bin/env python3
"""
DcisionAI MCP Server HTTP Implementation
========================================

HTTP server implementation for the MCP server.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from .config.settings import settings
from .utils.logging import get_logger
from .protocol.handler import protocol_handler

# Import FastMCP for AWS AgentCore compatibility
try:
    from mcp.server.fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("Warning: FastMCP not available, using custom HTTP server")


class MCPHTTPServer:
    """HTTP server for MCP protocol."""
    
    def __init__(self):
        self.app = FastAPI(
            title="DcisionAI MCP Server",
            description="MCP Server for DcisionAI Manufacturing Optimization Tools",
            version="1.0.0"
        )
        self.logger = get_logger(__name__)
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "service": "DcisionAI MCP Server"}
        
        @self.app.post("/mcp")
        async def handle_mcp_request(request: Request):
            """Handle MCP protocol requests."""
            try:
                # Read request body
                body = await request.body()
                message = body.decode('utf-8').strip()
                
                if not message:
                    raise HTTPException(status_code=400, detail="Empty request body")
                
                # Process MCP message
                response = await protocol_handler.process_message(message)
                
                if response:
                    # Parse response to ensure it's valid JSON
                    try:
                        json.loads(response)
                        return JSONResponse(content=json.loads(response))
                    except json.JSONDecodeError:
                        # Return as plain text if not JSON
                        return JSONResponse(content={"result": response})
                else:
                    return JSONResponse(content={"result": None})
                    
            except Exception as e:
                self.logger.exception(f"Error processing MCP request: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tools")
        async def list_tools():
            """List available tools."""
            try:
                tools = protocol_handler.list_tools()
                return JSONResponse(content=tools)
            except Exception as e:
                self.logger.exception(f"Error listing tools: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tools/{tool_name}")
        async def call_tool(tool_name: str, request: Request):
            """Call a specific tool."""
            try:
                # Read request body
                body = await request.json()
                
                # Create MCP tools/call message
                mcp_message = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": body
                    }
                })
                
                # Process MCP message
                response = await protocol_handler.process_message(mcp_message)
                
                if response:
                    try:
                        return JSONResponse(content=json.loads(response))
                    except json.JSONDecodeError:
                        return JSONResponse(content={"result": response})
                else:
                    return JSONResponse(content={"result": None})
                    
            except Exception as e:
                self.logger.exception(f"Error calling tool {tool_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the HTTP server."""
        try:
            self.logger.info(f"Starting MCP HTTP server on {host}:{port}")
            
            # Use FastMCP if available (AWS AgentCore compatible)
            if FASTMCP_AVAILABLE:
                self.logger.info("Using FastMCP for AWS AgentCore compatibility")
                # FastMCP will handle the server startup
                return
            else:
                # Fallback to custom HTTP server
                config = uvicorn.Config(
                    app=self.app,
                    host=host,
                    port=port,
                    log_level="info",
                    access_log=True
                )
                
                server = uvicorn.Server(config)
                await server.serve()
            
        except Exception as e:
            self.logger.exception(f"HTTP server error: {e}")
            raise


async def start_http_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the HTTP server."""
    server = MCPHTTPServer()
    await server.start(host, port)


if __name__ == "__main__":
    import sys
    
    host = "0.0.0.0"
    port = 8080
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    asyncio.run(start_http_server(host, port))
