#!/usr/bin/env python3
"""
Test Intent + Data AgentCore Runtime
===================================

Test the intent + data AgentCore runtime to verify it's working correctly.
Shows complete detailed output like local tests.
"""

import json
import time
import boto3
from datetime import datetime

# Configuration
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Intent_Only_1756334028-cvrf6864CE"
REGION = "us-east-1"

def test_intent_data_agentcore():
    """Test the intent + data AgentCore runtime with detailed output."""
    print("🧪 TESTING INTENT + DATA AGENTCORE RUNTIME")
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
            start_time = time.time()
            
            # Prepare request
            request_body = {
                "input": {
                    "prompt": query
                }
            }
            
            # Invoke AgentCore runtime
            response = client.invoke_agent_runtime(
                agentRuntimeArn=AGENT_RUNTIME_ARN,
                payload=json.dumps(request_body)
            )
            
            execution_time = time.time() - start_time
            print(f"⏱️ Execution time: {execution_time:.2f}s")
            
            # Extract response
            response_data = json.loads(response['output']['message']['content'][0]['text'])
            
            # Display results
            print(f"✅ AgentCore invocation completed successfully!")
            print(f"🔧 Workflow Type: {response_data.get('workflow_type', 'N/A')}")
            
            # Intent results
            intent_stage = response_data.get("stages", {}).get("intent", {})
            if intent_stage.get("success"):
                intent_result = intent_stage.get("result", {})
                print(f"\n🧠 INTENT ANALYSIS:")
                print(f"   🎯 Primary Intent: {intent_result.get('primary_intent', 'N/A')}")
                print(f"   📈 Confidence: {intent_result.get('confidence', 'N/A')}")
                print(f"   🎯 Objectives: {intent_result.get('objectives', [])}")
                print(f"   🏷️ Entities: {intent_result.get('entities', [])}")
                
                # Show specialist consensus if available
                classification_metadata = intent_result.get('classification_metadata', {})
                if classification_metadata:
                    specialist_consensus = classification_metadata.get('specialist_consensus', {})
                    if specialist_consensus:
                        print(f"   🤝 Specialist Consensus:")
                        for agent, analysis in specialist_consensus.items():
                            print(f"      {agent}: {analysis.get('classification', 'N/A')} (confidence: {analysis.get('confidence', 'N/A')})")
            
            # Data results
            data_stage = response_data.get("stages", {}).get("data", {})
            if data_stage.get("success"):
                data_result = data_stage.get("result", {})
                print(f"\n📊 DATA ANALYSIS:")
                print(f"   🆔 Analysis ID: {data_result.get('analysis_id', 'N/A')}")
                print(f"   🏭 Industry: {data_result.get('industry_context', 'N/A')}")
                print(f"   📋 Extracted Entities: {len(data_result.get('extracted_data_entities', []))}")
                print(f"   ❌ Missing Entities: {len(data_result.get('missing_data_entities', []))}")
                print(f"   📈 Optimization Readiness: {data_result.get('optimization_readiness_score', 'N/A')}")
                
                # Show sample data if available
                sample_data = data_result.get('sample_data_generated', {})
                if sample_data:
                    print(f"   📊 Sample Data Generated:")
                    for entity, values in sample_data.items():
                        print(f"      {entity}: {values}")
            
            # Show complete result structure
            print(f"\n📄 COMPLETE WORKFLOW RESULT:")
            print(json.dumps(response_data, indent=2, default=str))
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            continue
    
    print(f"\n🎉 Intent + Data AgentCore testing completed!")

def main():
    """Main test execution."""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_intent_data_agentcore()
    
    print(f"\n✅ Intent + Data AgentCore test completed!")

if __name__ == "__main__":
    main()
