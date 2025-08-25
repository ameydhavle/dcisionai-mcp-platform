"""
Shared Tools Registry
Central registry for managing all tools in the DcisionAI platform
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .interfaces import ToolInterface, ToolMetadata, ToolResponse, ToolType, ToolStatus
from .loader import CombinedToolLoader
from .base import ToolError, ToolExecutionError

logger = logging.getLogger(__name__)


class SharedToolsRegistry:
    """
    Central registry for managing all tools in the DcisionAI platform
    Provides unified access to Strands tools and custom DcisionAI tools
    """
    
    def __init__(self, custom_tools_directory: Optional[str] = None, max_workers: int = 10):
        self.loader = CombinedToolLoader(custom_tools_directory)
        self.tools: Dict[str, ToolInterface] = {}
        self.tool_usage_stats: Dict[str, Dict[str, Any]] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
    
    async def initialize(self, load_all: bool = False) -> bool:
        """
        Initialize the tools registry
        
        Args:
            load_all: If True, load all available tools. If False, load only essential tools.
        """
        async with self._initialization_lock:
            if self._initialized:
                return True
            
            try:
                logger.info("Initializing Shared Tools Registry...")
                
                if load_all:
                    self.tools = await self.loader.load_all_tools()
                else:
                    self.tools = await self.loader.load_essential_tools()
                
                # Initialize usage stats
                for tool_name in self.tools.keys():
                    self.tool_usage_stats[tool_name] = {
                        "total_calls": 0,
                        "successful_calls": 0,
                        "failed_calls": 0,
                        "total_execution_time": 0.0,
                        "average_execution_time": 0.0,
                        "last_used": None,
                        "error_rate": 0.0
                    }
                
                self._initialized = True
                
                # Log initialization results
                failed_tools = self.loader.get_failed_tools()
                logger.info(f"Tools Registry initialized successfully")
                logger.info(f"  - Loaded tools: {len(self.tools)}")
                logger.info(f"  - Failed tools: {len(failed_tools)}")
                
                if failed_tools:
                    logger.warning(f"Failed to load tools: {list(failed_tools.keys())}")
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to initialize Tools Registry: {e}")
                return False
    
    async def get_tool(self, tool_name: str) -> Optional[ToolInterface]:
        """Get a specific tool by name"""
        if not self._initialized:
            await self.initialize()
        
        return self.tools.get(tool_name)
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResponse:
        """
        Execute a tool with given parameters
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            ToolResponse with execution results
        """
        start_time = datetime.now()
        
        try:
            if not self._initialized:
                await self.initialize()
            
            tool = self.tools.get(tool_name)
            if tool is None:
                # Try to load the tool dynamically
                tool = await self._load_tool_dynamically(tool_name)
                if tool is None:
                    return ToolResponse(
                        success=False,
                        error=f"Tool '{tool_name}' not found",
                        tool_name=tool_name,
                        execution_time=0.0
                    )
            
            # Validate parameters
            if not await tool.validate_parameters(**kwargs):
                return ToolResponse(
                    success=False,
                    error=f"Invalid parameters for tool '{tool_name}'",
                    tool_name=tool_name,
                    execution_time=0.0
                )
            
            # Execute the tool
            response = await tool.execute(**kwargs)
            
            # Update usage statistics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_usage_stats(tool_name, response.success, execution_time)
            
            return response
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_usage_stats(tool_name, False, execution_time)
            
            logger.error(f"Tool execution failed for '{tool_name}': {e}")
            return ToolResponse(
                success=False,
                error=str(e),
                tool_name=tool_name,
                execution_time=execution_time
            )
    
    async def execute_tools_parallel(self, tool_calls: List[Dict[str, Any]]) -> List[ToolResponse]:
        """
        Execute multiple tools in parallel
        
        Args:
            tool_calls: List of tool calls, each containing 'tool_name' and 'parameters'
            
        Returns:
            List of ToolResponse objects
        """
        if not self._initialized:
            await self.initialize()
        
        tasks = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name")
            parameters = tool_call.get("parameters", {})
            
            if tool_name:
                task = self.execute_tool(tool_name, **parameters)
                tasks.append(task)
        
        if not tasks:
            return []
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error responses
            results = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    tool_name = tool_calls[i].get("tool_name", "unknown")
                    results.append(ToolResponse(
                        success=False,
                        error=str(response),
                        tool_name=tool_name,
                        execution_time=0.0
                    ))
                else:
                    results.append(response)
            
            return results
            
        except Exception as e:
            logger.error(f"Parallel tool execution failed: {e}")
            return [ToolResponse(
                success=False,
                error=str(e),
                tool_name="parallel_execution",
                execution_time=0.0
            )]
    
    async def _load_tool_dynamically(self, tool_name: str) -> Optional[ToolInterface]:
        """Try to load a tool dynamically"""
        try:
            # Try Strands tools first
            tool = await self.loader.strands_loader.load_tool(tool_name)
            if tool:
                self.tools[tool_name] = tool
                self.tool_usage_stats[tool_name] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "total_execution_time": 0.0,
                    "average_execution_time": 0.0,
                    "last_used": None,
                    "error_rate": 0.0
                }
                return tool
            
            # Try custom tools
            tool = await self.loader.custom_loader.load_tool(tool_name)
            if tool:
                self.tools[tool_name] = tool
                self.tool_usage_stats[tool_name] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "total_execution_time": 0.0,
                    "average_execution_time": 0.0,
                    "last_used": None,
                    "error_rate": 0.0
                }
                return tool
            
            return None
            
        except Exception as e:
            logger.error(f"Dynamic tool loading failed for '{tool_name}': {e}")
            return None
    
    def _update_usage_stats(self, tool_name: str, success: bool, execution_time: float):
        """Update usage statistics for a tool"""
        if tool_name not in self.tool_usage_stats:
            self.tool_usage_stats[tool_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_execution_time": 0.0,
                "average_execution_time": 0.0,
                "last_used": None,
                "error_rate": 0.0
            }
        
        stats = self.tool_usage_stats[tool_name]
        stats["total_calls"] += 1
        stats["total_execution_time"] += execution_time
        stats["last_used"] = datetime.now().isoformat()
        
        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
        
        # Update derived statistics
        stats["average_execution_time"] = stats["total_execution_time"] / stats["total_calls"]
        stats["error_rate"] = stats["failed_calls"] / stats["total_calls"]
    
    def get_available_tools(self) -> List[str]:
        """Get list of all available tool names"""
        return list(self.tools.keys())
    
    def get_tools_by_type(self, tool_type: ToolType) -> Dict[str, ToolInterface]:
        """Get tools by type"""
        return {
            name: tool for name, tool in self.tools.items()
            if tool.tool_type == tool_type
        }
    
    def get_tools_by_capability(self, capability: str) -> Dict[str, ToolInterface]:
        """Get tools by capability"""
        return {
            name: tool for name, tool in self.tools.items()
            if capability in tool.metadata.capabilities
        }
    
    def get_tools_by_status(self, status: ToolStatus) -> Dict[str, ToolInterface]:
        """Get tools by status"""
        return {
            name: tool for name, tool in self.tools.items()
            if tool.status == status
        }
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool"""
        tool = self.tools.get(tool_name)
        return tool.metadata if tool else None
    
    def get_tool_usage_stats(self, tool_name: str = None) -> Dict[str, Any]:
        """Get usage statistics for tools"""
        if tool_name:
            return self.tool_usage_stats.get(tool_name, {})
        return self.tool_usage_stats.copy()
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get overall registry status"""
        total_tools = len(self.tools)
        available_tools = len(self.get_tools_by_status(ToolStatus.AVAILABLE))
        error_tools = len(self.get_tools_by_status(ToolStatus.ERROR))
        
        strands_tools = len(self.get_tools_by_type(ToolType.STRANDS_OFFICIAL))
        custom_tools = len(self.get_tools_by_type(ToolType.DCISIONAI_CUSTOM))
        
        failed_tools = self.loader.get_failed_tools()
        
        return {
            "initialized": self._initialized,
            "total_tools": total_tools,
            "available_tools": available_tools,
            "error_tools": error_tools,
            "strands_tools": strands_tools,
            "custom_tools": custom_tools,
            "failed_tools": len(failed_tools),
            "failed_tool_names": list(failed_tools.keys()),
            "tool_types": {
                "strands_official": strands_tools,
                "dcisionai_custom": custom_tools,
                "external_mcp": len(self.get_tools_by_type(ToolType.EXTERNAL_MCP)),
                "plugin": len(self.get_tools_by_type(ToolType.PLUGIN))
            }
        }
    
    async def validate_tools(self) -> Dict[str, Any]:
        """Validate all tools in the registry"""
        validation_results = {
            "total_tools": len(self.tools),
            "valid_tools": 0,
            "invalid_tools": 0,
            "tool_validation": {}
        }
        
        for tool_name, tool in self.tools.items():
            try:
                # Basic validation - check if tool can be initialized
                is_valid = tool.is_initialized or await tool.initialize()
                
                validation_results["tool_validation"][tool_name] = {
                    "valid": is_valid,
                    "status": tool.status.value,
                    "error": tool.metadata.error_message
                }
                
                if is_valid:
                    validation_results["valid_tools"] += 1
                else:
                    validation_results["invalid_tools"] += 1
                    
            except Exception as e:
                validation_results["tool_validation"][tool_name] = {
                    "valid": False,
                    "status": "error",
                    "error": str(e)
                }
                validation_results["invalid_tools"] += 1
        
        return validation_results
    
    async def reload_tool(self, tool_name: str) -> bool:
        """Reload a specific tool"""
        try:
            # Remove existing tool
            if tool_name in self.tools:
                await self.tools[tool_name].cleanup()
                del self.tools[tool_name]
            
            # Reset usage stats
            if tool_name in self.tool_usage_stats:
                del self.tool_usage_stats[tool_name]
            
            # Load the tool again
            tool = await self._load_tool_dynamically(tool_name)
            return tool is not None
            
        except Exception as e:
            logger.error(f"Failed to reload tool '{tool_name}': {e}")
            return False
    
    async def cleanup(self):
        """Cleanup all tools and resources"""
        logger.info("Cleaning up Tools Registry...")
        
        for tool in self.tools.values():
            try:
                await tool.cleanup()
            except Exception as e:
                logger.warning(f"Error cleaning up tool {tool.name}: {e}")
        
        self.tools.clear()
        self.tool_usage_stats.clear()
        
        if self.executor:
            self.executor.shutdown(wait=True)
        
        self._initialized = False
        logger.info("Tools Registry cleanup completed")


# Global registry instance
_global_registry: Optional[SharedToolsRegistry] = None


def get_tool_registry(custom_tools_directory: Optional[str] = None) -> SharedToolsRegistry:
    """Get the global tools registry instance"""
    global _global_registry
    
    if _global_registry is None:
        _global_registry = SharedToolsRegistry(custom_tools_directory)
    
    return _global_registry


async def initialize_global_registry(load_all: bool = False, custom_tools_directory: Optional[str] = None) -> bool:
    """Initialize the global tools registry"""
    registry = get_tool_registry(custom_tools_directory)
    return await registry.initialize(load_all)


# Convenience functions for easy access
async def execute_tool(tool_name: str, **kwargs) -> ToolResponse:
    """Execute a tool using the global registry"""
    registry = get_tool_registry()
    return await registry.execute_tool(tool_name, **kwargs)


async def get_tool(tool_name: str) -> Optional[ToolInterface]:
    """Get a tool using the global registry"""
    registry = get_tool_registry()
    return await registry.get_tool(tool_name)


def get_available_tools() -> List[str]:
    """Get available tools using the global registry"""
    registry = get_tool_registry()
    return registry.get_available_tools()


def get_registry_status() -> Dict[str, Any]:
    """Get registry status using the global registry"""
    registry = get_tool_registry()
    return registry.get_registry_status()