#!/usr/bin/env python3
"""
DcisionAI MCP Server v2 Enhanced - With Real Manufacturing Tools
A clean MCP server that includes actual manufacturing optimization capabilities.
No fallback logic - either it works or it doesn't.
"""

import asyncio
import json
import logging
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime

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

class DcisionAI_MCP_Server_v2_Enhanced:
    """Enhanced DcisionAI MCP Server v2 - With Real Manufacturing Tools."""
    
    def __init__(self):
        self.server_name = "DcisionAI MCP Server v2 Enhanced"
        self.version = "2.1.0"
        self.initialized = False
        
        # Initialize manufacturing tools
        self.intent_tool = None
        self.data_tool = None
        self.model_tool = None
        self.solver_tool = None
        
        try:
            # Import and initialize tools
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
            # Don't raise exception - continue with basic functionality
        
        logger.info("✅ MCP Server v2 Enhanced initialized successfully")
    
    async def handle_initialize(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        try:
            self.initialized = True
            logger.info(f"✅ MCP Server v2 Enhanced initialized successfully")
            
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
                    "description": "Get the current status of manufacturing optimization capabilities",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Status query (e.g., 'check optimization tools')"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "analyze_manufacturing_optimization",
                    "description": "Analyze manufacturing optimization problems using intent classification, data analysis, model building, and solver execution",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Manufacturing optimization query (e.g., 'optimize production line efficiency')"
                            },
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier for tracking"
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
                query = arguments.get("query", "")
                
                logger.info(f"🔧 Executing manufacturing optimization status check: {query}")
                
                # Return current status
                result = {
                    "status": "operational",
                    "server": self.server_name,
                    "version": self.version,
                    "capabilities": {
                        "intent_classification": "available" if self.intent_tool else "not_available",
                        "data_analysis": "available" if self.data_tool else "not_available", 
                        "model_building": "available" if self.model_tool else "not_available",
                        "optimization_solving": "available" if self.solver_tool else "not_available",
                        "visualization": "roadmap"
                    },
                    "message": "DcisionAI MCP Server v2 Enhanced is operational and ready for manufacturing optimization queries"
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
                
            elif tool_name == "analyze_manufacturing_optimization":
                query = arguments.get("query", "")
                session_id = arguments.get("session_id", "default")
                
                logger.info(f"🔧 Executing manufacturing optimization analysis: {query}")
                
                # Execute the full optimization workflow
                workflow_result = await self._execute_optimization_workflow(query, session_id)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(workflow_result, indent=2)
                            }
                        ]
                    }
                }
            else:
                raise Exception(f"Unknown tool: {tool_name}")
                
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
    
    async def _execute_optimization_workflow(self, query: str, session_id: str) -> Dict[str, Any]:
        """Execute the full manufacturing optimization workflow."""
        workflow_result = {
            "workflow_id": f"workflow_{session_id}_{datetime.now().isoformat()}",
            "query": query,
            "session_id": session_id,
            "execution_time": 0.0,
            "stages": {}
        }
        
        start_time = datetime.now()
        
        # Stage 1: Intent Classification
        if self.intent_tool:
            try:
                logger.info("🔍 Stage 1: Intent Classification")
                intent_result = self.intent_tool.classify_intent(query=query)
                workflow_result["stages"]["intent_classification"] = {
                    "status": "success",
                    "primary_intent": str(intent_result.primary_intent),
                    "confidence": intent_result.confidence,
                    "entities": intent_result.entities,
                    "objectives": intent_result.objectives,
                    "reasoning": intent_result.reasoning
                }
            except Exception as e:
                logger.error(f"❌ Intent classification failed: {e}")
                workflow_result["stages"]["intent_classification"] = {
                    "status": "failed",
                    "error": str(e)
                }
        else:
            workflow_result["stages"]["intent_classification"] = {
                "status": "not_available",
                "message": "Intent tool not initialized"
            }
        
        # Stage 2: Data Analysis
        if self.data_tool:
            try:
                logger.info("📊 Stage 2: Data Analysis")
                data_result = self.data_tool.analyze_manufacturing_data(
                    query=query,
                    session_id=session_id
                )
                workflow_result["stages"]["data_analysis"] = {
                    "status": "success",
                    "data_insights": data_result.get("insights", []),
                    "data_quality": data_result.get("quality_assessment", {}),
                    "recommendations": data_result.get("recommendations", [])
                }
            except Exception as e:
                logger.error(f"❌ Data analysis failed: {e}")
                workflow_result["stages"]["data_analysis"] = {
                    "status": "failed",
                    "error": str(e)
                }
        else:
            workflow_result["stages"]["data_analysis"] = {
                "status": "not_available",
                "message": "Data tool not initialized"
            }
        
        # Stage 3: Model Building
        if self.model_tool:
            try:
                logger.info("🏗️ Stage 3: Model Building")
                model_result = self.model_tool.build_optimization_model(
                    query=query,
                    session_id=session_id
                )
                workflow_result["stages"]["model_building"] = {
                    "status": "success",
                    "model_type": model_result.get("model_type", "unknown"),
                    "variables": model_result.get("variables", []),
                    "constraints": model_result.get("constraints", []),
                    "objective": model_result.get("objective", "")
                }
            except Exception as e:
                logger.error(f"❌ Model building failed: {e}")
                workflow_result["stages"]["model_building"] = {
                    "status": "failed",
                    "error": str(e)
                }
        else:
            workflow_result["stages"]["model_building"] = {
                "status": "not_available",
                "message": "Model tool not initialized"
            }
        
        # Stage 4: Solver Execution
        if self.solver_tool:
            try:
                logger.info("⚡ Stage 4: Solver Execution")
                solver_result = self.solver_tool.solve_optimization_problem(
                    query=query,
                    session_id=session_id
                )
                workflow_result["stages"]["solver_execution"] = {
                    "status": "success",
                    "solver_used": solver_result.get("solver_used", "unknown"),
                    "solve_time": solver_result.get("solve_time", "unknown"),
                    "optimal_solution": solver_result.get("optimal_solution", False),
                    "objective_value": solver_result.get("objective_value", "unknown")
                }
            except Exception as e:
                logger.error(f"❌ Solver execution failed: {e}")
                workflow_result["stages"]["solver_execution"] = {
                    "status": "failed",
                    "error": str(e)
                }
        else:
            workflow_result["stages"]["solver_execution"] = {
                "status": "not_available",
                "message": "Solver tool not initialized"
            }
        
        # Calculate execution time
        end_time = datetime.now()
        workflow_result["execution_time"] = (end_time - start_time).total_seconds()
        
        # Overall status
        successful_stages = sum(1 for stage in workflow_result["stages"].values() if stage.get("status") == "success")
        total_stages = len(workflow_result["stages"])
        workflow_result["overall_status"] = "success" if successful_stages == total_stages else "partial_success"
        workflow_result["success_rate"] = f"{successful_stages}/{total_stages}"
        
        return workflow_result

# Create FastAPI app
server = DcisionAI_MCP_Server_v2_Enhanced()

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
        "tools_available": {
            "intent_tool": server.intent_tool is not None,
            "data_tool": server.data_tool is not None,
            "model_tool": server.model_tool is not None,
            "solver_tool": server.solver_tool is not None
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info(f"🚀 Starting {server.server_name} on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
