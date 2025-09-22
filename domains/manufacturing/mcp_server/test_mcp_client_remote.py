#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Remote Test Client
======================================================

Test client for the deployed MCP server using proper MCP protocol.
Based on AWS AgentCore MCP documentation.

Usage:
    export AGENT_ARN="<agent_runtime_arn>"
    export BEARER_TOKEN="<bearer_token>"
    python test_mcp_client_remote.py

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import os
import sys
import json
import logging

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | MCP Test Client | %(message)s"
)
logger = logging.getLogger(__name__)

async def test_mcp_server():
    """Test the deployed MCP server with all available tools."""
    
    # Get environment variables
    agent_arn = os.getenv('AGENT_ARN')
    bearer_token = os.getenv('BEARER_TOKEN')
    
    if not agent_arn or not bearer_token:
        logger.error("❌ Error: AGENT_ARN or BEARER_TOKEN environment variable is not set")
        logger.error("   Set them with:")
        logger.error("   export AGENT_ARN=\"<agent_runtime_arn>\"")
        logger.error("   export BEARER_TOKEN=\"<bearer_token>\"")
        sys.exit(1)
    
    # Construct MCP URL
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    headers = {
        "authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"🔗 Connecting to MCP server: {mcp_url}")
    logger.info(f"🔐 Using Bearer token: {bearer_token[:20]}...")
    
    try:
        async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize session
                logger.info("🚀 Initializing MCP session...")
                await session.initialize()
                
                # List available tools
                logger.info("📋 Listing available tools...")
                tools_result = await session.list_tools()
                logger.info(f"✅ Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    logger.info(f"   - {tool.name}: {tool.description}")
                
                # Test 1: Health Check
                logger.info("\n🧪 Test 1: Health Check")
                health_result = await session.call_tool("manufacturing_health_check", {})
                logger.info(f"✅ Health check result: {health_result.content}")
                
                # Test 2: Intent Classification
                logger.info("\n🧪 Test 2: Intent Classification")
                intent_result = await session.call_tool(
                    "manufacturing_intent_classification", 
                    {"query": "Optimize production line efficiency for maximum throughput"}
                )
                logger.info(f"✅ Intent classification result: {intent_result.content}")
                
                # Test 3: Data Analysis
                logger.info("\n🧪 Test 3: Data Analysis")
                data_analysis_result = await session.call_tool(
                    "manufacturing_data_analysis",
                    {
                        "data": {
                            "production_volume": 1000,
                            "defect_rate": 0.02,
                            "efficiency": 0.85,
                            "downtime": 120
                        },
                        "analysis_type": "comprehensive"
                    }
                )
                logger.info(f"✅ Data analysis result: {data_analysis_result.content}")
                
                # Test 4: Model Building
                logger.info("\n🧪 Test 4: Model Building")
                model_result = await session.call_tool(
                    "manufacturing_model_builder",
                    {
                        "problem_type": "production_optimization",
                        "constraints": {
                            "max_capacity": 1000,
                            "min_quality": 0.95,
                            "max_cost": 50000
                        },
                        "data": {
                            "demand": [100, 150, 200, 180, 120],
                            "capacity": [120, 120, 120, 120, 120],
                            "costs": [10, 12, 15, 11, 13]
                        }
                    }
                )
                logger.info(f"✅ Model building result: {model_result.content}")
                
                # Test 5: Optimization Solving
                logger.info("\n🧪 Test 5: Optimization Solving")
                optimization_result = await session.call_tool(
                    "manufacturing_optimization_solver",
                    {
                        "model": {
                            "objective": "maximize_production",
                            "variables": ["x1", "x2", "x3"],
                            "constraints": ["x1 + x2 <= 100", "x2 + x3 <= 150"],
                            "complexity": "medium"
                        },
                        "solver_type": "auto"
                    }
                )
                logger.info(f"✅ Optimization solving result: {optimization_result.content}")
                
                logger.info("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
                logger.info("✅ MCP server is working correctly with all tools")
                
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        logger.error("💡 Troubleshooting tips:")
        logger.error("1. Verify the agent runtime ARN is correct")
        logger.error("2. Check that the Bearer token is valid")
        logger.error("3. Ensure the MCP server is deployed and running")
        logger.error("4. Check AWS CloudWatch logs for runtime errors")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("🧪 TESTING DcisionAI Manufacturing MCP Server (Remote)")
    logger.info("========================================================")
    asyncio.run(test_mcp_server())
