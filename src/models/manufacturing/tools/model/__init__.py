"""
Model Builder Tool Package

This package contains the enhanced model builder components with Strands-Agents integration.
"""

try:
    from .model_builder_optimized import OptimizedModelBuilder as ModelBuilder
    __all__ = ["ModelBuilder"]
except ImportError:
    __all__ = []

__version__ = "1.0.0"
__author__ = "DcisionAI Team"
