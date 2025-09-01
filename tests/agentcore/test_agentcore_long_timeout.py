#!/usr/bin/env python3
"""
AgentCore Long Timeout Test
==========================

Test AgentCore runtime with longer timeout to see if data tool completes.
"""

import boto3
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_agentcore_long_timeout():
    """Test AgentCore with longer timeout"""
    try:
        # Initialize client
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Runtime ARN (fixed workflow version)
        agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_MCP_v1_v2_1756303333-8bMiQTGLpQ"
        
        logger.info("🧪 Testing AgentCore with longer timeout...")
        logger.info(f"📦 Runtime: {agent_runtime_arn}")
        
        # Test request (same as our local test)
        test_request = {
            "input": {
                "prompt": "Optimize the production schedule to minimize costs while meeting customer demand for automotive parts manufacturing."
            }
        }
        
        logger.info("📤 Sending request to AgentCore...")
        logger.info("⏱️  This may take up to 5 minutes...")
        
        start_time = time.time()
        
        # Invoke with longer timeout (if possible)
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            payload=json.dumps(test_request),
            mcpSessionId=f"long_timeout_test_{int(time.time())}",
            contentType="application/json"
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"📥 Received response after {duration:.2f} seconds!")
        logger.info(f"📊 Status: {response.get('statusCode', 'Unknown')}")
        
        # Parse response
        if 'response' in response:
            response_body = json.loads(response['response'].read())
            logger.info(f"📝 Response: {response_body}")
            
            # Check if we got a meaningful response
            if 'output' in response_body:
                output = response_body['output']
                logger.info(f"✅ SUCCESS: AgentCore workflow completed!")
                logger.info(f"📄 Message: {output.get('message', 'No message')}")
                logger.info(f"🔧 Tools used: {output.get('tools_used', [])}")
                
                # Check tool results
                tool_results = output.get('tool_results', {})
                if 'intent_classification' in tool_results:
                    logger.info("✅ Intent classification completed")
                if 'data_requirements' in tool_results:
                    logger.info("✅ Data analysis completed")
                if 'optimization_model' in tool_results:
                    logger.info("✅ Model building completed")
                if 'optimization_solution' in tool_results:
                    logger.info("✅ Solver completed")
                
                return True
            else:
                logger.warning("⚠️  Response doesn't contain expected 'output' field")
                return False
        else:
            logger.error("❌ No 'response' field in AgentCore response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_agentcore_long_timeout()
    if success:
        logger.info("🎉 AgentCore long timeout test PASSED!")
    else:
        logger.error("💥 AgentCore long timeout test FAILED!")
