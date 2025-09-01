#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent - Simple AgentCore Test
====================================================

Test script for the simple AgentCore deployment.
Based on: https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/

Usage:
    python scripts/deployment/test_agentcore_simple.py

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import boto3
import json
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | DcisionAI Simple Test | %(message)s"
)
logger = logging.getLogger(__name__)

def test_simple_agentcore():
    """Test the simple AgentCore deployment."""
    logger.info("🧪 TESTING DcisionAI Manufacturing Agent (Simple AgentCore)")
    logger.info("=" * 60)
    
    # Configuration
    region = "us-east-1"
    
    # Updated with the actual ARN from the successful deployment
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Simple_1756349655-OKRo8A5t7n"
    
    # Test payload - using the same prompt as local tests
    test_payload = json.dumps({
        "prompt": "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
    })
    
    # Generate session ID (must be 33+ characters)
    session_id = f"test-session-{int(time.time())}-dcisionai-manufacturing"
    
    logger.info(f"📋 Test Configuration:")
    logger.info(f"   Region: {region}")
    logger.info(f"   Agent Runtime ARN: {agent_runtime_arn}")
    logger.info(f"   Session ID: {session_id}")
    logger.info("")
    
    try:
        # Initialize AgentCore client
        client = boto3.client('bedrock-agentcore', region_name=region)
        
        logger.info("🔄 Invoking AgentCore agent...")
        
        # Invoke the agent
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            runtimeSessionId=session_id,
            payload=test_payload,
            qualifier="DEFAULT"
        )
        
        # Read response
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        logger.info("✅ AgentCore invocation completed successfully!")
        logger.info("=" * 60)
        
        # Display results
        logger.info("📊 Response Summary:")
        if "output" in response_data:
            output = response_data["output"]
            logger.info(f"   Message: {output.get('message', 'No message')}")
            logger.info(f"   Model: {output.get('model', 'Unknown')}")
            logger.info(f"   Timestamp: {output.get('timestamp', 'Unknown')}")
        else:
            logger.info(f"   Raw Response: {json.dumps(response_data, indent=2)}")
        
        logger.info("")
        logger.info("🔍 Full Response:")
        logger.info(json.dumps(response_data, indent=2))
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        logger.error("💡 Troubleshooting Tips:")
        logger.error("1. Make sure the agent runtime ARN is correct")
        logger.error("2. Verify the agent runtime is in READY status")
        logger.error("3. Check that the deployment completed successfully")
        logger.error("4. Ensure AWS credentials are configured correctly")
        raise

def list_agent_runtimes():
    """List all available agent runtimes."""
    logger.info("📋 LISTING AVAILABLE AGENT RUNTIMES")
    logger.info("=" * 50)
    
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        response = client.list_agent_runtimes()
        
        logger.info("Available Agent Runtimes:")
        for runtime in response.get('agentRuntimeSummaries', []):
            logger.info(f"   • {runtime.get('agentRuntimeName', 'Unknown')}")
            logger.info(f"     ARN: {runtime.get('agentRuntimeArn', 'Unknown')}")
            logger.info(f"     Status: {runtime.get('status', 'Unknown')}")
            logger.info("")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to list agent runtimes: {e}")
        raise

if __name__ == "__main__":
    # First, list available runtimes to help identify the correct ARN
    list_agent_runtimes()
    
    logger.info("")
    logger.info("💡 To test a specific agent runtime, update the agent_runtime_arn variable")
    logger.info("   in this script with the correct ARN from the list above.")
    logger.info("")
    
    # Run the test with the updated ARN
    test_simple_agentcore()
