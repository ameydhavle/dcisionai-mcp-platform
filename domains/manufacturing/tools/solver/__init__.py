"""
DcisionAI Shared Solver Tool Package
====================================

Universal optimization solver tool that can be used across all domains.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

from .solver_tool_optimized import SolverSwarmTool
from .solver_swarm_orchestrator import SolverSwarmOrchestrator

# Generic solver interface for easy domain integration
def create_shared_solver_tool():
    """Create a shared solver tool instance for any domain"""
    return SolverSwarmTool()

def solve_optimization_model(model_data: dict, domain: str = "generic", session_id: str = "default"):
    """
    Generic solver interface for any domain
    
    Args:
        model_data: Optimization model from domain's model builder
        domain: Domain name (manufacturing, logistics, finance, etc.)
        session_id: Session identifier
    
    Returns:
        Solver results with domain-agnostic format
    """
    solver = SolverSwarmTool()
    return solver.solve_optimization_model(
        model_data=model_data,
        domain=domain,
        session_id=session_id
    )

__all__ = [
    'SolverSwarmTool', 
    'SolverSwarmOrchestrator',
    'create_shared_solver_tool',
    'solve_optimization_model'
]
