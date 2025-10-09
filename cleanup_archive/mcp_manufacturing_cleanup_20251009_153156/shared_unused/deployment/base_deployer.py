#!/usr/bin/env python3
"""
DcisionAI Platform - Base Deployment Framework
=============================================

Base class for all domain-specific deployment scripts.
Provides common deployment functionality across all domains.
"""

import logging
import time
import subprocess
import boto3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeploymentConfig:
    """Configuration for domain deployment."""
    domain_name: str
    agent_name: str
    dockerfile_path: str
    requirements_path: str
    ecr_repo: str
    agent_runtime_prefix: str
    region: str
    role_arn: str
    max_wait_time: int = 600  # 10 minutes default

@dataclass
class DeploymentResult:
    """Result of deployment operation."""
    success: bool
    agent_runtime_arn: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    deployment_time: float = 0.0
    timestamp: datetime = None

class BaseDeployer:
    """
    Abstract base class for all domain-specific deployment scripts.
    
    Provides common deployment functionality that all domain deployers
    must implement.
    """
    
    def __init__(self, config: DeploymentConfig):
        """Initialize the base deployer with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{config.domain_name}_deployer")
        self.logger.setLevel(logging.INFO)
        
        # Initialize AWS clients
        self.ecr_client = boto3.client('ecr', region_name=config.region)
        self.agentcore_client = boto3.client('bedrock-agentcore-control', region_name=config.region)
        self.agentcore_runtime_client = boto3.client('bedrock-agentcore', region_name=config.region)
        
        self.logger.info(f"✅ {config.domain_name} Deployer initialized successfully")
    
    def deploy(self) -> DeploymentResult:
        """Execute the complete deployment process."""
        start_time = time.time()
        timestamp = datetime.now()
        
        try:
            self.logger.info(f"🚀 Starting deployment for {self.config.domain_name} domain")
            
            # Step 1: Authenticate with ECR
            if not self._authenticate_ecr():
                return DeploymentResult(
                    success=False,
                    error_message="ECR authentication failed",
                    deployment_time=time.time() - start_time,
                    timestamp=timestamp
                )
            
            # Step 2: Build and push Docker image
            if not self._build_and_push_image():
                return DeploymentResult(
                    success=False,
                    error_message="Docker build and push failed",
                    deployment_time=time.time() - start_time,
                    timestamp=timestamp
                )
            
            # Step 3: Create AgentCore runtime
            agent_runtime_arn = self._create_agent_runtime()
            if not agent_runtime_arn:
                return DeploymentResult(
                    success=False,
                    error_message="AgentCore runtime creation failed",
                    deployment_time=time.time() - start_time,
                    timestamp=timestamp
                )
            
            # Step 4: Wait for runtime to be ready
            status = self._wait_for_runtime_ready(agent_runtime_arn)
            if not status:
                return DeploymentResult(
                    success=False,
                    error_message="Runtime failed to become ready",
                    deployment_time=time.time() - start_time,
                    timestamp=timestamp
                )
            
            deployment_time = time.time() - start_time
            
            self.logger.info(f"✅ Deployment completed successfully in {deployment_time:.2f}s")
            
            return DeploymentResult(
                success=True,
                agent_runtime_arn=agent_runtime_arn,
                status=status,
                deployment_time=deployment_time,
                timestamp=timestamp
            )
            
        except Exception as e:
            deployment_time = time.time() - start_time
            error_msg = f"Deployment failed: {str(e)}"
            
            self.logger.error(error_msg, exc_info=True)
            
            return DeploymentResult(
                success=False,
                error_message=error_msg,
                deployment_time=deployment_time,
                timestamp=timestamp
            )
    
    def _authenticate_ecr(self) -> bool:
        """Authenticate with ECR registry."""
        try:
            self.logger.info("🔐 Authenticating with ECR...")
            
            # Get ECR login token
            response = self.ecr_client.get_authorization_token()
            token = response['authorizationData'][0]['authorizationToken']
            
            # Execute docker login
            cmd = f"echo {token} | docker login --username AWS --password-stdin {self.config.ecr_repo.split('/')[0]}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"ECR login failed: {result.stderr}")
                return False
            
            self.logger.info("✅ ECR authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"ECR authentication failed: {e}")
            return False
    
    def _build_and_push_image(self) -> bool:
        """Build and push Docker image to ECR."""
        try:
            self.logger.info("🐳 Building and pushing Docker image...")
            
            # Build image with buildx for multi-platform support
            build_cmd = f"""docker buildx build --platform linux/arm64 \
                -f {self.config.dockerfile_path} \
                -t {self.config.ecr_repo}:latest \
                --push ."""
            
            result = subprocess.run(build_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Docker build failed: {result.stderr}")
                return False
            
            self.logger.info("✅ Docker image built and pushed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Docker build and push failed: {e}")
            return False
    
    def _create_agent_runtime(self) -> Optional[str]:
        """Create AgentCore runtime."""
        try:
            self.logger.info("🤖 Creating AgentCore runtime...")
            
            timestamp = int(time.time())
            runtime_name = f"{self.config.agent_runtime_prefix}_{timestamp}"
            
            # Prepare runtime configuration
            artifact_config = {
                "containerConfiguration": {
                    "containerUri": f"{self.config.ecr_repo}:latest"
                }
            }
            
            network_config = {
                "networkMode": "PUBLIC"
            }
            
            # Create runtime
            response = self.agentcore_client.create_agent_runtime(
                agentRuntimeName=runtime_name,
                agentRuntimeArtifact=artifact_config,
                networkConfiguration=network_config,
                roleArn=self.config.role_arn
            )
            
            agent_runtime_arn = response['agentRuntimeArn']
            
            self.logger.info(f"✅ AgentCore runtime created: {agent_runtime_arn}")
            return agent_runtime_arn
            
        except Exception as e:
            self.logger.error(f"AgentCore runtime creation failed: {e}")
            return None
    
    def _wait_for_runtime_ready(self, agent_runtime_arn: str) -> Optional[str]:
        """Wait for runtime to become ready."""
        try:
            self.logger.info("⏳ Waiting for runtime to become ready...")
            
            start_time = time.time()
            while time.time() - start_time < self.config.max_wait_time:
                try:
                    # Get runtime status
                    response = self.agentcore_client.get_agent_runtime(
                        agentRuntimeId=agent_runtime_arn.split('/')[-1]
                    )
                    
                    status = response['agentRuntime']['status']
                    self.logger.info(f"Runtime status: {status}")
                    
                    if status == 'READY':
                        self.logger.info("✅ Runtime is ready")
                        return status
                    elif status == 'ERROR':
                        self.logger.error("❌ Runtime creation failed")
                        return None
                    
                    # Wait before checking again
                    time.sleep(30)
                    
                except Exception as e:
                    self.logger.warning(f"Error checking runtime status: {e}")
                    time.sleep(30)
            
            self.logger.error("❌ Timeout waiting for runtime to become ready")
            return None
            
        except Exception as e:
            self.logger.error(f"Error waiting for runtime: {e}")
            return None
    
    def get_deployment_summary(self) -> Dict[str, Any]:
        """Get deployment configuration summary."""
        return {
            "domain_name": self.config.domain_name,
            "agent_name": self.config.agent_name,
            "dockerfile_path": self.config.dockerfile_path,
            "requirements_path": self.config.requirements_path,
            "ecr_repo": self.config.ecr_repo,
            "agent_runtime_prefix": self.config.agent_runtime_prefix,
            "region": self.config.region,
            "role_arn": self.config.role_arn,
            "max_wait_time": self.config.max_wait_time
        }
    
    def cleanup(self, agent_runtime_arn: str) -> bool:
        """Clean up deployment resources."""
        try:
            self.logger.info(f"🧹 Cleaning up runtime: {agent_runtime_arn}")
            
            # Delete AgentCore runtime
            runtime_id = agent_runtime_arn.split('/')[-1]
            self.agentcore_client.delete_agent_runtime(agentRuntimeId=runtime_id)
            
            self.logger.info("✅ Cleanup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return False
    
    def get_runtime_status(self, agent_runtime_arn: str) -> Optional[str]:
        """Get current status of a runtime."""
        try:
            runtime_id = agent_runtime_arn.split('/')[-1]
            response = self.agentcore_client.get_agent_runtime(agentRuntimeId=runtime_id)
            return response['agentRuntime']['status']
            
        except Exception as e:
            self.logger.error(f"Failed to get runtime status: {e}")
            return None
