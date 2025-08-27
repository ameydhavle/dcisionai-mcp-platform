#!/usr/bin/env python3
"""
AWS Credentials Configuration for DcisionAI MCP Server
====================================================

Handles AWS credentials and configuration for AgentCore deployment.
Ensures proper credential setup for all manufacturing tools.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import os
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AWSCredentials:
    """AWS credentials configuration"""
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    region: str = "us-east-1"
    profile: Optional[str] = None

class AWSCredentialManager:
    """Manages AWS credentials for AgentCore deployment"""
    
    def __init__(self):
        self.credentials = self._load_credentials()
        self._configure_boto3()
    
    def _load_credentials(self) -> AWSCredentials:
        """Load AWS credentials from environment or IAM role"""
        try:
            # In AgentCore environment, credentials are provided via IAM role
            if self._is_agentcore_environment():
                logger.info("Running in AgentCore environment - using IAM role credentials")
                return AWSCredentials(
                    region=os.getenv("AWS_REGION", "us-east-1")
                )
            
            # For local development, try environment variables
            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            session_token = os.getenv("AWS_SESSION_TOKEN")
            region = os.getenv("AWS_REGION", "us-east-1")
            profile = os.getenv("AWS_PROFILE")
            
            if access_key and secret_key:
                logger.info("Using AWS credentials from environment variables")
                return AWSCredentials(
                    access_key_id=access_key,
                    secret_access_key=secret_key,
                    session_token=session_token,
                    region=region,
                    profile=profile
                )
            
            # Try AWS profile
            if profile:
                logger.info(f"Using AWS profile: {profile}")
                return AWSCredentials(
                    profile=profile,
                    region=region
                )
            
            # Default to IAM role (for EC2/ECS/AgentCore)
            logger.info("No explicit credentials found - using IAM role")
            return AWSCredentials(region=region)
            
        except Exception as e:
            logger.warning(f"Error loading AWS credentials: {e}")
            return AWSCredentials(region="us-east-1")
    
    def _is_agentcore_environment(self) -> bool:
        """Check if running in AgentCore environment"""
        agentcore_indicators = [
            "BEDROCK_AGENTCORE_RUNTIME" in os.environ,
            "AWS_EXECUTION_ENV" in os.environ and "AgentCore" in os.environ.get("AWS_EXECUTION_ENV", ""),
            os.path.exists("/opt/agentcore"),
            os.getenv("AGENTCORE_ENVIRONMENT") == "true"
        ]
        return any(agentcore_indicators)
    
    def _configure_boto3(self):
        """Configure boto3 with credentials"""
        try:
            if self.credentials.profile:
                boto3.setup_default_session(profile_name=self.credentials.profile, region_name=self.credentials.region)
            elif self.credentials.access_key_id:
                boto3.setup_default_session(
                    aws_access_key_id=self.credentials.access_key_id,
                    aws_secret_access_key=self.credentials.secret_access_key,
                    aws_session_token=self.credentials.session_token,
                    region_name=self.credentials.region
                )
            else:
                # Use IAM role (default behavior)
                boto3.setup_default_session(region_name=self.credentials.region)
            
            logger.info(f"AWS boto3 configured for region: {self.credentials.region}")
            
        except Exception as e:
            logger.warning(f"Error configuring boto3: {e}")
    
    def test_credentials(self) -> bool:
        """Test if AWS credentials are working"""
        try:
            # Try to access a simple AWS service
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            logger.info(f"AWS credentials working - Account: {identity.get('Account')}")
            return True
        except (ClientError, NoCredentialsError) as e:
            logger.warning(f"AWS credentials test failed: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error testing AWS credentials: {e}")
            return False
    
    def get_bedrock_client(self):
        """Get Bedrock client with proper credentials"""
        try:
            return boto3.client('bedrock', region_name=self.credentials.region)
        except Exception as e:
            logger.error(f"Error creating Bedrock client: {e}")
            raise
    
    def get_bedrock_agent_client(self):
        """Get Bedrock Agent client with proper credentials"""
        try:
            return boto3.client('bedrock-agent', region_name=self.credentials.region)
        except Exception as e:
            logger.error(f"Error creating Bedrock Agent client: {e}")
            raise

# Global credential manager instance
aws_credentials = AWSCredentialManager()

def is_agentcore_available() -> bool:
    """Check if AgentCore is available with proper credentials"""
    try:
        if not aws_credentials.test_credentials():
            return False
        
        # Test Bedrock Agent access
        bedrock_agent = aws_credentials.get_bedrock_agent_client()
        bedrock_agent.list_agents()
        logger.info("AgentCore (AWS Bedrock) deployment available")
        return True
        
    except Exception as e:
        logger.warning(f"AgentCore deployment not available: {e}")
        return False

def get_aws_credentials() -> AWSCredentials:
    """Get current AWS credentials"""
    return aws_credentials.credentials

def configure_aws_for_tools():
    """Configure AWS for all manufacturing tools"""
    try:
        # Test credentials
        if aws_credentials.test_credentials():
            logger.info("AWS credentials configured successfully for manufacturing tools")
            return True
        else:
            logger.warning("AWS credentials not available - tools will use local deployment")
            return False
    except Exception as e:
        logger.error(f"Error configuring AWS for tools: {e}")
        return False
