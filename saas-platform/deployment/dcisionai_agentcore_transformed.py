#!/usr/bin/env python3
"""
DcisionAI MCP Server - Transformed for AgentCore Runtime
========================================================

Transformed following AWS AgentCore best practices from:
https://aws.amazon.com/blogs/machine-learning/accelerate-development-with-the-amazon-bedrock-agentcore-mcpserver/

This version:
1. Uses BedrockAgentCoreApp for runtime integration
2. Imports necessary libraries including bedrock_agentcore
3. Decorates the main handler with @app.entrypoint
4. Preserves existing DcisionAI MCP server logic
5. Uses enhanced v1.7.3 with pattern-breaking strategies
"""

import os
import sys
import json
import logging
import asyncio
from typing import Any, Dict, List
from datetime import datetime

# Add the MCP server path to import our enhanced tools
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_root = os.path.abspath(os.path.join(current_dir, '../../../mcp-server'))
if mcp_server_root not in sys.path:
    sys.path.insert(0, mcp_server_root)

# Import AgentCore Runtime (following best practices)
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our enhanced DcisionAI tools
try:
    from dcisionai_mcp_server.tools import DcisionAITools
    logger.info("✅ Enhanced DcisionAI MCP tools imported successfully (v1.7.3)")
except Exception as e:
    logger.error(f"❌ Failed to import DcisionAITools: {e}")
    sys.exit(1)

# Initialize AgentCore App (following best practices)
app = BedrockAgentCoreApp()

# Initialize DcisionAI Tools
dcisionai_tools = DcisionAITools()

@app.entrypoint
async def invoke(payload: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main entrypoint for AgentCore Runtime.
    Handles optimization requests and routes to appropriate DcisionAI tools.
    
    Following AWS AgentCore best practices:
    - Decorated with @app.entrypoint
    - Handles payload and context
    - Preserves existing MCP server logic
    """
    try:
        logger.info(f"🚀 DcisionAI AgentCore Runtime invoked with payload: {payload}")
        
        # Extract the MCP message from payload
        if 'messages' in payload and payload['messages']:
            message = payload['messages'][0]
            if 'content' in message and 'text' in message['content']:
                mcp_content = message['content']['text']
            else:
                mcp_content = str(message)
        else:
            mcp_content = str(payload)
        
        # Parse the MCP request
        try:
            mcp_request = json.loads(mcp_content)
        except json.JSONDecodeError:
            # If not JSON, treat as direct problem description
            mcp_request = {
                "method": "tools/call",
                "params": {
                    "name": "classify_intent",
                    "arguments": {
                        "problem_description": mcp_content
                    }
                }
            }
        
        # Route to appropriate DcisionAI tool
        method = mcp_request.get('method', '')
        params = mcp_request.get('params', {})
        
        if method == 'tools/call':
            tool_name = params.get('name', '')
            arguments = params.get('arguments', {})
            
            logger.info(f"🔧 Calling DcisionAI tool: {tool_name}")
            
            # Map tool names to DcisionAI methods
            tool_method_map = {
                'classify_intent': dcisionai_tools.classify_intent,
                'analyze_data': dcisionai_tools.analyze_data,
                'select_solver': dcisionai_tools.select_solver,
                'build_model': dcisionai_tools.build_model,
                'solve_optimization': dcisionai_tools.solve_optimization,
                'simulate_scenarios': dcisionai_tools.simulate_scenarios,
                'get_workflow_templates': dcisionai_tools.get_workflow_templates,
                'explain_optimization': dcisionai_tools.explain_optimization,
                'execute_workflow': dcisionai_tools.execute_workflow
            }
            
            if tool_name not in tool_method_map:
                return {
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": list(tool_method_map.keys())
                }
            
            # Call the tool
            tool_method = tool_method_map[tool_name]
            result = await tool_method(**arguments)
            
            logger.info(f"✅ Tool {tool_name} completed successfully")
            
            # Return in MCP format
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result)
                    }
                ]
            }
            
        elif method == 'tools/list':
            # Return available tools
            return {
                "tools": [
                    {
                        "name": "classify_intent",
                        "description": "Classify optimization problem intent and requirements"
                    },
                    {
                        "name": "analyze_data",
                        "description": "Analyze data readiness and quality for optimization"
                    },
                    {
                        "name": "select_solver",
                        "description": "Select optimal solver based on problem characteristics"
                    },
                    {
                        "name": "build_model",
                        "description": "Build mathematical optimization model with pattern-breaking strategies"
                    },
                    {
                        "name": "solve_optimization",
                        "description": "Solve optimization problem using selected solver"
                    },
                    {
                        "name": "simulate_scenarios",
                        "description": "Run simulation analysis for risk assessment and scenario planning"
                    },
                    {
                        "name": "get_workflow_templates",
                        "description": "Get available industry workflow templates"
                    },
                    {
                        "name": "explain_optimization",
                        "description": "Provide business-facing explanation of optimization results"
                    },
                    {
                        "name": "execute_workflow",
                        "description": "Execute complete optimization workflow for specific industry"
                    }
                ]
            }
            
        else:
            # Default: treat as optimization problem
            logger.info("🎯 Treating as optimization problem")
            
            # Run complete optimization workflow
            problem_description = mcp_content
            
            # Step 1: Intent Classification
            intent_result = await dcisionai_tools.classify_intent(problem_description)
            if intent_result.get('status') != 'success':
                return {"error": "Intent classification failed", "details": intent_result}
            
            # Step 2: Data Analysis
            data_result = await dcisionai_tools.analyze_data(
                problem_description, 
                intent_result['result']
            )
            if data_result.get('status') != 'success':
                return {"error": "Data analysis failed", "details": data_result}
            
            # Step 3: Solver Selection
            solver_result = await dcisionai_tools.select_solver(
                optimization_type=intent_result['result']['optimization_type'],
                problem_size={
                    'num_variables': len(data_result['result'].get('variables_identified', [])),
                    'num_constraints': len(data_result['result'].get('constraints_identified', []))
                },
                performance_requirement='balanced'
            )
            if solver_result.get('status') != 'success':
                return {"error": "Solver selection failed", "details": solver_result}
            
            # Step 4: Model Building
            model_result = await dcisionai_tools.build_model(
                problem_description,
                intent_result['result'],
                data_result['result'],
                solver_result['result']
            )
            if model_result.get('status') != 'success':
                return {"error": "Model building failed", "details": model_result}
            
            # Step 5: Optimization Solving
            solve_result = await dcisionai_tools.solve_optimization(
                problem_description,
                intent_result['result'],
                data_result['result'],
                model_result['result']
            )
            if solve_result.get('status') != 'success':
                return {"error": "Optimization solving failed", "details": solve_result}
            
            # Step 6: Explainability
            explain_result = await dcisionai_tools.explain_optimization(
                problem_description,
                intent_result['result'],
                data_result['result'],
                model_result['result'],
                solve_result['result']
            )
            
            # Combine all results
            complete_result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "intent_classification": intent_result['result'],
                "data_analysis": data_result['result'],
                "solver_selection": solver_result['result'],
                "model_building": model_result['result'],
                "optimization_solution": solve_result['result'],
                "explainability": explain_result['result'] if explain_result.get('status') == 'success' else None
            }
            
            logger.info("🎉 Complete optimization workflow completed successfully")
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(complete_result)
                    }
                ]
            }
            
    except Exception as e:
        logger.error(f"❌ Error in DcisionAI AgentCore Runtime: {e}")
        return {
            "error": f"DcisionAI AgentCore Runtime error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Let AgentCore Runtime control the running of the agent (following best practices)
    app.run()
