#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent - Intent Only AgentCore Deployment
===============================================================

Simple deployment script for the intent-only AgentCore agent.
This version only does intent classification to avoid timeout issues.

Based on: https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/

Usage:
    python scripts/deployment/deploy_agentcore_intent_only.py

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
    format="%(asctime)s | %(levelname)s | DcisionAI Intent Only | %(message)s"
)
logger = logging.getLogger(__name__)

def deploy_intent_only_agent():
    """Deploy the intent-only AgentCore agent"""
    
    # Configuration
    region = "us-east-1"
    account_id = boto3.client('sts').get_caller_identity()['Account']
    ecr_repo = f"{account_id}.dkr.ecr.{region}.amazonaws.com/dcisionai-manufacturing-intent-only"
    
    # Generate unique agent runtime name
    timestamp = int(time.time())
    agent_runtime_name = f"DcisionAI_Manufacturing_Intent_Only_{timestamp}"
    
    logger.info("🚀 DEPLOYING DcisionAI Manufacturing Agent (Intent Only)")
    logger.info("=" * 70)
    logger.info(f"📋 Configuration:")
    logger.info(f"   Region: {region}")
    logger.info(f"   Account ID: {account_id}")
    logger.info(f"   ECR Repository: {ecr_repo}")
    logger.info(f"   Agent Runtime Name: {agent_runtime_name}")
    logger.info("")
    
    try:
        # Step 1: ECR Authentication
        logger.info("🔄 ECR authentication...")
        auth_cmd = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com"
        logger.info(f"   Command: {auth_cmd}")
        
        result = subprocess.run(auth_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ECR authentication failed: {result.stderr}")
        
        logger.info("✅ ECR authentication completed successfully")
        logger.info(f"   Output: {result.stdout.strip()}")
        
        # Step 2: Docker Build and Push
        logger.info("🔄 Docker build and push...")
        build_cmd = f"docker buildx build --platform linux/arm64 -f Dockerfile.agentcore_intent_only -t {ecr_repo}:latest --push ."
        logger.info(f"   Command: {build_cmd}")
        
        result = subprocess.run(build_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Docker build and push failed: {result.stderr}")
        
        logger.info("✅ Docker build and push completed successfully")
        
        # Step 3: AgentCore Deployment
        logger.info("🔄 AgentCore deployment...")
        
        # Create agent runtime artifact
        artifact = {
            "containerConfiguration": {
                "containerUri": f"{ecr_repo}:latest"
            }
        }
        
        # Create network configuration
        network_config = {
            "networkMode": "PUBLIC"
        }
        
        # Deploy to AgentCore
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        
        response = client.create_agent_runtime(
            agentRuntimeName=agent_runtime_name,
            agentRuntimeArtifact=artifact,
            networkConfiguration=network_config,
            roleArn=f"arn:aws:iam::{account_id}:role/AmazonBedrockAgentCoreSDKRuntime-{region}-3bddb2550f"
        )
        
        logger.info("✅ AgentCore deployment completed successfully")
        logger.info(f"   Agent Runtime ARN: {response.get('agentRuntimeArn', 'Unknown')}")
        logger.info(f"   Status: {response.get('status', 'Unknown')}")
        
        # Extract agent runtime ARN
        agent_runtime_arn = response['agentRuntimeArn']
        
        # Success summary
        logger.info("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info(f"🔗 Agent Runtime ARN: {agent_runtime_arn}")
        logger.info(f"📊 Status: {response.get('status', 'Unknown')}")
        logger.info(f"🏷️ Agent Runtime Name: {agent_runtime_name}")
        logger.info("")
        
        logger.info("📋 Next Steps:")
        logger.info("1. Test the deployment:")
        logger.info(f"   python scripts/deployment/test_agentcore_simple_intent_only.py")
        logger.info("")
        logger.info("2. Monitor logs:")
        logger.info(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_runtime_name}-* --follow")
        logger.info("")
        logger.info("3. Check status:")
        logger.info(f"   aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id {agent_runtime_name} --region {region}")
        
        return agent_runtime_arn
        
    except Exception as e:
        logger.error(f"❌ DEPLOYMENT FAILED: {e}")
        raise

if __name__ == "__main__":
    deploy_intent_only_agent()
