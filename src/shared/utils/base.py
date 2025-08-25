"""
Base Tool Classes and Exceptions
Provides base functionality for all tools in the DcisionAI platform
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from .interfaces import ToolInterface, ToolMetadata, ToolResponse, ToolType, ToolStatus
except ImportError:
    # Fallback for direct execution
    from interfaces import ToolInterface, ToolMetadata, ToolResponse, ToolType, ToolStatus

logger = logging.getLogger(__name__)


class ToolError(Exception):
    """Base exception for tool errors"""
    
    def __init__(self, message: str, tool_name: str = None, error_code: str = None):
        super().__init__(message)
        self.tool_name = tool_name
        self.error_code = error_code
        self.timestamp = datetime.now()


class ToolValidationError(ToolError):
    """Exception for tool validation errors"""
    pass


class ToolExecutionError(ToolError):
    """Exception for tool execution errors"""
    pass


class ToolInitializationError(ToolError):
    """Exception for tool initialization errors"""
    pass


class BaseTool(ABC):
    """Base class for all custom DcisionAI tools"""
    
    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version
        self.logger = logging.getLogger(f"tools.{name}")
        self._initialized = False
        self._metadata = None
        
        # Execution tracking
        self._execution_count = 0
        self._last_execution_time = None
        self._success_count = 0
        self._total_execution_time = 0.0
        
        # Session memory integration
        self.strands_agent = None
        self.strands_tools = {}
    
    @property
    def metadata(self) -> ToolMetadata:
        """Get tool metadata"""
        if self._metadata is None:
            self._metadata = ToolMetadata(
                name=self.name,
                description=self.description,
                tool_type=ToolType.DCISIONAI_CUSTOM,
                version=self.version,
                status=ToolStatus.AVAILABLE if self._initialized else ToolStatus.UNAVAILABLE
            )
        return self._metadata
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the tool"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate tool parameters"""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup tool resources - override if needed"""
        pass
    
    def _create_response(self, success: bool, data: Any = None, error: str = None, 
                        execution_time: float = 0.0, metadata: Dict[str, Any] = None) -> ToolResponse:
        """Create a standardized tool response"""
        return ToolResponse(
            success=success,
            data=data,
            error=error,
            execution_time=execution_time,
            tool_name=self.name,
            metadata=metadata or {}
        )
    
    def _log_execution(self, operation: str, parameters: Dict[str, Any], 
                      success: bool, execution_time: float, error: str = None):
        """Log tool execution and update metrics"""
        # Update execution metrics
        self._execution_count += 1
        self._last_execution_time = datetime.now().isoformat()
        self._total_execution_time += execution_time
        
        if success:
            self._success_count += 1
            self.logger.info(
                f"Tool {self.name} executed {operation} successfully in {execution_time:.3f}s",
                extra={
                    "tool_name": self.name,
                    "operation": operation,
                    "parameters": parameters,
                    "execution_time": execution_time,
                    "success": True
                }
            )
        else:
            self.logger.error(
                f"Tool {self.name} failed to execute {operation}: {error}",
                extra={
                    "tool_name": self.name,
                    "operation": operation,
                    "parameters": parameters,
                    "execution_time": execution_time,
                    "success": False,
                    "error": error
                }
            )
    
    @property
    def _success_rate(self) -> float:
        """Calculate success rate"""
        if self._execution_count == 0:
            return 1.0
        return self._success_count / self._execution_count
    
    @property
    def _avg_execution_time(self) -> float:
        """Calculate average execution time"""
        if self._execution_count == 0:
            return 0.0
        return self._total_execution_time / self._execution_count
    
    async def _initialize_strands_tools(self):
        """Initialize Strands tools integration (graceful degradation)"""
        try:
            from strands_tools import memory, retrieve, use_aws
            from strands import Agent
            
            self.strands_agent = Agent(tools=[memory, retrieve, use_aws])
            self.strands_tools = {
                'memory': self.strands_agent.tool.memory,
                'retrieve': self.strands_agent.tool.retrieve,
                'use_aws': self.strands_agent.tool.use_aws
            }
            self.logger.info(f"Strands tools initialized for {self.name}")
            
        except ImportError as e:
            self.logger.warning(f"Strands tools not available for {self.name}: {e}")
            self.strands_agent = None
            self.strands_tools = {}
        except Exception as e:
            self.logger.warning(f"Failed to initialize Strands tools for {self.name}: {e}")
            self.strands_agent = None
            self.strands_tools = {}


# IntentTool implementation moved to separate file: intent_tool.py