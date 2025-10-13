#!/usr/bin/env python3
"""
Simple Bedrock AgentCore Proxy
==============================

A simple Lambda function that proxies requests to Bedrock AgentCore.
Uses only boto3 (which is available in Lambda runtime) to avoid dependency issues.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import json
import logging
import boto3
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrock AgentCore configuration
BEDROCK_AGENTCORE_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/bedrock_agentcore_mcp_server-uZ4MxJ2bNZ"

# Initialize AWS client
bedrock_agentcore_client = boto3.client('bedrock-agentcore', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Lambda handler for Bedrock AgentCore proxy.
    """
    logger.info(f"🔄 Processing request: {event}")
    
    try:
        # Parse the request
        if 'body' in event:
            # API Gateway request
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct invocation
            body = event
        
        # Extract MCP request
        method = body.get('method', '')
        params = body.get('params', {})
        request_id = body.get('id', '1')
        
        logger.info(f"📤 MCP request: {method}")
        
        if method == "tools/call":
            tool_name = params.get('name', '')
            tool_args = params.get('arguments', {})
            
            if tool_name == "manufacturing_health_check":
                # Call Bedrock AgentCore
                response = bedrock_agentcore_client.invoke_agent_runtime(
                    agentRuntimeArn=BEDROCK_AGENTCORE_ARN,
                    payload=json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "tools/call",
                        "params": {
                            "name": "manufacturing_health_check",
                            "arguments": {}
                        }
                    })
                )
                
                # Parse response
                if 'completion' in response and 'chunk' in response['completion']:
                    result_text = ""
                    for chunk in response['completion']['chunk']:
                        if 'bytes' in chunk:
                            chunk_data = json.loads(chunk['bytes'].decode('utf-8'))
                            if 'result' in chunk_data:
                                result_text += json.dumps(chunk_data['result'])
                    
                    if result_text:
                        try:
                            result_data = json.loads(result_text)
                            return {
                                'statusCode': 200,
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                                    'Access-Control-Allow-Headers': 'Content-Type'
                                },
                                'body': json.dumps({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": result_data
                                })
                            }
                        except json.JSONDecodeError:
                            return {
                                'statusCode': 200,
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                                    'Access-Control-Allow-Headers': 'Content-Type'
                                },
                                'body': json.dumps({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": {
                                        "content": [{"type": "text", "text": result_text}]
                                    }
                                })
                            }
                
                # Fallback response
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type'
                    },
                    'body': json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": "Health check completed"}]
                        }
                    })
                }
            
            elif tool_name == "manufacturing_optimize":
                # Call Bedrock AgentCore for optimization
                response = bedrock_agentcore_client.invoke_agent_runtime(
                    agentRuntimeArn=BEDROCK_AGENTCORE_ARN,
                    payload=json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "tools/call",
                        "params": {
                            "name": "manufacturing_optimize",
                            "arguments": tool_args
                        }
                    })
                )
                
                # Parse response
                if 'completion' in response and 'chunk' in response['completion']:
                    result_text = ""
                    for chunk in response['completion']['chunk']:
                        if 'bytes' in chunk:
                            chunk_data = json.loads(chunk['bytes'].decode('utf-8'))
                            if 'result' in chunk_data:
                                result_text += json.dumps(chunk_data['result'])
                    
                    if result_text:
                        try:
                            result_data = json.loads(result_text)
                            return {
                                'statusCode': 200,
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                                    'Access-Control-Allow-Headers': 'Content-Type'
                                },
                                'body': json.dumps({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": result_data
                                })
                            }
                        except json.JSONDecodeError:
                            return {
                                'statusCode': 200,
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                                    'Access-Control-Allow-Headers': 'Content-Type'
                                },
                                'body': json.dumps({
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": {
                                        "content": [{"type": "text", "text": result_text}]
                                    }
                                })
                            }
                
                # Fallback response
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type'
                    },
                    'body': json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": "Optimization completed"}]
                        }
                    })
                }
        
        # Handle health check endpoint
        if event.get('httpMethod') == 'GET' and event.get('path') == '/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "service": "Bedrock AgentCore Proxy",
                    "bedrock_agentcore_arn": BEDROCK_AGENTCORE_ARN
                })
            }
        
        # Default response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": "Request processed"}]
                }
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing request: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "error": str(e),
                "message": "Internal server error"
            })
        }
