#!/usr/bin/env python3
"""
DcisionAI Fallback MCP Server
=============================

A fallback MCP server that shows all 6 tool responses
even without the strands framework, using enhanced dummy responses
that demonstrate the complete manufacturing optimization workflow.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DcisionAI Fallback MCP Server",
    description="Fallback MCP server showing all 6 tool responses",
    version="2.1.0"
)

class FallbackMCPServer:
    """Fallback MCP server with enhanced dummy responses for all 6 tools."""
    
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
        
        logger.info("✅ Fallback MCP server initialized with enhanced dummy responses")
    
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
                    "name": "DcisionAI Fallback MCP Server",
                    "version": "2.1.0",
                    "manufacturing_agent_available": False,
                    "fallback_mode": True
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
        """Handle complete manufacturing optimization workflow with all 6 tool responses."""
        query = arguments.get("query", "")
        session_id = arguments.get("session_id", "default")
        include_all_tools = arguments.get("include_all_tools", True)
        
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())
        
        try:
            # Simulate the complete workflow with all 6 tools
            start_time = datetime.utcnow()
            
            # Tool 1: Intent Classification (6-agent swarm)
            intent_result = await self._generate_intent_classification(query, session_id)
            
            # Tool 2: Data Analysis (3-stage analysis)
            data_result = await self._generate_data_analysis(query, intent_result, session_id)
            
            # Tool 3: Model Building (6-specialist swarm)
            model_result = await self._generate_model_building(intent_result, data_result, session_id)
            
            # Tool 4: Solver Execution (shared solver swarm)
            solver_result = await self._generate_solver_execution(model_result, session_id)
            
            # Tool 5: Visualization (roadmap - not implemented)
            visualization_result = {
                "status": "roadmap",
                "tool_name": "visualization",
                "message": "Visualization tool is on roadmap - not yet implemented",
                "capabilities": [
                    "Interactive dashboards",
                    "Real-time monitoring",
                    "Performance analytics",
                    "Trend visualization"
                ]
            }
            
            # Tool 6: Swarm Orchestration (coordination)
            swarm_result = {
                "status": "success",
                "tool_name": "swarm_orchestration",
                "agents_coordinated": 6,
                "coordination_pattern": "peer-to-peer",
                "performance_metrics": {
                    "total_execution_time": "2.3s",
                    "agent_utilization": "87%",
                    "communication_overhead": "12%",
                    "optimization_quality": "94%"
                },
                "swarm_intelligence": {
                    "collective_decision_making": True,
                    "adaptive_learning": True,
                    "emergent_behavior": True,
                    "robustness": "high"
                }
            }
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Format the complete response with all 6 tool results
            response_data = {
                "status": "success",
                "workflow_id": workflow_id,
                "query": query,
                "session_id": session_id,
                "current_stage": "analysis_complete",
                "execution_time": execution_time,
                "errors": [],
                "warnings": ["Using fallback mode - strands framework not available"],
                "tool_results": {
                    "intent_classification": intent_result,
                    "data_analysis": data_result,
                    "model_building": model_result,
                    "solver_results": solver_result,
                    "visualization": visualization_result,
                    "swarm_orchestration": swarm_result
                },
                "workflow_summary": {
                    "total_tools_executed": 6,
                    "tools_available": 4,
                    "tools_roadmap": 1,
                    "tools_coordination": 1,
                    "optimization_readiness": "ready",
                    "next_steps": [
                        "Implement visualization tool",
                        "Deploy to production environment",
                        "Add customer-specific optimizations"
                    ]
                }
            }
            
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
    
    async def _generate_intent_classification(self, query: str, session_id: str) -> Dict[str, Any]:
        """Generate enhanced intent classification response."""
        query_lower = query.lower()
        
        # Enhanced intent classification with 6-agent swarm simulation
        if any(word in query_lower for word in ["optimize", "production", "line", "cycle", "time"]):
            intent = "PRODUCTION_SCHEDULING"
            confidence = 0.92
            reasoning = "Query contains production optimization keywords"
            agents_used = ["scheduling_specialist", "efficiency_analyst", "workflow_optimizer"]
        elif any(word in query_lower for word in ["waste", "minimize", "cost", "reduce"]):
            intent = "COST_OPTIMIZATION"
            confidence = 0.88
            reasoning = "Query contains cost and waste reduction keywords"
            agents_used = ["cost_analyst", "waste_reduction_specialist", "efficiency_optimizer"]
        elif any(word in query_lower for word in ["quality", "control", "defect", "inspection"]):
            intent = "QUALITY_CONTROL"
            confidence = 0.95
            reasoning = "Query contains quality control keywords"
            agents_used = ["quality_specialist", "defect_analyst", "inspection_optimizer"]
        elif any(word in query_lower for word in ["energy", "consumption", "environmental", "sustainability"]):
            intent = "ENVIRONMENTAL_OPTIMIZATION"
            confidence = 0.90
            reasoning = "Query contains environmental optimization keywords"
            agents_used = ["environmental_specialist", "energy_analyst", "sustainability_optimizer"]
        elif any(word in query_lower for word in ["inventory", "stock", "management", "supply"]):
            intent = "INVENTORY_OPTIMIZATION"
            confidence = 0.87
            reasoning = "Query contains inventory management keywords"
            agents_used = ["inventory_specialist", "supply_chain_analyst", "stock_optimizer"]
        else:
            intent = "GENERAL_MANUFACTURING"
            confidence = 0.75
            reasoning = "Query appears to be general manufacturing related"
            agents_used = ["general_manufacturing_specialist", "process_analyst", "optimization_coordinator"]
        
        return {
            "status": "success",
            "tool_name": "intent_classification",
            "primary_intent": intent,
            "confidence": confidence,
            "reasoning": reasoning,
            "entities": ["manufacturing", "optimization", "efficiency"],
            "objectives": ["improve efficiency", "reduce costs", "enhance quality"],
            "agents_used": agents_used,
            "swarm_consensus": True,
            "classification_metadata": {
                "processing_time": "0.15s",
                "agents_consulted": 6,
                "consensus_threshold": 0.8,
                "classification_quality": "high"
            }
        }
    
    async def _generate_data_analysis(self, query: str, intent_result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Generate enhanced data analysis response."""
        intent = intent_result.get("primary_intent", "GENERAL_MANUFACTURING")
        
        # Enhanced data analysis with 3-stage analysis simulation
        data_requirements = {
            "PRODUCTION_SCHEDULING": [
                {"category": "production_data", "type": "cycle_times", "priority": "high"},
                {"category": "production_data", "type": "setup_times", "priority": "high"},
                {"category": "production_data", "type": "demand_forecasts", "priority": "medium"},
                {"category": "resource_data", "type": "machine_capacity", "priority": "high"},
                {"category": "resource_data", "type": "labor_availability", "priority": "medium"}
            ],
            "COST_OPTIMIZATION": [
                {"category": "cost_data", "type": "material_costs", "priority": "high"},
                {"category": "cost_data", "type": "labor_costs", "priority": "high"},
                {"category": "cost_data", "type": "overhead_costs", "priority": "medium"},
                {"category": "waste_data", "type": "scrap_rates", "priority": "high"},
                {"category": "waste_data", "type": "rework_rates", "priority": "high"}
            ],
            "QUALITY_CONTROL": [
                {"category": "quality_data", "type": "defect_rates", "priority": "high"},
                {"category": "quality_data", "type": "inspection_results", "priority": "high"},
                {"category": "quality_data", "type": "customer_complaints", "priority": "medium"},
                {"category": "process_data", "type": "control_charts", "priority": "high"},
                {"category": "process_data", "type": "capability_studies", "priority": "medium"}
            ]
        }
        
        requirements = data_requirements.get(intent, data_requirements["PRODUCTION_SCHEDULING"])
        
        return {
            "status": "success",
            "tool_name": "data_analysis",
            "query_data_requirements": requirements,
            "critical_data_gaps": [
                "Real-time production monitoring data",
                "Historical performance metrics",
                "Supplier quality data"
            ],
            "optimization_readiness": "ready",
            "data_quality_score": 0.85,
            "analysis_stages": [
                {
                    "stage": "requirement_analysis",
                    "status": "completed",
                    "findings": "Identified 5 critical data requirements"
                },
                {
                    "stage": "gap_analysis", 
                    "status": "completed",
                    "findings": "Found 3 critical data gaps"
                },
                {
                    "stage": "readiness_assessment",
                    "status": "completed", 
                    "findings": "System ready for optimization"
                }
            ],
            "execution_metadata": {
                "stages_completed": 3,
                "execution_time": 0.8,
                "agents_used": ["data_requirement_analyst", "gap_identification_specialist", "readiness_assessor"]
            }
        }
    
    async def _generate_model_building(self, intent_result: Dict[str, Any], data_result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Generate enhanced model building response."""
        intent = intent_result.get("primary_intent", "GENERAL_MANUFACTURING")
        
        # Enhanced model building with 6-specialist swarm simulation
        model_configs = {
            "PRODUCTION_SCHEDULING": {
                "model_type": "MIXED_INTEGER_LINEAR_PROGRAMMING",
                "decision_variables": [
                    {"name": "production_quantity", "type": "integer", "bounds": [0, 1000]},
                    {"name": "setup_time", "type": "continuous", "bounds": [0, 24]},
                    {"name": "machine_assignment", "type": "binary", "bounds": [0, 1]}
                ],
                "constraints": [
                    {"name": "capacity_constraint", "type": "inequality", "expression": "sum(production) <= capacity"},
                    {"name": "demand_constraint", "type": "equality", "expression": "production >= demand"}
                ],
                "objective": "minimize_total_cost"
            },
            "COST_OPTIMIZATION": {
                "model_type": "LINEAR_PROGRAMMING",
                "decision_variables": [
                    {"name": "material_usage", "type": "continuous", "bounds": [0, 1000]},
                    {"name": "labor_hours", "type": "continuous", "bounds": [0, 168]},
                    {"name": "waste_reduction", "type": "continuous", "bounds": [0, 100]}
                ],
                "constraints": [
                    {"name": "budget_constraint", "type": "inequality", "expression": "total_cost <= budget"},
                    {"name": "quality_constraint", "type": "inequality", "expression": "quality_score >= min_quality"}
                ],
                "objective": "minimize_total_cost"
            }
        }
        
        model_config = model_configs.get(intent, model_configs["PRODUCTION_SCHEDULING"])
        
        return {
            "status": "success",
            "tool_name": "model_building",
            "model": {
                "model_id": f"model_{session_id}_{intent.lower()}",
                "model_name": f"{intent} Optimization Model",
                "model_type": model_config["model_type"],
                "intent_classification": intent,
                "decision_variables": model_config["decision_variables"],
                "constraints": model_config["constraints"],
                "objective_functions": [{"name": "primary_objective", "sense": "minimize", "expression": model_config["objective"]}],
                "data_schema": {
                    "parameters": ["demand", "capacity", "costs"],
                    "sets": ["products", "machines", "time_periods"],
                    "scalars": ["budget", "quality_threshold"]
                },
                "compatible_solvers": ["CPLEX", "GUROBI", "SCIP"],
                "recommended_solver": "CPLEX",
                "model_complexity": "medium",
                "estimated_solve_time": "5-15 seconds",
                "model_validation_score": 0.92,
                "generation_metadata": {
                    "agents_used": ["model_architect", "constraint_specialist", "variable_optimizer", "objective_analyst", "solver_advisor", "validation_expert"],
                    "build_time": 1.2,
                    "complexity_assessment": "medium"
                }
            },
            "build_status": "completed",
            "execution_time": 1.2,
            "agents_used": 6
        }
    
    async def _generate_solver_execution(self, model_result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Generate enhanced solver execution response."""
        model = model_result.get("model", {})
        model_type = model.get("model_type", "MIXED_INTEGER_LINEAR_PROGRAMMING")
        
        # Enhanced solver execution with shared solver swarm simulation
        solver_results = {
            "MIXED_INTEGER_LINEAR_PROGRAMMING": {
                "solver_used": "CPLEX",
                "solution_status": "optimal",
                "objective_value": 125000,
                "solve_time": 8.5,
                "iterations": 1250,
                "gap": 0.001
            },
            "LINEAR_PROGRAMMING": {
                "solver_used": "GUROBI", 
                "solution_status": "optimal",
                "objective_value": 89000,
                "solve_time": 3.2,
                "iterations": 450,
                "gap": 0.0001
            }
        }
        
        solver_result = solver_results.get(model_type, solver_results["MIXED_INTEGER_LINEAR_PROGRAMMING"])
        
        return {
            "status": "success",
            "tool_name": "solver_execution",
            "solver_results": {
                "solver_used": solver_result["solver_used"],
                "solution_status": solver_result["solution_status"],
                "objective_value": solver_result["objective_value"],
                "solve_time": solver_result["solve_time"],
                "iterations": solver_result["iterations"],
                "gap": solver_result["gap"],
                "best_solution": {
                    "production_quantity": 850,
                    "setup_time": 2.5,
                    "machine_assignment": [1, 0, 1, 0, 1],
                    "total_cost": solver_result["objective_value"],
                    "efficiency_improvement": "23%"
                },
                "performance_metrics": {
                    "solution_quality": 0.94,
                    "computational_efficiency": 0.87,
                    "scalability_score": 0.91
                }
            },
            "execution_time": solver_result["solve_time"],
            "agents_used": ["solver_coordinator", "performance_analyst", "solution_validator", "optimization_monitor"]
        }
    
    async def _handle_intent_classification(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle intent classification."""
        query = arguments.get("query", "")
        session_id = arguments.get("session_id", "default")
        
        result = await self._generate_intent_classification(query, session_id)
        
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
    
    async def _handle_data_analysis(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle data analysis."""
        query = arguments.get("query", "")
        intent_classification = arguments.get("intent_classification", "")
        session_id = arguments.get("session_id", "default")
        
        # Parse intent classification if it's a string
        if isinstance(intent_classification, str):
            try:
                intent_data = json.loads(intent_classification)
            except:
                intent_data = {"primary_intent": "GENERAL_MANUFACTURING"}
        else:
            intent_data = intent_classification
        
        result = await self._generate_data_analysis(query, intent_data, session_id)
        
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
    
    async def _handle_model_building(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle model building."""
        intent_result = arguments.get("intent_result", "")
        data_result = arguments.get("data_result", "")
        session_id = arguments.get("session_id", "default")
        
        # Parse results if they're strings
        if isinstance(intent_result, str):
            try:
                intent_data = json.loads(intent_result)
            except:
                intent_data = {"primary_intent": "GENERAL_MANUFACTURING"}
        else:
            intent_data = intent_result
        
        if isinstance(data_result, str):
            try:
                data_data = json.loads(data_result)
            except:
                data_data = {}
        else:
            data_data = data_result
        
        result = await self._generate_model_building(intent_data, data_data, session_id)
        
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
    
    async def _handle_solver_execution(self, arguments: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Handle solver execution."""
        model_result = arguments.get("model_result", "")
        session_id = arguments.get("session_id", "default")
        
        # Parse model result if it's a string
        if isinstance(model_result, str):
            try:
                model_data = json.loads(model_result)
            except:
                model_data = {"model": {"model_type": "MIXED_INTEGER_LINEAR_PROGRAMMING"}}
        else:
            model_data = model_result
        
        result = await self._generate_solver_execution(model_data, session_id)
        
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
mcp_server = FallbackMCPServer()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer."""
    return {
        "status": "healthy",
        "service": "DcisionAI Fallback MCP Server",
        "version": "2.1.0",
        "manufacturing_agent_available": False,
        "fallback_mode": True,
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
        "service": "DcisionAI Fallback MCP Server",
        "version": "2.1.0",
        "manufacturing_agent_available": False,
        "fallback_mode": True,
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
        ],
        "tool_responses": "All 6 agent responses included in workflow"
    }

if __name__ == "__main__":
    # Get configuration from environment
    host = "0.0.0.0"
    port = 8080
    
    logger.info(f"Starting DcisionAI Fallback MCP Server on {host}:{port}")
    logger.info("✅ Fallback mode enabled - showing all 6 tool responses")
    
    # Run the server
    uvicorn.run(app, host=host, port=port, log_level="info")
