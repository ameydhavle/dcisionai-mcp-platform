"""
MCP Protocol Handler
===================

Handles MCP protocol communication and tool execution.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..config.settings import settings
from ..utils.logging import MCPLogger
from ..utils.metrics import metrics_collector
from ..tenants.manager import tenant_manager
from ..tools.base import tool_registry


class MCPProtocolHandler:
    """Handles MCP protocol communication."""
    
    def __init__(self):
        self.logger = MCPLogger("dcisionai.mcp.protocol")
        self.session_id: Optional[str] = None
        self.tenant_id: str = "default"
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        try:
            self.logger.info("Handling initialize request", params=params)
            
            # Create session for the tenant
            self.session_id = await tenant_manager.create_session(self.tenant_id)
            
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "DcisionAI MCP Server",
                    "version": "1.0.0"
                }
            }
        except Exception as e:
            self.logger.exception(f"Initialize failed: {e}")
            raise
    
    async def handle_tools_list(self) -> Dict[str, Any]:
        """Handle MCP tools/list request."""
        try:
            tools = tool_registry.list_tools()
            self.logger.info(f"Listing {len(tools)} tools")
            
            return {
                "tools": tools
            }
        except Exception as e:
            self.logger.exception(f"Tools list failed: {e}")
            raise
    
    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools/call request."""
        try:
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                raise ValueError("Tool name is required")
            
            self.logger.info(
                "Handling tool call",
                tool_name=tool_name,
                tenant_id=self.tenant_id,
                session_id=self.session_id
            )
            
            # Get the tool
            tool = tool_registry.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool {tool_name} not found")
            
            # Set tenant ID for the tool
            tool.tenant_id = self.tenant_id
            
            # Execute the tool
            result = await tool.execute(**arguments)
            
            if not result.success:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Tool execution failed: {result.error}"
                        }
                    ]
                }
            
            # Format the result
            content = []
            
            # Add main result
            if result.data:
                content.append({
                    "type": "text",
                    "text": json.dumps(result.data, indent=2)
                })
            
            # Add metadata if available
            if result.metadata:
                content.append({
                    "type": "text",
                    "text": f"\nMetadata: {json.dumps(result.metadata, indent=2)}"
                })
            
            self.logger.info(
                "Tool call completed successfully",
                tool_name=tool_name,
                result_success=result.success
            )
            
            return {
                "content": content
            }
            
        except Exception as e:
            self.logger.exception(f"Tool call failed: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool call failed: {str(e)}"
                    }
                ]
            }
    
    async def handle_notifications(self, method: str, params: Dict[str, Any]) -> None:
        """Handle MCP notifications."""
        self.logger.info(f"Received notification: {method}", params=params)
        
        # Update session activity
        if self.session_id:
            await tenant_manager.update_session_activity(self.session_id)
    
    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle MCP request."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            self.logger.debug(f"Handling request: {method}", request_id=request_id)
            
            # Handle different request types
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list()
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Return response if request has ID
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            return None
            
        except Exception as e:
            self.logger.exception(f"Request handling failed: {e}")
            
            # Return error response if request has ID
            if request.get("id") is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
            
            return None
    
    async def process_message(self, message: str) -> Optional[str]:
        """Process incoming MCP message."""
        try:
            # Parse JSON message
            data = json.loads(message)
            
            # Handle request
            if "method" in data:
                response = await self.handle_request(data)
                if response:
                    return json.dumps(response)
            
            # Handle notification
            elif "method" in data and "id" not in data:
                await self.handle_notifications(data["method"], data.get("params", {}))
            
            return None
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON message: {e}")
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            })
        except Exception as e:
            self.logger.exception(f"Message processing failed: {e}")
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            })


# Global protocol handler instance
protocol_handler = MCPProtocolHandler()
