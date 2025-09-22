#!/usr/bin/env python3
"""
DcisionAI Platform - Manufacturing Domain
========================================

Manufacturing optimization and production planning domain.
"""

# Import the invoke function from the AgentCore agent
from .agents.DcisionAI_Manufacturing_Agent_v1 import invoke

__version__ = "1.0.0"
__all__ = [
    "invoke"
]
