#!/usr/bin/env python3
"""
Direct test of swarm components without MCP server.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from manufacturing_intent_swarm import ManufacturingIntentSwarm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_swarm_direct():
    """Test swarm components directly."""
    print("🧪 Testing Swarm Components Directly")
    print("=" * 50)
    
    try:
        # Test 1: Initialize Intent Swarm
        print("1. Initializing ManufacturingIntentSwarm...")
        intent_swarm = ManufacturingIntentSwarm()
        print("   ✅ Intent swarm initialized successfully")
        
        # Test 2: Check swarm status
        print("2. Checking swarm status...")
        status = intent_swarm.get_swarm_status()
        print(f"   ✅ Swarm status: {status}")
        
        # Test 3: Test intent classification
        print("3. Testing intent classification...")
        test_query = "Optimize production line efficiency for maximum throughput"
        result = intent_swarm.classify_intent(test_query)
        print(f"   ✅ Intent classification result: {result}")
        
        # Test 4: Check if result is real or mock
        if result.get("status") == "success":
            print("   🎉 REAL SWARM RESPONSE!")
        else:
            print(f"   ❌ SWARM FAILED: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ SWARM TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_swarm_direct()
    if success:
        print("\n🎉 SWARM COMPONENTS WORKING!")
    else:
        print("\n❌ SWARM COMPONENTS FAILED!")
