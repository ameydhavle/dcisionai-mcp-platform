#!/usr/bin/env python3
"""
Simple Local Test
================

Test the basic workflow locally to ensure nothing is broken.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from mcp_server.tools.manufacturing.intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool_v6
from mcp_server.tools.manufacturing.data.DcisionAI_Data_Tool import create_data_tool

def test_basic_workflow():
    """Test basic intent and data tools"""
    print("🧪 Testing basic workflow...")
    
    # Test intent tool
    print("1. Testing intent tool...")
    intent_tool = create_dcisionai_intent_tool_v6()
    intent_result = intent_tool.classify_intent("Optimize production schedule to minimize costs")
    print(f"✅ Intent: {intent_result.primary_intent.value}")
    
    # Test data tool
    print("2. Testing data tool...")
    data_tool = create_data_tool()
    data_result = data_tool.analyze_data_requirements(
        "Optimize production schedule to minimize costs",
        {
            "primary_intent": intent_result.primary_intent.value,
            "confidence": intent_result.confidence,
            "objectives": intent_result.objectives
        }
    )
    print(f"✅ Data analysis completed")
    
    print("🎉 Basic workflow test PASSED!")

if __name__ == "__main__":
    test_basic_workflow()
