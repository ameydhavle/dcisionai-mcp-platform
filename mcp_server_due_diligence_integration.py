#!/usr/bin/env python3
"""
MCP Server Integration for Due Diligence Tool
============================================

This script shows how to integrate the due diligence validator into the MCP server
to automatically validate all AI responses before returning them to users.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent

# Import the due diligence validator
from implement_due_diligence_tool import DueDiligenceValidator, ValidationLevel, ValidationStatus

logger = logging.getLogger(__name__)

class DcisionAIMCPServerWithValidation:
    """
    Enhanced DcisionAI MCP Server with Due Diligence Validation
    
    This server automatically validates all AI responses before returning them
    to ensure transparency, honesty, and quality.
    """
    
    def __init__(self):
        self.validator = DueDiligenceValidator()
        self.server = Server("dcisionai-optimization-validated")
        self._register_handlers()
        logger.info("DcisionAI MCP Server with Due Diligence initialized")
    
    def _register_handlers(self):
        """Register MCP protocol handlers with validation."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools including the new validation tool."""
            return [
                # Existing tools
                Tool(
                    name="classify_intent",
                    description="Classify user intent for optimization requests (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "The user's optimization request or problem description"
                            },
                            "context": {
                                "type": "string",
                                "description": "Optional context about the business domain"
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="analyze_data",
                    description="Analyze and preprocess data for optimization (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Description of the optimization problem"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results from classify_intent",
                                "default": {}
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="build_model",
                    description="Build mathematical optimization model using Qwen 30B (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Detailed problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results",
                                "default": {}
                            },
                            "data_analysis": {
                                "type": "object",
                                "description": "Results from data analysis step",
                                "default": {}
                            },
                            "solver_selection": {
                                "type": "object",
                                "description": "Results from solver selection step",
                                "default": {}
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="solve_optimization",
                    description="Solve the optimization problem and generate results (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results",
                                "default": {}
                            },
                            "data_analysis": {
                                "type": "object",
                                "description": "Data analysis results",
                                "default": {}
                            },
                            "model_building": {
                                "type": "object",
                                "description": "Results from model building",
                                "default": {}
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="select_solver",
                    description="Select the best available solver for optimization problems (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "optimization_type": {
                                "type": "string",
                                "description": "Type of optimization problem (linear_programming, quadratic_programming, mixed_integer_linear_programming, etc.)"
                            },
                            "problem_size": {
                                "type": "object",
                                "description": "Problem size information (num_variables, num_constraints, etc.)",
                                "default": {}
                            },
                            "performance_requirement": {
                                "type": "string",
                                "description": "Performance requirement: speed, accuracy, or balanced",
                                "default": "balanced"
                            }
                        },
                        "required": ["optimization_type"]
                    }
                ),
                Tool(
                    name="explain_optimization",
                    description="Provide business-facing explainability for optimization results (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Original problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Results from intent classification",
                                "default": {}
                            },
                            "data_analysis": {
                                "type": "object",
                                "description": "Results from data analysis",
                                "default": {}
                            },
                            "model_building": {
                                "type": "object",
                                "description": "Results from model building",
                                "default": {}
                            },
                            "optimization_solution": {
                                "type": "object",
                                "description": "Results from optimization solving",
                                "default": {}
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="simulate_scenarios",
                    description="Simulate different scenarios for optimization analysis and risk assessment (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Description of the optimization problem"
                            },
                            "optimization_solution": {
                                "type": "object",
                                "description": "Results from optimization solving",
                                "default": {}
                            },
                            "scenario_parameters": {
                                "type": "object",
                                "description": "Parameters for scenario simulation",
                                "default": {}
                            },
                            "simulation_type": {
                                "type": "string",
                                "description": "Type of simulation (monte_carlo, discrete_event, agent_based, system_dynamics, stochastic_optimization)",
                                "default": "monte_carlo"
                            },
                            "num_trials": {
                                "type": "integer",
                                "description": "Number of simulation trials",
                                "default": 10000
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="get_workflow_templates",
                    description="Get available industry workflow templates (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="execute_workflow",
                    description="Execute a complete optimization workflow (with validation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "industry": {
                                "type": "string",
                                "description": "Target industry (manufacturing, healthcare, retail, marketing, financial, logistics, energy)"
                            },
                            "workflow_id": {
                                "type": "string",
                                "description": "Specific workflow to execute"
                            },
                            "user_input": {
                                "type": "object",
                                "description": "User input parameters",
                                "default": {}
                            }
                        },
                        "required": ["industry", "workflow_id"]
                    }
                ),
                # New validation tool
                Tool(
                    name="validate_ai_response",
                    description="Validate AI response for mathematical, logical, and business correctness",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tool_name": {
                                "type": "string",
                                "description": "Name of the tool that generated the response"
                            },
                            "response": {
                                "type": "object",
                                "description": "The AI response to validate"
                            },
                            "problem_description": {
                                "type": "string",
                                "description": "Original problem description"
                            },
                            "validation_level": {
                                "type": "string",
                                "description": "Level of validation: basic, deep, or expert",
                                "default": "basic"
                            },
                            "context": {
                                "type": "object",
                                "description": "Additional context for validation",
                                "default": {}
                            }
                        },
                        "required": ["tool_name", "response", "problem_description"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls with automatic validation."""
            try:
                # Import the actual tool functions
                from dcisionai_mcp_server.tools import (
                    classify_intent, analyze_data, build_model, solve_optimization,
                    select_solver, explain_optimization, simulate_scenarios,
                    get_workflow_templates, execute_workflow
                )
                
                # Get the original problem description for validation
                problem_description = arguments.get("problem_description", "")
                
                # Call the original tool function
                if name == "classify_intent":
                    result = await classify_intent(
                        arguments.get("problem_description", ""),
                        arguments.get("context")
                    )
                elif name == "analyze_data":
                    result = await analyze_data(
                        arguments.get("problem_description", ""),
                        arguments.get("intent_data", {})
                    )
                elif name == "build_model":
                    result = await build_model(
                        arguments.get("problem_description", ""),
                        arguments.get("intent_data", {}),
                        arguments.get("data_analysis", {}),
                        arguments.get("solver_selection", {})
                    )
                elif name == "solve_optimization":
                    result = await solve_optimization(
                        arguments.get("problem_description", ""),
                        arguments.get("intent_data", {}),
                        arguments.get("data_analysis", {}),
                        arguments.get("model_building", {})
                    )
                elif name == "select_solver":
                    result = await select_solver(
                        arguments.get("optimization_type", ""),
                        arguments.get("problem_size", {}),
                        arguments.get("performance_requirement", "balanced")
                    )
                elif name == "explain_optimization":
                    result = await explain_optimization(
                        arguments.get("problem_description", ""),
                        arguments.get("intent_data", {}),
                        arguments.get("data_analysis", {}),
                        arguments.get("model_building", {}),
                        arguments.get("optimization_solution", {})
                    )
                elif name == "simulate_scenarios":
                    result = await simulate_scenarios(
                        arguments.get("problem_description", ""),
                        arguments.get("optimization_solution", {}),
                        arguments.get("scenario_parameters", {}),
                        arguments.get("simulation_type", "monte_carlo"),
                        arguments.get("num_trials", 10000)
                    )
                elif name == "get_workflow_templates":
                    result = await get_workflow_templates()
                elif name == "execute_workflow":
                    result = await execute_workflow(
                        arguments.get("industry", ""),
                        arguments.get("workflow_id", ""),
                        arguments.get("user_input", {})
                    )
                elif name == "validate_ai_response":
                    # Direct validation call
                    validation_level = ValidationLevel(arguments.get("validation_level", "basic"))
                    validation_result = await self.validator.validate_ai_response(
                        tool_name=arguments.get("tool_name", ""),
                        response=arguments.get("response", {}),
                        problem_description=arguments.get("problem_description", ""),
                        validation_level=validation_level,
                        context=arguments.get("context", {})
                    )
                    
                    # Convert validation result to response format
                    result = {
                        "validation_status": validation_result.status.value,
                        "confidence_score": validation_result.confidence_score,
                        "validated_response": validation_result.validated_response,
                        "warnings": validation_result.warnings,
                        "errors": validation_result.errors,
                        "corrections": validation_result.corrections,
                        "validation_details": validation_result.validation_details,
                        "recommendations": validation_result.recommendations,
                        "risk_assessment": validation_result.risk_assessment
                    }
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                # Validate the result (except for the validation tool itself)
                if name != "validate_ai_response" and name != "get_workflow_templates":
                    validation_result = await self.validator.validate_ai_response(
                        tool_name=name,
                        response=result,
                        problem_description=problem_description,
                        validation_level=ValidationLevel.BASIC
                    )
                    
                    # If validation failed, return validation details
                    if validation_result.status == ValidationStatus.FAILED:
                        result = {
                            "original_response": result,
                            "validation_failed": True,
                            "validation_status": validation_result.status.value,
                            "confidence_score": validation_result.confidence_score,
                            "errors": validation_result.errors,
                            "warnings": validation_result.warnings,
                            "corrections": validation_result.corrections,
                            "recommendations": validation_result.recommendations,
                            "message": "Response failed validation and was not returned. Please review the errors and try again."
                        }
                    elif validation_result.status == ValidationStatus.WARNING:
                        # Add validation warnings to the response
                        result["validation_warnings"] = {
                            "status": validation_result.status.value,
                            "confidence_score": validation_result.confidence_score,
                            "warnings": validation_result.warnings,
                            "recommendations": validation_result.recommendations
                        }
                    else:
                        # Add validation success info
                        result["validation_passed"] = {
                            "status": validation_result.status.value,
                            "confidence_score": validation_result.confidence_score
                        }
                
                # Convert result to JSON string
                if isinstance(result, dict):
                    result_text = json.dumps(result, indent=2)
                else:
                    result_text = str(result)
                
                return [TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                error_result = {
                    "error": f"Tool execution failed: {str(e)}",
                    "tool": name,
                    "arguments": arguments
                }
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

# Example usage
async def main():
    """Example usage of the enhanced MCP server with validation."""
    server = DcisionAIMCPServerWithValidation()
    
    print("✅ Enhanced MCP Server with Due Diligence Validation initialized")
    print("🛡️ All AI responses will be automatically validated")
    print("📊 Validation results will be included in responses")
    print("🚨 Failed responses will be blocked and errors shown")
    print("⚠️ Warnings will be included for user review")

if __name__ == "__main__":
    asyncio.run(main())
