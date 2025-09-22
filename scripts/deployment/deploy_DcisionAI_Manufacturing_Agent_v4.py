#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Production AgentCore Deployment
====================================================================

Production deployment script for the DcisionAI Manufacturing MCP Server with:
- Real AWS Bedrock inference profiles
- Multi-tenant orchestration
- Real tool execution
- MCP Protocol compliance

Usage:
    python scripts/deployment/deploy_DcisionAI_Manufacturing_Agent_v4.py

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
    format="%(asctime)s | %(levelname)s | DcisionAI Manufacturing Agent v4 | %(message)s"
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

def deploy_dcisionai_manufacturing_agent_v4():
    """Deploy the DcisionAI Manufacturing Agent v4 using SDK integration."""
    logger.info("🚀 DEPLOYING DcisionAI Manufacturing Agent v4 (Production AgentCore)")
    logger.info("=" * 70)
    
    # Configuration
    region = "us-east-1"
    account_id = "808953421331"
    ecr_repo = f"{account_id}.dkr.ecr.{region}.amazonaws.com/dcisionai-manufacturing-v4"
    
    # Generate unique agent runtime name
    timestamp = int(time.time())
    agent_runtime_name = f"DcisionAI_Manufacturing_MCP_{timestamp}"
    
    logger.info(f"📋 Configuration:")
    logger.info(f"   Region: {region}")
    logger.info(f"   Account ID: {account_id}")
    logger.info(f"   ECR Repository: {ecr_repo}")
    logger.info(f"   Agent Runtime Name: {agent_runtime_name}")
    logger.info("")
    
    try:
        # Step 1: Create ECR repository if it doesn't exist
        try:
            create_repo_command = f"aws ecr create-repository --repository-name dcisionai-manufacturing-v4 --region {region}"
            run_command(create_repo_command, "ECR repository creation")
        except subprocess.CalledProcessError:
            logger.info("ℹ️ ECR repository already exists, continuing...")
        
        # Step 2: Authenticate with ECR
        auth_command = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com"
        run_command(auth_command, "ECR authentication")
        
        # Step 3: Build Docker image using the v4 agent
        build_command = f"docker buildx build --platform linux/arm64 -f domains/manufacturing/Dockerfile.DcisionAI_Manufacturing_MCP -t {ecr_repo}:latest --push ."
        run_command(build_command, "Docker build and push")
        
        # Step 4: Deploy to AgentCore
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
        
        # Save deployment info for easy access
        deployment_info = {
            "agent_runtime_arn": agent_runtime_arn,
            "agent_runtime_name": agent_runtime_name,
            "status": response_data.get('status', 'Unknown'),
            "ecr_repo": ecr_repo,
            "deployment_time": time.time(),
            "version": "v4"
        }
        
        with open("agentcore_v4_deployment.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        logger.info("📋 Next Steps:")
        logger.info("1. Test the deployment:")
        logger.info(f"   python scripts/deployment/test_DcisionAI_Manufacturing_Agent_v4.py")
        logger.info("")
        logger.info("2. Monitor logs:")
        logger.info(f"   aws logs tail /aws/bedrock-agentcore/runtimes/{agent_runtime_name}-* --follow")
        logger.info("")
        logger.info("3. Check status:")
        logger.info(f"   aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id {agent_runtime_name} --region {region}")
        
        return deployment_info
        
    except Exception as e:
        logger.error(f"❌ DEPLOYMENT FAILED: {e}")
        raise

if __name__ == "__main__":
    deploy_dcisionai_manufacturing_agent_v4()
