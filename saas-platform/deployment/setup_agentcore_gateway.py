#!/usr/bin/env python3
"""
Setup Amazon Bedrock AgentCore Gateway for DcisionAI
====================================================

This script sets up the AgentCore Gateway to expose our DcisionAI MCP server
as tools that can be accessed by AI agents through the Gateway.

Based on: https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-agentcore-gateway-transforming-enterprise-ai-agent-tool-development/
"""

import boto3
import json
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DcisionAIGatewaySetup:
    """Setup AgentCore Gateway for DcisionAI MCP server."""
    
    def __init__(self, region: str = "us-east-1"):
        """Initialize Gateway setup."""
        self.region = region
        self.gateway_client = boto3.client('bedrock-agentcore-control', region_name=region)
        self.agentcore_client = boto3.client('bedrock-agentcore', region_name=region)
        
        # Configuration
        self.gateway_name = "dcisionai-optimization-gateway"
        self.gateway_role_arn = self._get_or_create_gateway_role()
        
        # Cognito Configuration (from our existing setup)
        self.cognito_pool_id = "us-west-2_pEQfTkscK"
        self.cognito_client_id = "5h4o4dpu7r7qreusrjhu54umqo"
        self.discovery_url = f"https://cognito-idp.us-west-2.amazonaws.com/{self.cognito_pool_id}/.well-known/openid-configuration"
    
    def _get_or_create_gateway_role(self) -> str:
        """Get or create IAM role for Gateway."""
        iam_client = boto3.client('iam')
        role_name = "DcisionAIGatewayRole"
        
        try:
            # Try to get existing role
            response = iam_client.get_role(RoleName=role_name)
            logger.info(f"Using existing IAM role: {response['Role']['Arn']}")
            return response['Role']['Arn']
        except iam_client.exceptions.NoSuchEntityException:
            # Create new role
            logger.info(f"Creating new IAM role: {role_name}")
            
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "bedrock-agentcore.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            # Create role
            iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="IAM role for DcisionAI AgentCore Gateway"
            )
            
            # Attach necessary policies
            policies = [
                "arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess"
            ]
            
            for policy_arn in policies:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            # Get role ARN
            response = iam_client.get_role(RoleName=role_name)
            logger.info(f"Created IAM role: {response['Role']['Arn']}")
            return response['Role']['Arn']
    
    def create_gateway(self) -> Dict[str, Any]:
        """Create AgentCore Gateway with Cognito authentication."""
        logger.info(f"Creating AgentCore Gateway: {self.gateway_name}")
        
        # OAuth configuration for Cognito
        auth_config = {
            "customJWTAuthorizer": {
                "allowedClients": [self.cognito_client_id],
                "discoveryUrl": self.discovery_url
            }
        }
        
        # Enable semantic search for intelligent tool discovery
        search_config = {
            "mcp": {
                "searchType": "SEMANTIC",
                "supportedVersions": ["2025-03-26"]
            }
        }
        
        try:
            response = self.gateway_client.create_gateway(
                name=self.gateway_name,
                roleArn=self.gateway_role_arn,
                protocolType='MCP',
                authorizerType='CUSTOM_JWT',
                authorizerConfiguration=auth_config,
                protocolConfiguration=search_config,
                description='DcisionAI Optimization Platform Gateway - Exposes optimization tools via MCP',
                exceptionLevel="DEBUG"  # Enable debug mode for better error messages
            )
            
            gateway_arn = response['gatewayArn']
            logger.info(f"✅ Gateway created successfully: {gateway_arn}")
            
            return {
                "status": "success",
                "gateway_arn": gateway_arn,
                "gateway_name": self.gateway_name,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create Gateway: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_openapi_target(self, gateway_arn: str) -> Dict[str, Any]:
        """Create OpenAPI target for DcisionAI MCP server."""
        logger.info("Creating OpenAPI target for DcisionAI MCP server")
        
        # OpenAPI specification for DcisionAI tools
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "DcisionAI Optimization Platform",
                "description": "Mathematical optimization tools for AI agents",
                "version": "1.0.0"
            },
            "servers": [
                {
                    "url": "https://api.dcisionai.com",
                    "description": "DcisionAI API Server"
                }
            ],
            "paths": {
                "/tools/classify-intent": {
                    "post": {
                        "summary": "Classify optimization problem intent",
                        "description": "Analyze problem description to identify optimization type and requirements",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "problem_description": {"type": "string"},
                                            "context": {"type": "string"}
                                        },
                                        "required": ["problem_description"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Intent classification result",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "result": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/tools/build-model": {
                    "post": {
                        "summary": "Build mathematical optimization model",
                        "description": "Create optimization model with pattern-breaking strategies",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "problem_description": {"type": "string"},
                                            "intent_data": {"type": "object"},
                                            "data_analysis": {"type": "object"}
                                        },
                                        "required": ["problem_description"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Model building result",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "result": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        try:
            # Create Gateway target for OpenAPI
            target_response = self.gateway_client.create_gateway_target(
                gatewayArn=gateway_arn,
                name='dcisionai-openapi-tools',
                targetType='OPENAPI',
                targetConfiguration={
                    'openapi': {
                        'schema': openapi_spec
                    }
                },
                description='DcisionAI Optimization Tools via OpenAPI'
            )
            
            logger.info(f"✅ OpenAPI target created: {target_response['targetArn']}")
            
            return {
                "status": "success",
                "target_arn": target_response['targetArn']
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create OpenAPI target: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def setup_complete_gateway(self) -> Dict[str, Any]:
        """Setup complete Gateway with all components."""
        logger.info("🚀 Setting up complete DcisionAI AgentCore Gateway")
        
        # Step 1: Create Gateway
        gateway_result = self.create_gateway()
        if gateway_result['status'] != 'success':
            return gateway_result
        
        gateway_arn = gateway_result['gateway_arn']
        
        # Step 2: Create OpenAPI target
        target_result = self.create_openapi_target(gateway_arn)
        if target_result['status'] != 'success':
            return target_result
        
        # Step 3: Get Gateway endpoint
        try:
            gateway_info = self.gateway_client.get_gateway(gatewayArn=gateway_arn)
            gateway_endpoint = gateway_info['gateway']['endpoint']
            
            logger.info(f"🎉 Gateway setup complete!")
            logger.info(f"Gateway ARN: {gateway_arn}")
            logger.info(f"Gateway Endpoint: {gateway_endpoint}")
            
            return {
                "status": "success",
                "gateway_arn": gateway_arn,
                "gateway_endpoint": gateway_endpoint,
                "target_arn": target_result['target_arn'],
                "message": "DcisionAI AgentCore Gateway setup complete!"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get Gateway endpoint: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

def main():
    """Main setup function."""
    print("🚀 Setting up DcisionAI AgentCore Gateway")
    print("=" * 50)
    
    setup = DcisionAIGatewaySetup()
    result = setup.setup_complete_gateway()
    
    if result['status'] == 'success':
        print("\n✅ Gateway Setup Complete!")
        print(f"Gateway ARN: {result['gateway_arn']}")
        print(f"Gateway Endpoint: {result['gateway_endpoint']}")
        print(f"Target ARN: {result['target_arn']}")
        
        print("\n📋 Next Steps:")
        print("1. Test Gateway with MCP client")
        print("2. Update SaaS platform to use Gateway endpoint")
        print("3. Configure OAuth authentication")
        
    else:
        print(f"\n❌ Gateway Setup Failed: {result['error']}")

if __name__ == "__main__":
    main()
