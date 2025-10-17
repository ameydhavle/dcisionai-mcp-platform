#!/usr/bin/env python3
"""
MCP Client for DcisionAI SaaS Platform
=====================================

MCP client that connects to the hosted DcisionAI MCP server on AWS AgentCore.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DcisionAIMCPClient:
    """MCP client for connecting to DcisionAI MCP server."""
    
    def __init__(self, mcp_url: str = None, bearer_token: str = None):
        """Initialize the MCP client."""
        self.mcp_url = mcp_url or os.getenv('MCP_SERVER_URL', 'http://localhost:8000/mcp')
        self.bearer_token = bearer_token or os.getenv('BEARER_TOKEN')
        self.session = None
        
    async def _get_session(self) -> ClientSession:
        """Get or create MCP session."""
        if self.session is None:
            headers = {}
            if self.bearer_token:
                headers["authorization"] = f"Bearer {self.bearer_token}"
            
            # For local testing, use different transport
            if "localhost" in self.mcp_url or "127.0.0.1" in self.mcp_url:
                # Local MCP server
                self.read_stream, self.write_stream, _ = await streamablehttp_client(
                    self.mcp_url, headers, timeout=30, terminate_on_close=False
                )
            else:
                # Remote AgentCore MCP server
                self.read_stream, self.write_stream, _ = await streamablehttp_client(
                    self.mcp_url, headers, timeout=120, terminate_on_close=False
                )
            
            self.session = ClientSession(self.read_stream, self.write_stream)
            await self.session.initialize()
            
        return self.session
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the MCP server."""
        try:
            headers = {}
            if self.bearer_token:
                headers["authorization"] = f"Bearer {self.bearer_token}"
            
            async with streamablehttp_client(
                self.mcp_url, headers, timeout=30, terminate_on_close=False
            ) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool("health_check_tool", {})
                    if result.content:
                        try:
                            return json.loads(result.content[0].text)
                        except json.JSONDecodeError:
                            return {"status": "healthy", "message": result.content[0].text}
                    return {"status": "unknown"}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def classify_intent(self, problem_description: str, context: str = None) -> Dict[str, Any]:
        """Classify user intent for optimization requests."""
        try:
            headers = {}
            if self.bearer_token:
                headers["authorization"] = f"Bearer {self.bearer_token}"
            
            args = {"problem_description": problem_description}
            if context:
                args["context"] = context
            
            async with streamablehttp_client(
                self.mcp_url, headers, timeout=30, terminate_on_close=False
            ) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool("classify_intent_tool", args)
                    if result.content:
                        try:
                            return json.loads(result.content[0].text)
                        except json.JSONDecodeError:
                            return {"status": "success", "result": result.content[0].text}
                    return {"status": "error"}
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def analyze_data(self, problem_description: str, intent_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze and preprocess data for optimization."""
        try:
            session = await self._get_session()
            args = {"problem_description": problem_description}
            if intent_data:
                args["intent_data"] = intent_data
            
            result = await session.call_tool("analyze_data_tool", args)
            return result.content[0].text if result.content else {"status": "error"}
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def build_model(self, problem_description: str, intent_data: Dict[str, Any] = None, 
                         data_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build mathematical optimization model."""
        try:
            session = await self._get_session()
            args = {"problem_description": problem_description}
            if intent_data:
                args["intent_data"] = intent_data
            if data_analysis:
                args["data_analysis"] = data_analysis
            
            result = await session.call_tool("build_model_tool", args)
            return result.content[0].text if result.content else {"status": "error"}
        except Exception as e:
            logger.error(f"Model building failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def solve_optimization(self, problem_description: str, intent_data: Dict[str, Any] = None,
                                data_analysis: Dict[str, Any] = None, model_building: Dict[str, Any] = None) -> Dict[str, Any]:
        """Solve the optimization problem."""
        try:
            session = await self._get_session()
            args = {"problem_description": problem_description}
            if intent_data:
                args["intent_data"] = intent_data
            if data_analysis:
                args["data_analysis"] = data_analysis
            if model_building:
                args["model_building"] = model_building
            
            result = await session.call_tool("solve_optimization_tool", args)
            return result.content[0].text if result.content else {"status": "error"}
        except Exception as e:
            logger.error(f"Optimization solving failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def select_solver(self, optimization_type: str, problem_size: Dict[str, Any] = None,
                           performance_requirement: str = "balanced") -> Dict[str, Any]:
        """Select the best available solver for optimization problems."""
        try:
            session = await self._get_session()
            args = {"optimization_type": optimization_type, "performance_requirement": performance_requirement}
            if problem_size:
                args["problem_size"] = problem_size
            
            result = await session.call_tool("select_solver_tool", args)
            return result.content[0].text if result.content else {"status": "error"}
        except Exception as e:
            logger.error(f"Solver selection failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def explain_optimization(self, problem_description: str, intent_data: Dict[str, Any] = None,
                                  data_analysis: Dict[str, Any] = None, model_building: Dict[str, Any] = None,
                                  optimization_solution: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide business-facing explainability for optimization results."""
        try:
            session = await self._get_session()
            args = {"problem_description": problem_description}
            if intent_data:
                args["intent_data"] = intent_data
            if data_analysis:
                args["data_analysis"] = data_analysis
            if model_building:
                args["model_building"] = model_building
            if optimization_solution:
                args["optimization_solution"] = optimization_solution
            
            result = await session.call_tool("explain_optimization_tool", args)
            return result.content[0].text if result.content else {"status": "error"}
        except Exception as e:
            logger.error(f"Optimization explanation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_workflow_templates(self) -> Dict[str, Any]:
        """Get available industry workflow templates."""
        try:
            session = await self._get_session()
            result = await session.call_tool("get_workflow_templates_tool", {})
            return result.content[0].text if result.content else {"status": "error"}
        except Exception as e:
            logger.error(f"Workflow templates retrieval failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def execute_workflow(self, industry: str, workflow_id: str, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a complete optimization workflow."""
        try:
            session = await self._get_session()
            args = {"industry": industry, "workflow_id": workflow_id}
            if user_input:
                args["user_input"] = user_input
            
            result = await session.call_tool("execute_workflow_tool", args)
            return result.content[0].text if result.content else {"status": "error"}
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def close(self):
        """Close the MCP session."""
        if self.session:
            await self.session.close()
            self.session = None

# Global MCP client instance
_mcp_client = None

def get_mcp_client() -> DcisionAIMCPClient:
    """Get the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = DcisionAIMCPClient()
    return _mcp_client

def initialize_mcp_client(mcp_url: str = None, bearer_token: str = None) -> DcisionAIMCPClient:
    """Initialize the global MCP client instance."""
    global _mcp_client
    _mcp_client = DcisionAIMCPClient(mcp_url, bearer_token)
    return _mcp_client