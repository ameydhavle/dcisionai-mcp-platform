#!/usr/bin/env python3
"""
Test Intent Tool
===============

Test that the intent tool is working correctly with the main class.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server.tools.manufacturing.intent import create_intent_tool

def test_intent_tool():
    """Test the intent tool"""
    print("🧪 Testing Intent Tool...")
    
    try:
        # Create intent tool
        intent_tool = create_intent_tool()
        print("✅ Intent tool created successfully")
        
        # Test classification
        query = "I need to optimize my production schedule to minimize costs while meeting customer demand"
        result = intent_tool.classify_intent(query)
        
        print(f"✅ Intent classification successful:")
        print(f"   Primary Intent: {result.primary_intent}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Objectives: {result.objectives}")
        print(f"   Execution Time: {result.classification_metadata.get('execution_time', 0):.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Intent tool test failed: {e}")
        return False

if __name__ == "__main__":
    test_intent_tool()
