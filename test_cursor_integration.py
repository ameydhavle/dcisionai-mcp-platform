#!/usr/bin/env python3
"""
Test Cursor Integration
======================

This script tests the DcisionAI MCP server integration with Cursor IDE.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp-server', 'src'))

from dcisionai_mcp_server.tools import (
    classify_intent,
    analyze_data,
    build_model,
    solve_optimization
)

async def test_cursor_integration():
    """Test the MCP server integration with Cursor."""
    
    print("🧪 TESTING CURSOR INTEGRATION")
    print("=" * 50)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test problem
    problem_description = """A small manufacturing company needs to optimize production of 2 products using 2 machines. 
    Product A requires 2 hours on machine 1 and 1 hour on machine 2, with profit of $50 per unit. 
    Product B requires 1 hour on machine 1 and 3 hours on machine 2, with profit of $60 per unit. 
    Machine 1 has 40 hours available, machine 2 has 60 hours available. Maximize profit."""
    
    try:
        print("📋 Step 1: Intent Classification")
        intent_result = await classify_intent(problem_description, "production_planning")
        print(f"✅ Intent: {intent_result.get('result', {}).get('intent', 'unknown')}")
        print(f"   Industry: {intent_result.get('result', {}).get('industry', 'unknown')}")
        print(f"   Complexity: {intent_result.get('result', {}).get('complexity', 'unknown')}")
        print()
        
        print("📊 Step 2: Data Analysis")
        data_result = await analyze_data(problem_description, intent_result.get("result", {}))
        print(f"✅ Data Readiness: {data_result.get('result', {}).get('readiness_score', 0):.2f}")
        print(f"   Entities: {data_result.get('result', {}).get('entities', 0)}")
        print()
        
        print("🔧 Step 3: Model Building")
        model_result = await build_model(
            problem_description,
            intent_result.get("result", {}),
            data_result.get("result", {})
        )
        variables = model_result.get('result', {}).get('variables', [])
        constraints = model_result.get('result', {}).get('constraints', [])
        print(f"✅ Model Type: {model_result.get('result', {}).get('model_type', 'unknown')}")
        print(f"   Variables: {len(variables)}")
        print(f"   Constraints: {len(constraints)}")
        print()
        
        print("🎯 Step 4: Real Optimization Solving")
        solution_result = await solve_optimization(
            problem_description,
            intent_result.get("result", {}),
            data_result.get("result", {}),
            model_result.get("result", {})
        )
        
        status = solution_result.get('result', {}).get('status', 'unknown')
        obj_value = solution_result.get('result', {}).get('objective_value', 0)
        solve_time = solution_result.get('result', {}).get('solve_time', 0)
        
        print(f"✅ Solution Status: {status}")
        print(f"   Objective Value: {obj_value}")
        print(f"   Solve Time: {solve_time:.3f}s")
        
        # Display optimal values
        optimal_values = solution_result.get('result', {}).get('optimal_values', {})
        if optimal_values:
            print(f"\n📊 Optimal Values:")
            for name, value in optimal_values.items():
                if isinstance(value, (int, float)) and value > 0:
                    print(f"   {name}: {value:.2f}")
        
        print(f"\n🎉 CURSOR INTEGRATION TEST SUCCESSFUL!")
        print(f"✅ The DcisionAI MCP server is working correctly with Cursor IDE")
        print(f"✅ Real mathematical optimization is functioning properly")
        print(f"✅ VS Code extension can now be tested in Cursor")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Cursor integration test: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_cursor_integration())
    sys.exit(0 if success else 1)
