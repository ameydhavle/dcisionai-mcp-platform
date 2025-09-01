#!/usr/bin/env python3
"""
DcisionAI Platform - Shared Components
=====================================

Shared framework components for the multi-domain DcisionAI platform.
"""

from .core.base_agent import BaseAgent, AgentMetadata
from .core.domain_manager import DomainManager, DomainInfo
from .tools.base_tool import BaseTool, ToolMetadata, ToolResult
from .deployment.base_deployer import BaseDeployer, DeploymentConfig, DeploymentResult
from .config.settings import settings, Settings

__version__ = "1.0.0"
__all__ = [
    "BaseAgent",
    "AgentMetadata", 
    "DomainManager",
    "DomainInfo",
    "BaseTool",
    "ToolMetadata",
    "ToolResult",
    "BaseDeployer",
    "DeploymentConfig",
    "DeploymentResult",
    "settings",
    "Settings"
]
