#!/usr/bin/env python3
"""
DcisionAI MCP Server v5 - AWS AgentCore Compliant
=================================================

AWS Bedrock AgentCore compliant MCP server implementation.
Follows AWS guidelines for MCP server deployment:
- Uses FastMCP library with @mcp.tool() decorators
- Runs on port 8000 (AWS requirement)
- Supports stateless streamable-HTTP
- Handles Mcp-Session-Id header for session isolation
- Implements JSON-RPC 2.0 protocol correctly
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

# Import FastMCP for AWS AgentCore compatibility
try:
    from mcp.server.fastmcp import FastMCP
    from starlette.responses import JSONResponse
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("Error: FastMCP not available. Please install with: pip install mcp")

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

class DcisionAI_MCP_Server_v5:
    """DcisionAI MCP Server v5 - AWS AgentCore Compliant."""
    
    def __init__(self):
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP is required for AWS AgentCore deployment")
        
        self.server_name = "DcisionAI MCP Server v5 - AWS Compliant"
        self.version = "5.0.0"
        self.initialized = False
        
        # Initialize FastMCP server with AWS requirements
        # AWS requires: host="0.0.0.0", stateless_http=True
        self.mcp = FastMCP(host="0.0.0.0", stateless_http=True)
        
        # Initialize individual manufacturing tools
        self.intent_tool = None
        self.data_tool = None
        self.model_tool = None
        self.solver_tool = None
        
        try:
            # Import and initialize individual tools
            logger.info("🔧 Initializing individual manufacturing tools with strands framework...")
            
            # Import individual tools for direct access
            from models.manufacturing.tools.intent.DcisionAI_Intent_Tool_v6 import DcisionAI_Intent_Tool_v6
            from models.manufacturing.tools.data.DcisionAI_Data_Tool_v3 import create_dcisionai_data_tool_v3
            from models.manufacturing.tools.model.DcisionAI_Model_Builder_v1 import create_dcisionai_model_builder
            from shared.tools.solver import create_shared_solver_tool
            
            self.intent_tool = DcisionAI_Intent_Tool_v6()
            self.data_tool = create_dcisionai_data_tool_v3()
            self.model_tool = create_dcisionai_model_builder()
            self.solver_tool = create_shared_solver_tool()
            
            logger.info("✅ All individual manufacturing tools initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize manufacturing tools: {e}")
            raise Exception(f"Manufacturing tools initialization failed: {e}")
        
        # Register tools with proper @mcp.tool() decorators
        self._register_tools()
        
        logger.info("✅ MCP Server v5 AWS Compliant initialized successfully")
    
    def _register_tools(self):
        """Register all tools with proper @mcp.tool() decorators for AWS AgentCore."""
        
        @self.mcp.tool()
        def classify_intent(query: str, include_confidence: bool = True, include_reasoning: bool = True) -> str:
            """
            Classify manufacturing optimization queries using 6-agent swarm system.
            
            Args:
                query: Manufacturing optimization query to classify
                include_confidence: Include confidence scores in response
                include_reasoning: Include reasoning in response
            
            Returns:
                Classification result with intent analysis
            """
            try:
                logger.info(f"Processing intent classification for query: {query[:100]}...")
                
                # Execute the intent tool
                result = self.intent_tool.execute({
                    "query": query,
                    "include_confidence": include_confidence,
                    "include_reasoning": include_reasoning
                })
                
                if result.success:
                    return result.content[0]["text"] if result.content else "No classification result"
                else:
                    return f"Classification failed: {result.error}"
                    
            except Exception as e:
                logger.exception(f"Intent classification error: {e}")
                return f"Error during classification: {str(e)}"
        
        @self.mcp.tool()
        def analyze_data_requirements(query: str, include_data_sources: bool = True, include_validation: bool = True) -> str:
            """
            Analyze data requirements for manufacturing optimization.
            
            Args:
                query: Manufacturing optimization query
                include_data_sources: Include data source recommendations
                include_validation: Include data validation requirements
            
            Returns:
                Data requirements analysis
            """
            try:
                logger.info(f"Processing data requirements analysis for query: {query[:100]}...")
                
                # Execute the data tool
                result = self.data_tool.execute({
                    "query": query,
                    "include_data_sources": include_data_sources,
                    "include_validation": include_validation
                })
                
                if result.success:
                    return result.content[0]["text"] if result.content else "No data analysis result"
                else:
                    return f"Data analysis failed: {result.error}"
                    
            except Exception as e:
                logger.exception(f"Data analysis error: {e}")
                return f"Error during data analysis: {str(e)}"
        
        @self.mcp.tool()
        def build_optimization_model(query: str, model_type: str = "auto", include_constraints: bool = True) -> str:
            """
            Build mathematical optimization models for manufacturing problems.
            
            Args:
                query: Manufacturing optimization query
                model_type: Type of model to build (auto, linear, integer, etc.)
                include_constraints: Include constraint definitions
            
            Returns:
                Mathematical optimization model
            """
            try:
                logger.info(f"Processing model building for query: {query[:100]}...")
                
                # Execute the model tool
                result = self.model_tool.execute({
                    "query": query,
                    "model_type": model_type,
                    "include_constraints": include_constraints
                })
                
                if result.success:
                    return result.content[0]["text"] if result.content else "No model building result"
                else:
                    return f"Model building failed: {result.error}"
                    
            except Exception as e:
                logger.exception(f"Model building error: {e}")
                return f"Error during model building: {str(e)}"
        
        @self.mcp.tool()
        def solve_optimization_problem(query: str, solver_preference: str = "auto", include_solution_analysis: bool = True) -> str:
            """
            Solve optimization problems using multiple solver backends.
            
            Args:
                query: Manufacturing optimization query
                solver_preference: Preferred solver (auto, ortools, pulp, cvxpy, pyomo)
                include_solution_analysis: Include solution analysis and interpretation
            
            Returns:
                Optimization solution and analysis
            """
            try:
                logger.info(f"Processing optimization solving for query: {query[:100]}...")
                
                # Execute the solver tool
                result = self.solver_tool.execute({
                    "query": query,
                    "solver_preference": solver_preference,
                    "include_solution_analysis": include_solution_analysis
                })
                
                if result.success:
                    return result.content[0]["text"] if result.content else "No solver result"
                else:
                    return f"Solver execution failed: {result.error}"
                    
            except Exception as e:
                logger.exception(f"Solver execution error: {e}")
                return f"Error during solver execution: {str(e)}"
        
        @self.mcp.tool()
        def manufacturing_optimization_status() -> str:
            """
            Get the status of all manufacturing optimization tools.
            
            Returns:
                Status of all tools and their availability
            """
            try:
                status = {
                    "server": {
                        "name": self.server_name,
                        "version": self.version,
                        "status": "operational"
                    },
                    "tools": {
                        "intent_tool": {
                            "available": self.intent_tool is not None,
                            "type": "6-Agent Swarm Intelligence",
                            "status": "operational" if self.intent_tool else "unavailable"
                        },
                        "data_tool": {
                            "available": self.data_tool is not None,
                            "type": "3-Stage Data Analysis",
                            "status": "operational" if self.data_tool else "unavailable"
                        },
                        "model_tool": {
                            "available": self.model_tool is not None,
                            "type": "Mathematical Model Builder",
                            "status": "operational" if self.model_tool else "unavailable"
                        },
                        "solver_tool": {
                            "available": self.solver_tool is not None,
                            "type": "Multi-Solver Orchestration",
                            "status": "operational" if self.solver_tool else "unavailable"
                        }
                    },
                    "capabilities": [
                        "manufacturing_intent_classification",
                        "data_requirements_analysis", 
                        "optimization_model_building",
                        "optimization_problem_solving",
                        "comprehensive_workflow_orchestration"
                    ],
                    "aws_compliance": {
                        "fastmcp": True,
                        "stateless_http": True,
                        "port_8000": True,
                        "session_isolation": True,
                        "jsonrpc_2_0": True
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                return json.dumps(status, indent=2)
                
            except Exception as e:
                logger.exception(f"Status check error: {e}")
                return f"Error during status check: {str(e)}"
        
        logger.info("✅ All tools registered with @mcp.tool() decorators for AWS AgentCore")
    
    def run(self):
        """Run the FastMCP server on port 8000 (AWS requirement)."""
        try:
            logger.info(f"🚀 Starting {self.server_name} on http://0.0.0.0:8000/mcp")
            logger.info("✅ AWS AgentCore compliant - stateless HTTP, port 8000, session isolation")
            
            # Run with streamable-http transport (AWS requirement)
            self.mcp.run(transport="streamable-http")
            
        except Exception as e:
            logger.exception(f"FastMCP server error: {e}")
            raise

# Create server instance
server = DcisionAI_MCP_Server_v5()

if __name__ == "__main__":
    # Run the AWS-compliant MCP server
    server.run()
