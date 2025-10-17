#!/usr/bin/env python3
"""
DcisionAI MCP Server for AWS AgentCore
=====================================

MCP server configured for deployment to AWS Bedrock AgentCore Runtime.
Based on the AWS AgentCore MCP documentation.
"""

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
import asyncio
import json
import logging
import sys
import os

# Add the MCP server to the path
sys.path.append('/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/mcp-server')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server for AgentCore
mcp = FastMCP(host="0.0.0.0", stateless_http=True)

# Import our DcisionAI tools
try:
    from dcisionai_mcp_server.tools import (
        classify_intent,
        analyze_data,
        build_model,
        solve_optimization,
        select_solver,
        explain_optimization,
        get_workflow_templates,
        execute_workflow
    )
    logger.info("DcisionAI MCP tools imported successfully")
except ImportError as e:
    logger.error(f"Failed to import DcisionAI tools: {e}")
    # Fallback tools for testing
    @mcp.tool()
    def test_tool() -> str:
        """Test tool for AgentCore deployment"""
        return "DcisionAI MCP Server is running on AgentCore"

@mcp.tool()
def classify_intent_tool(problem_description: str, context: str = None) -> dict:
    """
    Classify user intent for optimization requests.
    
    Args:
        problem_description: The user's optimization request or problem description
        context: Optional context about the business domain
        
    Returns:
        Intent classification results
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(classify_intent(problem_description, context))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in classify_intent_tool: {e}")
        return {"error": str(e), "status": "failed"}

@mcp.tool()
def analyze_data_tool(problem_description: str, intent_data: dict = None) -> dict:
    """
    Analyze and preprocess data for optimization.
    
    Args:
        problem_description: Description of the optimization problem
        intent_data: Intent classification results from classify_intent
        
    Returns:
        Data analysis results
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(analyze_data(problem_description, intent_data))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in analyze_data_tool: {e}")
        return {"error": str(e), "status": "failed"}

@mcp.tool()
def build_model_tool(problem_description: str, intent_data: dict = None, data_analysis: dict = None) -> dict:
    """
    Build mathematical optimization model using Claude 3 Haiku.
    
    Args:
        problem_description: Detailed problem description
        intent_data: Intent classification results
        data_analysis: Results from data analysis step
        
    Returns:
        Model building results
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(build_model(problem_description, intent_data, data_analysis))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in build_model_tool: {e}")
        return {"error": str(e), "status": "failed"}

@mcp.tool()
def solve_optimization_tool(problem_description: str, intent_data: dict = None, 
                           data_analysis: dict = None, model_building: dict = None) -> dict:
    """
    Solve the optimization problem and generate results.
    
    Args:
        problem_description: Problem description
        intent_data: Intent classification results
        data_analysis: Data analysis results
        model_building: Model building results
        
    Returns:
        Optimization solution results
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(solve_optimization(
                problem_description, intent_data, data_analysis, model_building
            ))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in solve_optimization_tool: {e}")
        return {"error": str(e), "status": "failed"}

@mcp.tool()
def select_solver_tool(optimization_type: str, problem_size: dict = None, 
                      performance_requirement: str = "balanced") -> dict:
    """
    Select the best available solver for optimization problems.
    
    Args:
        optimization_type: Type of optimization problem (linear_programming, quadratic_programming, etc.)
        problem_size: Problem size information (num_variables, num_constraints, etc.)
        performance_requirement: Performance requirement: speed, accuracy, or balanced
        
    Returns:
        Solver selection results
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(select_solver(
                optimization_type, problem_size, performance_requirement
            ))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in select_solver_tool: {e}")
        return {"error": str(e), "status": "failed"}

@mcp.tool()
def explain_optimization_tool(problem_description: str, intent_data: dict = None,
                             data_analysis: dict = None, model_building: dict = None,
                             optimization_solution: dict = None) -> dict:
    """
    Provide business-facing explainability for optimization results.
    
    Args:
        problem_description: Original problem description
        intent_data: Results from intent classification
        data_analysis: Results from data analysis
        model_building: Results from model building
        optimization_solution: Results from optimization solving
        
    Returns:
        Business explainability results
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(explain_optimization(
                problem_description, intent_data, data_analysis, model_building, optimization_solution
            ))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in explain_optimization_tool: {e}")
        return {"error": str(e), "status": "failed"}

@mcp.tool()
def get_workflow_templates_tool() -> dict:
    """
    Get available industry workflow templates.
    
    Returns:
        Workflow templates for different industries
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_workflow_templates())
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in get_workflow_templates_tool: {e}")
        return {"error": str(e), "status": "failed"}

@mcp.tool()
def execute_workflow_tool(industry: str, workflow_id: str, user_input: dict = None) -> dict:
    """
    Execute a complete optimization workflow.
    
    Args:
        industry: Target industry (manufacturing, healthcare, retail, marketing, financial, logistics, energy)
        workflow_id: Specific workflow to execute
        user_input: User input parameters
        
    Returns:
        Workflow execution results
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(execute_workflow(industry, workflow_id, user_input))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error in execute_workflow_tool: {e}")
        return {"error": str(e), "status": "failed"}

@mcp.tool()
def health_check_tool() -> dict:
    """
    Check the health of the DcisionAI MCP server.
    
    Returns:
        Health status and server information
    """
    return {
        "status": "healthy",
        "server": "DcisionAI MCP Server",
        "version": "1.3.4",
        "tools_available": 8,
        "features": [
            "Claude 3 Haiku model building",
            "OR-Tools optimization",
            "8+ solver support",
            "Business explainability",
            "21 industry workflows"
        ],
        "deployment": "AWS AgentCore Runtime"
    }

if __name__ == "__main__":
    logger.info("Starting DcisionAI MCP Server for AWS AgentCore...")
    logger.info("Available tools:")
    logger.info("  - classify_intent_tool")
    logger.info("  - analyze_data_tool") 
    logger.info("  - build_model_tool")
    logger.info("  - solve_optimization_tool")
    logger.info("  - select_solver_tool")
    logger.info("  - explain_optimization_tool")
    logger.info("  - get_workflow_templates_tool")
    logger.info("  - execute_workflow_tool")
    logger.info("  - health_check_tool")
    
    mcp.run(transport="streamable-http")
