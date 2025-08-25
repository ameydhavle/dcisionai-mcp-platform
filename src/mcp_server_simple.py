#!/usr/bin/env python3
"""
DcisionAI Simple MCP Server
===========================

A simplified MCP server that works without complex dependencies.
This provides the core MCP protocol functionality for testing.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    """Simple MCP server implementation."""
    
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
    
    async def handle_request(self, request_data: str) -> Optional[str]:
        """Handle incoming MCP request."""
        try:
            request = json.loads(request_data)
            method = request.get("method")
            params = request.get("params", {})
            
            logger.info(f"Handling request: {method}")
            
            if method == "initialize":
                response = await self.handle_initialize(request)
            elif method == "tools/list":
                response = await self.handle_tools_list(request)
            elif method == "tools/call":
                response = await self.handle_tools_call(request)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return json.dumps(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            })
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            })

async def main():
    """Main entry point."""
    server = SimpleMCPServer()
    
    logger.info("Starting DcisionAI Simple MCP Server")
    logger.info("Reading from stdin, writing to stdout")
    
    try:
        while True:
            # Read line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            # Process the request
            response = await server.handle_request(line)
            
            # Send response if any
            if response:
                print(response, flush=True)
                # Also flush stderr to ensure logs are written
                sys.stderr.flush()
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
