#!/usr/bin/env python3
"""
DcisionAI MCP Server - FastMCP Implementation for AWS AgentCore
==============================================================

Production-ready FastMCP implementation for AWS AgentCore compatibility.
Integrates all manufacturing tools with proper error handling and logging.

Based on AWS AgentCore MCP documentation and production architecture.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import asdict

# Import FastMCP for AWS AgentCore compatibility
try:
    from mcp.server.fastmcp import FastMCP
    from starlette.responses import JSONResponse
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("Error: FastMCP not available. Please install with: pip install mcp")

# Import configuration and utilities
from .config.settings import settings
from .utils.logging import get_logger

# Import manufacturing tools with correct paths
from .tools.manufacturing.intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool_v6
from .tools.manufacturing.data.DcisionAI_Data_Tool import create_data_tool
from .tools.manufacturing.model.DcisionAI_Model_Builder import create_model_builder_tool
from .tools.manufacturing.solver import create_shared_solver_tool


class DcisionAIFastMCPServer:
    """Production-ready FastMCP server for DcisionAI manufacturing tools."""
    
    def __init__(self):
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP is required for AWS AgentCore deployment")
        
        # Initialize FastMCP with production settings
        self.mcp = FastMCP(
            host=settings.server_host,
            stateless_http=True
        )
        
        # Setup logging
        self.logger = get_logger(__name__)
        
        # Initialize tool instances
        self._initialize_tools()
        
        # Register all tools
        self._register_tools()
        
        self.logger.info("DcisionAI FastMCP Server initialized successfully")
    
    def _initialize_tools(self):
        """Initialize all manufacturing tool instances."""
        try:
            self.logger.info("Initializing manufacturing tools...")
            
            # Initialize intent classification tool
            self.intent_tool = create_dcisionai_intent_tool_v6()
            self.logger.info("✅ Intent classification tool initialized")
            
            # Initialize data analysis tool
            self.data_tool = create_data_tool()
            self.logger.info("✅ Data analysis tool initialized")
            
            # Initialize model builder tool
            self.model_tool = create_model_builder_tool()
            self.logger.info("✅ Model builder tool initialized")
            
            # Initialize solver tool
            self.solver_tool = create_shared_solver_tool()
            self.logger.info("✅ Solver tool initialized")
            
            self.logger.info("All manufacturing tools initialized successfully")
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize tools: {e}")
            raise
    
    def _register_tools(self):
        """Register all manufacturing tools with FastMCP."""
        try:
            self.logger.info("Registering manufacturing tools with FastMCP...")
            
            # Register intent classification tool
            @self.mcp.tool()
            def classify_manufacturing_intent(
                query: str,
                include_confidence: bool = True,
                include_reasoning: bool = True
            ) -> Dict[str, Any]:
                """
                Classify manufacturing optimization queries using 6-agent swarm system.
                
                Args:
                    query: Manufacturing optimization query to classify
                    include_confidence: Include confidence scores in response
                    include_reasoning: Include reasoning in response
                
                Returns:
                    Classification result with intent analysis, confidence, and reasoning
                """
                try:
                    self.logger.info(f"Processing intent classification for query: {query[:100]}...")
                    
                    # Execute intent classification
                    result = self.intent_tool.classify_intent(query)
                    
                    # Convert dataclass to dict for JSON serialization
                    response = asdict(result)
                    
                    # Add metadata
                    response["tool_name"] = "classify_manufacturing_intent"
                    response["version"] = "v6"
                    response["timestamp"] = result.classification_metadata.get("timestamp", "")
                    
                    self.logger.info(f"Intent classification completed: {result.primary_intent.value} (confidence: {result.confidence})")
                    return response
                        
                except Exception as e:
                    self.logger.exception(f"Intent classification error: {e}")
                    return {
                        "error": f"Classification failed: {str(e)}",
                        "tool_name": "classify_manufacturing_intent",
                        "status": "error"
                    }
            
            # Register data requirements analysis tool
            @self.mcp.tool()
            def analyze_data_requirements(
                query: str,
                intent_result: Optional[Dict[str, Any]] = None
            ) -> Dict[str, Any]:
                """
                Analyze data requirements for manufacturing optimization.
                
                Args:
                    query: Manufacturing optimization query
                    intent_result: Optional intent classification result
                
                Returns:
                    Data requirements analysis with recommendations
                """
                try:
                    self.logger.info(f"Analyzing data requirements for query: {query[:100]}...")
                    
                    # Execute data analysis
                    result = self.data_tool.analyze_data_requirements(query, intent_result)
                    
                    # Convert dataclass to dict for JSON serialization
                    response = asdict(result)
                    
                    # Add metadata
                    response["tool_name"] = "analyze_data_requirements"
                    response["version"] = "v3"
                    
                    self.logger.info("Data requirements analysis completed successfully")
                    return response
                        
                except Exception as e:
                    self.logger.exception(f"Data analysis error: {e}")
                    return {
                        "error": f"Data analysis failed: {str(e)}",
                        "tool_name": "analyze_data_requirements",
                        "status": "error"
                    }
            
            # Register model building tool
            @self.mcp.tool()
            def build_optimization_model(
                intent_result: Dict[str, Any],
                data_result: Dict[str, Any]
            ) -> Dict[str, Any]:
                """
                Build mathematical optimization model based on intent and data analysis.
                
                Args:
                    intent_result: Intent classification result
                    data_result: Data requirements analysis result
                
                Returns:
                    Mathematical optimization model with constraints and objectives
                """
                try:
                    self.logger.info("Building optimization model...")
                    
                    # Execute model building
                    result = self.model_tool.build_optimization_model(intent_result, data_result)
                    
                    # Convert dataclass to dict for JSON serialization
                    response = asdict(result)
                    
                    # Add metadata
                    response["tool_name"] = "build_optimization_model"
                    response["version"] = "v2"
                    
                    self.logger.info("Optimization model built successfully")
                    return response
                        
                except Exception as e:
                    self.logger.exception(f"Model building error: {e}")
                    return {
                        "error": f"Model building failed: {str(e)}",
                        "tool_name": "build_optimization_model",
                        "status": "error"
                    }
            
            # Register solver tool
            @self.mcp.tool()
            def solve_optimization_problem(
                model_result: Dict[str, Any],
                solver_preferences: Optional[Dict[str, Any]] = None
            ) -> Dict[str, Any]:
                """
                Solve optimization problem using multiple solver engines.
                
                Args:
                    model_result: Built optimization model
                    solver_preferences: Optional solver preferences
                
                Returns:
                    Optimization solution with results and recommendations
                """
                try:
                    self.logger.info("Solving optimization problem...")
                    
                    # Execute solving
                    result = self.solver_tool.solve_optimization_problem(model_result, solver_preferences)
                    
                    # Convert dataclass to dict for JSON serialization
                    response = asdict(result)
                    
                    # Add metadata
                    response["tool_name"] = "solve_optimization_problem"
                    response["version"] = "v1"
                    
                    self.logger.info("Optimization problem solved successfully")
                    return response
                        
                except Exception as e:
                    self.logger.exception(f"Solving error: {e}")
                    return {
                        "error": f"Solving failed: {str(e)}",
                        "tool_name": "solve_optimization_problem",
                        "status": "error"
                    }
            
            # Register comprehensive workflow tool
            @self.mcp.tool()
            def manufacturing_optimization_workflow(
                query: str,
                include_intermediate_results: bool = True
            ) -> Dict[str, Any]:
                """
                Complete manufacturing optimization workflow from query to solution.
                
                Args:
                    query: Manufacturing optimization query
                    include_intermediate_results: Include intermediate analysis results
                
                Returns:
                    Complete optimization workflow result
                """
                try:
                    self.logger.info(f"Starting complete optimization workflow for: {query[:100]}...")
                    
                    # Step 1: Intent Classification
                    intent_result = self.intent_tool.classify_intent(query)
                    self.logger.info(f"Intent classified: {intent_result.primary_intent.value}")
                    
                    # Step 2: Data Requirements Analysis
                    data_result = self.data_tool.analyze_data_requirements(query, asdict(intent_result))
                    self.logger.info("Data requirements analyzed")
                    
                    # Step 3: Model Building
                    model_result = self.model_tool.build_optimization_model(asdict(intent_result), asdict(data_result))
                    self.logger.info("Optimization model built")
                    
                    # Step 4: Problem Solving
                    solution_result = self.solver_tool.solve_optimization_problem(asdict(model_result))
                    self.logger.info("Optimization problem solved")
                    
                    # Build comprehensive response
                    workflow_result = {
                        "query": query,
                        "workflow_status": "completed",
                        "final_solution": asdict(solution_result),
                        "tool_name": "manufacturing_optimization_workflow",
                        "version": "v1",
                        "timestamp": intent_result.classification_metadata.get("timestamp", ""),
                        "execution_summary": {
                            "intent_classification": intent_result.primary_intent.value,
                            "confidence": intent_result.confidence,
                            "model_type": model_result.model_type if hasattr(model_result, 'model_type') else "unknown",
                            "solver_used": solution_result.solver_used if hasattr(solution_result, 'solver_used') else "unknown"
                        }
                    }
                    
                    if include_intermediate_results:
                        workflow_result["intermediate_results"] = {
                            "intent_analysis": asdict(intent_result),
                            "data_analysis": asdict(data_result),
                            "model_definition": asdict(model_result)
                        }
                    
                    self.logger.info("Complete optimization workflow finished successfully")
                    return workflow_result
                        
                except Exception as e:
                    self.logger.exception(f"Workflow error: {e}")
                    return {
                        "error": f"Workflow failed: {str(e)}",
                        "tool_name": "manufacturing_optimization_workflow",
                        "status": "error",
                        "query": query
                    }
            
            # Register tools status tool
            @self.mcp.tool()
            def manufacturing_tools_status() -> Dict[str, Any]:
                """
                Get status of all manufacturing tools.
                
                Returns:
                    Status information for all tools
                """
                try:
                    status = {
                        "tool_name": "manufacturing_tools_status",
                        "timestamp": "",
                        "tools": {
                            "intent_classification": {
                                "status": "available",
                                "version": "v6",
                                "description": "6-agent swarm intelligence for query classification"
                            },
                            "data_analysis": {
                                "status": "available",
                                "version": "v3",
                                "description": "3-stage data analysis for requirements"
                            },
                            "model_building": {
                                "status": "available",
                                "version": "v2",
                                "description": "Mathematical optimization model builder"
                            },
                            "solver": {
                                "status": "available",
                                "version": "v1",
                                "description": "Multi-solver orchestration"
                            },
                            "workflow": {
                                "status": "available",
                                "version": "v1",
                                "description": "Complete end-to-end optimization workflow"
                            }
                        },
                        "server_info": {
                            "host": settings.server_host,
                            "port": settings.server_port,
                            "environment": "production" if not settings.server_debug else "development"
                        }
                    }
                    
                    return status
                        
                except Exception as e:
                    self.logger.exception(f"Status check error: {e}")
                    return {
                        "error": f"Status check failed: {str(e)}",
                        "tool_name": "manufacturing_tools_status",
                        "status": "error"
                    }
            
            self.logger.info(f"✅ Registered {6} manufacturing tools with FastMCP")
            
        except Exception as e:
            self.logger.exception(f"Failed to register tools: {e}")
            raise
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a manufacturing message through the MCP tools.
        This method allows the FastAPI agent to invoke tools directly.
        
        Args:
            message: Manufacturing optimization query
            
        Returns:
            Dictionary with tool results and processing information
        """
        try:
            self.logger.info(f"Processing manufacturing message: {message[:100]}...")
            
            tool_results = {}
            tools_used = []
            
            # Step 1: Intent Classification
            try:
                intent_result = self.intent_tool.classify_intent(message)
                tool_results['intent_classification'] = asdict(intent_result)
                tools_used.append('classify_manufacturing_intent')
                self.logger.info(f"Intent classified: {intent_result.primary_intent.value}")
            except Exception as e:
                self.logger.error(f"Intent classification failed: {e}")
                tool_results['intent_classification'] = {"error": str(e)}
            
            # Step 2: Data Requirements Analysis
            try:
                intent_classification_str = tool_results.get('intent_classification', {}).get('primary_intent', 'unknown')
                data_result = self.data_tool.analyze_data_requirements(message, intent_classification_str)
                tool_results['data_requirements'] = asdict(data_result)
                tools_used.append('analyze_data_requirements')
                self.logger.info("Data requirements analyzed")
            except Exception as e:
                self.logger.error(f"Data analysis failed: {e}")
                tool_results['data_requirements'] = {"error": str(e)}
            
            # Step 3: Model Building (if we have intent and data results)
            if 'intent_classification' in tool_results and 'data_requirements' in tool_results:
                try:
                    # Use the enhanced async method
                    model_result = await self.model_tool.build_optimization_model_enhanced(
                        intent_result=tool_results['intent_classification'],
                        data_result=tool_results['data_requirements'],
                        query=message
                    )
                    tool_results['optimization_model'] = asdict(model_result)
                    tools_used.append('build_optimization_model')
                    self.logger.info("Optimization model built")
                except Exception as e:
                    self.logger.error(f"Model building failed: {e}")
                    tool_results['optimization_model'] = {"error": str(e)}
            
            # Step 4: Problem Solving (if we have a model)
            if 'optimization_model' in tool_results:
                try:
                    solver_result = self.solver_tool.solve_optimization_model(
                        model_data=tool_results['optimization_model'],
                        domain="manufacturing",
                        session_id="default"
                    )
                    tool_results['optimization_solution'] = asdict(solver_result) if hasattr(solver_result, '__dict__') else solver_result
                    tools_used.append('solve_optimization_problem')
                    self.logger.info("Optimization problem solved")
                except Exception as e:
                    self.logger.error(f"Problem solving failed: {e}")
                    tool_results['optimization_solution'] = {"error": str(e)}
            
            # Build comprehensive response
            response = {
                "message": f"Manufacturing optimization processed successfully. Used {len(tools_used)} tools.",
                "tools_used": tools_used,
                "tool_results": tool_results,
                "processing_summary": {
                    "total_tools": len(tools_used),
                    "successful_tools": len([r for r in tool_results.values() if "error" not in r]),
                    "failed_tools": len([r for r in tool_results.values() if "error" in r])
                }
            }
            
            self.logger.info(f"Message processing completed. Tools used: {tools_used}")
            return response
            
        except Exception as e:
            self.logger.exception(f"Message processing failed: {e}")
            return {
                "message": f"Failed to process manufacturing request: {str(e)}",
                "tools_used": [],
                "tool_results": {},
                "error": str(e)
            }
    
    def run(self):
        """Run the FastMCP server."""
        try:
            self.logger.info(f"Starting DcisionAI FastMCP server on {settings.server_host}:{settings.server_port}")
            self.logger.info("Server configured for AWS AgentCore deployment")
            
            # Run with streamable HTTP transport for AWS AgentCore
            self.mcp.run(transport="streamable-http")
            
        except Exception as e:
            self.logger.exception(f"FastMCP server error: {e}")
            raise


def create_fastmcp_server():
    """Create and return a FastMCP server instance."""
    # Configure AWS credentials for all tools
    try:
        from .config.aws_credentials import configure_aws_for_tools
        configure_aws_for_tools()
    except Exception as e:
        logging.warning(f"Could not configure AWS credentials: {e}")
    
    return DcisionAIFastMCPServer()


if __name__ == "__main__":
    # Create and run the server
    server = create_fastmcp_server()
    server.run()
