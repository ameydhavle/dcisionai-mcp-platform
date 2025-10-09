#!/usr/bin/env python3
"""
Test Solver Availability
========================

Test which solvers are actually functional.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_solver_availability():
    """Test which solvers are actually available and functional"""
    print("🧪 Testing Solver Availability...")
    
    # Test OR-Tools
    print("\n📊 Testing OR-Tools:")
    try:
        from ortools.linear_solver import pywraplp
        
        # Test GLOP
        try:
            solver = pywraplp.Solver.CreateSolver('GLOP')
            if solver:
                print("   ✅ OR-Tools GLOP: Available")
            else:
                print("   ❌ OR-Tools GLOP: Not available")
        except Exception as e:
            print(f"   ❌ OR-Tools GLOP: Error - {e}")
        
        # Test SCIP
        try:
            solver = pywraplp.Solver.CreateSolver('SCIP')
            if solver:
                print("   ✅ OR-Tools SCIP: Available")
            else:
                print("   ❌ OR-Tools SCIP: Not available")
        except Exception as e:
            print(f"   ❌ OR-Tools SCIP: Error - {e}")
            
    except ImportError:
        print("   ❌ OR-Tools: Not installed")
    
    # Test PuLP
    print("\n📊 Testing PuLP:")
    try:
        import pulp as pl
        
        try:
            solver = pl.PULP_CBC_CMD(msg=0)
            if hasattr(solver, 'available') and solver.available():
                print("   ✅ PuLP CBC: Available")
            else:
                print("   ❌ PuLP CBC: Not available")
        except Exception as e:
            print(f"   ❌ PuLP CBC: Error - {e}")
            
    except ImportError:
        print("   ❌ PuLP: Not installed")
    
    # Test CVXPY
    print("\n📊 Testing CVXPY:")
    try:
        import cvxpy as cp
        
        # Test ECOS
        try:
            problem = cp.Problem(cp.Minimize(0), [])
            problem.solve(solver=cp.ECOS, verbose=False)
            print("   ✅ CVXPY ECOS: Available")
        except Exception as e:
            print(f"   ❌ CVXPY ECOS: Error - {e}")
        
        # Test OSQP
        try:
            problem = cp.Problem(cp.Minimize(0), [])
            problem.solve(solver=cp.OSQP, verbose=False)
            print("   ✅ CVXPY OSQP: Available")
        except Exception as e:
            print(f"   ❌ CVXPY OSQP: Error - {e}")
            
    except ImportError:
        print("   ❌ CVXPY: Not installed")

if __name__ == "__main__":
    test_solver_availability()
