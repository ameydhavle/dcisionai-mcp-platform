#!/usr/bin/env python3
"""
Simple Test Lambda Function for DcisionAI Manufacturing Optimizer
================================================================

This is a minimal Lambda function to test basic functionality.
"""

import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Simple Lambda handler for testing."""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle health check
        if event.get('httpMethod') == 'GET' and event.get('path') == '/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'timestamp': '2025-10-07T21:15:00Z',
                    'tools_available': 2,
                    'bedrock_connected': True,
                    'version': '1.0.0-test',
                    'architecture': 'simple-test'
                })
            }
        
        # Handle MCP requests
        if event.get('httpMethod') == 'POST' and event.get('path') == '/mcp':
            body = json.loads(event.get('body', '{}'))
            
            if body.get('method') == 'tools/call':
                tool_name = body.get('params', {}).get('name')
                
                if tool_name == 'manufacturing_health_check':
                    result = {
                        'status': 'healthy',
                        'timestamp': '2025-10-07T21:15:00Z',
                        'tools_available': 2,
                        'bedrock_connected': True,
                        'version': '1.0.0-test',
                        'architecture': 'simple-test'
                    }
                elif tool_name == 'manufacturing_optimize':
                    result = {
                        'intent_classification': {
                            'intent': 'production_optimization',
                            'confidence': 0.9
                        },
                        'data_analysis': {
                            'entities': [],
                            'readiness': 0.8
                        },
                        'model_building': {
                            'model_type': 'linear_programming',
                            'variables': 5
                        },
                        'optimization_solution': {
                            'status': 'optimal',
                            'objective_value': 100.0
                        },
                        'performance_metrics': {
                            'total_execution_time': 1000,
                            'success': True,
                            'agent_count': 4
                        }
                    }
                else:
                    result = {'error': f'Unknown tool: {tool_name}'}
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                    },
                    'body': json.dumps({
                        'jsonrpc': '2.0',
                        'id': body.get('id'),
                        'result': result
                    })
                }
        
        # Handle OPTIONS requests for CORS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': ''
            }
        
        # Default response
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Not found'})
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
