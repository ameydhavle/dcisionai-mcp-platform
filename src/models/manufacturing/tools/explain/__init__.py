"""
DcisionAI Platform - Explain Tools Package
==========================================

Advanced customer-facing explanation with business-friendly language and UI-friendly output.
"""

from .explain_tool import ExplainTool
from .explain_swarm_orchestrator import (
    ExplainSwarmOrchestrator,
    ExplainSwarm,
    WorkflowExplanation,
    ToolExplanation,
    ExplanationType,
    AudienceType,
    SwarmStrategy,
    SwarmPerformanceMetrics
)

__version__ = "1.0.0"
__author__ = "DcisionAI"
__email__ = "support@dcisionai.com"

__all__ = [
    "ExplainTool",
    "ExplainSwarmOrchestrator",
    "ExplainSwarm",
    "WorkflowExplanation",
    "ToolExplanation",
    "ExplanationType",
    "AudienceType",
    "SwarmStrategy",
    "SwarmPerformanceMetrics"
]

# Production-ready tool with no fallbacks, no mocks
# All implementations must be production-ready from day one
