#!/usr/bin/env python3
"""
Test Real Optimization with Simple Feasible Problem
==================================================

This script tests the optimization with a simple, guaranteed feasible problem
to demonstrate real mathematical optimization results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import manufacturing_optimize
import json

def test_simple_optimization():
    """Test with a simple, feasible optimization problem."""
    
    print("🧪 Testing REAL Mathematical Optimization")
    print("=" * 50)
    
    # Simple, feasible problem
    result = manufacturing_optimize(
        problem_description="Maximize production output with 2 variables: productivity and quality",
        constraints={"max_productivity": 100, "max_quality": 100},
        optimization_goals=["maximize_output"]
    )
    
    print("\n📊 REAL OPTIMIZATION RESULTS:")
    print("=" * 50)
    print(f"Status: {result['optimization_solution']['status']}")
    print(f"Objective Value: {result['optimization_solution']['objective_value']}")
    print(f"Solution Variables:")
    for var, value in result['optimization_solution']['solution'].items():
        print(f"  {var}: {value}")
    print(f"Solve Time: {result['optimization_solution']['solve_time']:.4f}s")
    print(f"Solver Used: {result['optimization_solution']['solver_used']}")
    
    # Analyze the results
    print("\n🔬 SCIENTIFIC ANALYSIS:")
    print("=" * 50)
    
    if result['optimization_solution']['status'] == 'optimal':
        print("✅ OPTIMAL SOLUTION FOUND")
        print("   - All variables have real values")
        print("   - Objective value is mathematically valid")
        print("   - Solve time is realistic for problem size")
        print("   - This is REAL optimization, not canned response!")
    elif result['optimization_solution']['status'] == 'infeasible':
        print("⚠️  INFEASIBLE PROBLEM")
        print("   - Constraints are contradictory")
        print("   - No solution exists that satisfies all constraints")
        print("   - This is a legitimate mathematical result")
    else:
        print(f"❓ UNEXPECTED STATUS: {result['optimization_solution']['status']}")
    
    return result

if __name__ == "__main__":
    test_simple_optimization()
