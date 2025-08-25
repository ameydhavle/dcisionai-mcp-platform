"""
Simple Tool Coordinator
Lightweight coordination for production tools without complex abstractions
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from . import PRODUCTION_TOOLS

logger = logging.getLogger(__name__)


class ToolCoordinator:
    """
    Simple tool coordinator for production tools
    Follows architectural-design-reference.md: lightweight coordination without complex error recovery
    """
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all production tools"""
        try:
            logger.info("Initializing production tools...")
            
            for tool_name, tool_class in PRODUCTION_TOOLS.items():
                try:
                    tool_instance = tool_class()
                    if await tool_instance.initialize():
                        self.tools[tool_name] = tool_instance
                        logger.info(f"Initialized {tool_name}")
                    else:
                        logger.warning(f"Failed to initialize {tool_name}")
                except Exception as e:
                    logger.error(f"Error initializing {tool_name}: {e}")
            
            self.initialized = True
            logger.info(f"Tool coordinator initialized with {len(self.tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Tool coordinator initialization failed: {e}")
            return False
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool with simple error handling"""
        if not self.initialized:
            await self.initialize()
        
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not available")
        
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            raise
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get a tool instance"""
        return self.tools.get(tool_name)
    
    def list_available_tools(self) -> list:
        """List available initialized tools"""
        return list(self.tools.keys())
    
    async def cleanup(self):
        """Cleanup all tools"""
        for tool_name, tool in self.tools.items():
            try:
                await tool.cleanup()
            except Exception as e:
                logger.warning(f"Error cleaning up {tool_name}: {e}")
        
        self.tools.clear()
        self.initialized = False


# Global coordinator instance
_coordinator: Optional[ToolCoordinator] = None


def get_tool_coordinator() -> ToolCoordinator:
    """Get the global tool coordinator"""
    global _coordinator
    if _coordinator is None:
        _coordinator = ToolCoordinator()
    return _coordinator


async def initialize_tools() -> bool:
    """Initialize the global tool coordinator"""
    coordinator = get_tool_coordinator()
    return await coordinator.initialize()


async def execute_tool(tool_name: str, **kwargs) -> Any:
    """Execute a tool using the global coordinator"""
    coordinator = get_tool_coordinator()
    return await coordinator.execute_tool(tool_name, **kwargs)


def get_tool(tool_name: str) -> Optional[Any]:
    """Get a tool using the global coordinator"""
    coordinator = get_tool_coordinator()
    return coordinator.get_tool(tool_name)