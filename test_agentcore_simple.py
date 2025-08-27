#!/usr/bin/env python3
"""
Simple AgentCore Test
====================

Test AgentCore runtime with minimal request to verify it's working.
"""

import boto3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_agentcore_simple():
    """Test AgentCore with simple request"""
    try:
        # Initialize client
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Runtime ARN
        agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_MCP_v1_v2_1756272231-e0yCNBHlML"
        
        logger.info("🧪 Testing AgentCore with simple request...")
        logger.info(f"📦 Runtime: {agent_runtime_arn}")
        
        # Simple request
        simple_request = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, can you help me with production optimization?"
                }
            ]
        }
        
        logger.info("📤 Sending simple request...")
        
        # Invoke
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            payload=json.dumps(simple_request),
            mcpSessionId="simple_test_123",
            contentType="application/json"
        )
        
        logger.info("📥 Received response!")
        logger.info(f"📊 Status: {response.get('status', 'Unknown')}")
        
        # Parse response
        response_body = json.loads(response['payload'].read())
        logger.info(f"📝 Response: {response_body}")
        
        return response_body
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_agentcore_simple()
