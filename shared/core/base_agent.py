#!/usr/bin/env python3
"""
DcisionAI Platform - Base Agent Framework
========================================

Base class for all domain-specific agents in the DcisionAI platform.
Provides common functionality and interface for manufacturing, finance, pharma, etc.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class AgentMetadata:
    """Metadata for agent identification and versioning."""
    domain: str
    version: str
    description: str
    capabilities: List[str]
    created_at: datetime
    last_updated: datetime

class BaseAgent(ABC):
    """
    Abstract base class for all DcisionAI domain agents.
    
    This class provides the common interface and functionality that all
    domain-specific agents must implement.
    """
    
    def __init__(self, domain: str, version: str, description: str):
        """Initialize the base agent with domain information."""
        self.domain = domain
        self.version = version
        self.description = description
        self.metadata = AgentMetadata(
            domain=domain,
            version=version,
            description=description,
            capabilities=[],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Setup logging
        self.logger = logging.getLogger(f"{domain}_agent")
        self.logger.setLevel(logging.INFO)
        
        # Initialize tools
        self.tools = {}
        self._initialize_tools()
        
        self.logger.info(f"✅ {domain} Agent v{version} initialized successfully")
    
    @abstractmethod
    def _initialize_tools(self) -> None:
        """Initialize domain-specific tools. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a domain-specific request. Must be implemented by subclasses."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata for identification and discovery."""
        return {
            "domain": self.metadata.domain,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "capabilities": self.metadata.capabilities,
            "created_at": self.metadata.created_at.isoformat(),
            "last_updated": self.metadata.last_updated.isoformat(),
            "available_tools": list(self.tools.keys())
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status for monitoring."""
        return {
            "status": "healthy",
            "domain": self.domain,
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "tools_status": {name: "active" for name in self.tools.keys()}
        }
    
    def update_metadata(self, **kwargs) -> None:
        """Update agent metadata."""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
        
        self.metadata.last_updated = datetime.now()
        self.logger.info(f"Metadata updated: {kwargs}")
    
    def register_tool(self, name: str, tool: Any) -> None:
        """Register a tool with the agent."""
        self.tools[name] = tool
        self.metadata.capabilities.append(name)
        self.logger.info(f"Tool '{name}' registered successfully")
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a registered tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tools."""
        return list(self.tools.keys())
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate incoming request format. Can be overridden by subclasses."""
        required_fields = ["prompt", "domain"]
        return all(field in request for field in required_fields)
    
    def log_request(self, request: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Log request and response for monitoring and debugging."""
        self.logger.info(f"Request processed: {request.get('prompt', 'N/A')[:100]}...")
        self.logger.debug(f"Full request: {json.dumps(request, indent=2)}")
        self.logger.debug(f"Full response: {json.dumps(response, indent=2)}")
