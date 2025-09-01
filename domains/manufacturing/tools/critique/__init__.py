"""
DcisionAI Platform - Critique Tools Package
===========================================

Advanced multi-tool supervision with constructive criticism and human-in-the-loop capabilities.
"""

from .critique_tool import CritiqueTool
from .critique_swarm_orchestrator import (
    CritiqueSwarmOrchestrator,
    CritiqueSwarm,
    WorkflowCritique,
    ToolCritique,
    CritiqueType,
    ConfidenceLevel,
    SwarmStrategy,
    SwarmPerformanceMetrics
)

__version__ = "1.0.0"
__author__ = "DcisionAI"
__email__ = "support@dcisionai.com"

__all__ = [
    "CritiqueTool",
    "CritiqueSwarmOrchestrator",
    "CritiqueSwarm",
    "WorkflowCritique",
    "ToolCritique",
    "CritiqueType",
    "ConfidenceLevel",
    "SwarmStrategy",
    "SwarmPerformanceMetrics"
]

# Production-ready tool with no fallbacks, no mocks
# All implementations must be production-ready from day one
