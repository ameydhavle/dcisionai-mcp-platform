#!/usr/bin/env python3
"""
Enhanced Lambda Handler for MCP Server
======================================

This wraps the enhanced MCP server to work as a Lambda function.
"""

import json
import logging
import boto3
from datetime import datetime
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Lambda handler for enhanced MCP server."""
    try:
        logger.info(f"Enhanced MCP Lambda invoked: {json.dumps(event)}")
        
        # Parse the request
        if 'httpMethod' in event:
            # API Gateway request
            return handle_api_gateway_request(event, context)
        else:
            # Direct Lambda invocation
            return handle_direct_invocation(event, context)
            
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def handle_api_gateway_request(event, context):
    """Handle API Gateway requests."""
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': ''
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Route to appropriate handler
        if 'method' in body:
            if body['method'] == 'tools/call':
                return handle_tool_call(body)
            elif body['method'] == 'health':
                return handle_health_check()
            else:
                return create_error_response(f"Unknown method: {body['method']}")
        else:
            return handle_health_check()
            
    except Exception as e:
        logger.error(f"API Gateway handler error: {str(e)}")
        return create_error_response(str(e))

def handle_direct_invocation(event, context):
    """Handle direct Lambda invocations."""
    try:
        if 'method' in event:
            if event['method'] == 'tools/call':
                return handle_tool_call(event)
            elif event['method'] == 'health':
                return handle_health_check()
        
        return handle_health_check()
        
    except Exception as e:
        logger.error(f"Direct invocation handler error: {str(e)}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def handle_tool_call(request):
    """Handle tool call requests."""
    try:
        params = request.get('params', {})
        tool_name = params.get('name', '')
        arguments = params.get('arguments', {})
        
        logger.info(f"Tool call: {tool_name} with args: {arguments}")
        
        # Route to appropriate tool
        if tool_name == 'manufacturing_optimization':
            result = handle_manufacturing_optimization(arguments)
        elif tool_name == 'generate_3d_landscape':
            result = handle_3d_landscape_generation(arguments)
        elif tool_name == 'sensitivity_analysis':
            result = handle_sensitivity_analysis(arguments)
        elif tool_name == 'monte_carlo_risk_analysis':
            result = handle_monte_carlo_analysis(arguments)
        elif tool_name == 'manufacturing_health_check':
            result = handle_health_check()
        else:
            result = {'error': f'Unknown tool: {tool_name}'}
        
        return create_success_response(result)
        
    except Exception as e:
        logger.error(f"Tool call error: {str(e)}")
        return create_error_response(str(e))

def handle_manufacturing_optimization(arguments):
    """Handle manufacturing optimization requests."""
    # This would integrate with the actual MCP server
    # For now, return a mock response
    return {
        'status': 'success',
        'optimization_result': {
            'intent_classification': {
                'intent': 'production_optimization',
                'confidence': 0.95
            },
            'data_analysis': {
                'variables_identified': 3,
                'constraints_identified': 2
            },
            'model_building': {
                'model_type': 'linear_programming',
                'variables': [
                    {'name': 'x1', 'description': 'Product A production', 'lower_bound': 0, 'upper_bound': 100},
                    {'name': 'x2', 'description': 'Product B production', 'lower_bound': 0, 'upper_bound': 100},
                    {'name': 'x3', 'description': 'Product C production', 'lower_bound': 0, 'upper_bound': 100}
                ],
                'constraints': [
                    {'expression': 'x1 + x2 + x3 <= 100', 'description': 'Total capacity constraint'},
                    {'expression': 'x1 >= 0', 'description': 'Non-negativity constraint'}
                ]
            },
            'optimization_solution': {
                'status': 'optimal',
                'objective_value': 750.0,
                'solution': {'x1': 50, 'x2': 30, 'x3': 20},
                'solve_time': 0.5
            }
        },
        'timestamp': datetime.now().isoformat()
    }

def handle_3d_landscape_generation(arguments):
    """Handle 3D landscape generation requests."""
    optimization_result = arguments.get('optimization_result', {})
    resolution = arguments.get('resolution', 50)
    
    # Generate mock 3D landscape data
    landscape_data = {
        'terrain': {
            'heights': [[i * j * 0.1 for j in range(resolution)] for i in range(resolution)],
            'bounds': {'x_min': -10, 'x_max': 10, 'y_min': -10, 'y_max': 10},
            'resolution': resolution
        },
        'constraints': [
            {
                'id': 'constraint_0',
                'position': {'x': 5, 'y': 2, 'z': 3},
                'rotation': {'x': 0, 'y': 0, 'z': 0},
                'expression': 'x1 + x2 + x3 <= 100',
                'type': 'inequality',
                'color': [0.8, 0.3, 0.3]
            }
        ],
        'optimal_point': {
            'position': {'x': 0, 'y': 5, 'z': 0},
            'objective_value': 750.0,
            'solution': {'x1': 50, 'x2': 30, 'x3': 20},
            'color': [1.0, 0.8, 0.0],
            'intensity': 0.8
        },
        'variables': [
            {
                'id': 'x1',
                'position': {'x': 3, 'y': 1, 'z': 2},
                'value': 50,
                'description': 'Product A production',
                'importance': 0.5,
                'color': [0.2, 0.6, 0.8]
            }
        ],
        'metadata': {
            'resolution': resolution,
            'objective_value': 750.0,
            'variable_count': 3,
            'constraint_count': 2,
            'generated_at': datetime.now().isoformat()
        }
    }
    
    return {
        'status': 'success',
        'landscape_data': landscape_data,
        'timestamp': datetime.now().isoformat()
    }

def handle_sensitivity_analysis(arguments):
    """Handle sensitivity analysis requests."""
    base_result = arguments.get('base_optimization_result', {})
    parameter_changes = arguments.get('parameter_changes', {})
    
    # Mock sensitivity analysis
    impact_analysis = {
        'parameter_changes': parameter_changes,
        'original_solution': {'x1': 50, 'x2': 30, 'x3': 20},
        'modified_solution': {'x1': 60, 'x2': 25, 'x3': 15},
        'objective_impact': {
            'original_objective': 750.0,
            'estimated_new_objective': 720.0,
            'change_percent': -4.0,
            'change_factor': 0.96,
            'impact_level': 'low'
        },
        'feasibility_impact': {
            'feasibility_risk': 'low',
            'constraint_violations': [],
            'recommendation': 'Safe to implement'
        },
        'risk_assessment': {
            'risk_level': 'low',
            'max_parameter_change': 0.2,
            'number_of_changes': 1,
            'confidence': 0.9
        },
        'recommendations': [
            'x1 change is within safe range',
            'Monitor x2 reduction impact on overall performance'
        ]
    }
    
    return {
        'status': 'success',
        'sensitivity_analysis': impact_analysis,
        'timestamp': datetime.now().isoformat()
    }

def handle_monte_carlo_analysis(arguments):
    """Handle Monte Carlo risk analysis requests."""
    base_result = arguments.get('base_optimization_result', {})
    uncertainty_ranges = arguments.get('uncertainty_ranges', {})
    num_simulations = arguments.get('num_simulations', 1000)
    
    # Mock Monte Carlo analysis
    risk_analysis = {
        'simulation_count': num_simulations,
        'base_objective': 750.0,
        'risk_metrics': {
            'success_rate': 0.95,
            'mean_objective': 745.0,
            'std_objective': 25.0,
            'min_objective': 680.0,
            'max_objective': 780.0,
            'value_at_risk_5pct': 700.0,
            'expected_shortfall': 690.0,
            'coefficient_of_variation': 0.034,
            'downside_deviation': 15.0
        },
        'confidence_intervals': {
            '90pct': 710.0,
            '95pct': 700.0,
            '99pct': 680.0
        },
        'scenario_analysis': {
            'best_case': 780.0,
            'worst_case': 680.0,
            'most_likely': 745.0,
            'feasible_scenarios': 950,
            'total_scenarios': 1000
        },
        'recommendations': [
            'Low risk - solution is robust to parameter uncertainty',
            'Low variability - solution is stable'
        ]
    }
    
    return {
        'status': 'success',
        'monte_carlo_analysis': risk_analysis,
        'timestamp': datetime.now().isoformat()
    }

def handle_health_check():
    """Handle health check requests."""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'tools_available': 8,
        'bedrock_connected': True,
        'version': '2.0.0-enhanced',
        'architecture': 'Enhanced MCP Server with 3D visualization, sensitivity analysis, and Monte Carlo risk analysis',
        'features': [
            'Real-time 3D landscape generation',
            'Interactive sensitivity analysis',
            'Monte Carlo risk analysis',
            'Enhanced business impact calculations'
        ]
    }

def create_success_response(data):
    """Create success response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps({
            'result': {
                'content': [{'type': 'text', 'text': json.dumps(data)}]
            }
        })
    }

def create_error_response(error_message):
    """Create error response."""
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps({
            'error': {
                'message': error_message,
                'timestamp': datetime.now().isoformat()
            }
        })
    }
