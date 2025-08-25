"""
DcisionAI Shared Package

This package contains common utilities and configurations:
- utils: Common utility functions and base classes
- config: Configuration management and solver configurations
"""

# Import only utils to avoid circular imports
from . import utils

__all__ = ["utils"]
