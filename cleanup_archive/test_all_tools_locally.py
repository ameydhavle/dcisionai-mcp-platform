#!/usr/bin/env python3
"""
Test All Manufacturing Tools Locally
Comprehensive test of all tools with strands framework before container build.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_intent_tool():
    """Test the 6-agent intent classification tool."""
    print("🔍 Testing Intent Tool (6-Agent Swarm Intelligence)...")
    try:
        from models.manufacturing.tools.intent.DcisionAI_Intent_Tool_v6 import DcisionAI_Intent_Tool_v6
        
        intent_tool = DcisionAI_Intent_Tool_v6()
        
        # Test query
        query = "optimize production line efficiency for automotive manufacturing with energy constraints"
        result = intent_tool.classify_intent(query)
        
        print(f"✅ Intent Tool: {result.primary_intent.value} (confidence: {result.confidence}, swarm agreement: {result.swarm_agreement})")
        print(f"   Agents used: {result.classification_metadata.get('agents_used', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Intent Tool failed: {e}")
        return False

def test_data_tool():
    """Test the manufacturing data analysis tool."""
    print("🔍 Testing Data Tool...")
    try:
        from models.manufacturing.tools.data.DcisionAI_Data_Tool_v3 import create_dcisionai_data_tool_v3
        
        data_tool = create_dcisionai_data_tool_v3()
        
        # Test query
        query = "analyze production data for automotive manufacturing line"
        result = data_tool.analyze_data_requirements(query, "production_scheduling")
        
        print(f"✅ Data Tool: Analysis completed successfully")
        print(f"   Data requirements: {len(result.get('data_requirements', []))} items")
        return True
        
    except Exception as e:
        print(f"❌ Data Tool failed: {e}")
        return False

def test_model_tool():
    """Test the optimization model building tool."""
    print("🔍 Testing Model Tool...")
    try:
        from models.manufacturing.tools.model.DcisionAI_Model_Builder_v1 import create_dcisionai_model_builder
        
        model_tool = create_dcisionai_model_builder()
        
        # Test query
        query = "build optimization model for production scheduling"
        result = model_tool.build_optimization_model(query)
        
        print(f"✅ Model Tool: Model built successfully")
        print(f"   Model type: {result.get('model_type', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Model Tool failed: {e}")
        return False

def test_solver_tool():
    """Test the optimization solver tool."""
    print("🔍 Testing Solver Tool...")
    try:
        from shared.tools.solver import create_shared_solver_tool
        
        solver_tool = create_shared_solver_tool()
        
        # Test query
        query = "solve linear programming optimization problem"
        # Create a simple test model
        test_model = {
            "model_type": "linear_programming",
            "variables": ["x1", "x2"],
            "constraints": ["x1 + x2 <= 10", "x1 >= 0", "x2 >= 0"],
            "objective": "maximize x1 + 2*x2"
        }
        result = solver_tool.solve_optimization_model(test_model, "manufacturing", "test")
        
        print(f"✅ Solver Tool: Solver executed successfully")
        print(f"   Solver used: {result.get('solver_used', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Solver Tool failed: {e}")
        return False

def test_manufacturing_agent():
    """Test the full manufacturing agent workflow."""
    print("🔍 Testing Manufacturing Agent (Full Workflow)...")
    try:
        from models.manufacturing.DcisionAI_Manufacturing_Agent import DcisionAI_Manufacturing_Agent
        
        agent = DcisionAI_Manufacturing_Agent()
        
        # Test query
        query = "optimize production line efficiency for automotive manufacturing"
        result = agent.analyze_manufacturing_optimization(query)
        
        print(f"✅ Manufacturing Agent: Full workflow completed successfully")
        print(f"   Workflow stages: {len(result.get('workflow_stages', []))}")
        return True
        
    except Exception as e:
        print(f"❌ Manufacturing Agent failed: {e}")
        return False

def test_strands_framework():
    """Test strands framework availability."""
    print("🔍 Testing Strands Framework...")
    try:
        from strands import Agent, tool
        print("✅ Strands framework available")
        print(f"   Agent class: {Agent}")
        print(f"   Tool decorator: {tool}")
        return True
        
    except Exception as e:
        print(f"❌ Strands framework failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing All Manufacturing Tools Locally")
    print("=" * 50)
    
    start_time = time.time()
    results = {}
    
    # Test strands framework first
    results['strands_framework'] = test_strands_framework()
    print()
    
    # Test individual tools
    results['intent_tool'] = test_intent_tool()
    print()
    
    results['data_tool'] = test_data_tool()
    print()
    
    results['model_tool'] = test_model_tool()
    print()
    
    results['solver_tool'] = test_solver_tool()
    print()
    
    # Test full agent
    results['manufacturing_agent'] = test_manufacturing_agent()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print()
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    elapsed_time = time.time() - start_time
    print(f"Total Time: {elapsed_time:.2f}s")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Ready for container build.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please fix issues before container build.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
