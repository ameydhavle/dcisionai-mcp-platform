#!/usr/bin/env python3
"""
Gateway Setup for DcisionAI AgentCore
====================================

This script sets up AgentCore Gateway to convert existing Lambda functions
into tools that can be used by the AgentCore agent.
"""

import json
import logging
import uuid
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_dcisionai_gateway():
    """Set up Gateway with DcisionAI optimization tools."""
    
    # Create a unique name for the gateway (no underscores allowed)
    gateway_name = f"DcisionAI-Gateway-{uuid.uuid4().hex[:8]}"
    
    # Initialize client
    client = GatewayClient(region_name="us-east-1")
    client.logger.setLevel(logging.INFO)
    
    try:
        # Create OAuth authorizer with Cognito
        logger.info("Creating OAuth authorization server...")
        cognito_response = client.create_oauth_authorizer_with_cognito(gateway_name)
        logger.info("✅ Authorization server created")
        
        # Create Gateway
        logger.info("Creating Gateway...")
        gateway = client.create_mcp_gateway(
            name=gateway_name,
            role_arn=None,  # Auto-creates IAM role
            authorizer_config=cognito_response["authorizer_config"],
            enable_semantic_search=True,
        )
        logger.info(f"✅ Gateway created: {gateway['gatewayUrl']}")
        
        # IAM permissions are handled automatically by the Gateway creation
        logger.info("✅ IAM permissions configured automatically")
        
        # Add optimization Lambda target
        logger.info("Adding optimization Lambda target...")
        optimization_schema = {
            "inlinePayload": [
                {
                    "name": "classify_intent",
                    "description": "Classify optimization problem intent and extract key information",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Detailed description of the optimization problem"
                            }
                        },
                        "required": ["problem_description"]
                    }
                },
                {
                    "name": "analyze_data",
                    "description": "Analyze data requirements for optimization problem",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results"
                            }
                        },
                        "required": ["problem_description", "intent_data"]
                    }
                },
                {
                    "name": "build_model",
                    "description": "Build mathematical optimization model",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results"
                            },
                            "data_analysis": {
                                "type": "object",
                                "description": "Data analysis results"
                            }
                        },
                        "required": ["problem_description", "intent_data", "data_analysis"]
                    }
                },
                {
                    "name": "solve_optimization",
                    "description": "Solve optimization problem and return solution",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results"
                            },
                            "model_building": {
                                "type": "object",
                                "description": "Model building results"
                            }
                        },
                        "required": ["problem_description", "intent_data", "model_building"]
                    }
                },
                {
                    "name": "get_workflow_templates",
                    "description": "Get available workflow templates by industry",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "industry": {
                                "type": "string",
                                "description": "Industry name (manufacturing, healthcare, retail, etc.)"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "execute_workflow",
                    "description": "Execute a specific workflow with predefined problem description",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "industry": {
                                "type": "string",
                                "description": "Industry name"
                            },
                            "workflow_id": {
                                "type": "string",
                                "description": "Workflow ID"
                            }
                        },
                        "required": ["industry", "workflow_id"]
                    }
                }
            ]
        }
        
        # Get the existing Lambda function ARN
        lambda_arn = "arn:aws:lambda:us-east-1:808953421331:function:dcisionai-enhanced-workflows"
        
        lambda_config = {
            "arn": lambda_arn,
            "tools": optimization_schema["inlinePayload"]
        }
        
        lambda_target = client.create_mcp_gateway_target(
            gateway=gateway,
            name="DcisionAI-Optimization-Tools",
            target_type="lambda",
            target_payload={
                "toolSchema": optimization_schema,
                "lambdaArn": lambda_arn
            }
        )
        logger.info("✅ Optimization tools target added")
        
        # Get access token
        logger.info("Getting access token...")
        access_token = client.get_access_token_for_cognito(cognito_response["client_info"])
        logger.info("✅ Access token obtained")
        
        # Save configuration for agent
        config = {
            "gateway_url": gateway["gatewayUrl"],
            "gateway_id": gateway["gatewayId"],
            "access_token": access_token,
            "client_info": cognito_response["client_info"]
        }
        
        with open("gateway_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info("=" * 60)
        logger.info("✅ Gateway setup complete!")
        logger.info(f"Gateway URL: {gateway['gatewayUrl']}")
        logger.info(f"Gateway ID: {gateway['gatewayId']}")
        logger.info("\nConfiguration saved to: gateway_config.json")
        logger.info("=" * 60)
        
        return gateway, config
        
    except Exception as e:
        logger.error(f"Gateway setup failed: {str(e)}")
        raise

if __name__ == "__main__":
    setup_dcisionai_gateway()
