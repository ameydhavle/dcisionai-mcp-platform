#!/usr/bin/env python3
"""
Test script for MCP tools without running the server
===================================================

This script tests the MCP tools directly without needing the server to be running.
"""

import asyncio
import json
from mcp_server import manufacturing_optimize, manufacturing_health_check

async def test_manufacturing_optimize():
    """Test the manufacturing optimization tool."""
    print("🧪 Testing manufacturing_optimize tool")
    print("=" * 50)
    
    # Test case 1: Production line optimization
    print("\n📋 Test Case 1: Production Line Optimization")
    result1 = manufacturing_optimize(
        problem_description="Optimize production line efficiency with 50 workers across 3 manufacturing lines, considering skill sets, line capacities, and cost constraints",
        constraints={
            "total_workers": 50,
            "production_lines": 3,
            "max_cost": 10000
        },
        optimization_goals=["maximize_throughput", "minimize_cost"]
    )
    
    print(f"Status: {result1['status']}")
    if result1['status'] == 'success':
        intent = result1['intent_classification']
        solution = result1['optimization_solution']
        print(f"Intent: {intent['intent']} (confidence: {intent['confidence']})")
        print(f"Solution Status: {solution['status']}")
        print(f"Objective Value: {solution['objective_value']}")
        print(f"Solution: {solution['solution']}")
        print(f"Solve Time: {solution['solve_time']:.3f}s")
        print("✅ Test Case 1 PASSED")
    else:
        print(f"❌ Test Case 1 FAILED: {result1.get('error', 'Unknown error')}")
    
    # Test case 2: Supply chain optimization
    print("\n📋 Test Case 2: Supply Chain Optimization")
    result2 = manufacturing_optimize(
        problem_description="Optimize supply chain for 5 warehouses across different regions, considering demand forecasting, inventory costs, and transportation constraints",
        constraints={
            "warehouse_count": 5,
            "max_transportation_cost": 5000
        },
        optimization_goals=["minimize_total_cost", "maximize_service_level"]
    )
    
    print(f"Status: {result2['status']}")
    if result2['status'] == 'success':
        intent = result2['intent_classification']
        solution = result2['optimization_solution']
        print(f"Intent: {intent['intent']} (confidence: {intent['confidence']})")
        print(f"Solution Status: {solution['status']}")
        print(f"Objective Value: {solution['objective_value']}")
        print(f"Solution: {solution['solution']}")
        print(f"Solve Time: {solution['solve_time']:.3f}s")
        print("✅ Test Case 2 PASSED")
    else:
        print(f"❌ Test Case 2 FAILED: {result2.get('error', 'Unknown error')}")

async def test_health_check():
    """Test the health check tool."""
    print("\n🧪 Testing manufacturing_health_check tool")
    print("=" * 50)
    
    result = manufacturing_health_check()
    
    print(f"Status: {result['status']}")
    print(f"Version: {result['version']}")
    print(f"Architecture: {result['architecture']}")
    print(f"Tools Available: {result['tools_available']}")
    print(f"Bedrock Connected: {result['bedrock_connected']}")
    
    if result['status'] == 'healthy':
        print("✅ Health Check PASSED")
    else:
        print("❌ Health Check FAILED")

async def main():
    """Run all tests."""
    print("🚀 Testing DcisionAI Manufacturing MCP Tools")
    print("=" * 60)
    
    # Test health check
    await test_health_check()
    
    # Test manufacturing optimization
    await test_manufacturing_optimize()
    
    print("\n" + "=" * 60)
    print("🎉 All MCP tool tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
