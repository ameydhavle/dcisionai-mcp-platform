#!/usr/bin/env python3
"""
Test Intent-Only AgentCore Runtime
=================================

Test the intent-only AgentCore runtime to verify it's working correctly.
Shows complete detailed output like local tests.
"""

import json
import time
import boto3
from datetime import datetime

# Configuration
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Intent_Only_1756311981-SD7ngPGtiC"
REGION = "us-east-1"

def test_intent_only_agentcore():
    """Test the intent-only AgentCore runtime with detailed output."""
    print("🧪 TESTING INTENT-ONLY AGENTCORE RUNTIME")
    print("=" * 50)
    
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    
    # Test queries
    test_queries = [
        "I need to optimize my production schedule to minimize costs while meeting customer demand",
        "Help me optimize my inventory levels to reduce holding costs",
        "I need to optimize the allocation of workers and machines across multiple production lines"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        print("-" * 40)
        
        try:
            # Prepare request
            request_body = {
                "input": {
                    "prompt": query
                }
            }
            
            print(f"📤 Sending request to AgentCore...")
            start_time = time.time()
            
            # Invoke AgentCore
            response = client.invoke_agent_runtime(
                agentRuntimeArn=AGENT_RUNTIME_ARN,
                payload=json.dumps(request_body),
                mcpSessionId=f"intent_test_{i}_{int(time.time())}",
                contentType="application/json"
            )
            
            execution_time = time.time() - start_time
            print(f"⏱️ Execution time: {execution_time:.2f}s")
            
            # Parse response
            if 'response' in response:
                response_body = json.loads(response['response'].read())
            elif 'payload' in response:
                response_body = json.loads(response['payload'].read())
            elif 'responseBody' in response:
                response_body = json.loads(response['responseBody'].read())
            else:
                print(f"⚠️ Unexpected response format")
                continue
            
            print(f"✅ Response received successfully!")
            print(f"📊 Response length: {len(str(response_body))} characters")
            
            # Extract and display complete intent analysis
            if "response" in response_body and "output" in response_body["response"]:
                output = response_body["response"]["output"]
                
                print(f"\n🧠 COMPLETE INTENT ANALYSIS:")
                print(f"   📝 Message: {output.get('message', {}).get('content', [{}])[0].get('text', 'N/A')}")
                print(f"   🕐 Timestamp: {output.get('timestamp', 'N/A')}")
                print(f"   🤖 Model: {output.get('model', 'N/A')}")
                print(f"   🔧 Workflow Type: {output.get('workflow_type', 'N/A')}")
                print(f"   🛠️ Tools Used: {output.get('tools_used', [])}")
                
                # Detailed intent analysis
                intent_analysis = output.get('intent_analysis', {})
                if intent_analysis:
                    print(f"\n📊 DETAILED INTENT RESULTS:")
                    print(f"   🎯 Primary Intent: {intent_analysis.get('primary_intent', 'N/A')}")
                    print(f"   📈 Confidence: {intent_analysis.get('confidence', 'N/A')}")
                    print(f"   🎯 Objectives: {intent_analysis.get('objectives', [])}")
                    print(f"   🏷️ Entities: {intent_analysis.get('entities', [])}")
                
                # Show complete response structure
                print(f"\n📄 COMPLETE RESPONSE STRUCTURE:")
                print(json.dumps(response_body, indent=2))
                
            else:
                print(f"⚠️ Response doesn't contain expected structure")
                print(f"📋 Response preview: {str(response_body)[:500]}...")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            continue
    
    print(f"\n🎉 Intent-only AgentCore testing completed!")

def main():
    """Main test execution."""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Agent Runtime ARN: {AGENT_RUNTIME_ARN}")
    
    test_intent_only_agentcore()
    
    print(f"\n✅ Intent-only AgentCore test completed!")

if __name__ == "__main__":
    main()
