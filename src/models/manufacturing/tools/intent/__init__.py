"""
DcisionAI Intent Tool Package
============================

Enhanced DcisionAI Intent Classification Tool with 6-specialist AWS-style pattern.
Strict classification rules, expertise weighting, and robust consensus building.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

from .DcisionAI_Intent_Tool_v1 import (
    DcisionAI_Intent_Tool,
    IntentClassification,
    SwarmPerformanceMetrics,
    create_dcisionai_intent_tool
)

from .DcisionAI_Intent_Tool_v2 import (
    DcisionAI_Intent_Tool_v2,
    create_dcisionai_intent_tool_v2
)

from .DcisionAI_Intent_Tool_v3 import (
    DcisionAI_Intent_Tool_v3,
    create_dcisionai_intent_tool_v3
)

__all__ = [
    "DcisionAI_Intent_Tool",
    "IntentClassification", 
    "SwarmPerformanceMetrics",
    "create_dcisionai_intent_tool",
    "DcisionAI_Intent_Tool_v2",
    "create_dcisionai_intent_tool_v2",
    "DcisionAI_Intent_Tool_v3",
    "create_dcisionai_intent_tool_v3"
]
