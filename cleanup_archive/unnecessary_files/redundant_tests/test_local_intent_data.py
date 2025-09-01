#!/usr/bin/env python3
"""
Test Intent + Data Workflow Locally
==================================

Test the intent + data workflow locally before deploying to AgentCore.
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import the FastMCP server
from mcp_server.fastmcp_server_intent_data import DcisionAIFastMCPServerIntentData

def test_intent_data_workflow():
    """Test the intent + data workflow locally."""
    print("🧪 TESTING INTENT + DATA WORKFLOW LOCALLY")
    print("=" * 50)
    
    # Initialize the server
    print("🚀 Initializing FastMCP server...")
    server = DcisionAIFastMCPServerIntentData()
    print("✅ Server initialized successfully")
    
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
            
            # Process message
            workflow_result = asyncio.run(server.process_message(query))
            
            execution_time = time.time() - start_time
            print(f"⏱️ Execution time: {execution_time:.2f}s")
            
            # Display results
            if workflow_result.get("overall_success"):
                print(f"✅ Workflow completed successfully!")
                print(f"🔧 Workflow Type: {workflow_result.get('workflow_type')}")
                
                # Intent results
                intent_stage = workflow_result.get("stages", {}).get("intent", {})
                if intent_stage.get("success"):
                    intent_result = intent_stage.get("result", {})
                    print(f"\n🧠 INTENT ANALYSIS:")
                    print(f"   🎯 Primary Intent: {intent_result.get('primary_intent', 'N/A')}")
                    print(f"   📈 Confidence: {intent_result.get('confidence', 'N/A')}")
                    print(f"   🎯 Objectives: {intent_result.get('objectives', [])}")
                    print(f"   🏷️ Entities: {intent_result.get('entities', [])}")
                
                # Data results
                data_stage = workflow_result.get("stages", {}).get("data", {})
                if data_stage.get("success"):
                    data_result = data_stage.get("result", {})
                    print(f"\n📊 DATA ANALYSIS:")
                    print(f"   🆔 Analysis ID: {data_result.get('analysis_id', 'N/A')}")
                    print(f"   🏭 Industry: {data_result.get('industry_context', 'N/A')}")
                    print(f"   📋 Extracted Entities: {len(data_result.get('extracted_data_entities', []))}")
                    print(f"   ❌ Missing Entities: {len(data_result.get('missing_data_entities', []))}")
                    print(f"   📈 Optimization Readiness: {data_result.get('optimization_readiness_score', 'N/A')}")
                
                # Show complete result structure
                print(f"\n📄 COMPLETE WORKFLOW RESULT:")
                print(json.dumps(workflow_result, indent=2, default=str))
                
            else:
                print(f"❌ Workflow failed: {workflow_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            continue
    
    print(f"\n🎉 Intent + Data workflow testing completed!")

def main():
    """Main test execution."""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_intent_data_workflow()
    
    print(f"\n✅ Intent + Data workflow test completed!")

if __name__ == "__main__":
    main()
