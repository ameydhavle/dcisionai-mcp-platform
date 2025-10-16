#!/usr/bin/env python3
"""
Test script for DcisionAI Manufacturing MCP Server
=================================================

Tests the MCP protocol compliance and functionality.
"""

import asyncio
import json
import time
import httpx
from typing import Dict, Any

async def test_health_endpoint():
    """Test the health check endpoint."""
    print("🔍 Testing health endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data['status']}")
                print(f"   Version: {health_data['version']}")
                print(f"   Architecture: {health_data['architecture']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

async def test_mcp_tools_list():
    """Test MCP tools listing."""
    print("\n🔍 Testing MCP tools list...")
    
    try:
        # MCP tools/list request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "tools" in result["result"]:
                    tools = result["result"]["tools"]
                    print(f"✅ Tools list retrieved: {len(tools)} tools available")
                    for tool in tools:
                        print(f"   - {tool['name']}: {tool.get('description', 'No description')}")
                    return True
                else:
                    print(f"❌ Invalid tools response: {result}")
                    return False
            else:
                print(f"❌ Tools list failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Tools list error: {str(e)}")
        return False

async def test_manufacturing_optimization():
    """Test the manufacturing optimization tool."""
    print("\n🔍 Testing manufacturing optimization...")
    
    try:
        # MCP tools/call request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "manufacturing_optimize",
                "arguments": {
                    "problem_description": "Optimize production line efficiency with 50 workers across 3 manufacturing lines, considering skill sets, line capacities, and cost constraints",
                    "constraints": {
                        "total_workers": 50,
                        "production_lines": 3,
                        "max_cost": 10000
                    },
                    "optimization_goals": ["maximize_throughput", "minimize_cost"]
                }
            }
        }
        
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "http://localhost:8000/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"]
                    if isinstance(content, list) and len(content) > 0:
                        optimization_result = content[0].get("text", "{}")
                        if isinstance(optimization_result, str):
                            optimization_data = json.loads(optimization_result)
                        else:
                            optimization_data = optimization_result
                        
                        print(f"✅ Manufacturing optimization completed in {execution_time:.2f}s")
                        print(f"   Status: {optimization_data.get('status', 'unknown')}")
                        
                        if optimization_data.get('status') == 'success':
                            intent = optimization_data.get('intent_classification', {})
                            print(f"   Intent: {intent.get('intent', 'unknown')} (confidence: {intent.get('confidence', 0)})")
                            
                            solution = optimization_data.get('optimization_solution', {})
                            print(f"   Solution Status: {solution.get('status', 'unknown')}")
                            print(f"   Objective Value: {solution.get('objective_value', 0)}")
                            print(f"   Solve Time: {solution.get('solve_time', 0):.2f}s")
                            
                            return True
                        else:
                            print(f"   Error: {optimization_data.get('error', 'Unknown error')}")
                            return False
                    else:
                        print(f"❌ Invalid content format: {content}")
                        return False
                else:
                    print(f"❌ Invalid optimization response: {result}")
                    return False
            else:
                print(f"❌ Optimization request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Optimization test error: {str(e)}")
        return False

async def test_health_check_tool():
    """Test the health check tool."""
    print("\n🔍 Testing health check tool...")
    
    try:
        # MCP tools/call request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "manufacturing_health_check",
                "arguments": {}
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"]
                    if isinstance(content, list) and len(content) > 0:
                        health_data = content[0].get("text", "{}")
                        if isinstance(health_data, str):
                            health_info = json.loads(health_data)
                        else:
                            health_info = health_data
                        
                        print(f"✅ Health check tool passed: {health_info.get('status', 'unknown')}")
                        print(f"   Tools Available: {health_info.get('tools_available', 0)}")
                        print(f"   Bedrock Connected: {health_info.get('bedrock_connected', False)}")
                        return True
                    else:
                        print(f"❌ Invalid health content: {content}")
                        return False
                else:
                    print(f"❌ Invalid health response: {result}")
                    return False
            else:
                print(f"❌ Health check tool failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health check tool error: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting DcisionAI Manufacturing MCP Server Tests")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    await asyncio.sleep(2)
    
    # Run tests
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("MCP Tools List", test_mcp_tools_list),
        ("Health Check Tool", test_health_check_tool),
        ("Manufacturing Optimization", test_manufacturing_optimization),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server configuration.")

if __name__ == "__main__":
    asyncio.run(main())
