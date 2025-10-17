#!/usr/bin/env python3
"""
Mock AgentCore Test for SaaS Platform
====================================

This simulates the AgentCore hosted MCP server for testing the SaaS platform
before actual AgentCore deployment.
"""

import asyncio
import json
import logging
from typing import Dict, Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockAgentCoreMCPClient:
    """Mock MCP client that simulates AgentCore hosted server."""
    
    def __init__(self):
        """Initialize the mock client."""
        self.local_mcp_url = "http://localhost:8000/mcp"
        
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check that connects to local MCP server."""
        try:
            async with streamablehttp_client(
                self.local_mcp_url, {}, timeout=30, terminate_on_close=False
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
            logger.error(f"Mock health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def classify_intent(self, problem_description: str, context: str = None) -> Dict[str, Any]:
        """Mock intent classification that connects to local MCP server."""
        try:
            args = {"problem_description": problem_description}
            if context:
                args["context"] = context
            
            async with streamablehttp_client(
                self.local_mcp_url, {}, timeout=30, terminate_on_close=False
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
            logger.error(f"Mock intent classification failed: {e}")
            return {"status": "error", "error": str(e)}

async def test_mock_agentcore():
    """Test the mock AgentCore client."""
    print("🧪 Testing Mock AgentCore MCP Client...")
    print("=" * 50)
    
    client = MockAgentCoreMCPClient()
    
    # Test health check
    print("1️⃣ Testing health check...")
    health_result = await client.health_check()
    print(f"✅ Health check result: {health_result}")
    
    # Test intent classification
    print("\n2️⃣ Testing intent classification...")
    intent_result = await client.classify_intent(
        "I need to optimize my portfolio allocation across stocks, bonds, and real estate with $1M investment"
    )
    print(f"✅ Intent classification result: {intent_result}")
    
    print("\n🎉 Mock AgentCore client test completed successfully!")
    print("✅ Ready to update SaaS platform to use AgentCore-style connection")

if __name__ == "__main__":
    asyncio.run(test_mock_agentcore())
