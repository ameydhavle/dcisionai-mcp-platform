#!/usr/bin/env python3
"""
Local test for DcisionAI Manufacturing AgentCore Agent (SDK Integration)
Tests the agent locally before deployment to AgentCore
"""

import sys
import os
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_agentcore_sdk_agent():
    """Test the SDK-based AgentCore agent locally."""
    
    print("🧪 Testing DcisionAI Manufacturing AgentCore Agent (SDK Integration)")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import the agent module
        from mcp_server.agentcore_simple_agent import invoke
        
        # Test payload (matches AgentCore format)
        test_payload = {
            "input": {
                "prompt": "I need to optimize my manufacturing production schedule for 3 products with different demand patterns and capacity constraints."
            }
        }
        
        print(f"\n📝 Test payload: {json.dumps(test_payload, indent=2)}")
        
        # Invoke the agent
        print("\n🚀 Invoking agent...")
        start_time = datetime.now()
        
        response = invoke(test_payload)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Agent invocation completed in {duration:.2f} seconds")
        
        # Display response
        print(f"\n📋 Agent Response:")
        print(json.dumps(response, indent=2))
        
        # Validate response format
        print(f"\n🔍 Validating response format...")
        
        if "output" not in response:
            print("❌ Response missing 'output' key")
            return False
            
        output = response["output"]
        
        if "message" not in output:
            print("❌ Response missing 'message' key")
            return False
            
        if "timestamp" not in output:
            print("❌ Response missing 'timestamp' key")
            return False
            
        if "model" not in output:
            print("❌ Response missing 'model' key")
            return False
            
        print("✅ Response format validation passed")
        
        # Check if workflow executed successfully
        message_content = output["message"]["content"][0]["text"]
        
        if "workflow_summary" in message_content:
            print("✅ Workflow execution detected")
            
            # Parse the workflow summary
            try:
                workflow_data = json.loads(message_content)
                workflow_summary = workflow_data.get("workflow_summary", {})
                
                print(f"📊 Workflow Summary:")
                print(f"  - Intent Analysis: {'✅' if 'intent_analysis' in workflow_summary else '❌'}")
                print(f"  - Data Analysis: {'✅' if 'data_analysis' in workflow_summary else '❌'}")
                print(f"  - Model Definition: {'✅' if 'model_definition' in workflow_summary else '❌'}")
                print(f"  - Optimization Result: {'✅' if 'optimization_result' in workflow_summary else '❌'}")
                
                # Check for optimization results
                opt_result = workflow_summary.get("optimization_result", {})
                if "objective_value" in opt_result:
                    print(f"  - Objective Value: {opt_result['objective_value']}")
                if "status" in opt_result:
                    print(f"  - Optimization Status: {opt_result['status']}")
                    
            except json.JSONDecodeError:
                print("⚠️ Could not parse workflow summary JSON")
        else:
            print("⚠️ No workflow summary found in response")
        
        print(f"\n🎉 Local test completed successfully!")
        print(f"⏱️ Total duration: {duration:.2f} seconds")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the project root directory")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agentcore_sdk_agent()
    sys.exit(0 if success else 1)
