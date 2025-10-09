#!/usr/bin/env python3
"""
DcisionAI Platform - Base Tool Framework
=======================================

Base class for all domain-specific tools in the DcisionAI platform.
Provides common functionality and interface for tools across all domains.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
import time

@dataclass
class ToolMetadata:
    """Metadata for tool identification and capabilities."""
    name: str
    domain: str
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    capabilities: List[str]
    created_at: datetime
    last_updated: datetime

@dataclass
class ToolResult:
    """Standardized result structure for all tools."""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    errors: List[str] = None

class BaseTool(ABC):
    """
    Abstract base class for all DcisionAI domain tools.
    
    This class provides the common interface and functionality that all
    domain-specific tools must implement.
    """
    
    def __init__(self, name: str, domain: str, version: str, description: str):
        """Initialize the base tool with metadata."""
        self.name = name
        self.domain = domain
        self.version = version
        self.description = description
        
        # Setup metadata
        self.metadata = ToolMetadata(
            name=name,
            domain=domain,
            version=version,
            description=description,
            input_schema={},
            output_schema={},
            capabilities=[],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Setup logging
        self.logger = logging.getLogger(f"{domain}_{name}_tool")
        self.logger.setLevel(logging.INFO)
        
        # Initialize tool-specific components
        self._initialize_tool()
        
        self.logger.info(f"✅ {domain} {name} Tool v{version} initialized successfully")
    
    @abstractmethod
    def _initialize_tool(self) -> None:
        """Initialize tool-specific components. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool's main functionality. Must be implemented by subclasses."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get tool metadata for discovery and validation."""
        return {
            "name": self.metadata.name,
            "domain": self.metadata.domain,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "input_schema": self.metadata.input_schema,
            "output_schema": self.metadata.output_schema,
            "capabilities": self.metadata.capabilities,
            "created_at": self.metadata.created_at.isoformat(),
            "last_updated": self.metadata.last_updated.isoformat()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get tool health status for monitoring."""
        return {
            "status": "healthy",
            "name": self.name,
            "domain": self.domain,
            "version": self.version,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_metadata(self, **kwargs) -> None:
        """Update tool metadata."""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
        
        self.metadata.last_updated = datetime.now()
        self.logger.info(f"Metadata updated: {kwargs}")
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters. Can be overridden by subclasses."""
        # Basic validation - subclasses can implement domain-specific validation
        return True
    
    def execute_with_metrics(self, **kwargs) -> ToolResult:
        """Execute tool with performance metrics and error handling."""
        start_time = time.time()
        timestamp = datetime.now()
        
        try:
            # Validate input
            if not self.validate_input(**kwargs):
                return ToolResult(
                    success=False,
                    data=None,
                    metadata={"error": "Input validation failed"},
                    execution_time=0.0,
                    timestamp=timestamp,
                    errors=["Input validation failed"]
                )
            
            # Execute tool
            result = self.execute(**kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Update result with metrics
            result.execution_time = execution_time
            result.timestamp = timestamp
            
            # Log successful execution
            self.logger.info(f"Tool executed successfully in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tool execution failed: {str(e)}"
            
            self.logger.error(error_msg, exc_info=True)
            
            return ToolResult(
                success=False,
                data=None,
                metadata={"error": error_msg},
                execution_time=execution_time,
                timestamp=timestamp,
                errors=[error_msg]
            )
    
    def get_capabilities(self) -> List[str]:
        """Get list of tool capabilities."""
        return self.metadata.capabilities.copy()
    
    def add_capability(self, capability: str) -> None:
        """Add a capability to the tool."""
        if capability not in self.metadata.capabilities:
            self.metadata.capabilities.append(capability)
            self.logger.info(f"Capability '{capability}' added")
    
    def remove_capability(self, capability: str) -> None:
        """Remove a capability from the tool."""
        if capability in self.metadata.capabilities:
            self.metadata.capabilities.remove(capability)
            self.logger.info(f"Capability '{capability}' removed")
    
    def set_input_schema(self, schema: Dict[str, Any]) -> None:
        """Set the input schema for the tool."""
        self.metadata.input_schema = schema
        self.logger.info("Input schema updated")
    
    def set_output_schema(self, schema: Dict[str, Any]) -> None:
        """Set the output schema for the tool."""
        self.metadata.output_schema = schema
        self.logger.info("Output schema updated")
    
    def log_execution(self, kwargs: Dict[str, Any], result: ToolResult) -> None:
        """Log tool execution details for monitoring and debugging."""
        self.logger.info(f"Tool execution completed: {kwargs.get('query', 'N/A')[:100]}...")
        self.logger.debug(f"Input parameters: {json.dumps(kwargs, indent=2)}")
        self.logger.debug(f"Execution result: {json.dumps(result.__dict__, indent=2, default=str)}")
