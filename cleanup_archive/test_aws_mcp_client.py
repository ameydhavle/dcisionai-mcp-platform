#!/usr/bin/env python3
"""
Test MCP Client - AWS Documentation Example
==========================================

Exact implementation from AWS Bedrock AgentCore MCP documentation.
This tests our v6 MCP server locally to verify it works before deployment.

Based on: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html
"""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    mcp_url = "http://localhost:8000/mcp"
    headers = {}

    print("🔗 Connecting to MCP server at:", mcp_url)
    
    async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            print("✅ Connected to MCP server")
            
            # Initialize the session
            await session.initialize()
            print("✅ Session initialized")
            
            # List available tools
            tool_result = await session.list_tools()
            print("📋 Available tools:")
            for tool in tool_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test add_numbers tool
            print("\n🧮 Testing add_numbers tool...")
            add_result = await session.call_tool("add_numbers", {"a": 5, "b": 3})
            print(f"   Result: {add_result.content}")
            
            # Test multiply_numbers tool
            print("\n✖️  Testing multiply_numbers tool...")
            multiply_result = await session.call_tool("multiply_numbers", {"a": 4, "b": 7})
            print(f"   Result: {multiply_result.content}")
            
            # Test greet_user tool
            print("\n👋 Testing greet_user tool...")
            greet_result = await session.call_tool("greet_user", {"name": "DcisionAI"})
            print(f"   Result: {greet_result.content}")
            
            print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
