#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - AgentCore Deployment Script (v1)
====================================================================

Deploy DcisionAI Manufacturing MCP Server to AWS Bedrock AgentCore.
This script deploys the manufacturing optimization platform with all tools.

v1 Improvements:
- Fixed solver coefficient parsing (no more 0.0 objective values)
- Fixed JSON response parsing for solver orchestration
- Removed mock/fallback responses from intent tool
- Production-ready workflow with real solver execution
- Proper objective function evaluation and optimal solutions

Domain: Manufacturing Optimization & Decision Intelligence
Brand: DcisionAI
Platform: AWS Bedrock AgentCore

Usage:
    python scripts/deployment/dcisionai_manufacturing_deploy_agentcore.py

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import boto3
import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | DcisionAI Manufacturing | %(message)s"
)
logger = logging.getLogger(__name__)

def deploy_manufacturing_agent():
    """Deploy DcisionAI Manufacturing MCP Server to AgentCore"""
    try:
        # Initialize AgentCore client
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        # DcisionAI Manufacturing configuration
        agent_runtime_name = 'DcisionAI_Manufacturing_MCP_v1'
        container_uri = '808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-mcp:latest'
        role_arn = 'arn:aws:iam::808953421331:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-3bddb2550f'
        
        logger.info("🏭 Deploying DcisionAI Manufacturing MCP Server to AgentCore")
        logger.info(f"📦 Agent Runtime: {agent_runtime_name}")
        logger.info(f"🐳 Container URI: {container_uri}")
        logger.info(f"🔐 Role ARN: {role_arn}")
        
        # For now, let's just create a new agent runtime with a different name
        # since updating requires different API calls
        agent_runtime_name_v2 = f"{agent_runtime_name}_v2"
        logger.info(f"📦 Creating new agent runtime: {agent_runtime_name_v2}")
        
        response = client.create_agent_runtime(
            agentRuntimeName=agent_runtime_name_v2,
            agentRuntimeArtifact={
                'containerConfiguration': {
                    'containerUri': container_uri
                }
            },
            networkConfiguration={"networkMode": "PUBLIC"},
            roleArn=role_arn
        )
        logger.info("✅ Agent runtime created successfully")
        
        logger.info("✅ DcisionAI Manufacturing MCP Server deployed successfully!")
        logger.info(f"🔗 Agent Runtime ARN: {response['agentRuntimeArn']}")
        logger.info(f"📊 Status: {response['status']}")
        
        # Log manufacturing tools information
        logger.info("🛠️ Manufacturing Tools Available (v1 - Production Ready):")
        logger.info("   • Intent Classification (No fallbacks, production-ready)")
        logger.info("   • Data Analysis & Requirements (Industry-specific contextual data)")
        logger.info("   • Model Building & Optimization (Real mathematical formulations)")
        logger.info("   • Solver Orchestration (4 working solvers, proper coefficient parsing)")
        logger.info("   • Manufacturing Workflow Orchestration (Complete 4-stage pipeline)")
        logger.info("   • Critique & Explanation Tools (Real validation)")
        logger.info("   • ✅ Fixed: Objective function coefficient parsing")
        logger.info("   • ✅ Fixed: JSON response parsing")
        logger.info("   • ✅ Fixed: Removed mock/fallback responses")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to deploy DcisionAI Manufacturing MCP Server: {e}")
        raise

if __name__ == "__main__":
    logger.info("🚀 Starting DcisionAI Manufacturing MCP Server deployment...")
    deploy_manufacturing_agent()
    logger.info("🎉 Deployment process completed!")
