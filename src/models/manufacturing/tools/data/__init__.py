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

from .DcisionAI_Data_Tool_v1 import (
    DcisionAI_Data_Tool,
    DataAnalysisResult,
    DataRequirement,
    DataSourceRecommendation,
    DataCategory,
    DataSource,
    create_dcisionai_data_tool
)

from .DcisionAI_Data_Tool_v2 import (
    DcisionAI_Data_Tool_v2,
    create_dcisionai_data_tool_v2
)

__all__ = [
    "DcisionAI_Data_Tool",
    "DataAnalysisResult", 
    "DataRequirement",
    "DataSourceRecommendation",
    "DataCategory",
    "DataSource",
    "create_dcisionai_data_tool",
    "DcisionAI_Data_Tool_v2",
    "create_dcisionai_data_tool_v2"
]
