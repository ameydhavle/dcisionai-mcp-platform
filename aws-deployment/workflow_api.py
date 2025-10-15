#!/usr/bin/env python3
"""
Workflow API Integration for DcisionAI Platform
==============================================

API endpoints for predefined workflows that use the real optimization engine.
Integrates with existing 4-step optimization pipeline.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from workflow_templates import (
    get_workflows_for_industry, 
    get_workflow_details, 
    get_all_industries,
    get_workflow_summary
)

logger = logging.getLogger(__name__)

def handle_workflows_endpoint(path: str, method: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle workflow-related API endpoints."""
    
    # Parse the path to extract industry and workflow_id
    path_parts = path.strip('/').split('/')
    
    if len(path_parts) < 1 or path_parts[0] != 'workflows':
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
            },
            'body': json.dumps({
                "error": "Invalid workflow endpoint",
                "timestamp": datetime.now().isoformat()
            })
        }
    
    industry = path_parts[1] if len(path_parts) > 1 else None
    
    # GET /workflows - List all industries
    if method == 'GET' and len(path_parts) == 1:
        try:
            industries = get_all_industries()
            summary = get_workflow_summary()
            
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "industries": industries,
                "summary": summary,
                "total_industries": len(industries)
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                },
                'body': json.dumps(result)
            }
        except Exception as e:
            logger.error(f"Error getting industries: {str(e)}")
            return create_error_response(f"Error getting industries: {str(e)}")
    
    # GET /workflows/{industry} - Get workflows for specific industry
    elif method == 'GET' and len(path_parts) == 2 and industry:
        try:
            workflows = get_workflows_for_industry(industry)
            
            if not workflows:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                    },
                    'body': json.dumps({
                        "error": f"No workflows found for industry: {industry}",
                        "timestamp": datetime.now().isoformat()
                    })
                }
            
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "industry": industry,
                "workflows": workflows,
                "total_workflows": len(workflows)
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                },
                'body': json.dumps(result)
            }
        except Exception as e:
            logger.error(f"Error getting workflows for industry {industry}: {str(e)}")
            return create_error_response(f"Error getting workflows: {str(e)}")
    
    # GET /workflows/{industry}/{workflow_id} - Get workflow details
    elif method == 'GET' and len(path_parts) == 3:
        workflow_id = path_parts[2]
        try:
            workflow_details = get_workflow_details(industry, workflow_id)
            
            if not workflow_details:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                    },
                    'body': json.dumps({
                        "error": f"Workflow not found: {industry}/{workflow_id}",
                        "timestamp": datetime.now().isoformat()
                    })
                }
            
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "workflow": workflow_details
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                },
                'body': json.dumps(result)
            }
        except Exception as e:
            logger.error(f"Error getting workflow details {industry}/{workflow_id}: {str(e)}")
            return create_error_response(f"Error getting workflow details: {str(e)}")
    
    # POST /workflows/{industry}/{workflow_id}/execute - Execute workflow
    elif method == 'POST' and len(path_parts) == 4 and path_parts[3] == 'execute':
        workflow_id = path_parts[2]
        try:
            workflow_details = get_workflow_details(industry, workflow_id)
            
            if not workflow_details:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                    },
                    'body': json.dumps({
                        "error": f"Workflow not found: {industry}/{workflow_id}",
                        "timestamp": datetime.now().isoformat()
                    })
                }
            
            # Get custom parameters from request body (optional)
            custom_parameters = body.get('custom_parameters', {})
            
            # Execute the workflow using the real optimization pipeline
            result = execute_workflow(workflow_details, custom_parameters)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                },
                'body': json.dumps(result)
            }
        except Exception as e:
            logger.error(f"Error executing workflow {industry}/{workflow_id}: {str(e)}")
            return create_error_response(f"Error executing workflow: {str(e)}")
    
    else:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
            },
            'body': json.dumps({
                "error": "Invalid workflow endpoint or method",
                "timestamp": datetime.now().isoformat()
            })
        }

def execute_workflow(workflow_details: Dict[str, Any], custom_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a workflow using the real optimization pipeline.
    
    This function integrates with the existing 4-step optimization process:
    1. Intent Classification
    2. Data Analysis  
    3. Model Building
    4. Optimization Solving
    """
    try:
        # Import the existing optimization functions
        # These will be imported from the main lambda function
        from lambda_function import (
            classify_intent, 
            analyze_data, 
            build_model, 
            solve_optimization
        )
        
        logger.info(f"🚀 Executing workflow: {workflow_details['title']}")
        
        # Step 1: Intent Classification
        logger.info("🎯 Step 1: Intent Classification")
        intent_result = classify_intent(workflow_details['problem_description'])
        logger.info(f"✅ Intent classified: {intent_result.get('intent', 'unknown')}")
        
        # Step 2: Data Analysis
        logger.info("📊 Step 2: Data Analysis")
        data_result = analyze_data(
            workflow_details['problem_description'],
            intent_result
        )
        logger.info(f"✅ Data analyzed: {data_result.get('readiness_score', 0):.2%} readiness")
        
        # Step 3: Model Building
        logger.info("🏗️ Step 3: Model Building")
        model_result = build_model(
            workflow_details['problem_description'],
            intent_result,
            data_result
        )
        logger.info(f"✅ Model built: {model_result.get('model_type', 'unknown')}")
        
        # Step 4: Optimization Solving
        logger.info("🔧 Step 4: Optimization Solving")
        solver_result = solve_optimization(
            workflow_details['problem_description'],
            intent_result,
            model_result
        )
        logger.info(f"✅ Optimization solved: {solver_result.get('status', 'unknown')}")
        
        # Compile comprehensive result
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "workflow": {
                "id": workflow_details['id'],
                "title": workflow_details['title'],
                "description": workflow_details['description'],
                "industry": workflow_details['industry'],
                "category": workflow_details['category'],
                "difficulty": workflow_details['difficulty'],
                "estimated_time": workflow_details['estimated_time']
            },
            "optimization_pipeline": {
                "intent_classification": intent_result,
                "data_analysis": data_result,
                "model_building": model_result,
                "optimization_solution": solver_result
            },
            "custom_parameters": custom_parameters or {},
            "execution_summary": {
                "total_steps": 4,
                "completed_steps": 4,
                "success": True,
                "workflow_type": "predefined",
                "real_optimization": True
            }
        }
        
        logger.info(f"✅ Workflow execution completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "workflow": workflow_details,
            "error": str(e),
            "execution_summary": {
                "total_steps": 4,
                "completed_steps": 0,
                "success": False,
                "workflow_type": "predefined",
                "real_optimization": True
            }
        }

def create_error_response(error_message: str) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
        },
        'body': json.dumps({
            "status": "error",
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        })
    }
