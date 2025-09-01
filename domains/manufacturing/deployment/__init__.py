#!/usr/bin/env python3
"""
DcisionAI Platform - Manufacturing Domain Deployment
==================================================

Manufacturing domain deployment scripts and configurations.
"""

from .deploy_DcisionAI_Manufacturing_Agent_v1 import deploy_dcisionai_manufacturing_agent_v1
from .test_DcisionAI_Manufacturing_Agent_v1 import test_manufacturing_agent

__all__ = [
    "deploy_dcisionai_manufacturing_agent_v1",
    "test_manufacturing_agent"
]
