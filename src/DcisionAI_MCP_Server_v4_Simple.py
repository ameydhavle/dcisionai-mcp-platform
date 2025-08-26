#!/usr/bin/env python3
"""
DcisionAI MCP Server v4 Simple - Real 6-Agent Intent Classification
A focused MCP server that demonstrates the real 6-agent swarm intelligence system.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class DcisionAI_MCP_Server_v4_Simple:
    """DcisionAI MCP Server v4 Simple - Real 6-Agent Intent Classification."""
    
    def __init__(self):
        self.server_name = "DcisionAI MCP Server v4 Simple"
        self.version = "4.1.0"
        self.initialized = False
        
        # Initialize the real 6-agent intent tool
        self.intent_tool = None
        
        try:
            # Import and initialize the real 6-agent intent classification
            logger.info("🔧 Initializing real 6-agent intent classification with strands framework...")
            
            from models.manufacturing.tools.intent.DcisionAI_Intent_Tool_v6 import DcisionAI_Intent_Tool_v6
            self.intent_tool = DcisionAI_Intent_Tool_v6()
            
            logger.info("✅ 6-agent intent classification tool initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize 6-agent intent tool: {e}")
            raise Exception(f"6-agent intent tool initialization failed: {e}")
        
        logger.info("✅ MCP Server v4 Simple initialized successfully")
    
    async def handle_initialize(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        try:
            self.initialized = True
            logger.info("✅ MCP Server v4 Simple initialized")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": self.server_name,
                        "version": self.version
                    }
                }
            }
        except Exception as e:
            logger.error(f"❌ Initialize failed: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Initialize failed: {str(e)}"
                }
            }
    
    async def handle_tools_list(self, request_id: str) -> Dict[str, Any]:
        """Handle MCP tools/list request."""
        try:
            tools = [
                {
                    "name": "manufacturing_optimization_status",
                    "description": "Check the status of the DcisionAI MCP server and 6-agent intent classification",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Optional query to test"
                            }
                        }
                    }
                },
                {
                    "name": "classify_intent",
                    "description": "Classify manufacturing intent using the real 6-agent swarm intelligence system",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The query to classify using 6-agent consensus"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools
                }
            }
        except Exception as e:
            logger.error(f"❌ Tools list failed: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tools list failed: {str(e)}"
                }
            }
    
    async def handle_tools_call(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools/call request."""
        try:
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "manufacturing_optimization_status":
                return await self._handle_status_check(request_id, arguments)
            elif tool_name == "classify_intent":
                return await self._handle_intent_classification(request_id, arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        except Exception as e:
            logger.error(f"❌ Tool call failed: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool call failed: {str(e)}"
                }
            }
    
    async def _handle_status_check(self, request_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle manufacturing optimization status check."""
        query = arguments.get("query", "")
        
        status_response = {
            "status": "operational",
            "server": self.server_name,
            "version": self.version,
            "capabilities": {
                "intent_classification": "6-agent swarm intelligence (REAL)",
                "data_analysis": "roadmap",
                "model_building": "roadmap", 
                "optimization_solving": "roadmap",
                "visualization": "roadmap"
            },
            "tools_available": {
                "intent_tool": self.intent_tool is not None,
                "data_tool": False,
                "model_tool": False,
                "solver_tool": False,
                "manufacturing_agent": False
            },
            "message": f"{self.server_name} is operational with REAL 6-agent swarm intelligence for intent classification"
        }
        
        if query:
            status_response["test_query"] = query
            status_response["message"] += f" - Test query received: '{query}'"
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(status_response, indent=2)
                    }
                ]
            }
        }
    
    async def _handle_intent_classification(self, request_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent classification using the real 6-agent system."""
        query = arguments.get("query", "")
        
        if not query:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Query is required for intent classification"
                }
            }
        
        try:
            logger.info(f"🔍 Classifying intent for query: {query}")
            
            # Use the real 6-agent intent classification
            intent_result = self.intent_tool.classify_intent(query)
            
            # Convert to JSON-serializable format
            result = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "intent_classification": {
                    "primary_intent": intent_result.primary_intent.value,
                    "confidence": intent_result.confidence,
                    "entities": intent_result.entities,
                    "objectives": intent_result.objectives,
                    "reasoning": intent_result.reasoning,
                    "swarm_agreement": intent_result.swarm_agreement,
                    "classification_metadata": intent_result.classification_metadata
                },
                "6_agent_analysis": {
                    "description": "This result shows the REAL 6-agent swarm intelligence system in action",
                    "agents_used": [
                        "Operations Research Specialist",
                        "Production Systems Specialist", 
                        "Supply Chain Specialist",
                        "Quality Control Specialist",
                        "Sustainability Specialist",
                        "Cost Optimization Specialist"
                    ],
                    "consensus_mechanism": "Majority agreement with confidence scoring",
                    "swarm_agreement_score": intent_result.swarm_agreement
                }
            }
            
            logger.info(f"✅ 6-agent intent classification completed: {intent_result.primary_intent.value} (confidence: {intent_result.confidence}, swarm agreement: {intent_result.swarm_agreement})")
            
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
            
        except Exception as e:
            logger.error(f"❌ Intent classification failed: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Intent classification failed: {str(e)}"
                }
            }

# Create FastAPI app
server = DcisionAI_MCP_Server_v4_Simple()

# Simple HTTP server for testing
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title=server.server_name, version=server.version)

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP requests."""
    try:
        data = await request.json()
        method = data.get("method")
        request_id = data.get("id")
        params = data.get("params", {})

        if method == "initialize":
            return await server.handle_initialize(request_id, params)
        elif method == "tools/list":
            return await server.handle_tools_list(request_id)
        elif method == "tools/call":
            return await server.handle_tools_call(request_id, params)
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            })

    except Exception as e:
        logger.error(f"❌ Error handling request: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        })

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": server.server_name,
        "version": server.version,
        "capabilities": [
            "manufacturing_optimization_status",
            "classify_intent"
        ],
        "tools_available": {
            "intent_tool": server.intent_tool is not None,
            "data_tool": False,
            "model_tool": False,
            "solver_tool": False,
            "manufacturing_agent": False
        },
        "6_agent_system": "REAL - Operational",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info(f"🚀 Starting {server.server_name} on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
