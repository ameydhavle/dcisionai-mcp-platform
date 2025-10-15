"""
DcisionAI MCP Server
===================

A Model Context Protocol (MCP) server for AI-powered business optimization
with industry-specific workflows and Qwen 30B integration.

This package provides:
- Industry-specific optimization workflows
- Qwen 30B integration for mathematical reasoning
- AgentCore Gateway integration
- 21 pre-built workflows across 7 industries
- Production-ready optimization engine

Example usage:
    from dcisionai_mcp_server import DcisionAIMCPServer
    
    server = DcisionAIMCPServer()
    server.run()
"""

__version__ = "1.0.0"
__author__ = "DcisionAI Team"
__email__ = "team@dcisionai.com"
__description__ = "AI-powered business optimization MCP server"

from .server import DcisionAIMCPServer
from .tools import (
    classify_intent,
    analyze_data,
    build_model,
    solve_optimization,
    get_workflow_templates,
    execute_workflow,
)
from .workflows import WorkflowManager
from .config import Config

__all__ = [
    "DcisionAIMCPServer",
    "classify_intent",
    "analyze_data", 
    "build_model",
    "solve_optimization",
    "get_workflow_templates",
    "execute_workflow",
    "WorkflowManager",
    "Config",
]
