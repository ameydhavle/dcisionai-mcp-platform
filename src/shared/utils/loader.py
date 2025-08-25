"""
Tool Loading and Initialization System
Handles loading of Strands tools and custom DcisionAI tools
"""

import logging
import importlib
import importlib.util
from typing import Dict, Any, List, Optional, Callable, Type
from pathlib import Path

from .interfaces import (
    ToolInterface, ToolMetadata, ToolType, ToolStatus,
    StrandsToolInterface, CustomToolInterface
)
from .base import BaseTool, ToolError, ToolInitializationError

logger = logging.getLogger(__name__)


class ToolLoader:
    """Base tool loader class"""
    
    def __init__(self):
        self.loaded_tools: Dict[str, ToolInterface] = {}
        self.failed_tools: Dict[str, str] = {}
    
    async def load_tool(self, tool_name: str, **kwargs) -> Optional[ToolInterface]:
        """Load a specific tool"""
        raise NotImplementedError("Subclasses must implement load_tool")
    
    async def load_all_tools(self) -> Dict[str, ToolInterface]:
        """Load all available tools"""
        raise NotImplementedError("Subclasses must implement load_all_tools")
    
    def get_loaded_tools(self) -> Dict[str, ToolInterface]:
        """Get all loaded tools"""
        return self.loaded_tools.copy()
    
    def get_failed_tools(self) -> Dict[str, str]:
        """Get tools that failed to load"""
        return self.failed_tools.copy()
    
    def get_tool(self, tool_name: str) -> Optional[ToolInterface]:
        """Get a specific loaded tool"""
        return self.loaded_tools.get(tool_name)


class StrandsToolsLoader(ToolLoader):
    """Loader for Strands tools from strands-agents-tools package"""
    
    def __init__(self):
        super().__init__()
        self.strands_tools_mapping = {
            # Core computational tools
            "calculator": "strands_agents_tools.calculator",
            "python_repl": "strands_agents_tools.python_repl",
            "think": "strands_agents_tools.think",
            
            # File and data operations
            "file_read": "strands_agents_tools.file_read",
            "file_write": "strands_agents_tools.file_write",
            "editor": "strands_agents_tools.editor",
            
            # System and environment
            "shell": "strands_agents_tools.shell",
            "environment": "strands_agents_tools.environment",
            "current_time": "strands_agents_tools.current_time",
            
            # Data analysis and visualization
            "diagram": "strands_agents_tools.diagram",
            "graph": "strands_agents_tools.graph",
            "generate_image": "strands_agents_tools.generate_image",
            "image_reader": "strands_agents_tools.image_reader",
            
            # External data and APIs
            "http_request": "strands_agents_tools.http_request",
            "retrieve": "strands_agents_tools.retrieve",
            "rss": "strands_agents_tools.rss",
            
            # Memory and persistence
            "memory": "strands_agents_tools.memory",
            "mem0_memory": "strands_agents_tools.mem0_memory",
            "journal": "strands_agents_tools.journal",
            
            # Communication and integration
            "slack": "strands_agents_tools.slack",
            "a2a_client": "strands_agents_tools.a2a_client",
            "mcp_client": "strands_agents_tools.mcp_client",
            
            # Advanced capabilities
            "use_aws": "strands_agents_tools.use_aws",
            "use_browser": "strands_agents_tools.use_browser",
            "use_computer": "strands_agents_tools.use_computer",
            "use_llm": "strands_agents_tools.use_llm",
            "use_agent": "strands_agents_tools.use_agent",
            
            # Multi-agent capabilities
            "swarm": "strands_agents_tools.swarm",
            "batch": "strands_agents_tools.batch",
            "agent_graph": "strands_agents_tools.agent_graph",
            
            # Development and utilities
            "load_tool": "strands_agents_tools.load_tool",
            "cron": "strands_agents_tools.cron"
        }
    
    async def load_tool(self, tool_name: str, **kwargs) -> Optional[ToolInterface]:
        """Load a specific Strands tool"""
        try:
            if tool_name in self.loaded_tools:
                return self.loaded_tools[tool_name]
            
            if tool_name not in self.strands_tools_mapping:
                logger.warning(f"Unknown Strands tool: {tool_name}")
                self.failed_tools[tool_name] = f"Unknown tool: {tool_name}"
                return None
            
            module_path = self.strands_tools_mapping[tool_name]
            
            # Import the tool module
            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                logger.warning(f"Could not import Strands tool module {module_path}: {e}")
                self.failed_tools[tool_name] = f"Import failed: {e}"
                return None
            
            # Get the tool function from the module
            tool_func = getattr(module, tool_name, None)
            if tool_func is None:
                # Try to find the main tool function in the module
                for attr_name in dir(module):
                    if not attr_name.startswith('_'):
                        attr = getattr(module, attr_name)
                        if callable(attr) and hasattr(attr, '__name__'):
                            tool_func = attr
                            break
            
            if tool_func is None:
                logger.warning(f"Could not find tool function in module: {module_path}")
                self.failed_tools[tool_name] = f"Tool function not found in module"
                return None
            
            # Create tool metadata
            metadata = ToolMetadata(
                name=tool_name,
                description=getattr(tool_func, '__doc__', f"Strands tool: {tool_name}") or f"Strands tool: {tool_name}",
                tool_type=ToolType.STRANDS_OFFICIAL,
                module_path=module_path,
                status=ToolStatus.AVAILABLE,
                capabilities=self._get_tool_capabilities(tool_name),
                tags=["strands", "official"]
            )
            
            # Create tool interface
            tool_interface = StrandsToolInterface(metadata, tool_func)
            
            # Initialize the tool
            if await tool_interface.initialize():
                self.loaded_tools[tool_name] = tool_interface
                logger.info(f"Successfully loaded Strands tool: {tool_name}")
                return tool_interface
            else:
                self.failed_tools[tool_name] = f"Initialization failed"
                return None
                
        except Exception as e:
            logger.error(f"Failed to load Strands tool {tool_name}: {e}")
            self.failed_tools[tool_name] = str(e)
            return None
    
    async def load_all_tools(self) -> Dict[str, ToolInterface]:
        """Load all available Strands tools"""
        logger.info("Loading all Strands tools...")
        
        for tool_name in self.strands_tools_mapping.keys():
            await self.load_tool(tool_name)
        
        logger.info(f"Loaded {len(self.loaded_tools)} Strands tools, {len(self.failed_tools)} failed")
        return self.loaded_tools.copy()
    
    async def load_essential_tools(self) -> Dict[str, ToolInterface]:
        """Load essential Strands tools for basic functionality"""
        essential_tools = [
            "calculator",
            "file_read",
            "file_write",
            "memory",
            "http_request",
            "retrieve",
            "use_aws",
            "use_llm",
            "current_time"
        ]
        
        logger.info("Loading essential Strands tools...")
        
        for tool_name in essential_tools:
            await self.load_tool(tool_name)
        
        loaded_essential = {name: tool for name, tool in self.loaded_tools.items() if name in essential_tools}
        logger.info(f"Loaded {len(loaded_essential)} essential Strands tools")
        
        return loaded_essential
    
    def _get_tool_capabilities(self, tool_name: str) -> List[str]:
        """Get capabilities for a specific tool"""
        capabilities_map = {
            "calculator": ["computation", "math"],
            "python_repl": ["computation", "programming", "data_analysis"],
            "file_read": ["file_io", "data_access"],
            "file_write": ["file_io", "data_storage"],
            "memory": ["persistence", "state_management"],
            "http_request": ["networking", "api_access"],
            "retrieve": ["knowledge_base", "search"],
            "use_aws": ["cloud_services", "aws"],
            "use_llm": ["ai", "language_model"],
            "diagram": ["visualization", "graphics"],
            "shell": ["system", "command_execution"],
            "slack": ["communication", "messaging"],
            "use_browser": ["web_browsing", "automation"],
            "swarm": ["multi_agent", "orchestration"]
        }
        
        return capabilities_map.get(tool_name, ["general"])


class CustomToolsLoader(ToolLoader):
    """Loader for custom DcisionAI tools"""
    
    def __init__(self, tools_directory: Optional[str] = None):
        super().__init__()
        self.tools_directory = Path(tools_directory) if tools_directory else Path(__file__).parent / "custom"
        self.custom_tools_registry = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register built-in custom tools"""
        from .intent_tool import IntentTool
        from .model_builder_tool import ModelBuilderTool
        
        # Try to import DataTool if it exists
        try:
            from .custom.data_tool import DataTool
            data_tool_class = DataTool
        except ImportError:
            data_tool_class = None
        
        self.custom_tools_registry = {
            "intent_tool": IntentTool,
            "model_builder_tool": ModelBuilderTool,
            # Additional custom tools will be registered here
        }
        
        if data_tool_class:
            self.custom_tools_registry["data_tool"] = data_tool_class
    
    async def load_tool(self, tool_name: str, **kwargs) -> Optional[ToolInterface]:
        """Load a specific custom tool"""
        try:
            if tool_name in self.loaded_tools:
                return self.loaded_tools[tool_name]
            
            # Check if it's a registered built-in tool
            if tool_name in self.custom_tools_registry:
                tool_class = self.custom_tools_registry[tool_name]
                return await self._load_tool_class(tool_name, tool_class)
            
            # Try to load from tools directory
            tool_file = self.tools_directory / f"{tool_name}.py"
            if tool_file.exists():
                return await self._load_tool_from_file(tool_name, tool_file)
            
            logger.warning(f"Custom tool not found: {tool_name}")
            self.failed_tools[tool_name] = f"Tool not found: {tool_name}"
            return None
            
        except Exception as e:
            logger.error(f"Failed to load custom tool {tool_name}: {e}")
            self.failed_tools[tool_name] = str(e)
            return None
    
    async def _load_tool_class(self, tool_name: str, tool_class: Type[BaseTool]) -> Optional[ToolInterface]:
        """Load a tool from a class"""
        try:
            # Create tool metadata
            tool_instance = tool_class()
            metadata = tool_instance.metadata
            
            # Create tool interface
            tool_interface = CustomToolInterface(metadata, tool_class)
            
            # Initialize the tool
            if await tool_interface.initialize():
                self.loaded_tools[tool_name] = tool_interface
                logger.info(f"Successfully loaded custom tool: {tool_name}")
                return tool_interface
            else:
                self.failed_tools[tool_name] = f"Initialization failed"
                return None
                
        except Exception as e:
            logger.error(f"Failed to load tool class {tool_name}: {e}")
            self.failed_tools[tool_name] = str(e)
            return None
    
    async def _load_tool_from_file(self, tool_name: str, tool_file: Path) -> Optional[ToolInterface]:
        """Load a tool from a Python file"""
        try:
            # Load the module from file
            spec = importlib.util.spec_from_file_location(tool_name, tool_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find tool class in the module
            tool_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseTool) and attr != BaseTool:
                    tool_class = attr
                    break
            
            if tool_class is None:
                logger.warning(f"No tool class found in {tool_file}")
                self.failed_tools[tool_name] = f"No tool class found in file"
                return None
            
            return await self._load_tool_class(tool_name, tool_class)
            
        except Exception as e:
            logger.error(f"Failed to load tool from file {tool_file}: {e}")
            self.failed_tools[tool_name] = str(e)
            return None
    
    async def load_all_tools(self) -> Dict[str, ToolInterface]:
        """Load all available custom tools"""
        logger.info("Loading all custom tools...")
        
        # Load built-in tools
        for tool_name in self.custom_tools_registry.keys():
            await self.load_tool(tool_name)
        
        # Load tools from directory
        if self.tools_directory.exists():
            for tool_file in self.tools_directory.glob("*.py"):
                if not tool_file.name.startswith("_"):
                    tool_name = tool_file.stem
                    await self.load_tool(tool_name)
        
        logger.info(f"Loaded {len(self.loaded_tools)} custom tools, {len(self.failed_tools)} failed")
        return self.loaded_tools.copy()
    
    def register_tool(self, tool_name: str, tool_class: Type[BaseTool]):
        """Register a custom tool class"""
        self.custom_tools_registry[tool_name] = tool_class
        logger.info(f"Registered custom tool: {tool_name}")


class CombinedToolLoader:
    """Combined loader for both Strands and custom tools"""
    
    def __init__(self, custom_tools_directory: Optional[str] = None):
        self.strands_loader = StrandsToolsLoader()
        self.custom_loader = CustomToolsLoader(custom_tools_directory)
        self.all_tools: Dict[str, ToolInterface] = {}
    
    async def load_all_tools(self) -> Dict[str, ToolInterface]:
        """Load all tools from both loaders"""
        logger.info("Loading all tools (Strands + Custom)...")
        
        # Load Strands tools
        strands_tools = await self.strands_loader.load_all_tools()
        
        # Load custom tools
        custom_tools = await self.custom_loader.load_all_tools()
        
        # Combine tools
        self.all_tools = {**strands_tools, **custom_tools}
        
        logger.info(f"Loaded {len(self.all_tools)} total tools")
        logger.info(f"  - Strands tools: {len(strands_tools)}")
        logger.info(f"  - Custom tools: {len(custom_tools)}")
        
        return self.all_tools.copy()
    
    async def load_essential_tools(self) -> Dict[str, ToolInterface]:
        """Load essential tools for basic functionality"""
        logger.info("Loading essential tools...")
        
        # Load essential Strands tools
        essential_strands = await self.strands_loader.load_essential_tools()
        
        # Load essential custom tools
        essential_custom_names = ["intent_tool", "model_builder_tool"]
        essential_custom = {}
        for tool_name in essential_custom_names:
            tool = await self.custom_loader.load_tool(tool_name)
            if tool:
                essential_custom[tool_name] = tool
        
        # Combine essential tools
        essential_tools = {**essential_strands, **essential_custom}
        
        logger.info(f"Loaded {len(essential_tools)} essential tools")
        return essential_tools
    
    def get_tool(self, tool_name: str) -> Optional[ToolInterface]:
        """Get a specific tool"""
        return self.all_tools.get(tool_name)
    
    def get_tools_by_type(self, tool_type: ToolType) -> Dict[str, ToolInterface]:
        """Get tools by type"""
        return {
            name: tool for name, tool in self.all_tools.items()
            if tool.tool_type == tool_type
        }
    
    def get_tools_by_capability(self, capability: str) -> Dict[str, ToolInterface]:
        """Get tools by capability"""
        return {
            name: tool for name, tool in self.all_tools.items()
            if capability in tool.metadata.capabilities
        }
    
    def get_failed_tools(self) -> Dict[str, str]:
        """Get all failed tools from both loaders"""
        failed_tools = {}
        failed_tools.update(self.strands_loader.get_failed_tools())
        failed_tools.update(self.custom_loader.get_failed_tools())
        return failed_tools