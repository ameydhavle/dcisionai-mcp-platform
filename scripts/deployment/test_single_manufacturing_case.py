#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Single Use Case Test
========================================================

Test a single manufacturing optimization scenario with detailed metrics.
This script tests one use case at a time to isolate issues and validate performance.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import boto3
import json
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("DcisionAI Single Test")

# Project root path
PROJECT_ROOT = Path(__file__).parent.parent.parent

def test_production_line_optimization():
    """Test Production Line Optimization scenario"""
    
    logger.info("🚀 Testing Production Line Optimization")
    logger.info("=" * 50)
    
    # Setup AWS client
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        logger.info("✅ AWS Bedrock AgentCore client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to setup AWS client: {e}")
        return False
    
    # Test scenario
    scenario = {
        'name': 'Production Line Optimization',
        'prompt': """I need to optimize my automotive production line for maximum efficiency. 
        We have 3 assembly stations with different processing times and quality metrics. 
        Station A takes 45 minutes with 98% quality, Station B takes 38 minutes with 95% quality, 
        and Station C takes 52 minutes with 99% quality. We need to process 500 units per day 
        while maintaining overall quality above 97%. Can you help me:
        1. Classify the optimization intent
        2. Analyze what data we need
        3. Build an optimization model
        4. Solve for the best configuration
        5. Orchestrate the workflow
        6. Monitor the solution status""",
        'expected_tools': [
            "classify_manufacturing_intent",
            "analyze_data_requirements", 
            "build_optimization_model",
            "solve_optimization_problem",
            "manufacturing_optimization_workflow",
            "manufacturing_tools_status"
        ]
    }
    
    logger.info(f"📝 Scenario: {scenario['name']}")
    logger.info(f"📋 Expected Tools: {len(scenario['expected_tools'])} tools")
    
    # Create unique session ID
    session_id = f"dcisionai-manufacturing-test-{uuid.uuid4().hex[:8]}-{int(time.time())}"
    
    # Prepare request
    request_body = {
        "input": {
            "prompt": scenario['prompt']
        }
    }
    
    # Agent runtime ARN
    agent_runtime_arn = 'arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/dcisionai_manufacturing_mcp_server-nk8uWLCqPh'
    
    logger.info(f"🔗 Agent: {agent_runtime_arn}")
    logger.info(f"🆔 Session: {session_id}")
    logger.info(f"📝 Prompt: {scenario['prompt'][:100]}...")
    
    # Time the request
    start_time = time.time()
    
    try:
        # Make the API call
        logger.info("🔄 Invoking agent...")
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(request_body),
            qualifier="DEFAULT"
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Parse response
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        logger.info(f"✅ Response Time: {response_time:.2f}s")
        logger.info("✅ Request successful!")
        
        # Validate response
        output = response_data.get('output', {})
        tools_available = output.get('tools_available', [])
        message = output.get('message', '')
        model_name = output.get('model', '')
        server_ready = output.get('server_ready', False)
        
        # Log validation results
        logger.info("\n🔍 Validation Results:")
        logger.info(f"   Tools Available: {len(tools_available)}/6")
        logger.info(f"   Manufacturing Domain: {'manufacturing' in message.lower()}")
        logger.info(f"   Branding Correct: {'dcisionai-manufacturing' in model_name}")
        logger.info(f"   Server Ready: {server_ready}")
        logger.info(f"   Response Format: Complete")
        
        # Check if all expected tools are available
        missing_tools = [tool for tool in scenario['expected_tools'] if tool not in tools_available]
        if missing_tools:
            logger.warning(f"⚠️ Missing tools: {missing_tools}")
        else:
            logger.info("✅ All expected tools available!")
        
        # Log response summary
        logger.info(f"\n📝 Response Message: {message[:200]}...")
        logger.info(f"🏷️ Model: {model_name}")
        logger.info(f"🛠️ Tools Found: {tools_available}")
        
        # Performance metrics
        logger.info(f"\n📊 Performance Metrics:")
        logger.info(f"   Response Time: {response_time:.2f}s")
        logger.info(f"   Tools Available: {len(tools_available)}/6")
        logger.info(f"   Validation Passed: {len(missing_tools) == 0}")
        
        return True
        
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        
        logger.error(f"❌ Test Failed: {e}")
        logger.error(f"⏱️ Time to failure: {response_time:.2f}s")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting Single Manufacturing Use Case Test")
    logger.info("=" * 60)
    
    success = test_production_line_optimization()
    
    if success:
        logger.info("\n🎉 Test completed successfully!")
        return 0
    else:
        logger.error("\n❌ Test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
