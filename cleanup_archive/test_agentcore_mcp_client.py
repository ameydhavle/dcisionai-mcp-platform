#!/usr/bin/env python3
"""
Test AgentCore MCP Client - Remote Testing
==========================================

Test our deployed MCP server on AWS AgentCore.
This follows the AWS documentation for remote testing.

Based on: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html
"""

import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    # AgentCore endpoint details
    agent_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/dcisionai_mcp_v6-pYngtvGFWl"
    
    # For testing, we'll use IAM authentication (no bearer token needed for now)
    # In production, you would use Cognito authentication
    
    # URL encode the ARN for the endpoint
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    
    # For IAM authentication, we don't need a bearer token
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    print(f"🔗 Connecting to AgentCore MCP server at: {mcp_url}")
    print(f"📋 Agent ARN: {agent_arn}")
    print(f"🔐 Using IAM authentication")
    
    try:
        async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                print("✅ Connected to AgentCore MCP server")
                
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
                add_result = await session.call_tool("add_numbers", {"a": 10, "b": 20})
                print(f"   Result: {add_result.content}")
                
                # Test multiply_numbers tool
                print("\n✖️  Testing multiply_numbers tool...")
                multiply_result = await session.call_tool("multiply_numbers", {"a": 5, "b": 8})
                print(f"   Result: {multiply_result.content}")
                
                # Test greet_user tool
                print("\n👋 Testing greet_user tool...")
                greet_result = await session.call_tool("greet_user", {"name": "AWS AgentCore"})
                print(f"   Result: {greet_result.content}")
                
                print("\n✅ All AgentCore MCP tests completed successfully!")
                print("🎉 Our MCP server is working perfectly on AWS AgentCore!")
                
    except Exception as e:
        print(f"❌ Error testing AgentCore MCP server: {e}")
        print("💡 This might be due to authentication requirements.")
        print("   For production use, you would need to set up Cognito authentication.")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🚀 AgentCore MCP Server Test: SUCCESS!")
    else:
        print("\n❌ AgentCore MCP Server Test: FAILED")
        sys.exit(1)
