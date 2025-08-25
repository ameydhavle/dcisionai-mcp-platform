"""
MCP Server Base Tool
===================

Base class for all MCP tools in the DcisionAI server.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..config.settings import settings
from ..utils.logging import MCPLogger
from ..utils.metrics import metrics_collector, track_request
from ..tenants.manager import tenant_manager


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DcisionAITool(ABC):
    """Base class for all DcisionAI MCP tools."""
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.logger = MCPLogger(f"dcisionai.mcp.tools.{self.name}", tenant_id)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for MCP protocol."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for MCP protocol."""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """Input schema for MCP protocol."""
        pass
    
    @property
    def cost(self) -> float:
        """Cost per request for this tool."""
        return settings.get_tool_cost(self.name)
    
    async def validate_request(self) -> Dict[str, Any]:
        """Validate if the tenant can make a request for this tool."""
        return await tenant_manager.validate_request(self.tenant_id, self.name)
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with validation and metrics tracking."""
        try:
            # Validate request
            validation = await self.validate_request()
            if not validation["valid"]:
                return ToolResult(
                    success=False,
                    error=validation["error"]
                )
            
            # Track request metrics
            with track_request(metrics_collector, self.tenant_id, self.name):
                # Execute the actual tool logic
                result = await self._execute(**kwargs)
                
                # Record cost
                await tenant_manager.complete_request(self.tenant_id, self.name, self.cost)
                
                return result
                
        except Exception as e:
            self.logger.exception(f"Error executing tool {self.name}", error=str(e))
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )
    
    @abstractmethod
    async def _execute(self, **kwargs) -> ToolResult:
        """Actual tool implementation - to be implemented by subclasses."""
        pass
    
    def get_mcp_tool_definition(self) -> Dict[str, Any]:
        """Get MCP tool definition."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


class ToolRegistry:
    """Registry for managing all MCP tools."""
    
    def __init__(self):
        self.tools: Dict[str, DcisionAITool] = {}
        self.logger = MCPLogger("dcisionai.mcp.tool_registry")
    
    def register_tool(self, tool: DcisionAITool) -> None:
        """Register a tool in the registry."""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, tool_name: str) -> Optional[DcisionAITool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools."""
        return [tool.get_mcp_tool_definition() for tool in self.tools.values()]
    
    def get_tool_names(self) -> List[str]:
        """Get list of all tool names."""
        return list(self.tools.keys())


# Global tool registry
tool_registry = ToolRegistry()
