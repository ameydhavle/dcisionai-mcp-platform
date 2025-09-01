#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent - Simple AgentCore Deployment
==========================================================

Simple deployment script following the official AgentCore SDK approach.
Based on: https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/

This script follows the "Option A: SDK Integration" approach which is much simpler.

Usage:
    python scripts/deployment/deploy_agentcore_simple.py

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import boto3
import json
import logging
import subprocess
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | DcisionAI Simple AgentCore | %(message)s"
)
logger = logging.getLogger(__name__)

def run_command(command: str, description: str) -> subprocess.CompletedProcess:
    """Run a shell command and log the result."""
    logger.info(f"🔄 {description}...")
    logger.info(f"   Command: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        logger.info(f"✅ {description} completed successfully")
        if result.stdout.strip():
            logger.info(f"   Output: {result.stdout.strip()}")
    else:
        logger.error(f"❌ {description} failed")
        logger.error(f"   Error: {result.stderr.strip()}")
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
    
    return result

def deploy_simple_agentcore():
    """Deploy the simple AgentCore agent using SDK integration."""
    logger.info("🚀 DEPLOYING DcisionAI Manufacturing Agent (Simple AgentCore)")
    logger.info("=" * 70)
    
    # Configuration
    region = "us-east-1"
    account_id = "808953421331"
    ecr_repo = f"{account_id}.dkr.ecr.{region}.amazonaws.com/dcisionai-manufacturing-simple"
    
    # Generate unique agent runtime name
    timestamp = int(time.time())
    agent_runtime_name = f"DcisionAI_Manufacturing_Simple_{timestamp}"
    
    logger.info(f"📋 Configuration:")
    logger.info(f"   Region: {region}")
    logger.info(f"   Account ID: {account_id}")
    logger.info(f"   ECR Repository: {ecr_repo}")
    logger.info(f"   Agent Runtime Name: {agent_runtime_name}")
    logger.info("")
    
    try:
        # Step 1: Authenticate with ECR
        auth_command = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com"
        run_command(auth_command, "ECR authentication")
        
        # Step 2: Build Docker image (using simple Dockerfile)
        build_command = f"docker buildx build --platform linux/arm64 -f Dockerfile.agentcore_simple -t {ecr_repo}:latest --push ."
        run_command(build_command, "Docker build and push")
        
        # Step 3: Deploy to AgentCore
        role_arn = "arn:aws:iam::808953421331:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-3bddb2550f"
        
        deploy_command = f"""aws bedrock-agentcore-control create-agent-runtime \
            --agent-runtime-name "{agent_runtime_name}" \
            --agent-runtime-artifact '{{"containerConfiguration": {{"containerUri": "{ecr_repo}:latest"}}}}' \
            --network-configuration '{{"networkMode": "PUBLIC"}}' \
            --role-arn "{role_arn}" \
            --region {region}"""
        
        result = run_command(deploy_command, "AgentCore deployment")
        
        # Extract ARN from response
        response_data = json.loads(result.stdout)
        agent_runtime_arn = response_data['agentRuntimeArn']
        
        logger.info("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info(f"🔗 Agent Runtime ARN: {agent_runtime_arn}")
        logger.info(f"📊 Status: {response_data.get('status', 'Unknown')}")
        logger.info(f"🏷️ Agent Runtime Name: {agent_runtime_name}")
        logger.info("")
        
        logger.info("📋 Next Steps:")
        logger.info("1. Test the deployment:")
        logger.info(f"   python scripts/deployment/test_agentcore_simple.py")
        logger.info("")
        logger.info("2. Monitor logs:")
        logger.info(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_runtime_name}-* --follow")
        logger.info("")
        logger.info("3. Check status:")
        logger.info(f"   aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id {agent_runtime_name} --region {region}")
        
        return {
            "agent_runtime_arn": agent_runtime_arn,
            "agent_runtime_name": agent_runtime_name,
            "status": response_data.get('status', 'Unknown'),
            "ecr_repo": ecr_repo
        }
        
    except Exception as e:
        logger.error(f"❌ DEPLOYMENT FAILED: {e}")
        raise

if __name__ == "__main__":
    deploy_simple_agentcore()
