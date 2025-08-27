#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Complete Build & Deploy Script
===================================================================

Complete deployment pipeline for DcisionAI Manufacturing MCP Server.
This script handles building, pushing to ECR, and deploying to AgentCore.

Domain: Manufacturing Optimization & Decision Intelligence
Brand: DcisionAI
Platform: AWS Bedrock AgentCore

Usage:
    python scripts/deployment/dcisionai_manufacturing_build_and_deploy.py

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import subprocess
import sys
import logging
import time
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

def run_command(command, description):
    """Run a shell command with logging"""
    logger.info(f"🔄 {description}")
    logger.info(f"💻 Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        if result.stdout:
            logger.info(f"📤 Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed")
        logger.error(f"📤 Error: {e.stderr}")
        raise

def build_manufacturing_image():
    """Build ARM64 Docker image for DcisionAI Manufacturing"""
    logger.info("🏭 Building DcisionAI Manufacturing MCP Server Docker image...")
    
    # Build ARM64 image for DcisionAI Manufacturing
    build_command = "docker buildx build --platform linux/arm64 -f Dockerfile -t dcisionai-manufacturing-mcp:arm64 --load ."
    run_command(build_command, "Docker ARM64 build")
    
    logger.info("✅ Manufacturing image built successfully")

def setup_ecr_repository():
    """Setup ECR repository for DcisionAI Manufacturing"""
    logger.info("🏭 Setting up ECR repository for DcisionAI Manufacturing...")
    
    # Create ECR repository
    create_repo_command = "aws ecr create-repository --repository-name dcisionai-manufacturing-mcp --region us-east-1"
    try:
        run_command(create_repo_command, "ECR repository creation")
    except:
        logger.info("ℹ️ ECR repository already exists")
    
    # Login to ECR
    login_command = "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 808953421331.dkr.ecr.us-east-1.amazonaws.com"
    run_command(login_command, "ECR login")
    
    logger.info("✅ ECR repository setup completed")

def push_to_ecr():
    """Push manufacturing image to ECR"""
    logger.info("🏭 Pushing DcisionAI Manufacturing image to ECR...")
    
    # Tag image
    tag_command = "docker tag dcisionai-manufacturing-mcp:arm64 808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-mcp:latest"
    run_command(tag_command, "Docker image tagging")
    
    # Push to ECR
    push_command = "docker push 808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-mcp:latest"
    run_command(push_command, "ECR push")
    
    logger.info("✅ Manufacturing image pushed to ECR successfully")

def deploy_to_agentcore():
    """Deploy to AgentCore"""
    logger.info("🏭 Deploying DcisionAI Manufacturing MCP Server to AgentCore...")
    
    # Import and run deployment
    from scripts.deployment.dcisionai_manufacturing_deploy_agentcore import deploy_manufacturing_agent
    deploy_manufacturing_agent()
    
    logger.info("✅ Manufacturing MCP Server deployed to AgentCore")

def test_deployment():
    """Test the deployed manufacturing agent"""
    logger.info("🏭 Testing DcisionAI Manufacturing MCP Server deployment...")
    
    # Wait for deployment to be ready
    logger.info("⏳ Waiting for deployment to be ready...")
    time.sleep(30)
    
    # Import and run invocation
    from scripts.deployment.dcisionai_manufacturing_invoke_agentcore import invoke_manufacturing_agent
    invoke_manufacturing_agent()
    
    logger.info("✅ Manufacturing MCP Server deployment tested successfully")

def main():
    """Main deployment pipeline"""
    logger.info("🚀 Starting DcisionAI Manufacturing MCP Server deployment pipeline...")
    
    try:
        # Step 1: Build Docker image
        build_manufacturing_image()
        
        # Step 2: Setup ECR
        setup_ecr_repository()
        
        # Step 3: Push to ECR
        push_to_ecr()
        
        # Step 4: Deploy to AgentCore
        deploy_to_agentcore()
        
        # Step 5: Test deployment
        test_deployment()
        
        logger.info("🎉 DcisionAI Manufacturing MCP Server deployment pipeline completed successfully!")
        logger.info("🏭 Manufacturing Optimization Platform is now live on AWS AgentCore!")
        
    except Exception as e:
        logger.error(f"❌ Deployment pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
