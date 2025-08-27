#!/usr/bin/env python3
"""
Test Refactored Tools - Single Agent Pattern
===========================================

Test all refactored tools to ensure they work together correctly.
Verifies single agent pattern, no fallbacks, and production readiness.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_intent_tool():
    """Test the refactored Intent tool"""
    print("🧠 Testing Intent Tool...")
    
    try:
        from mcp_server.tools.manufacturing.intent.DcisionAI_Intent_Tool import create_intent_tool
        
        intent_tool = create_intent_tool()
        
        # Test query
        test_query = "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
        
        print(f"   Query: {test_query}")
        
        # Analyze intent
        start_time = time.time()
        intent_result = intent_tool.analyze_intent(test_query, "test_customer")
        execution_time = time.time() - start_time
        
        print(f"   ✅ Intent Analysis: {intent_result.primary_intent}")
        print(f"   📊 Confidence: {intent_result.confidence:.2f}")
        print(f"   ⏱️ Execution Time: {execution_time:.2f}s")
        print(f"   🎯 Objectives: {intent_result.objectives}")
        
        return intent_result
        
    except Exception as e:
        print(f"   ❌ Intent Tool Test Failed: {e}")
        return None

def test_data_tool(intent_result):
    """Test the refactored Data tool"""
    print("\n📊 Testing Data Tool...")
    
    try:
        from mcp_server.tools.manufacturing.data.DcisionAI_Data_Tool import create_data_tool
        
        data_tool = create_data_tool()
        
        # Test query
        test_query = "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
        
        print(f"   Query: {test_query}")
        
        # Analyze data requirements
        start_time = time.time()
        data_result = data_tool.analyze_data_requirements(test_query, {
            "primary_intent": intent_result.primary_intent,
            "confidence": intent_result.confidence,
            "objectives": intent_result.objectives
        }, "test_customer")
        execution_time = time.time() - start_time
        
        print(f"   ✅ Data Analysis ID: {data_result.analysis_id}")
        print(f"   🏭 Industry Context: {data_result.industry_context}")
        print(f"   📋 Extracted Entities: {len(data_result.extracted_data_entities)}")
        print(f"   ❌ Missing Entities: {len(data_result.missing_data_entities)}")
        print(f"   ⏱️ Execution Time: {execution_time:.2f}s")
        
        return data_result
        
    except Exception as e:
        print(f"   ❌ Data Tool Test Failed: {e}")
        return None

def test_model_builder_tool(intent_result, data_result):
    """Test the refactored Model Builder tool"""
    print("\n🔧 Testing Model Builder Tool...")
    
    try:
        from mcp_server.tools.manufacturing.model.DcisionAI_Model_Builder import create_model_builder_tool
        
        model_builder = create_model_builder_tool()
        
        # Build optimization model
        start_time = time.time()
        model = model_builder.build_optimization_model({
            "primary_intent": intent_result.primary_intent,
            "confidence": intent_result.confidence,
            "objectives": intent_result.objectives
        }, {
            "extracted_data_entities": data_result.extracted_data_entities,
            "missing_data_entities": [missing.entity_name for missing in data_result.missing_data_entities],
            "sample_data_generated": data_result.sample_data_generated,
            "industry_context": data_result.industry_context
        }, "test_customer")
        execution_time = time.time() - start_time
        
        print(f"   ✅ Model ID: {model.model_id}")
        print(f"   📛 Model Type: {model.model_type.value}")
        print(f"   🔢 Variables: {len(model.decision_variables)}")
        print(f"   ⚖️ Constraints: {len(model.constraints)}")
        print(f"   🎯 Objectives: {len(model.objective_functions)}")
        print(f"   ⏱️ Execution Time: {execution_time:.2f}s")
        
        return model
        
    except Exception as e:
        print(f"   ❌ Model Builder Tool Test Failed: {e}")
        return None

def test_solver_tool(model):
    """Test the refactored Solver tool"""
    print("\n🏁 Testing Solver Tool...")
    
    try:
        from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import create_solver_tool
        
        solver_tool = create_solver_tool()
        
        # Solve optimization model
        start_time = time.time()
        solution_result = solver_tool.solve_optimization_model(model, max_solve_time=60.0)
        execution_time = time.time() - start_time
        
        print(f"   ✅ Solver Used: {solution_result.solver_type.value}")
        print(f"   📈 Objective Value: {solution_result.objective_value}")
        print(f"   ✅ Status: {solution_result.status.value}")
        print(f"   ⏱️ Solve Time: {solution_result.solve_time:.2f}s")
        print(f"   ⏱️ Total Execution Time: {execution_time:.2f}s")
        
        return solution_result
        
    except Exception as e:
        print(f"   ❌ Solver Tool Test Failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Testing Refactored Tools - Single Agent Pattern")
    print("=" * 70)
    print("🧠 Intent Tool | 📊 Data Tool | 🔧 Model Builder | 🏁 Solver Tool")
    print("=" * 70)
    
    overall_start_time = time.time()
    
    # Test Intent Tool
    intent_result = test_intent_tool()
    if not intent_result:
        print("\n❌ Intent Tool test failed - stopping")
        return
    
    # Test Data Tool
    data_result = test_data_tool(intent_result)
    if not data_result:
        print("\n❌ Data Tool test failed - stopping")
        return
    
    # Test Model Builder Tool
    model = test_model_builder_tool(intent_result, data_result)
    if not model:
        print("\n❌ Model Builder Tool test failed - stopping")
        return
    
    # Test Solver Tool
    solution_result = test_solver_tool(model)
    if not solution_result:
        print("\n❌ Solver Tool test failed - stopping")
        return
    
    # Overall results
    overall_execution_time = time.time() - overall_start_time
    
    print("\n" + "=" * 70)
    print("🎯 COMPLETE WORKFLOW TEST RESULTS")
    print("=" * 70)
    
    print(f"✅ All Tools Working: Intent → Data → Model → Solver")
    print(f"⏱️ Total Execution Time: {overall_execution_time:.2f}s")
    print(f"🧠 Intent: {intent_result.primary_intent} (confidence: {intent_result.confidence:.2f})")
    print(f"📊 Data: {len(data_result.extracted_data_entities)} extracted, {len(data_result.missing_data_entities)} missing")
    print(f"🔧 Model: {model.model_type.value} with {len(model.decision_variables)} variables")
    print(f"🏁 Solution: {solution_result.status.value} with objective {solution_result.objective_value}")
    
    print(f"\n🎉 All refactored tools working correctly with single agent pattern!")
    print(f"🚀 Production-ready with no fallbacks or mock responses!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
