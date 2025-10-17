#!/usr/bin/env python3
"""
DcisionAI MCP Server - AgentCore Runtime Compatible Version
Transformed for AWS Bedrock AgentCore Runtime deployment
"""

import os
import sys
import json
import logging
from typing import Any, Dict, List
from datetime import datetime

# Add the parent directory to the path to import dcisionai_mcp_server.tools
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_root = os.path.abspath(os.path.join(current_dir, '../../mcp-server'))
if mcp_server_root not in sys.path:
    sys.path.insert(0, mcp_server_root)

# Import AgentCore Runtime
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Import our DcisionAI tools
try:
    from dcisionai_mcp_server.tools import DcisionAITools
    logger = logging.getLogger(__name__)
    logger.info("DcisionAI MCP tools imported successfully")
except Exception as e:
    logger.error(f"Failed to import DcisionAITools: {e}")
    sys.exit(1)

# Initialize AgentCore App
app = BedrockAgentCoreApp()

# Initialize DcisionAI Tools
dcisionai_tools = DcisionAITools()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.entrypoint
def invoke(payload: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main entrypoint for AgentCore Runtime.
    Handles MCP protocol messages and routes to appropriate tools.
    """
    try:
        logger.info(f"Received payload: {payload}")
        
        # For AgentCore Runtime, the payload might be a direct MCP message
        # or wrapped in a message field
        if "message" in payload:
            mcp_message = payload["message"]
        else:
            mcp_message = payload
            
        method = mcp_message.get("method")
        message_id = mcp_message.get("id", 1)
        
        logger.info(f"Processing MCP method: {method}")
        
        if method == "initialize":
            return handle_initialize(mcp_message)
        elif method == "tools/list":
            return handle_tools_list(mcp_message)
        elif method == "tools/call":
            return handle_tools_call(mcp_message)
        else:
            logger.warning(f"Unknown method: {method}")
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
    except Exception as e:
        logger.error(f"Error in invoke: {e}")
        import traceback
        traceback.print_exc()
        return {
            "jsonrpc": "2.0",
            "id": payload.get("id", 1),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

def handle_initialize(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP initialize request."""
    logger.info("Handling initialize request")
    return {
        "jsonrpc": "2.0",
        "id": message.get("id", 1),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "dcisionai-optimization",
                "version": "1.3.4"
            }
        }
    }

def handle_tools_list(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tools/list request."""
    logger.info("Handling tools/list request")
    
    tools = [
        {
            "name": "classify_intent",
            "description": "Classify user intent for optimization requests",
            "inputSchema": {
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
        },
        {
            "name": "analyze_data",
            "description": "Analyze and preprocess data for optimization",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem_description": {
                        "type": "string",
                        "description": "Description of the optimization problem"
                    },
                    "intent_data": {
                        "type": "object",
                        "description": "Results from intent classification"
                    }
                },
                "required": ["problem_description"]
            }
        },
        {
            "name": "build_model",
            "description": "Build mathematical optimization model using Claude 3 Haiku",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem_description": {
                        "type": "string",
                        "description": "Detailed problem description"
                    },
                    "intent_data": {
                        "type": "object",
                        "description": "Results from intent classification"
                    },
                    "data_analysis": {
                        "type": "object",
                        "description": "Results from data analysis"
                    }
                },
                "required": ["problem_description"]
            }
        },
        {
            "name": "solve_optimization",
            "description": "Solve the optimization problem and generate results",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem_description": {
                        "type": "string",
                        "description": "Problem description"
                    },
                    "intent_data": {
                        "type": "object",
                        "description": "Results from intent classification"
                    },
                    "data_analysis": {
                        "type": "object",
                        "description": "Results from data analysis"
                    },
                    "model_building": {
                        "type": "object",
                        "description": "Results from model building"
                    }
                },
                "required": ["problem_description"]
            }
        },
        {
            "name": "select_solver",
            "description": "Select the best available solver for optimization problems",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "optimization_type": {
                        "type": "string",
                        "description": "Type of optimization problem (linear_programming, quadratic_programming, mixed_integer_linear_programming, etc.)"
                    },
                    "problem_size": {
                        "type": "object",
                        "description": "Problem size information (num_variables, num_constraints, etc.)"
                    },
                    "performance_requirement": {
                        "type": "string",
                        "description": "Performance requirement: speed, accuracy, or balanced"
                    }
                },
                "required": ["optimization_type"]
            }
        },
        {
            "name": "explain_optimization",
            "description": "Provide business-facing explainability for optimization results",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem_description": {
                        "type": "string",
                        "description": "Original problem description"
                    },
                    "intent_data": {
                        "type": "object",
                        "description": "Results from intent classification"
                    },
                    "data_analysis": {
                        "type": "object",
                        "description": "Results from data analysis"
                    },
                    "model_building": {
                        "type": "object",
                        "description": "Results from model building"
                    },
                    "optimization_solution": {
                        "type": "object",
                        "description": "Results from optimization solving"
                    }
                },
                "required": ["problem_description"]
            }
        },
        {
            "name": "get_workflow_templates",
            "description": "Get available industry workflow templates",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "execute_workflow",
            "description": "Execute a complete optimization workflow",
            "inputSchema": {
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
                        "description": "User input parameters"
                    }
                },
                "required": ["industry", "workflow_id"]
            }
        }
    ]
    
    return {
        "jsonrpc": "2.0",
        "id": message.get("id", 1),
        "result": {
            "tools": tools
        }
    }

def handle_tools_call(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tools/call request."""
    logger.info("Handling tools/call request")
    
    params = message.get("params", {})
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
    
    try:
        # Route to appropriate tool method
        if tool_name == "classify_intent":
            result = dcisionai_tools.classify_intent(
                problem_description=arguments.get("problem_description", ""),
                context=arguments.get("context")
            )
        elif tool_name == "analyze_data":
            result = dcisionai_tools.analyze_data(
                problem_description=arguments.get("problem_description", ""),
                intent_data=arguments.get("intent_data")
            )
        elif tool_name == "build_model":
            result = dcisionai_tools.build_model(
                problem_description=arguments.get("problem_description", ""),
                intent_data=arguments.get("intent_data"),
                data_analysis=arguments.get("data_analysis")
            )
        elif tool_name == "solve_optimization":
            result = dcisionai_tools.solve_optimization(
                problem_description=arguments.get("problem_description", ""),
                intent_data=arguments.get("intent_data"),
                data_analysis=arguments.get("data_analysis"),
                model_building=arguments.get("model_building")
            )
        elif tool_name == "select_solver":
            result = dcisionai_tools.select_solver(
                optimization_type=arguments.get("optimization_type", ""),
                problem_size=arguments.get("problem_size", {}),
                performance_requirement=arguments.get("performance_requirement", "balanced")
            )
        elif tool_name == "explain_optimization":
            result = dcisionai_tools.explain_optimization(
                problem_description=arguments.get("problem_description", ""),
                intent_data=arguments.get("intent_data"),
                data_analysis=arguments.get("data_analysis"),
                model_building=arguments.get("model_building"),
                optimization_solution=arguments.get("optimization_solution")
            )
        elif tool_name == "get_workflow_templates":
            result = dcisionai_tools.get_workflow_templates()
        elif tool_name == "execute_workflow":
            result = dcisionai_tools.execute_workflow(
                industry=arguments.get("industry", ""),
                workflow_id=arguments.get("workflow_id", ""),
                user_input=arguments.get("user_input", {})
            )
        else:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id", 1),
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }
        
        # Return the result in MCP format
        return {
            "jsonrpc": "2.0",
            "id": message.get("id", 1),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "jsonrpc": "2.0",
            "id": message.get("id", 1),
            "error": {
                "code": -32603,
                "message": f"Tool execution error: {str(e)}"
            }
        }

if __name__ == "__main__":
    logger.info("Starting DcisionAI MCP Server for AgentCore Runtime...")
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
