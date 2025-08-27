#!/usr/bin/env python3
"""
Test Solver Coefficient Parsing Fix
===================================

Test that the solver properly extracts coefficients from objective functions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import SolverTool

def test_coefficient_extraction():
    """Test the coefficient extraction method"""
    solver = SolverTool()
    
    # Test cases
    test_cases = [
        ("10*x1 + 8*x2", "x1", 10.0),
        ("10*x1 + 8*x2", "x2", 8.0),
        ("x1 + x2", "x1", 1.0),
        ("x1 + x2", "x2", 1.0),
        ("-5*x1 + 3*x2", "x1", -5.0),
        ("-5*x1 + 3*x2", "x2", 3.0),
        ("cost*x1 + revenue*x2", "x1", 1.0),  # Default for symbolic
        ("cost*x1 + revenue*x2", "x2", 1.0),  # Default for symbolic
    ]
    
    print("🧪 Testing coefficient extraction...")
    all_passed = True
    
    for expression, variable, expected in test_cases:
        result = solver._extract_coefficient(expression, variable)
        status = "✅" if abs(result - expected) < 0.001 else "❌"
        print(f"   {status} {expression} -> {variable}: {result} (expected: {expected})")
        if abs(result - expected) >= 0.001:
            all_passed = False
    
    if all_passed:
        print("🎉 All coefficient extraction tests passed!")
    else:
        print("❌ Some coefficient extraction tests failed!")
    
    return all_passed

if __name__ == "__main__":
    test_coefficient_extraction()
