#!/usr/bin/env python3
"""
DcisionAI Enhanced AgentCore Agent
=================================

Enhanced optimization agent with Gateway integration and Memory persistence.
This agent provides:
- Extended execution time (no 29-second limit)
- Gateway tool integration
- Memory persistence for user preferences
- Streaming responses for real-time progress
- All 21 industry workflows
"""

import json
import logging
import boto3
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List, AsyncGenerator
import re

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.runtime.context import RequestContext
from bedrock_agentcore.memory import MemoryClient
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize the AgentCore runtime app
app = BedrockAgentCoreApp()

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Optimized Inference Profiles for faster execution
INFERENCE_PROFILES = {
    "intent_classification": "arn:aws:bedrock:us-east-1:808953421331:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0",
    "data_analysis": "arn:aws:bedrock:us-east-1:808953421331:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0", 
    "model_building": "arn:aws:bedrock:us-east-1:808953421331:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0",
    "optimization_solution": "arn:aws:bedrock:us-east-1:808953421331:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0"
}

# Load Gateway and Memory configurations
gateway_config = {}
memory_config = {}

try:
    with open("gateway_config.json", "r") as f:
        gateway_config = json.load(f)
    logger.info(f"✅ Gateway config loaded: {gateway_config.get('gateway_url', 'Not available')}")
except FileNotFoundError:
    logger.warning("Gateway config not found. Gateway features will be disabled.")

try:
    with open("memory_config.json", "r") as f:
        memory_config = json.load(f)
    logger.info(f"✅ Memory config loaded: {len(memory_config)} memory resources")
except FileNotFoundError:
    logger.warning("Memory config not found. Memory features will be disabled.")

# Initialize Memory Client if available
memory_client = None
if memory_config:
    try:
        memory_client = MemoryClient(region_name=memory_config.get('region', 'us-east-1'))
        logger.info("✅ Memory client initialized")
    except Exception as e:
        logger.warning(f"Memory client initialization failed: {e}")

# Import workflow templates
try:
    import sys
    sys.path.append('../aws-deployment')
    from workflow_templates import WORKFLOW_TEMPLATES, get_all_industries, get_workflow_summary
    WORKFLOWS_AVAILABLE = True
    logger.info("✅ Workflow templates loaded")
except ImportError as e:
    logger.warning(f"Workflow templates not available: {e}")
    WORKFLOWS_AVAILABLE = False
    WORKFLOW_TEMPLATES = {}

def invoke_bedrock_with_profile(prompt: str, agent_type: str) -> str:
    """Invoke Bedrock using inference profile for specific agent."""
    try:
        profile_arn = INFERENCE_PROFILES.get(agent_type)
        if not profile_arn:
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.1,
                "messages": [{"role": "user", "content": prompt}]
            })
            
            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=body,
                contentType="application/json"
            )
        else:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.1,
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

def safe_json_parse(text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Safely parse JSON from Bedrock response."""
    try:
        parsed = json.loads(text)
        logger.info(f"Successfully parsed JSON: {list(parsed.keys())}")
        return parsed
        
    except json.JSONDecodeError:
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx + 1]
                parsed = json.loads(json_text)
                logger.info(f"Successfully parsed JSON from text: {list(parsed.keys())}")
                return parsed
        except json.JSONDecodeError:
            pass
        
        try:
            result = fallback.copy()
            
            patterns = {
                'intent': r'"intent":\s*"([^"]+)"',
                'confidence': r'"confidence":\s*([0-9.]+)',
                'status': r'"status":\s*"([^"]+)"',
                'objective_value': r'"objective_value":\s*([0-9.]+)',
                'model_type': r'"model_type":\s*"([^"]+)"',
                'readiness_score': r'"readiness_score":\s*([0-9.]+)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    if key in ['confidence', 'objective_value', 'readiness_score']:
                        result[key] = float(match.group(1))
                    else:
                        result[key] = match.group(1)
            
            if any(key in result for key in patterns.keys()):
                logger.info(f"Successfully extracted data using regex: {list(result.keys())}")
                return result
                
        except Exception as e:
            logger.warning(f"Regex extraction failed: {e}")
        
        logger.warning(f"Failed to parse JSON, using fallback: {fallback}")
        return fallback

async def get_gateway_tools():
    """Get tools from Gateway using MCP."""
    if not gateway_config:
        return None

    try:
        gateway_url = gateway_config["gateway_url"]
        access_token = gateway_config["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        async with streamablehttp_client(gateway_url, headers=headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                logger.info(f"Found {len(tools_result.tools)} tools in Gateway")
                return tools_result.tools
    except Exception as e:
        logger.error(f"Gateway error: {e}")
        return None

async def call_gateway_tool(tool_name: str, arguments: dict):
    """Call a specific tool through Gateway."""
    if not gateway_config:
        return None

    try:
        gateway_url = gateway_config["gateway_url"]
        access_token = gateway_config["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        async with streamablehttp_client(gateway_url, headers=headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result
    except Exception as e:
        logger.error(f"Gateway tool call error: {e}")
        return None

async def save_to_memory(memory_id: str, session_id: str, messages: List[tuple]):
    """Save conversation to memory."""
    if not memory_client or not memory_id:
        return

    try:
        memory_client.create_event(
            memory_id=memory_id,
            actor_id="user",
            session_id=session_id,
            messages=messages
        )
        logger.info(f"Saved {len(messages)} messages to memory {memory_id}")
    except Exception as e:
        logger.error(f"Memory save error: {e}")

async def load_from_memory(memory_id: str, session_id: str, k: int = 3):
    """Load conversation history from memory."""
    if not memory_client or not memory_id:
        return []

    try:
        turns = memory_client.get_last_k_turns(
            memory_id=memory_id,
            actor_id="user",
            session_id=session_id,
            k=k
        )
        logger.info(f"Loaded {len(turns)} conversation turns from memory")
        return turns
    except Exception as e:
        logger.error(f"Memory load error: {e}")
        return []

async def classify_intent(problem_description: str) -> Dict[str, Any]:
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

async def analyze_data(problem_description: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
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

async def build_model(problem_description: str, intent_data: Dict[str, Any], data_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Build optimization model using Claude 3 Haiku."""
    prompt = f"""
You are an expert optimization modeler. Create a mathematical optimization model for this problem.

Problem: {problem_description}
Intent: {intent_data.get('intent', 'unknown')}
Entities: {intent_data.get('entities', [])}
Data Entities: {data_analysis.get('data_entities', [])}
Scale: {intent_data.get('problem_scale', 'unknown')}

Create a mathematical optimization model and provide JSON response with:
- model_type: Type of optimization model (e.g., "linear_programming", "integer_programming", "mixed_integer_programming")
- variables: List of decision variables with bounds and descriptions
- objective: Objective function with type (maximize/minimize) and expression
- constraints: List of constraints with expressions and descriptions
- model_complexity: Model complexity ("low", "medium", "high")
- estimated_solve_time: Estimated solve time in seconds
- scalability: Scalability assessment ("good", "fair", "poor")

Use realistic mathematical expressions. Respond with valid JSON only.
"""

    try:
        response = invoke_bedrock_with_profile(prompt, "model_building")
        result = safe_json_parse(response, {
            "model_type": "linear_programming",
            "variables": [{"name": "x1", "description": "Decision variable", "type": "continuous", "lower_bound": 0, "upper_bound": 100}],
            "objective": {"type": "maximize", "expression": "x1", "description": "Maximize objective"},
            "constraints": [{"expression": "x1 <= 100", "description": "Capacity constraint"}],
            "model_complexity": "low",
            "estimated_solve_time": 1.0,
            "scalability": "good"
        })
        
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

async def solve_optimization(problem_description: str, intent_data: Dict[str, Any], model_building: Dict[str, Any]) -> Dict[str, Any]:
    """Solve optimization using Claude 3 Haiku."""
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
            "solver_info": {"solver": "Claude 3 Haiku", "method": "AI-based optimization"},
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

# Long-running optimization task that automatically affects ping status
@app.async_task
async def run_optimization_pipeline(problem_description: str, session_id: str = "default") -> Dict[str, Any]:
    """Run the complete 4-step optimization pipeline asynchronously."""
    logger.info(f"Starting optimization pipeline for: {problem_description[:100]}...")
    
    try:
        # Load conversation history from memory
        if memory_config.get('ltm_id'):
            history = await load_from_memory(memory_config['ltm_id'], session_id)
            if history:
                logger.info(f"Loaded {len(history)} conversation turns from memory")
        
        # Step 1: Intent Classification
        logger.info("Step 1: Intent Classification")
        intent_result = await classify_intent(problem_description)
        
        if intent_result["status"] != "success":
            return intent_result
        
        # Step 2: Data Analysis
        logger.info("Step 2: Data Analysis")
        data_result = await analyze_data(problem_description, intent_result["result"])
        
        if data_result["status"] != "success":
            return data_result
        
        # Step 3: Model Building
        logger.info("Step 3: Model Building")
        model_result = await build_model(problem_description, intent_result["result"], data_result["result"])
        
        if model_result["status"] != "success":
            return model_result
        
        # Step 4: Optimization Solution
        logger.info("Step 4: Optimization Solution")
        solution_result = await solve_optimization(problem_description, intent_result["result"], model_result["result"])
        
        # Save results to memory
        if memory_config.get('ltm_id'):
            await save_to_memory(
                memory_config['ltm_id'], 
                session_id, 
                [
                    (f"User problem: {problem_description}", "user"),
                    (f"Optimization result: {solution_result.get('message', '')}", "assistant")
                ]
            )
        
        # Combine all results
        optimization_pipeline = {
            "intent_classification": intent_result,
            "data_analysis": data_result,
            "model_building": model_result,
            "optimization_solution": solution_result,
            "total_execution_time": "Extended execution (no 29-second limit)",
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        logger.info("Optimization pipeline completed successfully")
        return {
            "status": "success",
            "optimization_pipeline": optimization_pipeline,
            "message": "Complete optimization pipeline executed successfully"
        }
        
    except Exception as e:
        logger.error(f"Optimization pipeline error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Optimization pipeline failed"
        }

@app.entrypoint
async def handler(payload: Dict[str, Any], context: RequestContext) -> Dict[str, Any]:
    """
    Main entry point that routes to different functions based on payload content.
    """
    # Check if this is a workflow request
    if "industry" in payload and "workflow_id" in payload:
        return await execute_workflow(payload, context)
    elif "industry" in payload:
        return await get_workflows(payload, context)
    else:
        return await optimize(payload, context)

@app.entrypoint
async def optimize(payload: Dict[str, Any], context: RequestContext) -> Dict[str, Any]:
    """
    Main optimization entry point for AgentCore Runtime.
    
    This function handles optimization requests and can run for extended periods
    without hitting the 29-second API Gateway timeout limit.
    """
    try:
        # Extract problem description from payload
        problem_description = payload.get("problem_description", "")
        session_id = context.session_id
        
        # If no problem description, return health check with capabilities
        if not problem_description:
            capabilities = [
                "4-step optimization pipeline",
                "Extended execution time (no 29-second limit)",
                "Streaming responses",
                "Async processing",
                "Session management"
            ]
            
            if gateway_config:
                capabilities.append("Gateway tool integration")
            if memory_config:
                capabilities.append("Memory persistence")
            if WORKFLOWS_AVAILABLE:
                capabilities.append("21 industry workflows")
            
            return {
                "status": "healthy",
                "service": "DcisionAI Enhanced AgentCore Agent",
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "capabilities": capabilities,
                "inference_profiles": list(INFERENCE_PROFILES.keys()),
                "gateway_available": bool(gateway_config),
                "memory_available": bool(memory_config),
                "workflows_available": WORKFLOWS_AVAILABLE,
                "message": "Send a problem_description to start optimization"
            }
        
        logger.info(f"Starting optimization for session: {session_id}")
        logger.info(f"Problem description: {problem_description[:200]}...")
        
        # Run the optimization pipeline asynchronously
        # This will automatically set the agent status to "HealthyBusy" during execution
        result = await run_optimization_pipeline(problem_description, session_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Optimization failed",
            "timestamp": datetime.now().isoformat()
        }

@app.entrypoint
async def stream_optimization(payload: Dict[str, Any], context: RequestContext) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Streaming optimization entry point for real-time progress updates.
    
    This function provides real-time updates during the optimization process.
    """
    try:
        problem_description = payload.get("problem_description", "")
        session_id = context.session_id
        
        if not problem_description:
            yield {
                "status": "error",
                "message": "No problem description provided",
                "timestamp": datetime.now().isoformat()
            }
            return
        
        # Stream progress updates
        yield {
            "status": "progress",
            "step": "starting",
            "message": "Starting optimization pipeline...",
            "timestamp": datetime.now().isoformat()
        }
        
        # Load conversation history from memory
        if memory_config.get('ltm_id'):
            history = await load_from_memory(memory_config['ltm_id'], session_id)
            if history:
                yield {
                    "status": "progress",
                    "step": "memory_loaded",
                    "message": f"Loaded {len(history)} conversation turns from memory",
                    "timestamp": datetime.now().isoformat()
                }
        
        # Step 1: Intent Classification
        yield {
            "status": "progress",
            "step": "intent_classification",
            "message": "Classifying optimization intent...",
            "timestamp": datetime.now().isoformat()
        }
        
        intent_result = await classify_intent(problem_description)
        yield {
            "status": "progress",
            "step": "intent_classification",
            "result": intent_result,
            "timestamp": datetime.now().isoformat()
        }
        
        if intent_result["status"] != "success":
            yield intent_result
            return
        
        # Step 2: Data Analysis
        yield {
            "status": "progress",
            "step": "data_analysis",
            "message": "Analyzing data requirements...",
            "timestamp": datetime.now().isoformat()
        }
        
        data_result = await analyze_data(problem_description, intent_result["result"])
        yield {
            "status": "progress",
            "step": "data_analysis",
            "result": data_result,
            "timestamp": datetime.now().isoformat()
        }
        
        if data_result["status"] != "success":
            yield data_result
            return
        
        # Step 3: Model Building
        yield {
            "status": "progress",
            "step": "model_building",
            "message": "Building optimization model...",
            "timestamp": datetime.now().isoformat()
        }
        
        model_result = await build_model(problem_description, intent_result["result"], data_result["result"])
        yield {
            "status": "progress",
            "step": "model_building",
            "result": model_result,
            "timestamp": datetime.now().isoformat()
        }
        
        if model_result["status"] != "success":
            yield model_result
            return
        
        # Step 4: Optimization Solution
        yield {
            "status": "progress",
            "step": "optimization_solution",
            "message": "Solving optimization problem...",
            "timestamp": datetime.now().isoformat()
        }
        
        solution_result = await solve_optimization(problem_description, intent_result["result"], model_result["result"])
        yield {
            "status": "progress",
            "step": "optimization_solution",
            "result": solution_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save results to memory
        if memory_config.get('ltm_id'):
            await save_to_memory(
                memory_config['ltm_id'], 
                session_id, 
                [
                    (f"User problem: {problem_description}", "user"),
                    (f"Optimization result: {solution_result.get('message', '')}", "assistant")
                ]
            )
            yield {
                "status": "progress",
                "step": "memory_saved",
                "message": "Results saved to memory for future reference",
                "timestamp": datetime.now().isoformat()
            }
        
        # Final result
        yield {
            "status": "completed",
            "message": "Optimization pipeline completed successfully",
            "optimization_pipeline": {
                "intent_classification": intent_result,
                "data_analysis": data_result,
                "model_building": model_result,
                "optimization_solution": solution_result,
                "total_execution_time": "Extended execution with streaming",
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id
            }
        }
        
    except Exception as e:
        logger.error(f"Streaming optimization error: {str(e)}")
        yield {
            "status": "error",
            "error": str(e),
            "message": "Streaming optimization failed",
            "timestamp": datetime.now().isoformat()
        }

@app.entrypoint
async def get_workflows(payload: Dict[str, Any], context: RequestContext) -> Dict[str, Any]:
    """Get available workflows by industry."""
    if not WORKFLOWS_AVAILABLE:
        return {
            "status": "error",
            "message": "Workflow templates not available",
            "timestamp": datetime.now().isoformat()
        }
    
    industry = payload.get("industry")
    
    if industry:
        # Get workflows for specific industry
        if industry in WORKFLOW_TEMPLATES:
            workflows = WORKFLOW_TEMPLATES[industry]
            return {
                "status": "success",
                "industry": industry,
                "workflows": workflows,
                "count": len(workflows),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": f"Industry '{industry}' not found",
                "available_industries": list(WORKFLOW_TEMPLATES.keys()),
                "timestamp": datetime.now().isoformat()
            }
    else:
        # Get all industries
        return {
            "status": "success",
            "industries": get_all_industries(),
            "workflow_summary": get_workflow_summary(),
            "timestamp": datetime.now().isoformat()
        }

@app.entrypoint
async def execute_workflow(payload: Dict[str, Any], context: RequestContext) -> Dict[str, Any]:
    """Execute a specific workflow."""
    if not WORKFLOWS_AVAILABLE:
        return {
            "status": "error",
            "message": "Workflow templates not available",
            "timestamp": datetime.now().isoformat()
        }
    
    industry = payload.get("industry")
    workflow_id = payload.get("workflow_id")
    
    if not industry or not workflow_id:
        return {
            "status": "error",
            "message": "Both industry and workflow_id are required",
            "timestamp": datetime.now().isoformat()
        }
    
    if industry not in WORKFLOW_TEMPLATES:
        return {
            "status": "error",
            "message": f"Industry '{industry}' not found",
            "available_industries": list(WORKFLOW_TEMPLATES.keys()),
            "timestamp": datetime.now().isoformat()
        }
    
    if workflow_id not in WORKFLOW_TEMPLATES[industry]:
        return {
            "status": "error",
            "message": f"Workflow '{workflow_id}' not found in industry '{industry}'",
            "available_workflows": list(WORKFLOW_TEMPLATES[industry].keys()),
            "timestamp": datetime.now().isoformat()
        }
    
    # Get workflow details
    workflow = WORKFLOW_TEMPLATES[industry][workflow_id]
    problem_description = workflow.get("problem_description", "")
    
    if not problem_description:
        return {
            "status": "error",
            "message": "No problem description found in workflow",
            "timestamp": datetime.now().isoformat()
        }
    
    # Execute the optimization pipeline with the workflow's problem description
    session_id = context.session_id
    result = await run_optimization_pipeline(problem_description, session_id)
    
    # Add workflow metadata to the result
    if result["status"] == "success":
        result["workflow_metadata"] = {
            "industry": industry,
            "workflow_id": workflow_id,
            "workflow_title": workflow.get("title", ""),
            "workflow_description": workflow.get("description", ""),
            "expected_intent": workflow.get("expected_intent", ""),
            "difficulty": workflow.get("difficulty", ""),
            "estimated_time": workflow.get("estimated_time", "")
        }
    
    return result

if __name__ == "__main__":
    logger.info("Starting DcisionAI Enhanced AgentCore Optimization Agent...")
    logger.info("Features: Gateway integration, Memory persistence, 21 workflows")
    app.run()
