#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server for AgentCore Deployment
Follows AWS AgentCore MCP documentation pattern
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our manufacturing tools
try:
    from mcp_server.tools.manufacturing.intent.DcisionAI_Intent_Tool import DcisionAI_Intent_Tool
    from mcp_server.tools.manufacturing.data.DcisionAI_Data_Tool import DataTool
    from mcp_server.tools.manufacturing.model.DcisionAI_Model_Builder import ModelBuilderTool
    from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import SolverTool
    logger.info("✅ All manufacturing tools imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import manufacturing tools: {e}")
    raise

class DcisionAIMCPServer:
    """MCP Server for DcisionAI Manufacturing Tools"""
    
    def __init__(self):
        """Initialize the MCP server with all manufacturing tools"""
        self.tools = {
            "intent": DcisionAI_Intent_Tool(),
            "data": DataTool(),
            "model": ModelBuilderTool(),
            "solver": SolverTool()
        }
        logger.info(f"✅ MCP Server initialized with {len(self.tools)} tools")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": "intent_analysis",
                "description": "Analyze user intent using specialist agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "User query to analyze"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "data_analysis",
                "description": "Analyze data requirements and generate sample data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "intent": {"type": "string", "description": "Intent category from intent analysis"},
                        "query": {"type": "string", "description": "Original user query"}
                    },
                    "required": ["intent", "query"]
                }
            },
            {
                "name": "model_building",
                "description": "Build optimization models based on intent and data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "intent": {"type": "string", "description": "Intent category"},
                        "data_entities": {"type": "array", "items": {"type": "string"}},
                        "query": {"type": "string", "description": "Original user query"}
                    },
                    "required": ["intent", "data_entities", "query"]
                }
            },
            {
                "name": "solver_execution",
                "description": "Execute optimization using available solvers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model_type": {"type": "string", "description": "Type of optimization model"},
                        "constraints": {"type": "array", "items": {"type": "object"}},
                        "objective": {"type": "object", "description": "Objective function"}
                    },
                    "required": ["model_type", "constraints", "objective"]
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool by name"""
        try:
            if name == "intent_analysis":
                result = await self.tools["intent"].analyze_intent(arguments["query"])
                return {"success": True, "result": result}
            
            elif name == "data_analysis":
                result = await self.tools["data"].analyze_data(
                    intent=arguments["intent"],
                    query=arguments["query"]
                )
                return {"success": True, "result": result}
            
            elif name == "model_building":
                result = await self.tools["model"].build_model(
                    intent=arguments["intent"],
                    data_entities=arguments["data_entities"],
                    query=arguments["query"]
                )
                return {"success": True, "result": result}
            
            elif name == "solver_execution":
                result = await self.tools["solver"].solve_optimization(
                    model_type=arguments["model_type"],
                    constraints=arguments["constraints"],
                    objective=arguments["objective"]
                )
                return {"success": True, "result": result}
            
            else:
                return {"success": False, "error": f"Unknown tool: {name}"}
                
        except Exception as e:
            logger.error(f"❌ Error calling tool {name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming MCP requests"""
        try:
            method = request.get("method")
            
            if method == "tools/list":
                tools = await self.list_tools()
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"tools": tools}
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await self.call_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }

# Create global server instance
mcp_server = DcisionAIMCPServer()

async def handle_request(request_data: str) -> str:
    """Handle incoming request and return response"""
    try:
        request = json.loads(request_data)
        response = await mcp_server.process_request(request)
        return json.dumps(response)
    except Exception as e:
        logger.error(f"❌ Error handling request: {e}")
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
        })

# For local testing
if __name__ == "__main__":
    async def test_server():
        """Test the MCP server locally"""
        logger.info("🧪 Testing MCP server locally...")
        
        # Test list tools
        tools = await mcp_server.list_tools()
        logger.info(f"📋 Available tools: {[t['name'] for t in tools]}")
        
        # Test intent analysis
        test_query = "I need to optimize my production schedule to minimize costs while meeting customer demand"
        result = await mcp_server.call_tool("intent_analysis", {"query": test_query})
        logger.info(f"🧠 Intent analysis result: {result.get('success', False)}")
        
        logger.info("✅ Local test completed")
    
    asyncio.run(test_server())
