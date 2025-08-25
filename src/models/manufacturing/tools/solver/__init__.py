"""Manufacturing-specific solver tools"""

try:
    from .solver_tool_optimized import OptimizedSolverTool as SolverTool
    __all__ = ["SolverTool"]
except ImportError:
    __all__ = []
