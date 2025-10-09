#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent v4 - AgentCore Deployment
======================================================

Production-ready AgentCore deployment with 18-agent swarm architecture.
This is the main entry point for the AgentCore runtime.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, Optional

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | DcisionAI Manufacturing Agent v4 | %(message)s"
)
logger = logging.getLogger(__name__)

# Import AgentCore SDK
try:
    from bedrock_agentcore.runtime import BedrockAgentCoreApp
    AGENTCORE_AVAILABLE = True
    logger.info("✅ AgentCore SDK loaded successfully")
except ImportError as e:
    logger.error(f"❌ AgentCore SDK not available: {e}")
    AGENTCORE_AVAILABLE = False

# Import our MCP server
try:
    # Try to import the MCP server directly
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp_server'))
    from mcp_server_swarm import ManufacturingMCP
    MCP_AVAILABLE = True
    logger.info("✅ Manufacturing MCP server loaded successfully")
except ImportError as e:
    logger.error(f"❌ MCP server not available: {e}")
    MCP_AVAILABLE = False

class DcisionAIManufacturingAgentV4:
    """
    DcisionAI Manufacturing Agent v4 for AgentCore deployment.
    
    Features:
    - 18-agent swarm architecture (Intent, Data, Model, Solver)
    - Cross-region optimization
    - Consensus mechanism
    - Real AWS Bedrock integration
    - Production-ready error handling
    """
    
    def __init__(self):
        self.app = None
        self.mcp_server = None
        self.initialized = False
        
        if AGENTCORE_AVAILABLE:
            self.app = BedrockAgentCoreApp()
            logger.info("🚀 AgentCore app initialized")
        
        if MCP_AVAILABLE:
            self.mcp_server = ManufacturingMCP()
            logger.info("🏭 Manufacturing MCP server initialized")
    
    async def initialize(self):
        """Initialize the agent and MCP server."""
        try:
            if not self.app:
                raise RuntimeError("AgentCore app not available")
            
            if not self.mcp_server:
                raise RuntimeError("MCP server not available")
            
            # Register MCP tools with AgentCore
            await self._register_tools()
            
            self.initialized = True
            logger.info("✅ DcisionAI Manufacturing Agent v4 initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise
    
    async def _register_tools(self):
        """Register MCP tools with AgentCore."""
        try:
            # Get tools from MCP server
            tools = self.mcp_server.get_tools()
            
            for tool in tools:
                # Register each tool with AgentCore
                self.app.register_tool(
                    name=tool.name,
                    description=tool.description,
                    handler=self._create_tool_handler(tool)
                )
                logger.info(f"🔧 Registered tool: {tool.name}")
            
            logger.info(f"✅ Registered {len(tools)} tools with AgentCore")
            
        except Exception as e:
            logger.error(f"❌ Failed to register tools: {e}")
            raise
    
    def _create_tool_handler(self, tool):
        """Create a handler function for a tool."""
        async def handler(**kwargs):
            try:
                logger.info(f"🔄 Executing tool: {tool.name}")
                
                # Call the MCP tool
                result = await self.mcp_server.call_tool(tool.name, kwargs)
                
                logger.info(f"✅ Tool {tool.name} completed successfully")
                return result
                
            except Exception as e:
                logger.error(f"❌ Tool {tool.name} failed: {e}")
                return {
                    "error": str(e),
                    "tool": tool.name,
                    "status": "failed"
                }
        
        return handler
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming requests."""
        try:
            if not self.initialized:
                await self.initialize()
            
            logger.info(f"📨 Received request: {request.get('type', 'unknown')}")
            
            # Process the request through the MCP server
            if self.mcp_server:
                response = await self.mcp_server.process_request(request)
                logger.info("✅ Request processed successfully")
                return response
            else:
                return {
                    "error": "MCP server not available",
                    "status": "failed"
                }
                
        except Exception as e:
            logger.error(f"❌ Request handling failed: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "v4.0.0",
            "initialized": self.initialized,
            "agentcore_available": AGENTCORE_AVAILABLE,
            "mcp_available": MCP_AVAILABLE,
            "timestamp": asyncio.get_event_loop().time()
        }

# Global agent instance
agent = DcisionAIManufacturingAgentV4()

async def main():
    """Main entry point for AgentCore deployment."""
    try:
        logger.info("🚀 Starting DcisionAI Manufacturing Agent v4")
        
        # Initialize the agent
        await agent.initialize()
        
        # Start the AgentCore app
        if agent.app:
            logger.info("🌐 Starting AgentCore app...")
            await agent.app.run()
        else:
            logger.error("❌ AgentCore app not available")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Failed to start agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
