#!/usr/bin/env python3
"""
Test AgentCore Full Workflow
============================

Test the complete 4-tool workflow on AWS Bedrock AgentCore.
This script invokes the AgentCore runtime to test our enhanced Model Builder.

Usage:
    python test_agentcore_workflow.py
"""

import boto3
import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | AgentCore Test | %(message)s"
)
logger = logging.getLogger(__name__)

def test_agentcore_workflow():
    """Test the complete workflow on AgentCore"""
    try:
        # Initialize Bedrock AgentCore client
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # AgentCore runtime ARN (latest deployment with enhanced Model Builder)
        agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_MCP_v1_v2_1756272231-e0yCNBHlML"
        
        logger.info("🎯 Testing NEW AgentCore runtime with enhanced Model Builder!")
        
        # Test prompt (same as our local test)
        test_prompt = """Optimize the production schedule to minimize costs while meeting customer demand for automotive parts manufacturing."""
        
        logger.info("🚀 Testing AgentCore Full Workflow")
        logger.info(f"📦 Agent Runtime: {agent_runtime_arn}")
        logger.info(f"🔍 Test Prompt: {test_prompt}")
        
        # Prepare the request (correct format for AgentCore FastAPI)
        request_body = {
            "input": {
                "prompt": test_prompt
            }
        }
        
        logger.info("📤 Sending request to AgentCore...")
        
        # Invoke the AgentCore runtime
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            payload=json.dumps(request_body),
            mcpSessionId=f"test_session_{int(time.time())}",
            contentType="application/json"
        )
        
        logger.info("📥 Received response from AgentCore")
        logger.info(f"📊 Response keys: {list(response.keys())}")
        
        # Parse the response (check different possible response structures)
        if 'response' in response:
            response_body = json.loads(response['response'].read())
        elif 'payload' in response:
            response_body = json.loads(response['payload'].read())
        elif 'responseBody' in response:
            response_body = json.loads(response['responseBody'].read())
        else:
            logger.info(f"📝 Full response: {response}")
            response_body = response
        
        logger.info("✅ AgentCore Workflow Test Results:")
        logger.info(f"📊 Response Status: {response.get('status', 'Unknown')}")
        logger.info(f"📝 Response Content: {response_body}")
        
        # Check if the response contains our expected workflow components
        content = response_body.get('content', [])
        if content:
            text_content = content[0].get('text', '')
            logger.info(f"📄 Full Response Text: {text_content}")
            
            # Check for workflow indicators
            workflow_indicators = [
                'intent', 'data', 'model', 'solver', 'optimization', 
                'production', 'schedule', 'cost', 'demand'
            ]
            
            found_indicators = [indicator for indicator in workflow_indicators 
                              if indicator.lower() in text_content.lower()]
            
            logger.info(f"🔍 Workflow Indicators Found: {found_indicators}")
            
            if len(found_indicators) >= 3:
                logger.info("🎉 SUCCESS: AgentCore workflow appears to be working!")
                logger.info("✅ Multiple workflow components detected in response")
            else:
                logger.warning("⚠️  WARNING: Limited workflow components detected")
                
        else:
            logger.error("❌ No content found in AgentCore response")
            
        return response_body
        
    except Exception as e:
        logger.error(f"❌ Failed to test AgentCore workflow: {e}")
        raise

if __name__ == "__main__":
    import time
    logger.info("🧪 Starting AgentCore Full Workflow Test...")
    test_agentcore_workflow()
    logger.info("🏁 AgentCore Full Workflow Test Complete!")
