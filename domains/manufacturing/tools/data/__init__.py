#!/usr/bin/env python3
"""
DcisionAI Data Tool Package
===========================

Three-stage data analysis for manufacturing optimization:
1. Query data extraction (intent-aware)
2. Customer data source analysis (honest assessment)
3. External data recommendations (intent-specific)

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

from .DcisionAI_Data_Tool import (
    DataTool,
    DataAnalysisResult,
    DataRequirement,
    create_data_tool
)

__all__ = [
    "DataTool",
    "DataAnalysisResult", 
    "DataRequirement",
    "create_data_tool"
]
