#!/usr/bin/env python3
"""
Test Solver Functionality
=========================

Test that the solver tool can actually solve a basic optimization problem.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import SolverTool, OptimizationModel

def test_solver_functionality():
    """Test that the solver can solve a basic problem"""
    print("🧪 Testing Solver Functionality...")
    
    try:
        # Create solver tool
        solver_tool = SolverTool()
        print("✅ Solver tool created successfully")
        
        # Create a simple test model
        test_model = OptimizationModel(
            model_id="test_model_001",
            model_name="Simple Test Model",
            model_type="linear_programming",
            decision_variables=[
                {
                    "name": "x1",
                    "variable_type": "continuous",
                    "bounds": (0, None),
                    "description": "Production quantity - Product A"
                },
                {
                    "name": "x2", 
                    "variable_type": "continuous",
                    "bounds": (0, None),
                    "description": "Production quantity - Product B"
                }
            ],
            constraints=[
                {
                    "name": "capacity",
                    "expression": "2*x1 + 3*x2 <= 100",
                    "sense": "<=",
                    "rhs_value": 100,
                    "description": "Production capacity constraint"
                },
                {
                    "name": "demand",
                    "expression": "x1 >= 10",
                    "sense": ">=",
                    "rhs_value": 10,
                    "description": "Minimum demand for Product A"
                }
            ],
            objective_functions=[
                {
                    "name": "maximize_profit",
                    "sense": "maximize",
                    "expression": "10*x1 + 8*x2",
                    "description": "Maximize total profit"
                }
            ],
            data_schema={},
            compatible_solvers=["or_tools_glop"],
            recommended_solver="or_tools_glop"
        )
        
        print("✅ Test model created successfully")
        
        # Solve the model
        print("🔧 Solving optimization model...")
        result = solver_tool.solve_optimization_model(test_model, max_solve_time=30.0)
        
        print(f"✅ Solver completed successfully!")
        print(f"   Solver Used: {result.solver_type.value}")
        print(f"   Status: {result.status.value}")
        print(f"   Objective Value: {result.objective_value}")
        print(f"   Solve Time: {result.solve_time:.2f}s")
        print(f"   Solution Variables: {result.solution_variables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Solver functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_solver_functionality()
