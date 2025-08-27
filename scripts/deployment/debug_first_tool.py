#!/usr/bin/env python3
"""
Debug First Tool - Test Intent Classification Only
=================================================

Simple test to debug why the first tool is hanging.
"""

import boto3
import json
import logging
import sys
import time
import uuid
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("Debug First Tool")

def test_intent_tool_only():
    """Test only the intent classification tool"""
    
    logger.info("🔍 Debugging Intent Classification Tool")
    logger.info("=" * 50)
    
    # Setup AWS client
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        logger.info("✅ AWS Bedrock AgentCore client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to setup AWS client: {e}")
        return False
    
    # Comprehensive test prompt for full workflow
    test_prompt = "I need to optimize my automotive production line for maximum efficiency. We have 3 assembly stations with different processing times and quality metrics. Station A takes 45 minutes with 98% quality, Station B takes 38 minutes with 95% quality, and Station C takes 52 minutes with 99% quality. We need to process 500 units per day while maintaining overall quality above 97%."
    
    # Create unique session ID (must be 33+ characters)
    session_id = f"debug-intent-{uuid.uuid4().hex}-{int(time.time())}"
    
    # Prepare request
    request_body = {
        "input": {
            "prompt": test_prompt
        }
    }
    
    # Agent runtime ARN
    agent_runtime_arn = 'arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/dcisionai_manufacturing_mcp_server_v12-0YTUnBAoZm'
    
    logger.info(f"🔗 Agent: {agent_runtime_arn}")
    logger.info(f"🆔 Session: {session_id}")
    logger.info(f"📝 Prompt: {test_prompt}")
    
    # Time the request
    start_time = time.time()
    
    try:
        logger.info("🔄 Invoking agent (this may take a while)...")
        logger.info("⏰ Starting timer...")
        
        # Make the API call with timeout
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(request_body),
            qualifier="DEFAULT"
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        logger.info(f"✅ Response Time: {response_time:.2f}s")
        logger.info("✅ Request completed!")
        
        # Parse response
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        # Log the full response for debugging
        logger.info("📄 Full Response:")
        logger.info(json.dumps(response_data, indent=2))
        
        return True
        
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        
        logger.error(f"❌ Test Failed: {e}")
        logger.error(f"⏱️ Time to failure: {response_time:.2f}s")
        return False

def main():
    """Main debug function"""
    logger.info("🚀 Starting Intent Tool Debug")
    logger.info("=" * 60)
    
    success = test_intent_tool_only()
    
    if success:
        logger.info("\n🎉 Intent tool test completed!")
        return 0
    else:
        logger.error("\n❌ Intent tool test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
