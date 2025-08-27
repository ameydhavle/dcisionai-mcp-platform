#!/usr/bin/env python3
"""
DcisionAI Enhanced MCP Server
=============================

An enhanced MCP server that uses the actual manufacturing agent
to provide all 6 tool responses (intent, data, model, solver, etc.).
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

# Add the project root to Python path
import os
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DcisionAI Enhanced MCP Server",
    description="Enhanced MCP server using actual manufacturing agent",
    version="2.0.0"
)

class EnhancedMCPServer:
    """Enhanced MCP server using actual manufacturing agent."""
    
    def __init__(self):
        self.tools = {
            "manufacturing_optimization_workflow": {
                "name": "manufacturing_optimization_workflow",
                "description": "Complete manufacturing optimization workflow using all 6 tools (intent, data, model, solver, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Manufacturing optimization query"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for tracking",
                            "default": "default"
                        },
                        "include_all_tools": {
                            "type": "boolean",
                            "description": "Include all 6 tool responses",
                            "default": True
                        }
                    },
                    "required": ["query"]
                }
            },
            "intent_classification": {
                "name": "intent_classification",
                "description": "Manufacturing intent classification using 6-agent swarm",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Manufacturing query to classify"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for tracking",
                            "default": "default"
                        }
                    },
                    "required": ["query"]
                }
            },
            "data_analysis": {
                "name": "data_analysis",
                "description": "Data analysis and requirements using 3-stage analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Manufacturing query for data analysis"
                        },
                        "intent_classification": {
                            "type": "string",
                            "description": "Intent classification result"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for tracking",
                            "default": "default"
                        }
                    },
                    "required": ["query", "intent_classification"]
                }
            },
            "model_building": {
                "name": "model_building",
                "description": "Optimization model building using 6-specialist swarm",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "intent_result": {
                            "type": "string",
                            "description": "Intent classification result"
                        },
                        "data_result": {
                            "type": "string",
                            "description": "Data analysis result"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for tracking",
                            "default": "default"
                        }
                    },
                    "required": ["intent_result", "data_result"]
                }
            },
            "solver_execution": {
                "name": "solver_execution",
                "description": "Optimization solver execution using shared solver swarm",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model_result": {
                            "type": "string",
                            "description": "Model building result"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for tracking",
                            "default": "default"
                        }
                    },
                    "required": ["model_result"]
                }
            }
        }
        
        # Initialize manufacturing agent
        try:
            from src.models.manufacturing.DcisionAI_Manufacturing_Agent import DcisionAI_Manufacturing_Agent
            self.manufacturing_agent = DcisionAI_Manufacturing_Agent()
            self.agent_available = True
            logger.info("✅ Manufacturing agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize manufacturing agent: {e}")
            self.manufacturing_agent = None
            self.agent_available = False
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        logger.info("Handling initialize request")
        return {
            "jsonrpc": "2.0",
            "id": params.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "DcisionAI Enhanced MCP Server",
                    "version": "2.0.0",
                    "manufacturing_agent_available": self.agent_available
                }
            }
        }
    
    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        logger.info("Handling tools/list request")
        return {
            "jsonrpc": "2.0",
            "id": params.get("id"),
            "result": {
                "tools": list(self.tools.values())
            }
        }
    
    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Handling tools/call request for {tool_name}")
        
        if tool_name == "manufacturing_optimization_workflow":
            return await self._handle_complete_workflow(arguments, params.get("id"))
        elif tool_name == "intent_classification":
            return await self._handle_intent_classification(arguments, params.get("id"))
        elif tool_name == "data_analysis":
            return await self._handle_data_analysis(arguments, params.get("id"))
        elif tool_name == "model_building":
            return await self._handle_model_building(arguments, params.get("id"))
        elif tool_name == "solver_execution":
            return await self._handle_solver_execution(arguments, params.get("id"))
        else:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {tool_name}"
                }
            }
    
    async def _handle_complete_workflow(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle complete manufacturing optimization workflow."""
        query = arguments.get("query", "")
        session_id = arguments.get("session_id", "default")
        include_all_tools = arguments.get("include_all_tools", True)
        
        if not self.agent_available:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": "Manufacturing agent not available",
                                "message": "The manufacturing agent could not be initialized. Please check dependencies."
                            }, indent=2)
                        }
                    ]
                }
            }
        
        try:
            # Run the complete workflow
            result = self.manufacturing_agent.analyze_manufacturing_optimization(query, session_id)
            
            # Format the response with all tool results
            response_data = {
                "status": "success",
                "workflow_id": result.workflow_id,
                "query": result.query,
                "session_id": result.session_id,
                "current_stage": result.current_stage.value,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "warnings": result.warnings,
                "tool_results": {}
            }
            
            # Add individual tool results
            if result.intent_analysis:
                response_data["tool_results"]["intent_classification"] = result.intent_analysis
            
            if result.data_analysis:
                response_data["tool_results"]["data_analysis"] = result.data_analysis
            
            if result.model_building:
                response_data["tool_results"]["model_building"] = result.model_building
            
            if result.solver_results:
                response_data["tool_results"]["solver_results"] = result.solver_results
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(response_data, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": str(e),
                                "message": "Workflow execution failed"
                            }, indent=2)
                        }
                    ]
                }
            }
    
    async def _handle_intent_classification(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle intent classification using manufacturing agent."""
        query = arguments.get("query", "")
        session_id = arguments.get("session_id", "default")
        
        if not self.agent_available:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": "Manufacturing agent not available"
                            }, indent=2)
                        }
                    ]
                }
            }
        
        try:
            # Import the intent tool function
            from src.models.manufacturing.DcisionAI_Manufacturing_Agent import intent_classification_tool
            
            # Call the intent tool
            result = intent_classification_tool(query, session_id)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": str(e)
                            }, indent=2)
                        }
                    ]
                }
            }
    
    async def _handle_data_analysis(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle data analysis using manufacturing agent."""
        query = arguments.get("query", "")
        intent_classification = arguments.get("intent_classification", "")
        session_id = arguments.get("session_id", "default")
        
        if not self.agent_available:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": "Manufacturing agent not available"
                            }, indent=2)
                        }
                    ]
                }
            }
        
        try:
            # Import the data analysis tool function
            from src.models.manufacturing.DcisionAI_Manufacturing_Agent import data_analysis_tool
            
            # Call the data analysis tool
            result = data_analysis_tool(query, intent_classification, session_id)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Data analysis error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": str(e)
                            }, indent=2)
                        }
                    ]
                }
            }
    
    async def _handle_model_building(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle model building using manufacturing agent."""
        intent_result = arguments.get("intent_result", "")
        data_result = arguments.get("data_result", "")
        session_id = arguments.get("session_id", "default")
        
        if not self.agent_available:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": "Manufacturing agent not available"
                            }, indent=2)
                        }
                    ]
                }
            }
        
        try:
            # Import the model building tool function
            from src.models.manufacturing.DcisionAI_Manufacturing_Agent import model_building_tool
            
            # Call the model building tool
            result = model_building_tool(intent_result, data_result, session_id)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Model building error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": str(e)
                            }, indent=2)
                        }
                    ]
                }
            }
    
    async def _handle_solver_execution(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle solver execution using manufacturing agent."""
        model_result = arguments.get("model_result", "")
        session_id = arguments.get("session_id", "default")
        
        if not self.agent_available:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": "Manufacturing agent not available"
                            }, indent=2)
                        }
                    ]
                }
            }
        
        try:
            # Import the solver tool function
            from src.models.manufacturing.DcisionAI_Manufacturing_Agent import solver_tool
            
            # Call the solver tool
            result = solver_tool(model_result, session_id)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Solver execution error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "status": "error",
                                "error": str(e)
                            }, indent=2)
                        }
                    ]
                }
            }
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request."""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            
            logger.info(f"Handling request: {method}")
            
            if method == "initialize":
                response = await self.handle_initialize(params)
            elif method == "tools/list":
                response = await self.handle_tools_list(params)
            elif method == "tools/call":
                response = await self.handle_tools_call(params)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id") if 'request_data' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

# Create server instance
mcp_server = EnhancedMCPServer()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer."""
    return {
        "status": "healthy",
        "service": "DcisionAI Enhanced MCP Server",
        "version": "2.0.0",
        "manufacturing_agent_available": mcp_server.agent_available,
        "timestamp": datetime.utcnow().isoformat()
    }

# MCP protocol endpoint
@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP protocol requests."""
    try:
        # Parse request body
        body = await request.json()
        
        # Handle the request
        response = await mcp_server.handle_request(body)
        
        return JSONResponse(content=response)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
        )
    except Exception as e:
        logger.error(f"Request handling error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "DcisionAI Enhanced MCP Server",
        "version": "2.0.0",
        "manufacturing_agent_available": mcp_server.agent_available,
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp"
        },
        "available_tools": [
            "manufacturing_optimization_workflow",
            "intent_classification", 
            "data_analysis",
            "model_building",
            "solver_execution"
        ]
    }

if __name__ == "__main__":
    # Get configuration from environment
    host = "0.0.0.0"
    port = 8080
    
    logger.info(f"Starting DcisionAI Enhanced MCP Server on {host}:{port}")
    logger.info(f"Manufacturing agent available: {mcp_server.agent_available}")
    
    # Run the server
    uvicorn.run(app, host=host, port=port, log_level="info")
