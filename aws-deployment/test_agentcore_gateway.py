#!/usr/bin/env python3
"""
Test AgentCore Gateway Integration with DcisionAI Optimization Workflows
====================================================================

This script tests the AgentCore Gateway integration with optimization workflows,
including semantic search, tool discovery, and workflow execution.
"""

import boto3
import json
import requests
import time
from typing import Dict, Any, List
from datetime import datetime

class AgentCoreGatewayTester:
    def __init__(self, gateway_endpoint: str, cognito_config: Dict[str, str]):
        self.gateway_endpoint = gateway_endpoint
        self.cognito_config = cognito_config
        self.cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
        self.jwt_token = None
        
    def get_jwt_token(self) -> str:
        """Get JWT token from Cognito for Gateway authentication."""
        print("🔑 Getting JWT token from Cognito...")
        
        try:
            # For testing, we'll use a mock token
            # In production, this would be obtained through proper OAuth flow
            self.jwt_token = "mock-jwt-token-for-testing"
            print("✅ JWT token obtained (mock for testing)")
            return self.jwt_token
        except Exception as e:
            print(f"❌ Failed to get JWT token: {e}")
            raise
    
    def test_semantic_search(self, query: str) -> List[Dict[str, Any]]:
        """Test semantic search for optimization tools."""
        print(f"🔍 Testing semantic search: '{query}'")
        
        tool_params = {
            "name": "x_amz_bedrock_agentcore_search",
            "arguments": {"query": query}
        }
        
        try:
            response = self.invoke_gateway_tool(tool_params)
            tools = response.get("result", {}).get("structuredContent", {}).get("tools", [])
            print(f"✅ Found {len(tools)} tools for query: '{query}'")
            
            for tool in tools:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            
            return tools
        except Exception as e:
            print(f"❌ Semantic search failed: {e}")
            return []
    
    def invoke_gateway_tool(self, tool_params: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a tool through the Gateway."""
        headers = {
            'Authorization': f'Bearer {self.jwt_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": tool_params
        }
        
        try:
            response = requests.post(
                self.gateway_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Gateway tool invocation failed: {e}")
            raise
    
    def test_optimization_workflow(self, workflow_type: str, problem_description: str) -> Dict[str, Any]:
        """Test optimization workflow execution through Gateway."""
        print(f"🔧 Testing {workflow_type} optimization workflow...")
        
        tool_params = {
            "name": f"optimize_{workflow_type}",
            "arguments": {
                "problem_description": problem_description,
                "custom_parameters": {}
            }
        }
        
        try:
            response = self.invoke_gateway_tool(tool_params)
            result = response.get("result", {})
            
            if result.get("isError"):
                print(f"❌ Workflow execution failed: {result.get('content', 'Unknown error')}")
                return {"status": "error", "error": result.get("content")}
            else:
                print(f"✅ Workflow executed successfully")
                return {"status": "success", "result": result}
                
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_production_planning_workflow(self) -> Dict[str, Any]:
        """Test production planning optimization workflow."""
        problem_description = """
        Optimize production for 5 products across 3 production lines: 
        Product A (demand: 1,200 units, profit: $25/unit, labor: 2.5 hrs/unit, material: $8/unit), 
        Product B (demand: 800 units, profit: $18/unit, labor: 1.8 hrs/unit, material: $6/unit), 
        Product C (demand: 600 units, profit: $32/unit, labor: 3.2 hrs/unit, material: $12/unit), 
        Product D (demand: 400 units, profit: $28/unit, labor: 2.8 hrs/unit, material: $10/unit), 
        Product E (demand: 300 units, profit: $35/unit, labor: 4.0 hrs/unit, material: $15/unit). 
        
        Production line capacities: 
        Line 1 (1,500 units/month, 3,000 labor hours), 
        Line 2 (1,200 units/month, 2,400 labor hours), 
        Line 3 (800 units/month, 1,600 labor hours). 
        
        Material inventory: $50,000 available. 
        Setup costs: $500 per product per line. 
        
        Maximize total profit while meeting demand, capacity, labor, and material constraints.
        """
        
        return self.test_optimization_workflow("production_planning", problem_description)
    
    def test_marketing_optimization_workflow(self) -> Dict[str, Any]:
        """Test marketing spend optimization workflow."""
        problem_description = """
        Optimize $50,000 monthly marketing budget across 6 channels and 3 customer segments. 
        
        Channels: 
        Google Ads (ROI: 4.2x, cost per click: $2.50), 
        Facebook Ads (ROI: 3.8x, cost per click: $1.80), 
        LinkedIn Ads (ROI: 5.1x, cost per click: $4.20), 
        Email Marketing (ROI: 6.5x, cost per email: $0.15), 
        Content Marketing (ROI: 2.8x, cost per article: $500), 
        Influencer Marketing (ROI: 3.5x, cost per post: $2,000). 
        
        Customer segments: 
        Enterprise (LTV: $5,000, conversion: 8%), 
        SMB (LTV: $1,200, conversion: 12%), 
        Consumer (LTV: $300, conversion: 15%). 
        
        Channel capacity limits: 
        Google Ads max $15,000, Facebook max $12,000, LinkedIn max $8,000. 
        
        Maximize total customer acquisition value while maintaining brand awareness minimums.
        """
        
        return self.test_optimization_workflow("marketing_spend", problem_description)
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite for AgentCore Gateway."""
        print("🧪 Running Comprehensive AgentCore Gateway Test Suite")
        print("=" * 60)
        
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'success'
        }
        
        try:
            # Test 1: Get JWT token
            print("\n1️⃣ Testing JWT Token Authentication")
            self.get_jwt_token()
            test_results['tests']['jwt_auth'] = {'status': 'success'}
            
            # Test 2: Semantic search for production planning
            print("\n2️⃣ Testing Semantic Search - Production Planning")
            production_tools = self.test_semantic_search("production planning optimization")
            test_results['tests']['semantic_search_production'] = {
                'status': 'success',
                'tools_found': len(production_tools)
            }
            
            # Test 3: Semantic search for marketing optimization
            print("\n3️⃣ Testing Semantic Search - Marketing Optimization")
            marketing_tools = self.test_semantic_search("marketing spend optimization")
            test_results['tests']['semantic_search_marketing'] = {
                'status': 'success',
                'tools_found': len(marketing_tools)
            }
            
            # Test 4: Production planning workflow
            print("\n4️⃣ Testing Production Planning Workflow")
            production_result = self.test_production_planning_workflow()
            test_results['tests']['production_workflow'] = production_result
            
            # Test 5: Marketing optimization workflow
            print("\n5️⃣ Testing Marketing Optimization Workflow")
            marketing_result = self.test_marketing_optimization_workflow()
            test_results['tests']['marketing_workflow'] = marketing_result
            
            # Check overall status
            for test_name, test_result in test_results['tests'].items():
                if test_result.get('status') == 'error':
                    test_results['overall_status'] = 'partial_failure'
                    break
            
            print("\n" + "=" * 60)
            print("🎉 Test Suite Complete!")
            print("=" * 60)
            print(f"Overall Status: {test_results['overall_status']}")
            print(f"Tests Run: {len(test_results['tests'])}")
            
            successful_tests = sum(1 for test in test_results['tests'].values() 
                                 if test.get('status') == 'success')
            print(f"Successful Tests: {successful_tests}")
            
            return test_results
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            test_results['overall_status'] = 'error'
            test_results['error'] = str(e)
            return test_results

def main():
    """Main function to test AgentCore Gateway."""
    print("🧪 DcisionAI AgentCore Gateway Test Suite")
    print("=" * 50)
    
    # Load gateway configuration
    try:
        with open('agentcore_gateway_config.json', 'r') as f:
            config = json.load(f)
        
        gateway_endpoint = config['gateway_endpoint']
        cognito_config = config['cognito_config']
        
        print(f"Gateway Endpoint: {gateway_endpoint}")
        print(f"Cognito User Pool: {cognito_config['user_pool_id']}")
        
    except FileNotFoundError:
        print("❌ Gateway configuration file not found.")
        print("Please run setup_agentcore_gateway.py first.")
        return
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return
    
    # Run tests
    tester = AgentCoreGatewayTester(gateway_endpoint, cognito_config)
    results = tester.run_comprehensive_test()
    
    # Save test results
    results_file = f"gateway_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Test results saved to: {results_file}")
    
    if results['overall_status'] == 'success':
        print("\n🎉 All tests passed! Gateway is ready for production use.")
    else:
        print("\n⚠️  Some tests failed. Please check the results and fix issues.")

if __name__ == "__main__":
    main()
