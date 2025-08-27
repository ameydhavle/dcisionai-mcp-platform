#!/usr/bin/env python3
"""
Debug Objective Function Coefficient Extraction
=============================================

Test the coefficient extraction method to understand why we're getting 0.0 objective values.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import create_solver_tool
from mcp_server.tools.manufacturing.model.DcisionAI_Model_Builder import create_model_builder_tool
from mcp_server.tools.manufacturing.data.DcisionAI_Data_Tool import create_data_tool
from mcp_server.tools.manufacturing.intent.DcisionAI_Intent_Tool import create_intent_tool

def debug_objective_function():
    """Debug the objective function coefficient extraction"""
    
    # Test query
    user_query = "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
    
    print("🔍 DEBUGGING OBJECTIVE FUNCTION COEFFICIENT EXTRACTION")
    print("=" * 60)
    
    try:
        # Step 1: Create intent
        print("1. Creating intent...")
        intent_tool = create_intent_tool()
        intent_result = intent_tool.classify_intent(user_query)
        print(f"   Intent: {intent_result.primary_intent.value}")
        
        # Step 2: Create data
        print("2. Creating data...")
        data_tool = create_data_tool()
        data_result = data_tool.analyze_data_requirements(user_query, {
            "primary_intent": intent_result.primary_intent.value,
            "confidence": intent_result.confidence,
            "objectives": intent_result.objectives
        }, "debug_test")
        
        # Step 3: Create model
        print("3. Creating model...")
        model_builder = create_model_builder_tool()
        model_result = model_builder.build_optimization_model({
            "primary_intent": intent_result.primary_intent.value,
            "confidence": intent_result.confidence,
            "objectives": intent_result.objectives
        }, {
            "extracted_data_entities": data_result.extracted_data_entities,
            "missing_data_entities": [missing.entity_name for missing in data_result.missing_data_entities],
            "sample_data_generated": data_result.sample_data_generated,
            "industry_context": data_result.industry_context
        }, "debug_test")
        
        # Step 4: Debug objective function
        print("4. Debugging objective function...")
        print(f"   Model ID: {model_result.model_id}")
        print(f"   Variables count: {len(model_result.decision_variables)}")
        print(f"   Variables: {[var.name for var in model_result.decision_variables]}")
        print(f"   Objectives count: {len(model_result.objective_functions)}")
        
        if model_result.objective_functions:
            obj = model_result.objective_functions[0]
            print(f"   Objective Sense: {obj.sense}")
            print(f"   Objective Expression: {obj.expression}")
            
            # Test coefficient extraction
            solver_tool = create_solver_tool()
            for var in model_result.decision_variables:
                var_name = var.name
                coefficient = solver_tool._extract_coefficient(obj.expression, var_name)
                print(f"   Coefficient for {var_name}: {coefficient}")
        else:
            print("   ❌ No objective functions found!")
            print(f"   Model object type: {type(model_result)}")
            print(f"   Model attributes: {dir(model_result)}")
        
        # Step 5: Test solver
        print("5. Testing solver...")
        solver_result = solver_tool.solve_optimization_model(model_result, max_solve_time=30.0)
        print(f"   Solver: {solver_result.solver_type.value}")
        print(f"   Status: {solver_result.status.value}")
        print(f"   Objective Value: {solver_result.objective_value}")
        print(f"   Solution Variables: {solver_result.solution_variables}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_objective_function()
