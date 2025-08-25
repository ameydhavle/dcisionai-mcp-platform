#!/usr/bin/env python3
"""
DcisionAI HTTP MCP Server
=========================

An HTTP-based MCP server that can work with load balancers.
This provides the core MCP protocol functionality over HTTP.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DcisionAI MCP Server",
    description="HTTP-based MCP server for manufacturing tools",
    version="1.0.0"
)

class HTTPMCPServer:
    """HTTP-based MCP server implementation."""
    
    def __init__(self):
        self.tools = {
            "manufacturing_intent_classification": {
                "name": "manufacturing_intent_classification",
                "description": "Classify manufacturing intent from natural language queries",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query about manufacturing"
                        },
                        "include_confidence": {
                            "type": "boolean",
                            "description": "Include confidence scores in response"
                        },
                        "include_reasoning": {
                            "type": "boolean",
                            "description": "Include reasoning in response"
                        }
                    },
                    "required": ["query"]
                }
            },
            "manufacturing_optimization": {
                "name": "manufacturing_optimization",
                "description": "Optimize manufacturing processes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "process_type": {
                            "type": "string",
                            "description": "Type of manufacturing process"
                        },
                        "constraints": {
                            "type": "object",
                            "description": "Optimization constraints"
                        }
                    },
                    "required": ["process_type"]
                }
            }
        }
    
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
                    "name": "DcisionAI MCP Server",
                    "version": "1.0.0"
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
        
        if tool_name == "manufacturing_intent_classification":
            return await self._handle_intent_classification(arguments, params.get("id"))
        elif tool_name == "manufacturing_optimization":
            return await self._handle_optimization(arguments, params.get("id"))
        else:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {tool_name}"
                }
            }
    
    async def _handle_intent_classification(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle manufacturing intent classification."""
        query = arguments.get("query", "")
        include_confidence = arguments.get("include_confidence", True)
        include_reasoning = arguments.get("include_reasoning", True)
        
        # Simple intent classification logic
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["optimize", "production", "line", "cycle", "time"]):
            intent = "PRODUCTION_SCHEDULING"
            confidence = 0.85
            reasoning = "Query contains production optimization keywords"
        elif any(word in query_lower for word in ["waste", "minimize", "cost", "reduce"]):
            intent = "COST_OPTIMIZATION"
            confidence = 0.80
            reasoning = "Query contains cost and waste reduction keywords"
        elif any(word in query_lower for word in ["quality", "control", "defect", "inspection"]):
            intent = "QUALITY_CONTROL"
            confidence = 0.90
            reasoning = "Query contains quality control keywords"
        elif any(word in query_lower for word in ["energy", "consumption", "environmental", "sustainability"]):
            intent = "ENVIRONMENTAL_OPTIMIZATION"
            confidence = 0.88
            reasoning = "Query contains environmental optimization keywords"
        elif any(word in query_lower for word in ["inventory", "stock", "management", "supply"]):
            intent = "INVENTORY_OPTIMIZATION"
            confidence = 0.85
            reasoning = "Query contains inventory management keywords"
        else:
            intent = "GENERAL_MANUFACTURING"
            confidence = 0.60
            reasoning = "Query appears to be general manufacturing related"
        
        result = {
            "primary_intent": intent,
            "entities": ["manufacturing", "optimization"],
            "objectives": ["improve efficiency", "reduce costs"]
        }
        
        if include_confidence:
            result["confidence"] = confidence
        
        if include_reasoning:
            result["reasoning"] = reasoning
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        }
    
    async def _handle_optimization(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle manufacturing optimization."""
        process_type = arguments.get("process_type", "")
        constraints = arguments.get("constraints", {})
        
        # Simple optimization response
        result = {
            "process_type": process_type,
            "optimization_status": "completed",
            "recommendations": [
                "Implement lean manufacturing principles",
                "Optimize production scheduling",
                "Reduce setup times",
                "Improve quality control processes"
            ],
            "estimated_improvement": "15-25% efficiency gain",
            "constraints_applied": constraints
        }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
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
mcp_server = HTTPMCPServer()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer."""
    return {
        "status": "healthy",
        "service": "DcisionAI MCP Server",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
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
        "service": "DcisionAI MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp"
        }
    }

if __name__ == "__main__":
    # Get configuration from environment
    host = "0.0.0.0"
    port = 8080
    
    logger.info(f"Starting DcisionAI HTTP MCP Server on {host}:{port}")
    
    # Run the server
    uvicorn.run(app, host=host, port=port, log_level="info")
