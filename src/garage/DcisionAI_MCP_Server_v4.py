#!/usr/bin/env python3
"""
DcisionAI MCP Server v4 - Real Manufacturing Tools with Strands Framework
A production-ready MCP server that integrates the actual manufacturing optimization tools.
Uses the real 6-agent swarm intelligence system for intent classification.
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

class DcisionAI_MCP_Server_v4:
    """DcisionAI MCP Server v4 - Real Manufacturing Tools with Strands Framework."""
    
    def __init__(self):
        self.server_name = "DcisionAI MCP Server v4"
        self.version = "4.0.0"
        self.initialized = False
        
        # Initialize manufacturing tools
        self.intent_tool = None
        self.data_tool = None
        self.model_tool = None
        self.solver_tool = None
        self.manufacturing_agent = None
        
        try:
            # Import and initialize the real manufacturing tools
            logger.info("🔧 Initializing real manufacturing tools with strands framework...")
            
            # Import the actual manufacturing agent
            from models.manufacturing.DcisionAI_Manufacturing_Agent import DcisionAI_Manufacturing_Agent
            self.manufacturing_agent = DcisionAI_Manufacturing_Agent()
            logger.info("✅ Manufacturing agent initialized successfully")
            
            # Import individual tools for direct access
            from models.manufacturing.tools.intent.DcisionAI_Intent_Tool_v6 import create_dcisionai_intent_tool_v6
            from models.manufacturing.tools.data.DcisionAI_Data_Tool_v3 import create_dcisionai_data_tool_v3
            from models.manufacturing.tools.model.DcisionAI_Model_Builder_v1 import create_dcisionai_model_builder_v1
            from shared.tools.solver.solver_tool_optimized import create_solver_tool_optimized
            
            self.intent_tool = create_dcisionai_intent_tool_v6()
            self.data_tool = create_dcisionai_data_tool_v3()
            self.model_tool = create_dcisionai_model_builder_v1()
            self.solver_tool = create_solver_tool_optimized()
            
            logger.info("✅ All manufacturing tools initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize manufacturing tools: {e}")
            raise Exception(f"Manufacturing tools initialization failed: {e}")
        
        logger.info("✅ MCP Server v4 initialized successfully")
    
    async def handle_initialize(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        try:
            self.initialized = True
            logger.info("✅ MCP Server v4 initialized")
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
                    "description": "Check the status of the DcisionAI MCP server and available tools",
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
                    "name": "analyze_manufacturing_optimization",
                    "description": "Analyze a manufacturing optimization query using the real 6-agent swarm intelligence system",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The manufacturing optimization query to analyze"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "classify_intent",
                    "description": "Classify manufacturing intent using the 6-agent swarm intelligence system",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The query to classify"
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
            elif tool_name == "analyze_manufacturing_optimization":
                return await self._handle_optimization_analysis(request_id, arguments)
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
                "intent_classification": "6-agent swarm intelligence",
                "data_analysis": "real manufacturing data tool",
                "model_building": "real optimization model builder",
                "optimization_solving": "real solver with multiple backends",
                "visualization": "roadmap generation"
            },
            "tools_available": {
                "intent_tool": self.intent_tool is not None,
                "data_tool": self.data_tool is not None,
                "model_tool": self.model_tool is not None,
                "solver_tool": self.solver_tool is not None,
                "manufacturing_agent": self.manufacturing_agent is not None
            },
            "message": f"{self.server_name} is operational with real manufacturing tools and 6-agent swarm intelligence"
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
                }
            }
            
            logger.info(f"✅ Intent classification completed: {intent_result.primary_intent.value} (confidence: {intent_result.confidence})")
            
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
    
    async def _handle_optimization_analysis(self, request_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle full manufacturing optimization analysis using real tools."""
        query = arguments.get("query", "")
        
        if not query:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Query is required for optimization analysis"
                }
            }
        
        try:
            logger.info(f"🔍 Analyzing optimization query: {query}")
            
            # Use the real manufacturing agent's full workflow
            result = self.manufacturing_agent.analyze_manufacturing_optimization(query)
            
            # Convert to JSON-serializable format
            analysis_result = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "analysis": result,
                "summary": {
                    "status": "completed",
                    "tools_used": [
                        "6-agent intent classification",
                        "manufacturing data analysis", 
                        "optimization model building",
                        "solver execution"
                    ]
                }
            }
            
            logger.info(f"✅ Full optimization analysis completed for: {query}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(analysis_result, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Optimization analysis failed: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Optimization analysis failed: {str(e)}"
                }
            }

# Create FastAPI app
server = DcisionAI_MCP_Server_v4()

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
            "analyze_manufacturing_optimization",
            "classify_intent"
        ],
        "tools_available": {
            "intent_tool": server.intent_tool is not None,
            "data_tool": server.data_tool is not None,
            "model_tool": server.model_tool is not None,
            "solver_tool": server.solver_tool is not None,
            "manufacturing_agent": server.manufacturing_agent is not None
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info(f"🚀 Starting {server.server_name} on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
