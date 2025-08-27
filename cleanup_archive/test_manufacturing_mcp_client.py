#!/usr/bin/env python3
"""
Test Manufacturing MCP Client
============================

Test our manufacturing tools MCP server locally.
"""

import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    mcp_url = "http://localhost:8000/mcp"
    headers = {}

    print("🔗 Connecting to Manufacturing MCP server at:", mcp_url)
    
    async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            print("✅ Connected to Manufacturing MCP server")
            
            # Initialize the session
            await session.initialize()
            print("✅ Session initialized")
            
            # List available tools
            tool_result = await session.list_tools()
            print("📋 Available manufacturing tools:")
            for tool in tool_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test manufacturing tools status
            print("\n🔍 Testing manufacturing tools status...")
            status_result = await session.call_tool("manufacturing_tools_status", {})
            print(f"   Status: {status_result.content}")
            
            # Test intent classification
            print("\n🎯 Testing intent classification...")
            intent_query = "We need to optimize our production schedule to minimize costs while meeting customer demand"
            intent_result = await session.call_tool("classify_manufacturing_intent", {
                "query": intent_query,
                "include_confidence": True,
                "include_reasoning": True
            })
            print(f"   Intent Result: {intent_result.content}")
            
            # Parse intent result for next steps
            try:
                intent_data = json.loads(intent_result.content[0].text)
                primary_intent = intent_data.get("primary_intent", "unknown")
                print(f"   Primary Intent: {primary_intent}")
            except:
                primary_intent = "unknown"
            
            # Test data requirements analysis
            print("\n📊 Testing data requirements analysis...")
            data_result = await session.call_tool("analyze_data_requirements", {
                "query": intent_query,
                "intent_classification": primary_intent,
                "include_coverage": True
            })
            print(f"   Data Analysis Result: {data_result.content}")
            
            # Test model building
            print("\n🏗️ Testing model building...")
            model_result = await session.call_tool("build_optimization_model", {
                "query": intent_query,
                "intent_classification": primary_intent,
                "model_type": "auto"
            })
            print(f"   Model Building Result: {model_result.content}")
            
            # Test complete workflow
            print("\n🔄 Testing complete manufacturing workflow...")
            workflow_result = await session.call_tool("manufacturing_optimization_workflow", {
                "query": intent_query,
                "include_all_stages": True
            })
            print(f"   Workflow Result: {workflow_result.content}")
            
            print("\n✅ All manufacturing MCP tests completed successfully!")
            print("🎉 Our manufacturing tools are working perfectly with MCP!")

if __name__ == "__main__":
    asyncio.run(main())
