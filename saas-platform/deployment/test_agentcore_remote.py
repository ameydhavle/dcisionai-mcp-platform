#!/usr/bin/env python3
"""
Test Client for DcisionAI MCP Server on AWS AgentCore (Simulated)
================================================================

This simulates the remote AgentCore connection for testing the SaaS platform
before actual AgentCore deployment.
"""

import asyncio
import os
import sys
import json
from datetime import datetime

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def test_agentcore_remote_simulation():
    """Test the MCP server as if it were deployed on AgentCore."""
    
    print("🧪 Testing DcisionAI MCP Server (AgentCore Simulation)...")
    print("=" * 60)
    
    # Simulate AgentCore environment variables
    agent_arn = "arn:aws:bedrock-agentcore:us-west-2:808953421331:runtime/dcisionai-mcp-server-xyz123"
    bearer_token = "eyJraWQiOiJsM1FpRWI1T01JVWhnNnpQRmNsM1R1SVRBRHh5MmxyTkh2bis2T2ljY3dnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJhODExNjM0MC0wMDUxLTcwNTQtMmU4ZC1jMzBkNjhlYjQ1MjEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9wRVFmVGtzY0siLCJjbGllbnRfaWQiOiI1aDRvNGRwdTdyN3FyZXVzcmpodTU0dW1xbyIsIm9yaWdpbl9qdGkiOiIzYWYzZmE3Yy1lNWQxLTQ2OTktYWU0Ny02OTBjY2Y0YWJmMTEiLCJldmVudF9pZCI6IjkzMmEwZWE3LWRiNzktNDQ4OC1iMTZiLWM2ZWJkODRhYTIzZSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NjA2NDEyNzEsImV4cCI6MTc2MDY0NDg3MSwiaWF0IjoxNzYwNjQxMjcyLCJqdGkiOiJmODY2Y2ZkMy05MTU1LTQwMTYtODBhZS1mZTBlNDA4ODYzODgiLCJ1c2VybmFtZSI6ImRjaXNpb25haS11c2VyIn0.S0CL8NDvfsw42AJ_yIn1hSFNixjQnAENPwg7phIyo9Xr2CyvoTuxXg8bdfnESroUNAd0b1yHafW9YSveXD06zjXKld5jLh9mGwTOFp8mpVDQBaJPSRHiq4Ov0Ej_11MX28pKOS-R5jlHeAxDmBbq-qk67CSLRgg215XYC9yVjVyZZue0ha-RHolOKyfg2SZqjVmumJaYswAJ6jX07MhQnRT-m2gB5DI_uawR-GyHmHiCijRXYan0Fo-OPnuSRxyxhWbOTsFctWgaayvLekLBJTMyTjoySaMeu_dVQ9WlVNHcKx1PuMq4-_fOcYFbGvYdSi0Yqxgcr9iSl9P0P9oZFA"
    
    # For testing, we'll use localhost but simulate the AgentCore URL structure
    # In real deployment, this would be the actual AgentCore URL
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"http://localhost:8000/mcp"  # Simulating AgentCore URL
    # Real AgentCore URL would be: f"https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    
    headers = {
        "authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Mcp-Session-Id": "test-session-123"  # Simulate AgentCore session ID
    }
    
    print(f"🔗 Simulated AgentCore URL: {mcp_url}")
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
                print("✅ DcisionAI MCP Server is working correctly (AgentCore simulation)")
                print("✅ Ready for SaaS platform integration")
                print("✅ Ready for actual AgentCore deployment")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("")
        print("🔍 Troubleshooting:")
        print("1. Check if the MCP server is running locally")
        print("2. Verify the MCP server is accessible at localhost:8000")
        print("3. Check MCP server logs for errors")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_agentcore_remote_simulation())
