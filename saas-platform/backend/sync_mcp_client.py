#!/usr/bin/env python3
"""
Enhanced MCP Client for DcisionAI SaaS Platform
==============================================

Direct integration with DcisionAI MCP Server v1.7.3 with pattern-breaking strategies.
Uses the MCP server directly for best AgentCore compatibility.
"""

import json
import logging
import os
import sys
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Add the MCP server path
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_root = os.path.abspath(os.path.join(current_dir, '../../../mcp-server'))
if mcp_server_root not in sys.path:
    sys.path.insert(0, mcp_server_root)

# Import our enhanced DcisionAI tools directly
try:
    from dcisionai_mcp_server.tools import DcisionAITools
    logger = logging.getLogger(__name__)
    logger.info("✅ Enhanced DcisionAI MCP tools imported successfully (v1.7.3)")
except Exception as e:
    logger.error(f"❌ Failed to import DcisionAITools: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncDcisionAIMCPClient:
    """Enhanced MCP client using DcisionAI tools directly for best AgentCore compatibility."""
    
    def __init__(self, mcp_url: str = None, bearer_token: str = None):
        """Initialize the enhanced MCP client with direct tool integration."""
        self.mcp_url = mcp_url or os.getenv('MCP_SERVER_URL', 'direct_integration')
        self.bearer_token = bearer_token or os.getenv('BEARER_TOKEN')
        
        # Initialize DcisionAI tools directly
        self.dcisionai_tools = DcisionAITools()
        logger.info("🚀 Enhanced DcisionAI MCP client initialized with pattern-breaking strategies")
        
    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call MCP tool using subprocess to avoid async conflicts."""
        try:
            # Create a temporary script to call the MCP tool
            script_content = f'''
import asyncio
import json
import sys
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def call_tool():
    mcp_url = "{self.mcp_url}"
    headers = {{}}
    if "{self.bearer_token}":
        headers["authorization"] = f"Bearer {self.bearer_token}"
    
    async with streamablehttp_client(mcp_url, headers, timeout=30, terminate_on_close=False) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("{tool_name}", {arguments or {}})
            if result.content:
                try:
                    return json.loads(result.content[0].text)
                except json.JSONDecodeError:
                    return {{"status": "success", "result": result.content[0].text}}
            return {{"status": "error"}}

if __name__ == "__main__":
    result = asyncio.run(call_tool())
    print(json.dumps(result))
'''
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                # Run the script
                result = subprocess.run([
                    sys.executable, script_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return json.loads(result.stdout)
                else:
                    logger.error(f"MCP tool call failed: {result.stderr}")
                    return {"status": "error", "error": result.stderr}
                    
            finally:
                # Clean up temporary file
                os.unlink(script_path)
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {"status": "error", "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the MCP server."""
        return self._call_mcp_tool("health_check_tool")
    
    def classify_intent(self, problem_description: str, context: str = None) -> Dict[str, Any]:
        """Classify user intent for optimization requests."""
        args = {"problem_description": problem_description}
        if context:
            args["context"] = context
        return self._call_mcp_tool("classify_intent_tool", args)
    
    def analyze_data(self, problem_description: str, intent_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze and preprocess data for optimization."""
        args = {"problem_description": problem_description}
        if intent_data:
            args["intent_data"] = intent_data
        return self._call_mcp_tool("analyze_data_tool", args)
    
    def build_model(self, problem_description: str, intent_data: Dict[str, Any] = None, 
                   data_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build mathematical optimization model."""
        args = {"problem_description": problem_description}
        if intent_data:
            args["intent_data"] = intent_data
        if data_analysis:
            args["data_analysis"] = data_analysis
        return self._call_mcp_tool("build_model_tool", args)
    
    def solve_optimization(self, problem_description: str, intent_data: Dict[str, Any] = None,
                          data_analysis: Dict[str, Any] = None, model_building: Dict[str, Any] = None) -> Dict[str, Any]:
        """Solve the optimization problem."""
        args = {"problem_description": problem_description}
        if intent_data:
            args["intent_data"] = intent_data
        if data_analysis:
            args["data_analysis"] = data_analysis
        if model_building:
            args["model_building"] = model_building
        return self._call_mcp_tool("solve_optimization_tool", args)
    
    def select_solver(self, optimization_type: str, problem_size: Dict[str, Any] = None,
                     performance_requirement: str = "balanced") -> Dict[str, Any]:
        """Select the best available solver for optimization problems."""
        args = {"optimization_type": optimization_type, "performance_requirement": performance_requirement}
        if problem_size:
            args["problem_size"] = problem_size
        return self._call_mcp_tool("select_solver_tool", args)
    
    def explain_optimization(self, problem_description: str, intent_data: Dict[str, Any] = None,
                            data_analysis: Dict[str, Any] = None, model_building: Dict[str, Any] = None,
                            optimization_solution: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide business-facing explainability for optimization results."""
        args = {"problem_description": problem_description}
        if intent_data:
            args["intent_data"] = intent_data
        if data_analysis:
            args["data_analysis"] = data_analysis
        if model_building:
            args["model_building"] = model_building
        if optimization_solution:
            args["optimization_solution"] = optimization_solution
        return self._call_mcp_tool("explain_optimization_tool", args)
    
    def get_workflow_templates(self) -> Dict[str, Any]:
        """Get available industry workflow templates."""
        return self._call_mcp_tool("get_workflow_templates_tool")
    
    def execute_workflow(self, industry: str, workflow_id: str, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a complete optimization workflow."""
        args = {"industry": industry, "workflow_id": workflow_id}
        if user_input:
            args["user_input"] = user_input
        return self._call_mcp_tool("execute_workflow_tool", args)

# Global MCP client instance
_sync_mcp_client = None

def get_sync_mcp_client() -> SyncDcisionAIMCPClient:
    """Get the global synchronous MCP client instance."""
    global _sync_mcp_client
    if _sync_mcp_client is None:
        _sync_mcp_client = SyncDcisionAIMCPClient()
    return _sync_mcp_client

def initialize_sync_mcp_client(mcp_url: str = None, bearer_token: str = None) -> SyncDcisionAIMCPClient:
    """Initialize the global synchronous MCP client instance."""
    global _sync_mcp_client
    _sync_mcp_client = SyncDcisionAIMCPClient(mcp_url, bearer_token)
    return _sync_mcp_client
