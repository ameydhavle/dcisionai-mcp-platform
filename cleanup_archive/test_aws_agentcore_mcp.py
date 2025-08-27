#!/usr/bin/env python3
"""
Test AWS AgentCore MCP Server
=============================

Test script for the deployed MCP server on AWS Bedrock AgentCore.
"""

import asyncio
import os
import sys
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# AgentCore endpoint details
AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/dcisionai_mcp_final-CDEhMdFJY8"
BEARER_TOKEN = "test-token"  # For testing without authentication

async def test_mcp_server():
    """Test the deployed MCP server."""
    try:
        # URL encode the agent ARN
        encoded_arn = AGENT_ARN.replace(':', '%3A').replace('/', '%2F')
        mcp_url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
        
        headers = {
            "authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        print(f"Testing MCP server at: {mcp_url}")
        print(f"Headers: {headers}")
        
        async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                # Test 1: Initialize
                print("\n1. Testing initialize...")
                await session.initialize()
                print("✅ Initialize successful")
                
                # Test 2: List tools
                print("\n2. Testing tools/list...")
                tools_result = await session.list_tools()
                print(f"✅ Tools list successful: {len(tools_result.tools)} tools found")
                
                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description[:100]}...")
                
                # Test 3: Get tools status
                print("\n3. Testing manufacturing_tools_status...")
                status_result = await session.call_tool("manufacturing_tools_status", {})
                print("✅ Tools status successful")
                print(f"Status: {status_result.content[0].text[:200]}...")
                
                # Test 4: Test intent classification
                print("\n4. Testing classify_manufacturing_intent...")
                intent_result = await session.call_tool("classify_manufacturing_intent", {
                    "query": "Optimize production schedule with energy constraints",
                    "include_confidence": True,
                    "include_reasoning": True
                })
                print("✅ Intent classification successful")
                print(f"Result: {intent_result.content[0].text[:200]}...")
                
                print("\n🎉 All tests passed! MCP server is working correctly on AWS AgentCore!")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
