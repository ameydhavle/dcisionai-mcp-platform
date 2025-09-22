#!/usr/bin/env python3
"""
MCP Protocol Compliance Testing Module
=====================================

This module provides comprehensive testing for MCP (Model Context Protocol) compliance
to ensure DcisionAI Platform meets all protocol requirements for private listing.

Testing covers:
- Core protocol compliance
- Tool management
- Resource management
- Authentication & security
- Error handling & resilience
"""

__version__ = "1.0.0"
__author__ = "DcisionAI Platform Team"
__status__ = "Production Ready"

from .mcp_compliance_tester import MCPComplianceTester
from .mcp_compliance_validator import MCPComplianceValidator

__all__ = [
    "MCPComplianceTester",
    "MCPComplianceValidator"
]
