#!/usr/bin/env python3
"""
DcisionAI MCP Server - Production AgentCore Runtime Version
Full optimization capabilities with real tools
"""

import os
import sys
import json
import logging
import asyncio
from typing import Any, Dict, List
from datetime import datetime

# Add the parent directory to the path to import dcisionai_mcp_server.tools
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_root = os.path.abspath(os.path.join(current_dir, '../../mcp-server'))
if mcp_server_root not in sys.path:
    sys.path.insert(0, mcp_server_root)

# Import AgentCore Runtime
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our DcisionAI tools
try:
    from dcisionai_mcp_server.tools import DcisionAITools
    logger.info("DcisionAI MCP tools imported successfully")
except Exception as e:
    logger.error(f"Failed to import DcisionAITools: {e}")
    sys.exit(1)

# Initialize AgentCore App
app = BedrockAgentCoreApp()

# Initialize DcisionAI Tools
dcisionai_tools = DcisionAITools()

@app.entrypoint
async def invoke(payload: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main entrypoint for AgentCore Runtime.
    Handles optimization requests and routes to appropriate tools.
    """
    try:
        logger.info(f"Received payload: {payload}")
        
        # Extract the request details
        prompt = payload.get("prompt", "")
        tool_name = payload.get("tool", "")
        arguments = payload.get("arguments", {})
        
        logger.info(f"Processing request - Tool: {tool_name}, Prompt: {prompt[:100]}...")
        
        # If no specific tool is requested, provide available tools
        if not tool_name:
            return {
                "status": "success",
                "message": "DcisionAI Optimization Server is running on AWS AgentCore Runtime",
                "available_tools": [
                    "classify_intent",
                    "analyze_data", 
                    "build_model",
                    "solve_optimization",
                    "select_solver",
                    "explain_optimization",
                    "get_workflow_templates",
                    "execute_workflow"
                ],
                "usage": "Use 'tool' parameter to specify which tool to call, and 'arguments' for tool parameters",
                "features": [
                    "Claude 3 Haiku model building",
                    "OR-Tools optimization with 8+ solvers",
                    "Business explainability",
                    "21 industry workflows",
                    "AWS AgentCore Runtime hosting"
                ],
                "version": "1.3.4-production"
            }
        
        # Route to appropriate tool method with real optimization capabilities
        if tool_name == "classify_intent":
            result = await dcisionai_tools.classify_intent(
                problem_description=arguments.get("problem_description", prompt),
                context=arguments.get("context")
            )
        elif tool_name == "analyze_data":
            result = await dcisionai_tools.analyze_data(
                problem_description=arguments.get("problem_description", prompt),
                intent_data=arguments.get("intent_data")
            )
        elif tool_name == "build_model":
            result = await dcisionai_tools.build_model(
                problem_description=arguments.get("problem_description", prompt),
                intent_data=arguments.get("intent_data"),
                data_analysis=arguments.get("data_analysis")
            )
        elif tool_name == "solve_optimization":
            result = await dcisionai_tools.solve_optimization(
                problem_description=arguments.get("problem_description", prompt),
                intent_data=arguments.get("intent_data"),
                data_analysis=arguments.get("data_analysis"),
                model_building=arguments.get("model_building")
            )
        elif tool_name == "select_solver":
            result = await dcisionai_tools.select_solver(
                optimization_type=arguments.get("optimization_type", ""),
                problem_size=arguments.get("problem_size", {}),
                performance_requirement=arguments.get("performance_requirement", "balanced")
            )
        elif tool_name == "explain_optimization":
            result = await dcisionai_tools.explain_optimization(
                problem_description=arguments.get("problem_description", prompt),
                intent_data=arguments.get("intent_data"),
                data_analysis=arguments.get("data_analysis"),
                model_building=arguments.get("model_building"),
                optimization_solution=arguments.get("optimization_solution")
            )
        elif tool_name == "get_workflow_templates":
            result = await dcisionai_tools.get_workflow_templates()
        elif tool_name == "execute_workflow":
            result = await dcisionai_tools.execute_workflow(
                industry=arguments.get("industry", ""),
                workflow_id=arguments.get("workflow_id", ""),
                user_input=arguments.get("user_input", {})
            )
        else:
            return {
                "status": "error",
                "message": f"Unknown tool: {tool_name}",
                "available_tools": [
                    "classify_intent", "analyze_data", "build_model", "solve_optimization",
                    "select_solver", "explain_optimization", "get_workflow_templates", "execute_workflow"
                ]
            }
        
        # Return the result
        return {
            "status": "success",
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "version": "1.3.4-production"
        }
        
    except Exception as e:
        logger.error(f"Error in invoke: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Internal error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.ping
def health_check():
    """Custom health check for the DcisionAI optimization server."""
    return {
        "status": "healthy",
        "server": "DcisionAI Optimization Server",
        "version": "1.3.4-production",
        "tools_available": 8,
        "features": [
            "Claude 3 Haiku model building",
            "OR-Tools optimization with 8+ solvers",
            "Business explainability",
            "21 industry workflows",
            "AWS AgentCore Runtime hosting"
        ],
        "deployment": "AWS AgentCore Runtime",
        "capabilities": "Full optimization with real mathematical solvers",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting DcisionAI Optimization Server for AgentCore Runtime (Production)...")
    logger.info("Available tools:")
    logger.info("  - classify_intent")
    logger.info("  - analyze_data") 
    logger.info("  - build_model")
    logger.info("  - solve_optimization")
    logger.info("  - select_solver")
    logger.info("  - explain_optimization")
    logger.info("  - get_workflow_templates")
    logger.info("  - execute_workflow")
    
    # Run the AgentCore app
    app.run()
