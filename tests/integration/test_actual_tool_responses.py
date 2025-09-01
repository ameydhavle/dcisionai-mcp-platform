#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Actual Tool Response Test
=============================================================

Test each individual manufacturing tool to verify they provide meaningful responses.
This script invokes each tool directly and captures their actual output.

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
logger = logging.getLogger("DcisionAI Tool Response Test")

# Project root path
PROJECT_ROOT = Path(__file__).parent.parent.parent

def test_individual_tool(client, tool_name: str, test_prompt: str, session_id: str):
    """Test a single manufacturing tool and capture its response"""
    
    logger.info(f"\n🛠️ Testing Tool: {tool_name}")
    logger.info("-" * 40)
    
    # Prepare request with specific tool invocation
    request_body = {
        "input": {
            "prompt": test_prompt,
            "tool": tool_name,
            "parameters": {
                "manufacturing_context": "production_optimization",
                "data_requirements": "comprehensive",
                "optimization_target": "efficiency_and_quality"
            }
        }
    }
    
    # Agent runtime ARN
    agent_runtime_arn = 'arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/dcisionai_manufacturing_mcp_server_v2-MZWN2S2SBU'
    
    start_time = time.time()
    
    try:
        logger.info(f"📝 Prompt: {test_prompt[:100]}...")
        logger.info(f"🔧 Tool: {tool_name}")
        
        # Make the API call
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            runtimeSessionId=f"{session_id}-{tool_name}",
            payload=json.dumps(request_body),
            qualifier="DEFAULT"
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Parse response
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        logger.info(f"✅ Response Time: {response_time:.2f}s")
        
        # Analyze the response
        output = response_data.get('output', {})
        message = output.get('message', '')
        tools_available = output.get('tools_available', [])
        
        # Check if this specific tool responded
        tool_responded = tool_name in tools_available
        
        logger.info(f"📝 Response Message: {message[:200]}...")
        logger.info(f"🛠️ Tool Available: {tool_responded}")
        logger.info(f"📊 Response Length: {len(message)} characters")
        
        # Check for meaningful content
        meaningful_response = len(message) > 50 and not message.startswith("DcisionAI Manufacturing MCP Server received:")
        
        if meaningful_response:
            logger.info("✅ Tool provided meaningful response")
        else:
            logger.warning("⚠️ Tool response may be generic")
        
        return {
            'tool_name': tool_name,
            'success': True,
            'response_time': response_time,
            'response_length': len(message),
            'tool_responded': tool_responded,
            'meaningful_response': meaningful_response,
            'message': message,
            'full_response': response_data
        }
        
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        
        logger.error(f"❌ Tool {tool_name} failed: {e}")
        return {
            'tool_name': tool_name,
            'success': False,
            'error': str(e),
            'response_time': response_time
        }

def test_all_manufacturing_tools():
    """Test all 6 manufacturing tools individually"""
    
    logger.info("🚀 Testing Individual Manufacturing Tool Responses")
    logger.info("=" * 60)
    
    # Setup AWS client
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        logger.info("✅ AWS Bedrock AgentCore client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to setup AWS client: {e}")
        return False
    
    # Define test scenarios for each tool
    tool_tests = [
        {
            'name': 'classify_manufacturing_intent',
            'prompt': 'I need to optimize my automotive production line with 3 stations. Station A: 45min, 98% quality. Station B: 38min, 95% quality. Station C: 52min, 99% quality. Target: 500 units/day, 97%+ quality. Please classify my optimization intent.',
            'expected_response_type': 'intent_classification'
        },
        {
            'name': 'analyze_data_requirements',
            'prompt': 'For my production line optimization, what specific data do I need to collect? I have processing times and quality metrics, but what else should I measure to build an effective optimization model?',
            'expected_response_type': 'data_requirements_analysis'
        },
        {
            'name': 'build_optimization_model',
            'prompt': 'Build an optimization model for my production line. I have 3 stations with different processing times and quality metrics. I need to maximize throughput while maintaining quality above 97%. What type of model should I use?',
            'expected_response_type': 'model_building'
        },
        {
            'name': 'solve_optimization_problem',
            'prompt': 'Solve my production line optimization problem. Station A: 45min, 98% quality. Station B: 38min, 95% quality. Station C: 52min, 99% quality. Target: 500 units/day, 97%+ quality. Find the optimal configuration.',
            'expected_response_type': 'problem_solving'
        },
        {
            'name': 'manufacturing_optimization_workflow',
            'prompt': 'Create a workflow for my production line optimization. I need to go from data collection to implementation. What steps should I follow and in what order?',
            'expected_response_type': 'workflow_orchestration'
        },
        {
            'name': 'manufacturing_tools_status',
            'prompt': 'What is the current status of all manufacturing tools? Are they all operational and ready for optimization tasks?',
            'expected_response_type': 'status_monitoring'
        }
    ]
    
    # Create session ID
    session_id = f"dcisionai-tool-test-{uuid.uuid4().hex[:8]}-{int(time.time())}"
    
    # Test each tool
    results = []
    
    for tool_test in tool_tests:
        result = test_individual_tool(
            client, 
            tool_test['name'], 
            tool_test['prompt'], 
            session_id
        )
        results.append(result)
        
        # Wait between tests
        time.sleep(3)
    
    # Generate comprehensive report
    generate_tool_response_report(results, tool_tests)
    
    return results

def generate_tool_response_report(results, tool_tests):
    """Generate comprehensive report of tool responses"""
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 Manufacturing Tool Response Report")
    logger.info("=" * 60)
    
    successful_tools = [r for r in results if r['success']]
    failed_tools = [r for r in results if not r['success']]
    
    logger.info(f"🎯 Total Tools Tested: {len(results)}")
    logger.info(f"✅ Successful: {len(successful_tools)}")
    logger.info(f"❌ Failed: {len(failed_tools)}")
    logger.info(f"📈 Success Rate: {(len(successful_tools)/len(results)*100):.1f}%")
    
    if successful_tools:
        avg_response_time = sum(r['response_time'] for r in successful_tools) / len(successful_tools)
        logger.info(f"⏱️ Average Response Time: {avg_response_time:.2f}s")
    
    # Detailed results for each tool
    logger.info("\n🔍 Detailed Tool Results:")
    
    for i, result in enumerate(results, 1):
        logger.info(f"\n   Tool {i}: {result['tool_name']}")
        
        if result['success']:
            logger.info(f"      ✅ Response Time: {result['response_time']:.2f}s")
            logger.info(f"      ✅ Response Length: {result['response_length']} chars")
            logger.info(f"      ✅ Tool Responded: {result['tool_responded']}")
            logger.info(f"      ✅ Meaningful Response: {result['meaningful_response']}")
            
            # Show first 100 chars of response
            message_preview = result['message'][:100].replace('\n', ' ')
            logger.info(f"      📝 Preview: {message_preview}...")
        else:
            logger.info(f"      ❌ Error: {result['error']}")
    
    # Summary of meaningful responses
    meaningful_responses = [r for r in successful_tools if r.get('meaningful_response', False)]
    logger.info(f"\n📊 Meaningful Responses: {len(meaningful_responses)}/{len(successful_tools)}")
    
    # Save detailed report
    report_file = PROJECT_ROOT / "manufacturing_tool_responses_report.json"
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'tool_tests': tool_tests,
            'summary': {
                'total_tools': len(results),
                'successful_tools': len(successful_tools),
                'failed_tools': len(failed_tools),
                'meaningful_responses': len(meaningful_responses),
                'success_rate': len(successful_tools)/len(results)*100 if results else 0
            }
        }, f, indent=2, default=str)
    
    logger.info(f"\n📄 Detailed report saved to: {report_file}")
    
    # Final assessment
    if len(meaningful_responses) == len(successful_tools):
        logger.info("🎉 All tools providing meaningful responses!")
    elif len(meaningful_responses) > len(successful_tools) * 0.5:
        logger.info("✅ Most tools providing meaningful responses")
    else:
        logger.warning("⚠️ Many tools may not be providing meaningful responses")

def main():
    """Main test function"""
    logger.info("🚀 Starting Manufacturing Tool Response Test")
    logger.info("=" * 60)
    
    results = test_all_manufacturing_tools()
    
    if results:
        successful_count = len([r for r in results if r['success']])
        if successful_count == len(results):
            logger.info("\n🎉 All tools tested successfully!")
            return 0
        else:
            logger.warning(f"\n⚠️ {len(results) - successful_count} tools failed")
            return 1
    else:
        logger.error("\n❌ Tool testing failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
