#!/usr/bin/env python3
"""
DcisionAI Platform - Platform Core Components
============================================

Platform-level components for the multi-domain DcisionAI platform.
"""

from .orchestrator.platform_manager import platform_manager, PlatformManager

__version__ = "1.0.0"
__all__ = [
    "platform_manager",
    "PlatformManager"
]
