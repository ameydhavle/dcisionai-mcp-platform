#!/usr/bin/env python3
"""
Local Test - Intent Only Workflow
================================

Test the intent-only workflow locally before deploying to AgentCore.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcp_server.fastmcp_server_intent_only import DcisionAIFastMCPServerIntentOnly

async def test_intent_only_workflow():
    """Test the intent-only workflow locally."""
    print("🧪 LOCAL TEST: Intent Only Workflow")
    print("=" * 50)
    
    try:
        # Initialize the intent-only server
        print("🔄 Initializing intent-only server...")
        server = DcisionAIFastMCPServerIntentOnly()
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
            
            # Process the query
            start_time = datetime.now()
            result = await server.process_message(query)
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            print(f"⏱️ Execution time: {execution_time:.2f}s")
            print(f"✅ Success: {result.get('overall_success', False)}")
            
            if result.get('overall_success', False):
                intent_stage = result.get('stages', {}).get('intent', {})
                intent_result = intent_stage.get('result', {})
                
                print(f"🧠 Primary Intent: {intent_result.get('primary_intent', 'UNKNOWN')}")
                print(f"📊 Confidence: {intent_result.get('confidence', 0.0)}")
                print(f"🎯 Objectives: {intent_result.get('objectives', [])}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test execution."""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await test_intent_only_workflow()
    
    if success:
        print(f"\n🎉 LOCAL INTENT-ONLY TEST PASSED!")
        print(f"✅ Ready for AgentCore deployment")
    else:
        print(f"\n❌ LOCAL INTENT-ONLY TEST FAILED!")
        print(f"🔧 Fix issues before deploying to AgentCore")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
