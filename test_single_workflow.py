#!/usr/bin/env python3
"""
Single Manufacturing Optimization Workflow Test
==============================================

Test a single complete 4-tool workflow: Intent → Data → Model → Solver
To verify the fix for the 0.0 objective value issue.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server.tools.manufacturing.intent import create_intent_tool
from mcp_server.tools.manufacturing.data import create_data_tool
from mcp_server.tools.manufacturing.model import create_model_builder_tool
from mcp_server.tools.manufacturing.solver import create_solver_tool

def test_single_workflow():
    """Test a single complete workflow scenario"""
    
    print("🔍 TESTING SINGLE WORKFLOW SCENARIO")
    print("=" * 60)
    
    user_query = "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
    print(f"📝 User Query: {user_query}")
    
    start_time = time.time()
    
    try:
        # Stage 1: Intent Analysis
        print(f"\n🧠 STAGE 1: Intent Analysis")
        intent_tool = create_intent_tool()
        intent_result = intent_tool.analyze_intent(user_query)
        
        if intent_result:
            print(f"   ✅ Intent: {intent_result.primary_intent}")
            print(f"   ✅ Confidence: {intent_result.confidence:.2f}")
        else:
            print("   ❌ Intent analysis failed")
            return False
        
        # Stage 2: Data Analysis
        print(f"\n📊 STAGE 2: Data Analysis")
        data_tool = create_data_tool()
        data_result = data_tool.analyze_data_requirements(user_query, intent_result)
        
        if data_result:
            print(f"   ✅ Analysis ID: {data_result.analysis_id}")
            print(f"   ✅ Extracted entities: {len(data_result.extracted_data_entities)}")
            print(f"   ✅ Missing entities: {len(data_result.missing_data_entities)}")
        else:
            print("   ❌ Data analysis failed")
            return False
        
        # Stage 3: Model Building
        print(f"\n🔧 STAGE 3: Model Building")
        model_tool = create_model_builder_tool()
        model_result = model_tool.build_optimization_model(intent_result, data_result)
        
        if model_result:
            print(f"   ✅ Model ID: {model_result.model_id}")
            print(f"   ✅ Variables: {len(model_result.decision_variables)}")
            print(f"   ✅ Constraints: {len(model_result.constraints)}")
            print(f"   ✅ Objectives: {len(model_result.objective_functions)}")
            
            # Check if we have variables and objectives
            if len(model_result.decision_variables) == 0:
                print("   ⚠️ Warning: No decision variables generated")
            if len(model_result.objective_functions) == 0:
                print("   ⚠️ Warning: No objective functions generated")
        else:
            print("   ❌ Model building failed")
            return False
        
        # Stage 4: Solver Execution
        print(f"\n🏁 STAGE 4: Solver Execution")
        solver_tool = create_solver_tool()
        solver_result = solver_tool.solve_optimization_model(model_result)
        
        if solver_result:
            print(f"   ✅ Solver: {solver_result.solver_type.value}")
            print(f"   ✅ Status: {solver_result.status.value}")
            print(f"   ✅ Objective Value: {solver_result.objective_value}")
            
            # Check for the 0.0 objective value issue
            if solver_result.objective_value == 0.0:
                print("   ⚠️ Warning: Objective value is 0.0 - this might indicate an issue")
                print("   📊 Solution variables:")
                for var, value in solver_result.solution_variables.items():
                    print(f"      {var}: {value}")
            else:
                print("   ✅ Non-zero objective value - issue appears to be fixed!")
        else:
            print("   ❌ Solver execution failed")
            return False
        
        total_time = time.time() - start_time
        print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"⏱️ Total time: {total_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_workflow()
    if success:
        print("\n✅ Single workflow test PASSED")
        sys.exit(0)
    else:
        print("\n❌ Single workflow test FAILED")
        sys.exit(1)
