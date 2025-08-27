#!/usr/bin/env python3
"""
Test Solver Only - Debug Solver Issues
====================================

Test the Solver tool in isolation to identify the exact error.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_solver():
    """Test Solver in isolation"""
    print("🏁 Testing Solver in isolation...")
    
    try:
        from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import create_solver_tool, OptimizationModel
        
        # Create solver tool
        solver_tool = create_solver_tool()
        print("✅ Solver tool created successfully")
        
        # Create a simple test model
        test_model = OptimizationModel(
            model_id="test_model",
            model_name="Test Optimization Model",
            model_type="linear_programming",
            decision_variables=[
                {"name": "x1", "variable_type": "continuous", "bounds": (0, None)},
                {"name": "x2", "variable_type": "continuous", "bounds": (0, None)}
            ],
            constraints=[
                {"name": "capacity", "expression": "x1 + x2 <= 100", "sense": "<=", "rhs_value": 100}
            ],
            objective_functions=[
                {"name": "minimize_cost", "sense": "minimize", "expression": "10*x1 + 8*x2"}
            ],
            data_schema={},
            compatible_solvers=["or_tools_glop"],
            recommended_solver="or_tools_glop"
        )
        
        print("📝 Test model created:")
        print(f"   Model ID: {test_model.model_id}")
        print(f"   Type: {test_model.model_type}")
        print(f"   Variables: {len(test_model.decision_variables)}")
        print(f"   Constraints: {len(test_model.constraints)}")
        
        # Solve model
        print("\n🏁 Solving optimization model...")
        start_time = time.time()
        
        solver_result = solver_tool.solve_optimization_model(test_model, max_solve_time=30.0)
        
        execution_time = time.time() - start_time
        
        print(f"✅ Solver completed successfully!")
        print(f"   Solver: {solver_result.solver_type}")
        print(f"   Status: {solver_result.status}")
        print(f"   Objective: {solver_result.objective_value}")
        print(f"   Time: {execution_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Solver test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_solver()
