#!/usr/bin/env python3
"""
Simple AgentCore Deployment Script for DcisionAI Manufacturing MCP Server

This script deploys the MCP server directly to AWS AgentCore using the BedrockAgentCoreApp.
"""

import os
import sys
import json
import logging
import boto3
from pathlib import Path
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the MCP server
from mcp_server_swarm import ManufacturingSwarmTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | AgentCore Deploy | %(message)s"
)
logger = logging.getLogger(__name__)

def deploy_to_agentcore():
    """Deploy the MCP server to AWS AgentCore."""
    logger.info("🚀 Starting deployment to AWS AgentCore...")
    
    try:
        # Import BedrockAgentCoreApp
        from bedrock_agentcore import BedrockAgentCoreApp
        
        # Create the MCP server instance
        logger.info("📦 Creating MCP server instance...")
        mcp_server = ManufacturingSwarmTools()
        
        # Create AgentCore app
        logger.info("🏗️ Creating AgentCore application...")
        app = BedrockAgentCoreApp(
            name="dcisionai-manufacturing-mcp",
            version="2.0.0",
            description="DcisionAI Manufacturing MCP Server with Swarm Architecture"
        )
        
        # Add the MCP server as a tool
        logger.info("🔧 Adding MCP server tools to AgentCore...")
        
        # Add all manufacturing tools
        app.add_tool(
            name="manufacturing_intent_classification",
            description="Classify manufacturing intent using 5-agent peer-to-peer swarm",
            handler=mcp_server.manufacturing_intent_classification
        )
        
        app.add_tool(
            name="manufacturing_data_analysis", 
            description="Analyze manufacturing data requirements using 3-agent swarm",
            handler=mcp_server.manufacturing_data_analysis
        )
        
        app.add_tool(
            name="manufacturing_model_builder",
            description="Build optimization models using 4-agent swarm", 
            handler=mcp_server.manufacturing_model_builder
        )
        
        app.add_tool(
            name="manufacturing_optimization_solver",
            description="Solve optimization problems using 6-agent swarm",
            handler=mcp_server.manufacturing_optimization_solver
        )
        
        app.add_tool(
            name="manufacturing_health_check",
            description="Check health status of manufacturing MCP server",
            handler=mcp_server.manufacturing_health_check
        )
        
        # Deploy to AgentCore
        logger.info("🚀 Deploying to AWS AgentCore...")
        deployment_result = app.deploy(
            region="us-east-1",
            memory=2048,
            timeout=300,
            environment_variables={
                "AWS_REGION": "us-east-1",
                "BEDROCK_MODEL_ID": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                "INFERENCE_PROFILE_ID": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                "CROSS_REGION_ENABLED": "true",
                "MAX_PARALLEL_REQUESTS": "5",
                "LOG_LEVEL": "INFO"
            }
        )
        
        logger.info("✅ Deployment completed successfully!")
        logger.info(f"Deployment result: {json.dumps(deployment_result, indent=2)}")
        
        return deployment_result
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {str(e)}")
        raise

def test_deployment(endpoint: str):
    """Test the deployed AgentCore application."""
    logger.info(f"🧪 Testing deployment at {endpoint}...")
    
    try:
        import requests
        
        # Test health check
        health_url = f"{endpoint}/health"
        response = requests.get(health_url, timeout=30)
        
        if response.status_code == 200:
            logger.info("✅ Health check passed")
            health_data = response.json()
            logger.info(f"Health status: {health_data.get('overall_status', 'unknown')}")
        else:
            logger.warning(f"⚠️ Health check failed: {response.status_code}")
        
        # Test MCP endpoint
        mcp_url = f"{endpoint}/mcp"
        mcp_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        response = requests.post(
            mcp_url,
            json=mcp_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info("✅ MCP endpoint is responding")
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                tools = [tool["name"] for tool in data["result"]["tools"]]
                logger.info(f"Available tools: {tools}")
        else:
            logger.warning(f"⚠️ MCP endpoint test failed: {response.status_code}")
        
        logger.info("🎉 Deployment testing completed!")
        
    except Exception as e:
        logger.error(f"❌ Testing failed: {str(e)}")

def main():
    """Main deployment function."""
    logger.info("🚀 DcisionAI Manufacturing MCP Server - AgentCore Deployment")
    logger.info("Features to deploy:")
    logger.info("  ✅ Intent Swarm: 5-agent peer-to-peer consensus")
    logger.info("  ✅ Data Swarm: 3-agent peer-to-peer analysis")
    logger.info("  ✅ Model Swarm: 4-agent peer-to-peer modeling")
    logger.info("  ✅ Solver Swarm: 6-agent peer-to-peer optimization")
    logger.info("  ✅ Cross-region parallel execution")
    logger.info("  ✅ Real AWS Bedrock inference profiles")
    logger.info("  ✅ NO MOCK RESPONSES policy enforced")
    
    try:
        # Deploy to AgentCore
        deployment_result = deploy_to_agentcore()
        
        # Extract endpoint if available
        endpoint = deployment_result.get("endpoint") or deployment_result.get("url")
        if endpoint:
            logger.info(f"🌐 Deployment endpoint: {endpoint}")
            
            # Wait a bit for deployment to stabilize
            logger.info("⏳ Waiting for deployment to stabilize...")
            import time
            time.sleep(30)
            
            # Test the deployment
            test_deployment(endpoint)
        else:
            logger.info("📋 Deployment completed. Check AWS console for endpoint details.")
        
        logger.info("🎉 AgentCore deployment completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
