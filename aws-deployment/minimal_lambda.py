import json

def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    
    try:
        # Handle health check
        if event.get('httpMethod') == 'GET' and event.get('path') == '/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'timestamp': '2025-10-07T21:20:00Z',
                    'version': 'minimal-test'
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
                        'timestamp': '2025-10-07T21:20:00Z',
                        'tools_available': 2,
                        'bedrock_connected': True,
                        'version': 'minimal-test'
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
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'jsonrpc': '2.0',
                        'id': body.get('id'),
                        'result': result
                    })
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
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
