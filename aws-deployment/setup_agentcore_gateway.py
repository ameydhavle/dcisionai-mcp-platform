#!/usr/bin/env python3
"""
Setup Amazon Bedrock AgentCore Gateway for DcisionAI Optimization Platform
=======================================================================

This script sets up the complete AgentCore Gateway infrastructure including:
- IAM roles and policies
- Amazon Cognito for authentication
- AgentCore Gateway creation
- MCP tool conversion for optimization workflows
- Semantic search configuration
"""

import boto3
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class DcisionAIAgentCoreGateway:
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.account_id = boto3.client('sts').get_caller_identity()['Account']
        
        # Initialize AWS clients
        self.iam_client = boto3.client('iam', region_name=region)
        self.cognito_client = boto3.client('cognito-idp', region_name=region)
        self.gateway_client = boto3.client('bedrock-agentcore-control', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        
        # Configuration
        self.gateway_name = 'dcisionai-optimization-gateway'
        self.cognito_pool_name = 'dcisionai-gateway-auth'
        self.iam_role_name = 'dcisionai-agentcore-gateway-role'
        
    def create_iam_role(self) -> str:
        """Create IAM role for AgentCore Gateway with necessary permissions."""
        print("🔐 Creating IAM role for AgentCore Gateway...")
        
        # Trust policy for AgentCore Gateway
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
        
        # Create the role
        try:
            response = self.iam_client.create_role(
                RoleName=self.iam_role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='IAM role for DcisionAI AgentCore Gateway'
            )
            role_arn = response['Role']['Arn']
            print(f"✅ Created IAM role: {role_arn}")
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print(f"✅ IAM role already exists: {self.iam_role_name}")
            role_arn = f"arn:aws:iam::{self.account_id}:role/{self.iam_role_name}"
        
        # Attach necessary policies
        policies_to_attach = [
            'arn:aws:iam::aws:policy/AmazonBedrockFullAccess',
            'arn:aws:iam::aws:policy/AWSLambda_FullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess',
            'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'
        ]
        
        for policy_arn in policies_to_attach:
            try:
                self.iam_client.attach_role_policy(
                    RoleName=self.iam_role_name,
                    PolicyArn=policy_arn
                )
                print(f"✅ Attached policy: {policy_arn}")
            except Exception as e:
                print(f"⚠️  Could not attach policy {policy_arn}: {e}")
        
        # Create custom policy for optimization workflows
        custom_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "lambda:InvokeFunction",
                        "lambda:GetFunction",
                        "lambda:ListFunctions"
                    ],
                    "Resource": [
                        f"arn:aws:lambda:{self.region}:{self.account_id}:function:dcisionai-*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            self.iam_client.put_role_policy(
                RoleName=self.iam_role_name,
                PolicyName='DcisionAIOptimizationPolicy',
                PolicyDocument=json.dumps(custom_policy)
            )
            print("✅ Created custom optimization policy")
        except Exception as e:
            print(f"⚠️  Could not create custom policy: {e}")
        
        return role_arn
    
    def setup_cognito_auth(self) -> Dict[str, str]:
        """Set up Amazon Cognito for Gateway authentication."""
        print("🔑 Setting up Amazon Cognito authentication...")
        
        # Create user pool
        try:
            pool_response = self.cognito_client.create_user_pool(
                PoolName=self.cognito_pool_name,
                Policies={
                    'PasswordPolicy': {
                        'MinimumLength': 8,
                        'RequireUppercase': True,
                        'RequireLowercase': True,
                        'RequireNumbers': True,
                        'RequireSymbols': False
                    }
                },
                UsernameAttributes=['email'],
                AutoVerifiedAttributes=['email'],
                Schema=[
                    {
                        'Name': 'email',
                        'AttributeDataType': 'String',
                        'Required': True,
                        'Mutable': True
                    }
                ],
                UserPoolTags={
                    'Project': 'DcisionAI',
                    'Component': 'AgentCore-Gateway'
                }
            )
            user_pool_id = pool_response['UserPool']['Id']
            print(f"✅ Created Cognito User Pool: {user_pool_id}")
        except self.cognito_client.exceptions.UsernameExistsException:
            # Get existing pool
            pools = self.cognito_client.list_user_pools(MaxResults=50)
            for pool in pools['UserPools']:
                if pool['Name'] == self.cognito_pool_name:
                    user_pool_id = pool['Id']
                    print(f"✅ Using existing Cognito User Pool: {user_pool_id}")
                    break
        
        # Create user pool client
        try:
            client_response = self.cognito_client.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName='dcisionai-gateway-client',
                GenerateSecret=False,  # Public client for frontend
                ExplicitAuthFlows=[
                    'ALLOW_USER_SRP_AUTH',
                    'ALLOW_REFRESH_TOKEN_AUTH'
                ],
                SupportedIdentityProviders=['COGNITO'],
                CallbackURLs=['http://localhost:3000/callback'],
                LogoutURLs=['http://localhost:3000/logout'],
                AllowedOAuthFlows=['code'],
                AllowedOAuthScopes=['openid', 'email', 'profile'],
                AllowedOAuthFlowsUserPoolClient=True
            )
            client_id = client_response['UserPoolClient']['ClientId']
            print(f"✅ Created Cognito Client: {client_id}")
        except Exception as e:
            print(f"⚠️  Could not create Cognito client: {e}")
            client_id = "placeholder-client-id"
        
        # Get discovery URL
        discovery_url = f"https://cognito-idp.{self.region}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
        
        return {
            'user_pool_id': user_pool_id,
            'client_id': client_id,
            'discovery_url': discovery_url
        }
    
    def create_gateway(self, role_arn: str, cognito_config: Dict[str, str]) -> str:
        """Create the AgentCore Gateway."""
        print("🚀 Creating AgentCore Gateway...")
        
        # Authentication configuration
        auth_config = {
            "customJWTAuthorizer": {
                "allowedClients": [cognito_config['client_id']],
                "discoveryUrl": cognito_config['discovery_url']
            }
        }
        
        # Enable semantic search
        search_config = {
            "mcp": {
                "searchType": "SEMANTIC",
                "supportedVersions": ["2025-03-26"]
            }
        }
        
        try:
            response = self.gateway_client.create_gateway(
                name=self.gateway_name,
                roleArn=role_arn,
                protocolType='MCP',
                authorizerType='CUSTOM_JWT',
                authorizerConfiguration=auth_config,
                protocolConfiguration=search_config,
                description='DcisionAI Optimization Workflow Gateway',
                exceptionLevel='DEBUG'  # Enable debug mode for troubleshooting
            )
            gateway_id = response['gatewayId']
            gateway_endpoint = response['gatewayEndpoint']
            print(f"✅ Created Gateway: {gateway_id}")
            print(f"✅ Gateway Endpoint: {gateway_endpoint}")
            return gateway_id
        except Exception as e:
            print(f"❌ Failed to create Gateway: {e}")
            raise
    
    def create_lambda_target(self, gateway_id: str) -> str:
        """Create Lambda target for optimization workflows."""
        print("🔧 Creating Lambda target for optimization workflows...")
        
        lambda_target_config = {
            "mcp": {
                "lambda": {
                    "functionArn": f"arn:aws:lambda:{self.region}:{self.account_id}:function:dcisionai-enhanced-workflows"
                }
            }
        }
        
        try:
            response = self.gateway_client.create_gateway_target(
                gatewayId=gateway_id,
                name='optimization-workflows',
                targetType='LAMBDA',
                targetConfiguration=lambda_target_config,
                description='Lambda functions for optimization workflows'
            )
            target_id = response['targetId']
            print(f"✅ Created Lambda target: {target_id}")
            return target_id
        except Exception as e:
            print(f"❌ Failed to create Lambda target: {e}")
            raise
    
    def create_openapi_target(self, gateway_id: str) -> str:
        """Create OpenAPI target for Bedrock models."""
        print("📡 Creating OpenAPI target for Bedrock models...")
        
        # OpenAPI specification for Bedrock models
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "DcisionAI Bedrock Models API",
                "version": "1.0.0",
                "description": "API for accessing Bedrock models for optimization"
            },
            "servers": [
                {
                    "url": f"https://bedrock-runtime.{self.region}.amazonaws.com",
                    "description": "Bedrock Runtime API"
                }
            ],
            "paths": {
                "/model/{modelId}/invoke": {
                    "post": {
                        "summary": "Invoke Bedrock model",
                        "description": "Invoke a Bedrock model for optimization tasks",
                        "parameters": [
                            {
                                "name": "modelId",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Bedrock model identifier"
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "prompt": {"type": "string"},
                                            "max_tokens": {"type": "integer"},
                                            "temperature": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Model response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "response": {"type": "string"},
                                                "usage": {"type": "object"}
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
        
        openapi_target_config = {
            "mcp": {
                "openApiSchema": {
                    "inline": openapi_spec
                }
            }
        }
        
        try:
            response = self.gateway_client.create_gateway_target(
                gatewayId=gateway_id,
                name='bedrock-models',
                targetType='OPENAPI',
                targetConfiguration=openapi_target_config,
                description='OpenAPI specification for Bedrock models'
            )
            target_id = response['targetId']
            print(f"✅ Created OpenAPI target: {target_id}")
            return target_id
        except Exception as e:
            print(f"❌ Failed to create OpenAPI target: {e}")
            raise
    
    def setup_complete_gateway(self) -> Dict[str, Any]:
        """Set up the complete AgentCore Gateway infrastructure."""
        print("🚀 Setting up DcisionAI AgentCore Gateway...")
        print("=" * 60)
        
        try:
            # Step 1: Create IAM role
            role_arn = self.create_iam_role()
            
            # Step 2: Set up Cognito authentication
            cognito_config = self.setup_cognito_auth()
            
            # Step 3: Create Gateway
            gateway_id = self.create_gateway(role_arn, cognito_config)
            
            # Step 4: Create targets
            lambda_target_id = self.create_lambda_target(gateway_id)
            openapi_target_id = self.create_openapi_target(gateway_id)
            
            # Get gateway details
            gateway_details = self.gateway_client.get_gateway(gatewayId=gateway_id)
            gateway_endpoint = gateway_details['gatewayEndpoint']
            
            result = {
                'gateway_id': gateway_id,
                'gateway_endpoint': gateway_endpoint,
                'role_arn': role_arn,
                'cognito_config': cognito_config,
                'lambda_target_id': lambda_target_id,
                'openapi_target_id': openapi_target_id,
                'status': 'success'
            }
            
            print("\n" + "=" * 60)
            print("🎉 AgentCore Gateway Setup Complete!")
            print("=" * 60)
            print(f"Gateway ID: {gateway_id}")
            print(f"Gateway Endpoint: {gateway_endpoint}")
            print(f"Cognito User Pool: {cognito_config['user_pool_id']}")
            print(f"Cognito Client ID: {cognito_config['client_id']}")
            print("=" * 60)
            
            return result
            
        except Exception as e:
            print(f"❌ Gateway setup failed: {e}")
            return {'status': 'error', 'error': str(e)}

def main():
    """Main function to set up AgentCore Gateway."""
    print("🚀 DcisionAI AgentCore Gateway Setup")
    print("=" * 50)
    
    gateway_setup = DcisionAIAgentCoreGateway()
    result = gateway_setup.setup_complete_gateway()
    
    if result['status'] == 'success':
        print("\n📋 Next Steps:")
        print("1. Test the Gateway with optimization workflows")
        print("2. Update frontend to use AgentCore Gateway")
        print("3. Enable semantic search for tool discovery")
        print("4. Monitor Gateway performance with CloudWatch")
        
        # Save configuration
        config_file = f"agentcore_gateway_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(config_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Configuration saved to: {config_file}")
    else:
        print(f"\n❌ Setup failed: {result['error']}")

if __name__ == "__main__":
    main()
