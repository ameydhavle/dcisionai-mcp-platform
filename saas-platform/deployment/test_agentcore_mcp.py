#!/usr/bin/env python3
"""
Test Client for DcisionAI MCP Server on AWS AgentCore
====================================================

Test client for the deployed MCP server on AWS Bedrock AgentCore Runtime.
Based on the AWS AgentCore MCP documentation.
"""

import asyncio
import os
import sys
import json
from datetime import datetime

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def test_agentcore_mcp():
    """Test the deployed MCP server on AgentCore."""
    
    print("🧪 Testing DcisionAI MCP Server on AWS AgentCore...")
    print("=" * 60)
    
    # Get environment variables
    agent_arn = os.getenv('AGENT_ARN')
    bearer_token = os.getenv('BEARER_TOKEN')
    
    if not agent_arn or not bearer_token:
        print("❌ Error: AGENT_ARN or BEARER_TOKEN environment variable is not set")
        print("")
        print("Please set the following environment variables:")
        print("  export AGENT_ARN=\"your_agent_runtime_arn\"")
        print("  export BEARER_TOKEN=\"your_bearer_token\"")
        print("")
        print("You can get these values from:")
        print("  1. AgentCore deployment output (AGENT_ARN)")
        print("  2. Cognito setup script (BEARER_TOKEN)")
        sys.exit(1)
    
    # Construct the MCP URL
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    
    headers = {
        "authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    print(f"🔗 MCP URL: {mcp_url}")
    print(f"🔑 Headers: {headers}")
    print("")
    
    try:
        async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                print("📡 Initializing MCP session...")
                await session.initialize()
                print("✅ MCP session initialized")
                
                print("")
                print("🔧 Testing available tools...")
                
                # Test 1: List tools
                print("1️⃣ Listing available tools...")
                tools_result = await session.list_tools()
                print(f"✅ Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                print("")
                print("2️⃣ Testing health check...")
                
                # Test 2: Health check
                health_result = await session.call_tool("health_check_tool", {})
                print("✅ Health check result:")
                print(json.dumps(health_result.content, indent=2))
                
                print("")
                print("3️⃣ Testing intent classification...")
                
                # Test 3: Intent classification
                intent_result = await session.call_tool("classify_intent_tool", {
                    "problem_description": "I need to optimize my portfolio allocation across stocks, bonds, and real estate with $1M investment"
                })
                print("✅ Intent classification result:")
                print(json.dumps(intent_result.content, indent=2))
                
                print("")
                print("4️⃣ Testing workflow templates...")
                
                # Test 4: Workflow templates
                workflow_result = await session.call_tool("get_workflow_templates_tool", {})
                print("✅ Workflow templates result:")
                print(json.dumps(workflow_result.content, indent=2))
                
                print("")
                print("🎉 All tests completed successfully!")
                print("=" * 60)
                print("✅ DcisionAI MCP Server is working correctly on AWS AgentCore")
                print("✅ Ready for SaaS platform integration")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("")
        print("🔍 Troubleshooting:")
        print("1. Check if the MCP server is deployed correctly")
        print("2. Verify the AGENT_ARN is correct")
        print("3. Ensure the BEARER_TOKEN is valid")
        print("4. Check AWS credentials and permissions")
        sys.exit(1)

async def test_local_mcp():
    """Test the MCP server locally before deployment."""
    
    print("🧪 Testing DcisionAI MCP Server locally...")
    print("=" * 50)
    
    mcp_url = "http://localhost:8000/mcp"
    headers = {}
    
    print(f"🔗 Local MCP URL: {mcp_url}")
    print("")
    
    try:
        async with streamablehttp_client(mcp_url, headers, timeout=30, terminate_on_close=False) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                print("📡 Initializing local MCP session...")
                await session.initialize()
                print("✅ Local MCP session initialized")
                
                print("")
                print("🔧 Testing local tools...")
                
                # List tools
                tools_result = await session.list_tools()
                print(f"✅ Found {len(tools_result.tools)} tools locally")
                
                # Health check
                health_result = await session.call_tool("health_check_tool", {})
                print("✅ Local health check passed")
                
                print("")
                print("🎉 Local tests completed successfully!")
                print("✅ Ready for AgentCore deployment")
                
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        print("Make sure the MCP server is running locally: python agentcore_mcp_server.py")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        asyncio.run(test_local_mcp())
    else:
        asyncio.run(test_agentcore_mcp())
