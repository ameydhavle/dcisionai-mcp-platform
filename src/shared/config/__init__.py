"""
DcisionAI Shared Configuration

Configuration management and solver configurations used across the platform.
"""

# Import only the most essential configuration modules to avoid circular imports
from .solver_configuration_manager import SolverConfigurationManager
from .enhanced_solver_registry import EnhancedSolverRegistry
from .bedrock_inference_profile import BedrockInferenceProfileManager

__all__ = [
    # Configuration managers
    "SolverConfigurationManager",
    "EnhancedSolverRegistry",
    "BedrockInferenceProfileManager"
]
