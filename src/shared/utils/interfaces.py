"""
Tool Interfaces and Data Models
Defines standard interfaces for all tools in the DcisionAI platform
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ToolType(str, Enum):
    """Tool type enumeration"""
    STRANDS_OFFICIAL = "strands_official"
    DCISIONAI_CUSTOM = "dcisionai_custom"
    EXTERNAL_MCP = "external_mcp"
    PLUGIN = "plugin"


class ToolStatus(str, Enum):
    """Tool status enumeration"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    LOADING = "loading"
    DEPRECATED = "deprecated"


class ToolMetadata(BaseModel):
    """Tool metadata model"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    tool_type: ToolType = Field(..., description="Type of tool")
    status: ToolStatus = Field(default=ToolStatus.AVAILABLE, description="Tool status")
    version: str = Field(default="1.0.0", description="Tool version")
    module_path: Optional[str] = Field(default=None, description="Python module path")
    dependencies: List[str] = Field(default_factory=list, description="Tool dependencies")
    capabilities: List[str] = Field(default_factory=list, description="Tool capabilities")
    tags: List[str] = Field(default_factory=list, description="Tool tags")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if status is ERROR")
    
    class Config:
        use_enum_values = True


class ToolResponse(BaseModel):
    """Standard tool response model"""
    success: bool = Field(..., description="Whether tool execution succeeded")
    data: Any = Field(default=None, description="Tool output data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    tool_name: str = Field(..., description="Name of the tool that generated this response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        use_enum_values = True


class ToolInterface(ABC):
    """Abstract base interface for all tools"""
    
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the tool"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate tool parameters"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup tool resources"""
        pass
    
    @property
    def is_initialized(self) -> bool:
        """Check if tool is initialized"""
        return self._initialized
    
    @property
    def name(self) -> str:
        """Get tool name"""
        return self.metadata.name
    
    @property
    def description(self) -> str:
        """Get tool description"""
        return self.metadata.description
    
    @property
    def tool_type(self) -> ToolType:
        """Get tool type"""
        return self.metadata.tool_type
    
    @property
    def status(self) -> ToolStatus:
        """Get tool status"""
        return self.metadata.status
    
    def update_status(self, status: ToolStatus, error_message: Optional[str] = None):
        """Update tool status"""
        self.metadata.status = status
        self.metadata.error_message = error_message
        self.metadata.updated_at = datetime.now()


class StrandsToolInterface(ToolInterface):
    """Interface for Strands tools"""
    
    def __init__(self, metadata: ToolMetadata, strands_tool: Callable):
        super().__init__(metadata)
        self.strands_tool = strands_tool
    
    async def initialize(self) -> bool:
        """Initialize Strands tool"""
        try:
            # Verify the tool is callable and has Strands attributes
            if not callable(self.strands_tool):
                raise ValueError(f"Strands tool {self.name} is not callable")
            
            # Check for Strands tool attributes
            if not hasattr(self.strands_tool, '__name__'):
                raise ValueError(f"Strands tool {self.name} missing __name__ attribute")
            
            self._initialized = True
            self.update_status(ToolStatus.AVAILABLE)
            return True
            
        except Exception as e:
            self.update_status(ToolStatus.ERROR, str(e))
            return False
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute Strands tool"""
        start_time = datetime.now()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.is_initialized:
                raise RuntimeError(f"Tool {self.name} failed to initialize")
            
            # Execute the Strands tool
            result = await self.strands_tool(**kwargs) if hasattr(self.strands_tool, '__await__') else self.strands_tool(**kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=True,
                data=result,
                metadata={
                    "tool_type": self.tool_type,
                    "strands_tool": True,
                    "parameters": kwargs
                },
                execution_time=execution_time,
                tool_name=self.name
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=False,
                error=str(e),
                metadata={
                    "tool_type": self.tool_type,
                    "strands_tool": True,
                    "parameters": kwargs
                },
                execution_time=execution_time,
                tool_name=self.name
            )
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters for Strands tool"""
        try:
            # Basic validation - check if tool accepts the parameters
            import inspect
            sig = inspect.signature(self.strands_tool)
            
            # Check if all required parameters are provided
            for param_name, param in sig.parameters.items():
                if param.default == inspect.Parameter.empty and param_name not in kwargs:
                    if param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                        return False
            
            return True
            
        except Exception:
            return False
    
    async def cleanup(self) -> None:
        """Cleanup Strands tool resources"""
        # Most Strands tools don't require explicit cleanup
        pass


class CustomToolInterface(ToolInterface):
    """Interface for custom DcisionAI tools"""
    
    def __init__(self, metadata: ToolMetadata, tool_class: type):
        super().__init__(metadata)
        self.tool_class = tool_class
        self.tool_instance = None
    
    async def initialize(self) -> bool:
        """Initialize custom tool"""
        try:
            self.tool_instance = self.tool_class()
            
            # Initialize the tool instance if it has an initialize method
            if hasattr(self.tool_instance, 'initialize'):
                await self.tool_instance.initialize()
            
            self._initialized = True
            self.update_status(ToolStatus.AVAILABLE)
            return True
            
        except Exception as e:
            self.update_status(ToolStatus.ERROR, str(e))
            return False
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute custom tool"""
        start_time = datetime.now()
        
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.is_initialized:
                raise RuntimeError(f"Tool {self.name} failed to initialize")
            
            # Execute the custom tool
            if hasattr(self.tool_instance, 'execute'):
                result = await self.tool_instance.execute(**kwargs)
            else:
                raise NotImplementedError(f"Tool {self.name} does not implement execute method")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=True,
                data=result,
                metadata={
                    "tool_type": self.tool_type,
                    "custom_tool": True,
                    "parameters": kwargs
                },
                execution_time=execution_time,
                tool_name=self.name
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=False,
                error=str(e),
                metadata={
                    "tool_type": self.tool_type,
                    "custom_tool": True,
                    "parameters": kwargs
                },
                execution_time=execution_time,
                tool_name=self.name
            )
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters for custom tool"""
        try:
            if hasattr(self.tool_instance, 'validate_parameters'):
                return await self.tool_instance.validate_parameters(**kwargs)
            return True
            
        except Exception:
            return False
    
    async def cleanup(self) -> None:
        """Cleanup custom tool resources"""
        try:
            if self.tool_instance and hasattr(self.tool_instance, 'cleanup'):
                await self.tool_instance.cleanup()
        except Exception:
            pass  # Ignore cleanup errors