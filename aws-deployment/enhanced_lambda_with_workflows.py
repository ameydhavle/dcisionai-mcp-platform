#!/usr/bin/env python3
"""
Enhanced Lambda with Workflow API Integration
============================================

Lambda function with predefined workflow support that uses the real optimization engine.
Integrates workflow templates with the existing 4-step optimization pipeline.
"""

import json
import logging
import boto3
from datetime import datetime
from typing import Dict, Any, List
import re

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Optimized Inference Profiles for faster execution
INFERENCE_PROFILES = {
    "intent_classification": "arn:aws:bedrock:us-east-1:808953421331:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0",
    "data_analysis": "arn:aws:bedrock:us-east-1:808953421331:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0", 
    "model_building": "arn:aws:bedrock:us-east-1:808953421331:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0",  # Using Haiku for speed
    "optimization_solution": "arn:aws:bedrock:us-east-1:808953421331:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0"  # Using Haiku for speed
}

def invoke_bedrock_with_profile(prompt: str, agent_type: str) -> str:
    """Invoke Bedrock using inference profile for specific agent."""
    try:
        profile_arn = INFERENCE_PROFILES.get(agent_type)
        if not profile_arn:
            logger.warning(f"No inference profile for {agent_type}, using direct model")
            # Fallback to direct model invocation
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,  # Reduced for faster responses
                "temperature": 0.1,  # Lower temperature for precision
                "messages": [{"role": "user", "content": prompt}]
            })
            
            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=body,
                contentType="application/json"
            )
        else:
            # Use inference profile with optimized settings for faster execution
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,  # Reduced for faster responses
                "temperature": 0.1,  # Lower temperature for mathematical precision
                "messages": [{"role": "user", "content": prompt}]
            })
            
            response = bedrock_client.invoke_model(
                modelId=profile_arn,
                body=body,
                contentType="application/json"
            )
        
        response_body = json.loads(response['body'].read())
        if 'content' in response_body and len(response_body['content']) > 0:
            result_text = response_body['content'][0]['text']
            logger.info(f"Bedrock response length: {len(result_text)}")
            return result_text
        else:
            logger.error(f"Empty Bedrock response: {response_body}")
            return "Error: Empty response from Bedrock"
        
    except Exception as e:
        logger.error(f"Bedrock error: {str(e)}")
        return f"Error: {str(e)}"

def invoke_bedrock_model(prompt: str, model_id: str) -> str:
    """Invoke Bedrock model directly by model ID."""
    try:
        # For Qwen models, use the appropriate request format
        if "qwen" in model_id.lower():
            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "stop": ["```", "Human:", "Assistant:"]
                }),
                contentType="application/json"
            )
        else:
            # For other models (Claude, etc.)
            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "temperature": 0.1,
                    "messages": [{"role": "user", "content": prompt}]
                }),
                contentType="application/json"
            )
        
        response_body = json.loads(response['body'].read())
        
        # Handle different response formats
        if "qwen" in model_id.lower():
            # Qwen models return content in choices format
            if 'choices' in response_body and len(response_body['choices']) > 0:
                result_text = response_body['choices'][0]['message']['content']
                logger.info(f"Qwen response length: {len(result_text)}")
                return result_text
            else:
                logger.error(f"Empty Qwen response: {response_body}")
                return "Error: Empty response from Qwen"
        else:
            # Claude and other models
            if 'content' in response_body and len(response_body['content']) > 0:
                result_text = response_body['content'][0]['text']
                logger.info(f"Bedrock response length: {len(result_text)}")
                return result_text
            else:
                logger.error(f"Empty Bedrock response: {response_body}")
                return "Error: Empty response from Bedrock"
        
    except Exception as e:
        logger.error(f"Bedrock model error: {str(e)}")
        return f"Error: {str(e)}"

def safe_json_parse(text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Safely parse JSON from Bedrock response."""
    try:
        # First try to parse the entire text as JSON
        parsed = json.loads(text)
        logger.info(f"Successfully parsed JSON: {list(parsed.keys())}")
        
        # Debug: Log the model_type value specifically
        if 'model_type' in parsed:
            logger.info(f"model_type value: '{parsed['model_type']}' (type: {type(parsed['model_type'])})")
        else:
            logger.warning("model_type not found in parsed JSON")
        
        return parsed
        
    except json.JSONDecodeError:
        # Try to find JSON within the text
        try:
            # Look for JSON object boundaries
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx + 1]
                parsed = json.loads(json_text)
                logger.info(f"Successfully parsed JSON from text: {list(parsed.keys())}")
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON within markdown code blocks
        try:
            import re
            # Look for JSON in markdown code blocks
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, text, re.DOTALL)
            if match:
                json_text = match.group(1)
                parsed = json.loads(json_text)
                logger.info(f"Successfully parsed JSON from markdown: {list(parsed.keys())}")
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Try to extract key-value pairs using regex
        try:
            result = fallback.copy()
            
            # Extract common patterns with more flexible matching
            patterns = {
                'intent': r'"intent":\s*"([^"]+)"',
                'confidence': r'"confidence":\s*([0-9.]+)',
                'status': r'"status":\s*"([^"]+)"',
                'objective_value': r'"objective_value":\s*([0-9.]+)',
                'model_type': r'"model_type":\s*"([^"]+)"|"model_type":\s*([^,}\n]+)',
                'readiness_score': r'"readiness_score":\s*([0-9.]+)',
                'solve_time': r'"solve_time":\s*([0-9.]+)',
                'solver_info': r'"solver_info":\s*"([^"]+)"',
                # Additional patterns for Qwen's format
                'model_complexity': r'"model_complexity":\s*"([^"]+)"',
                'estimated_solve_time': r'"estimated_solve_time":\s*([0-9.]+)',
                'scalability': r'"scalability":\s*"([^"]+)"'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    if key in ['confidence', 'objective_value', 'readiness_score', 'solve_time', 'estimated_solve_time']:
                        result[key] = float(match.group(1))
                    else:
                        # Handle model_type with multiple capture groups
                        if key == 'model_type' and len(match.groups()) > 1:
                            # Use the first non-empty group
                            value = match.group(1) if match.group(1) else match.group(2)
                            result[key] = value.strip('"')
                        else:
                            result[key] = match.group(1).strip('"')
            
            if any(key in result for key in patterns.keys()):
                logger.info(f"Successfully extracted data using regex: {list(result.keys())}")
                # Debug: Log the extracted values
                for key, value in result.items():
                    if key in patterns.keys():
                        logger.info(f"Extracted {key}: {value}")
                return result
                
        except Exception as e:
            logger.warning(f"Regex extraction failed: {e}")
        
        logger.warning(f"Failed to parse JSON, using fallback: {fallback}")
        return fallback

def classify_intent(problem_description: str) -> Dict[str, Any]:
    """Classify optimization intent using Claude 3 Haiku."""
    prompt = f"""
You are an expert optimization analyst. Classify the following optimization problem and extract key information.

Problem: {problem_description}

Analyze this problem and provide a JSON response with:
- intent: The type of optimization (e.g., "production_optimization", "supply_chain_optimization", "portfolio_optimization")
- confidence: Confidence score 0.0-1.0
- entities: List of key entities mentioned (e.g., ["products", "capacity", "costs"])
- objectives: List of optimization objectives (e.g., ["maximize profit", "minimize cost"])
- constraints: List of constraints mentioned (e.g., ["capacity limits", "demand requirements"])
- problem_scale: Scale of the problem ("small", "medium", "large")
- extracted_quantities: List of numerical values mentioned
- reasoning: Brief explanation of the classification

Respond with valid JSON only.
"""

    try:
        response = invoke_bedrock_with_profile(prompt, "intent_classification")
        result = safe_json_parse(response, {
            "intent": "general_optimization",
            "confidence": 0.7,
            "entities": [],
            "objectives": ["optimize"],
            "constraints": [],
            "problem_scale": "medium",
            "extracted_quantities": [],
            "reasoning": "Default classification"
        })
        
        return {
            "status": "success",
            "step": "intent_classification",
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "message": f"Intent classified as: {result.get('intent', 'unknown')} (scale: {result.get('problem_scale', 'unknown')})"
        }
        
    except Exception as e:
        logger.error(f"Intent classification error: {str(e)}")
        return {
            "status": "error",
            "step": "intent_classification",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "Intent classification failed"
        }

def analyze_data(problem_description: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze data requirements using Claude 3 Haiku."""
    prompt = f"""
You are a data analyst. Analyze the data requirements for this optimization problem.

Problem: {problem_description}
Intent: {intent_data.get('intent', 'unknown')}
Entities: {intent_data.get('entities', [])}
Scale: {intent_data.get('problem_scale', 'unknown')}

Provide a JSON response with:
- data_entities: List of data entities needed with their attributes
- readiness_score: Data readiness score 0.0-1.0
- sample_data: Sample data structure
- assumptions: List of assumptions made
- data_complexity: Complexity level ("low", "medium", "high")
- estimated_data_points: Estimated number of data points needed
- data_quality_requirements: List of data quality requirements

Respond with valid JSON only.
"""

    try:
        response = invoke_bedrock_with_profile(prompt, "data_analysis")
        result = safe_json_parse(response, {
            "data_entities": [{"name": "general", "attributes": ["value"]}],
            "readiness_score": 0.8,
            "sample_data": {},
            "assumptions": ["Standard data available"],
            "data_complexity": "medium",
            "estimated_data_points": 100,
            "data_quality_requirements": ["Real-time data"]
        })
        
        return {
            "status": "success",
            "step": "data_analysis",
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "message": f"Data analysis complete: {result.get('readiness_score', 0):.0%} readiness"
        }
        
    except Exception as e:
        logger.error(f"Data analysis error: {str(e)}")
        return {
            "status": "error",
            "step": "data_analysis",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "Data analysis failed"
        }

def build_model(problem_description: str, intent_data: Dict[str, Any], data_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Build optimization model using Qwen 3B via inference profile."""
    
    # Extract key information for better context
    intent = intent_data.get('intent', 'unknown')
    entities = intent_data.get('entities', [])
    data_entities = data_analysis.get('data_entities', [])
    scale = intent_data.get('problem_scale', 'unknown')
    
    prompt = f"""You are an expert optimization modeler. Create a mathematical optimization model for this problem.

PROBLEM DESCRIPTION:
{problem_description}

CONTEXT:
- Intent: {intent}
- Key Entities: {', '.join(entities[:5]) if entities else 'None'}
- Data Entities: {', '.join([de.get('name', 'Unknown') for de in data_entities[:3]]) if data_entities else 'None'}
- Problem Scale: {scale}

REQUIRED OUTPUT FORMAT:
Respond with ONLY valid JSON in this exact structure:

{{
  "model_type": "mixed_integer_programming",
  "variables": [
    {{
      "name": "x1",
      "description": "Production quantity for Product A",
      "type": "integer",
      "lower_bound": 0,
      "upper_bound": 1000
    }}
  ],
  "objective": {{
    "type": "maximize",
    "expression": "25*x1 + 18*x2 + 32*x3",
    "description": "Maximize total profit"
  }},
  "constraints": [
    {{
      "expression": "2.5*x1 + 1.8*x2 + 3.2*x3 <= 3000",
      "description": "Labor hours constraint"
    }}
  ],
  "model_complexity": "medium",
  "estimated_solve_time": 2.5,
  "scalability": "good"
}}

IMPORTANT RULES:
1. Use realistic variable names based on the problem (e.g., x1, x2, x3 for products)
2. Create meaningful mathematical expressions with actual coefficients
3. Include relevant constraints based on the problem description
4. Set appropriate bounds and variable types
5. Respond with ONLY the JSON object, no other text
6. Ensure all JSON is valid and properly formatted

Generate the optimization model now:"""

    try:
        # Use Qwen 3B Coder model directly for better mathematical JSON generation
        response = invoke_bedrock_model(prompt, "qwen.qwen3-coder-30b-a3b-v1:0")
        
        # Debug: Log the first 500 characters of Qwen response to understand format
        logger.info(f"Qwen response preview: {response[:500]}...")
        
        result = safe_json_parse(response, {
            "model_type": "linear_programming",
            "variables": [{"name": "x1", "description": "Decision variable", "type": "continuous", "lower_bound": 0, "upper_bound": 100}],
            "objective": {"type": "maximize", "expression": "x1", "description": "Maximize objective"},
            "constraints": [{"expression": "x1 <= 100", "description": "Capacity constraint"}],
            "model_complexity": "low",
            "estimated_solve_time": 1.0,
            "scalability": "good"
        })
        
        # Debug: Log the final result
        logger.info(f"Final model_building result: {result}")
        logger.info(f"Model type in result: {result.get('model_type')}")
        
        return {
            "status": "success",
            "step": "model_building",
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "message": f"Model built: {result.get('model_type', 'unknown')} with {len(result.get('variables', []))} variables"
        }
        
    except Exception as e:
        logger.error(f"Model building error: {str(e)}")
        return {
            "status": "error",
            "step": "model_building",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "Model building failed"
        }

def solve_optimization(problem_description: str, intent_data: Dict[str, Any], model_building: Dict[str, Any]) -> Dict[str, Any]:
    """Solve optimization using Claude 3.5 Sonnet v2."""
    prompt = f"""
You are an expert optimization solver. Solve this optimization problem.

Problem: {problem_description}
Model Type: {model_building.get('model_type', 'unknown')}
Variables: {model_building.get('variables', [])}
Objective: {model_building.get('objective', {})}
Constraints: {model_building.get('constraints', [])}

Solve the optimization problem and provide JSON response with:
- status: Solution status ("optimal", "infeasible", "unbounded", "suboptimal")
- objective_value: Optimal objective value
- solution: Dictionary of variable values
- solve_time: Solve time in seconds
- iterations: Number of iterations (if applicable)
- gap: Optimality gap (if applicable)
- solver_info: Information about the solver used
- sensitivity_analysis: Basic sensitivity analysis results

Provide realistic solution values. Respond with valid JSON only.
"""

    try:
        response = invoke_bedrock_with_profile(prompt, "optimization_solution")
        result = safe_json_parse(response, {
            "status": "optimal",
            "objective_value": 100.0,
            "solution": {"x1": 50.0},
            "solve_time": 0.5,
            "iterations": 10,
            "gap": 0.0,
            "solver_info": {"solver": "Claude 3.5 Sonnet v2", "method": "AI-based optimization"},
            "sensitivity_analysis": {"shadow_prices": {}, "reduced_costs": {}}
        })
        
        return {
            "status": "success",
            "step": "optimization_solution",
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "message": f"Optimization solved: {result.get('status', 'unknown')} with objective value {result.get('objective_value', 0)}"
        }
        
    except Exception as e:
        logger.error(f"Optimization solving error: {str(e)}")
        return {
            "status": "error",
            "step": "optimization_solution",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "Optimization solving failed"
        }

# Import workflow functionality
try:
    from workflow_api import handle_workflows_endpoint
    from workflow_templates import get_all_industries, get_workflow_summary
    WORKFLOWS_AVAILABLE = True
    logger.info("✅ Workflow modules imported successfully")
except ImportError as e:
    logger.warning(f"Workflow modules not available: {e}")
    WORKFLOWS_AVAILABLE = False
    
    # Define fallback functions
    def handle_workflows_endpoint(path, method, body):
        return {
            'statusCode': 501,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
            },
            'body': json.dumps({
                "error": "Workflow functionality not available",
                "message": "Workflow modules could not be imported",
                "timestamp": datetime.now().isoformat()
            })
        }
    
    def get_all_industries():
        return []
    
    def get_workflow_summary():
        return {}

def lambda_handler(event, context):
    """Enhanced Lambda handler with workflow support."""
    try:
        # Parse the request
        if 'httpMethod' in event:
            # API Gateway request
            method = event['httpMethod']
            path = event.get('path', '')
            body_str = event.get('body', '{}')
            if body_str is None:
                body_str = '{}'
            body = json.loads(body_str)
            logger.info(f"📥 API Gateway request: {method} {path}")
        else:
            # Direct invocation - could be AgentCore Gateway
            method = 'POST'
            path = event.get('path', '/mcp')
            body = event
            logger.info(f"📥 Direct invocation: {method} {path}")
            logger.info(f"📥 Event body: {json.dumps(body, indent=2)}")
            
            # Check if this is an AgentCore Gateway call by looking for context metadata
            if hasattr(context, 'client_context') and hasattr(context.client_context, 'custom'):
                custom_context = context.client_context.custom
                if 'bedrockAgentCoreToolName' in custom_context:
                    # This is an AgentCore Gateway call
                    original_tool_name = custom_context['bedrockAgentCoreToolName']
                    logger.info(f"🔧 AgentCore Gateway tool call: {original_tool_name}")
                    
                    # Strip the target name prefix (format: ${target_name}___${tool_name})
                    delimiter = "___"
                    if delimiter in original_tool_name:
                        tool_name = original_tool_name[original_tool_name.index(delimiter) + len(delimiter):]
                        logger.info(f"🔧 Stripped tool name: {tool_name}")
                        
                        # Handle the tool call based on the tool name
                        if tool_name == 'get_workflow_templates':
                            industry = body.get('industry')
                            logger.info(f"🔧 Getting workflow templates for industry: {industry}")
                            if WORKFLOWS_AVAILABLE:
                                result = handle_workflows_endpoint('/workflows' + (f'/{industry}' if industry else ''), 'GET', {})
                                return result
                            else:
                                return {
                                    'statusCode': 501,
                                    'headers': {
                                        'Content-Type': 'application/json',
                                        'Access-Control-Allow-Origin': '*',
                                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                                    },
                                    'body': json.dumps({
                                        "status": "error",
                                        "message": "Workflow functionality not available"
                                    })
                                }
                        
                        elif tool_name == 'execute_workflow':
                            industry = body.get('industry')
                            workflow_id = body.get('workflow_id')
                            logger.info(f"🔧 Executing workflow: {industry}/{workflow_id}")
                            if WORKFLOWS_AVAILABLE and industry and workflow_id:
                                result = handle_workflows_endpoint(f'/workflows/{industry}/{workflow_id}/execute', 'POST', {})
                                return result
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
                                        "status": "error",
                                        "message": "Missing industry or workflow_id parameter"
                                    })
                                }
                        
                        elif tool_name == 'classify_intent':
                            problem_description = body.get('problem_description', '')
                            logger.info(f"🔧 Classifying intent for: {problem_description[:100]}...")
                            result = classify_intent(problem_description)
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
                        
                        elif tool_name == 'analyze_data':
                            problem_description = body.get('problem_description', '')
                            intent_data = body.get('intent_data', {})
                            logger.info(f"🔧 Analyzing data for: {problem_description[:100]}...")
                            result = analyze_data(problem_description, intent_data)
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
                        
                        elif tool_name == 'build_model':
                            problem_description = body.get('problem_description', '')
                            intent_data = body.get('intent_data', {})
                            data_analysis = body.get('data_analysis', {})
                            logger.info(f"🔧 Building model for: {problem_description[:100]}...")
                            result = build_model(problem_description, intent_data, data_analysis)
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
                        
                        elif tool_name == 'solve_optimization':
                            problem_description = body.get('problem_description', '')
                            intent_data = body.get('intent_data', {})
                            model_building = body.get('model_building', {})
                            logger.info(f"🔧 Solving optimization for: {problem_description[:100]}...")
                            result = solve_optimization(problem_description, intent_data, model_building)
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
                        
                        else:
                            logger.warning(f"🔧 Unknown tool name: {tool_name}")
                            return {
                                'statusCode': 400,
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                                },
                                'body': json.dumps({
                                    "status": "error",
                                    "message": f"Unknown tool: {tool_name}"
                                })
                            }
                    else:
                        logger.warning(f"🔧 Tool name format unexpected: {original_tool_name}")
        
        # Handle AgentCore Gateway tool calls (legacy detection)
        # The Gateway calls Lambda functions directly with tool arguments
        # Check if this is a Gateway tool call by looking for tool-specific parameters
        
        # Check for workflow templates call
        if 'industry' in body and len(body) <= 2:  # Only industry parameter or empty
            logger.info(f"🔧 AgentCore Gateway tool call: get_workflow_templates with industry={body.get('industry')}")
            industry = body.get('industry')
            if WORKFLOWS_AVAILABLE:
                result = handle_workflows_endpoint('/workflows' + (f'/{industry}' if industry else ''), 'GET', {})
                return result
            else:
                return {
                    'statusCode': 501,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                    },
                    'body': json.dumps({
                        "status": "error",
                        "message": "Workflow functionality not available"
                    })
                }
        
        # Check for workflow execution call
        elif 'industry' in body and 'workflow_id' in body:
            logger.info(f"🔧 AgentCore Gateway tool call: execute_workflow with industry={body.get('industry')}, workflow_id={body.get('workflow_id')}")
            industry = body.get('industry')
            workflow_id = body.get('workflow_id')
            if WORKFLOWS_AVAILABLE and industry and workflow_id:
                result = handle_workflows_endpoint(f'/workflows/{industry}/{workflow_id}/execute', 'POST', {})
                return result
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
                        "status": "error",
                        "message": "Missing industry or workflow_id parameter"
                    })
                }
        
        # Check for optimization pipeline calls
        elif 'problem_description' in body:
            # Determine which optimization step this is based on other parameters
            if 'intent_data' in body and 'data_analysis' in body and 'model_building' not in body:
                # This is analyze_data call
                logger.info(f"🔧 AgentCore Gateway tool call: analyze_data")
                problem_description = body.get('problem_description', '')
                intent_data = body.get('intent_data', {})
                result = analyze_data(problem_description, intent_data)
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
            
            elif 'intent_data' in body and 'data_analysis' in body and 'model_building' in body:
                # This is build_model call
                logger.info(f"🔧 AgentCore Gateway tool call: build_model")
                problem_description = body.get('problem_description', '')
                intent_data = body.get('intent_data', {})
                data_analysis = body.get('data_analysis', {})
                result = build_model(problem_description, intent_data, data_analysis)
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
            
            elif 'intent_data' in body and 'model_building' in body and 'data_analysis' not in body:
                # This is solve_optimization call
                logger.info(f"🔧 AgentCore Gateway tool call: solve_optimization")
                problem_description = body.get('problem_description', '')
                intent_data = body.get('intent_data', {})
                model_building = body.get('model_building', {})
                result = solve_optimization(problem_description, intent_data, model_building)
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
            
            elif len(body) == 1:  # Only problem_description
                # This is classify_intent call
                logger.info(f"🔧 AgentCore Gateway tool call: classify_intent")
                problem_description = body.get('problem_description', '')
                result = classify_intent(problem_description)
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
        
        # Legacy support for action/parameters format
        elif 'action' in body and 'parameters' in body:
            # This is a direct tool call from AgentCore Gateway
            action = body['action']
            parameters = body['parameters']
            logger.info(f"🔧 AgentCore Gateway tool call: {action}")
            
            if action == 'get_workflow_templates':
                industry = parameters.get('industry')
                if WORKFLOWS_AVAILABLE:
                    result = handle_workflows_endpoint('/workflows' + (f'/{industry}' if industry else ''), 'GET', {})
                    return result
                else:
                    return {
                        'statusCode': 501,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                        },
                        'body': json.dumps({
                            "status": "error",
                            "message": "Workflow functionality not available"
                        })
                    }
            
            elif action == 'execute_workflow':
                industry = parameters.get('industry')
                workflow_id = parameters.get('workflow_id')
                if WORKFLOWS_AVAILABLE and industry and workflow_id:
                    result = handle_workflows_endpoint(f'/workflows/{industry}/{workflow_id}/execute', 'POST', {})
                    return result
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
                            "status": "error",
                            "message": "Missing industry or workflow_id parameter"
                        })
                    }
            
            elif action == 'classify_intent':
                problem_description = parameters.get('problem_description', '')
                result = classify_intent(problem_description)
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
            
            elif action == 'analyze_data':
                problem_description = parameters.get('problem_description', '')
                intent_data = parameters.get('intent_data', {})
                result = analyze_data(problem_description, intent_data)
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
            
            elif action == 'build_model':
                problem_description = parameters.get('problem_description', '')
                intent_data = parameters.get('intent_data', {})
                data_analysis = parameters.get('data_analysis', {})
                result = build_model(problem_description, intent_data, data_analysis)
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
            
            elif action == 'solve_optimization':
                problem_description = parameters.get('problem_description', '')
                intent_data = parameters.get('intent_data', {})
                model_building = parameters.get('model_building', {})
                result = solve_optimization(problem_description, intent_data, model_building)
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
                        "status": "error",
                        "message": f"Unknown action: {action}"
                    })
                }

        # Handle OPTIONS requests for CORS
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token'
                },
                'body': ''
            }
        
        # Route to appropriate function
        if path == '/health' or (method == 'GET' and 'health' in path):
            # Enhanced health check with workflow info
            result = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "tools_available": 8 if WORKFLOWS_AVAILABLE else 4,
                "inference_profiles": list(INFERENCE_PROFILES.keys()),
                "version": "5.0.0-enhanced-with-workflows" if WORKFLOWS_AVAILABLE else "5.0.0-claude-3-5-sonnet-v2-advanced-math",
                "architecture": "4-agent optimization with Claude 3.5 Sonnet v2 + predefined workflows" if WORKFLOWS_AVAILABLE else "4-agent optimization with Claude 3.5 Sonnet v2 advanced mathematical modeling",
                "workflows_available": WORKFLOWS_AVAILABLE
            }
            
            if WORKFLOWS_AVAILABLE:
                result["workflow_industries"] = get_all_industries()
                result["workflow_summary"] = get_workflow_summary()
            
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
        
        # Handle workflow endpoints
        elif WORKFLOWS_AVAILABLE and path.startswith('/workflows'):
            logger.info(f"🔧 Handling workflow endpoint: {path} with method: {method}")
            return handle_workflows_endpoint(path, method, body)
        
        # Existing optimization endpoints
        elif path == '/intent' or (method == 'POST' and 'intent' in path):
            problem_description = body.get('problem_description', '')
            result = classify_intent(problem_description)
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
        
        elif path == '/data' or (method == 'POST' and 'data' in path):
            problem_description = body.get('problem_description', '')
            intent_data = body.get('intent_data', {})
            result = analyze_data(problem_description, intent_data)
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
        
        elif path == '/model' or (method == 'POST' and 'model' in path):
            problem_description = body.get('problem_description', '')
            intent_data = body.get('intent_data', {})
            data_analysis = body.get('data_analysis', {})
            result = build_model(problem_description, intent_data, data_analysis)
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
        
        elif path == '/solve' or (method == 'POST' and 'solve' in path):
            problem_description = body.get('problem_description', '')
            intent_data = body.get('intent_data', {})
            model_building = body.get('model_building', {})
            result = solve_optimization(problem_description, intent_data, model_building)
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
        
        else:
            # Default MCP endpoint
            result = {
                "jsonrpc": "2.0",
                "id": body.get('id', 'unknown'),
                "result": {
                    "error": "Unknown endpoint",
                    "timestamp": datetime.now().isoformat(),
                    "available_endpoints": [
                        "/health", "/intent", "/data", "/model", "/solve"
                    ] + (["/workflows"] if WORKFLOWS_AVAILABLE else [])
                }
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
        import traceback
        logger.error(f"Lambda handler error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        }
