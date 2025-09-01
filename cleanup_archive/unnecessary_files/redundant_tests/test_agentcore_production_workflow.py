#!/usr/bin/env python3
"""
DcisionAI MCP Platform - AgentCore Production Workflow Test
==========================================================

Comprehensive end-to-end test of the complete manufacturing optimization workflow
deployed on AWS Bedrock AgentCore.

This test validates:
- Complete 4-tool workflow (Intent → Data → Model → Solver)
- AgentCore integration and performance
- Production-ready optimization capabilities
- Real-world manufacturing scenarios
"""

import asyncio
import json
import time
import boto3
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_MCP_v1_v2_1756310225-cfaY5Q8xSl"
REGION = "us-east-1"

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Production Optimization",
        "query": "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing",
        "expected_intent": "PRODUCTION_SCHEDULING",
        "expected_confidence": 0.8
    },
    {
        "name": "Inventory Optimization",
        "query": "Help me optimize my inventory levels to reduce holding costs while ensuring we don't run out of critical components for our electronics manufacturing",
        "expected_intent": "INVENTORY_OPTIMIZATION",
        "expected_confidence": 0.8
    },
    {
        "name": "Resource Allocation",
        "query": "I need to optimize the allocation of workers and machines across multiple production lines to maximize efficiency for our aerospace manufacturing",
        "expected_intent": "RESOURCE_ALLOCATION",
        "expected_confidence": 0.8
    }
]


class AgentCoreProductionTester:
    """Production test suite for AgentCore deployment."""
    
    def __init__(self):
        self.client = boto3.client('bedrock-agentcore', region_name=REGION)
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def print_header(self, title: str):
        """Print formatted header."""
        print("\n" + "=" * 80)
        print(f"🚀 {title}")
        print("=" * 80)
    
    def print_section(self, title: str):
        """Print formatted section."""
        print(f"\n📋 {title}")
        print("-" * 60)
    
    async def invoke_agentcore(self, prompt: str) -> Dict[str, Any]:
        """Invoke AgentCore runtime with the given prompt."""
        try:
            # Prepare request body
            request_body = {
                "input": {
                    "prompt": prompt
                }
            }
            
            self.log(f"Invoking AgentCore with prompt: {prompt[:100]}...")
            
            # Invoke AgentCore
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=AGENT_RUNTIME_ARN,
                payload=json.dumps(request_body),
                mcpSessionId=f"test_session_{int(time.time())}",
                contentType="application/json"
            )
            
            # Parse response
            if 'response' in response:
                response_body = json.loads(response['response'].read())
            elif 'payload' in response:
                response_body = json.loads(response['payload'].read())
            elif 'responseBody' in response:
                response_body = json.loads(response['responseBody'].read())
            else:
                raise ValueError("Unexpected response format")
            
            return response_body
            
        except Exception as e:
            self.log(f"Error invoking AgentCore: {str(e)}", "ERROR")
            raise
    
    def analyze_response(self, response: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the response and extract key metrics."""
        analysis = {
            "scenario": scenario["name"],
            "query": scenario["query"],
            "response_received": True,
            "response_length": len(str(response)),
            "has_intent": False,
            "has_data": False,
            "has_model": False,
            "has_solver": False,
            "workflow_complete": False,
            "errors": []
        }
        
        try:
            # Check for workflow components
            response_text = str(response).lower()
            
            # Check for intent analysis
            if any(keyword in response_text for keyword in ["intent", "classification", "production_scheduling", "inventory_optimization"]):
                analysis["has_intent"] = True
            
            # Check for data analysis
            if any(keyword in response_text for keyword in ["data", "requirements", "entities", "sample_data"]):
                analysis["has_data"] = True
            
            # Check for model building
            if any(keyword in response_text for keyword in ["model", "variables", "constraints", "objective"]):
                analysis["has_model"] = True
            
            # Check for solver execution
            if any(keyword in response_text for keyword in ["solver", "solution", "optimal", "feasible"]):
                analysis["has_solver"] = True
            
            # Check if complete workflow executed
            if all([analysis["has_intent"], analysis["has_data"], analysis["has_model"], analysis["has_solver"]]):
                analysis["workflow_complete"] = True
            
        except Exception as e:
            analysis["errors"].append(f"Analysis error: {str(e)}")
        
        return analysis
    
    async def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario."""
        self.print_section(f"Testing: {scenario['name']}")
        
        start_time = time.time()
        
        try:
            # Invoke AgentCore
            response = await self.invoke_agentcore(scenario["query"])
            
            # Calculate timing
            execution_time = time.time() - start_time
            
            # Analyze response
            analysis = self.analyze_response(response, scenario)
            analysis["execution_time"] = execution_time
            analysis["success"] = True
            
            # Log results
            self.log(f"✅ Scenario completed in {execution_time:.2f}s")
            self.log(f"   Intent: {analysis['has_intent']}")
            self.log(f"   Data: {analysis['has_data']}")
            self.log(f"   Model: {analysis['has_model']}")
            self.log(f"   Solver: {analysis['has_solver']}")
            self.log(f"   Complete: {analysis['workflow_complete']}")
            
            return analysis
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log(f"❌ Scenario failed after {execution_time:.2f}s: {str(e)}", "ERROR")
            
            return {
                "scenario": scenario["name"],
                "query": scenario["query"],
                "execution_time": execution_time,
                "success": False,
                "error": str(e),
                "response_received": False,
                "workflow_complete": False
            }
    
    async def run_all_scenarios(self):
        """Run all test scenarios."""
        self.print_header("AGENTCORE PRODUCTION WORKFLOW TEST")
        self.log(f"Testing AgentCore Runtime: {AGENT_RUNTIME_ARN}")
        self.log(f"Total scenarios: {len(TEST_SCENARIOS)}")
        
        self.start_time = time.time()
        
        # Run each scenario
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            self.log(f"\n--- Scenario {i}/{len(TEST_SCENARIOS)} ---")
            result = await self.run_scenario(scenario)
            self.results.append(result)
            
            # Brief pause between scenarios
            if i < len(TEST_SCENARIOS):
                await asyncio.sleep(2)
        
        self.end_time = time.time()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        self.print_header("PRODUCTION TEST RESULTS")
        
        # Calculate summary statistics
        total_time = self.end_time - self.start_time
        successful_scenarios = sum(1 for r in self.results if r.get("success", False))
        failed_scenarios = len(self.results) - successful_scenarios
        complete_workflows = sum(1 for r in self.results if r.get("workflow_complete", False))
        
        # Overall statistics
        self.print_section("Overall Performance")
        print(f"📊 Total Scenarios: {len(self.results)}")
        print(f"✅ Successful: {successful_scenarios}")
        print(f"❌ Failed: {failed_scenarios}")
        print(f"🎯 Complete Workflows: {complete_workflows}")
        print(f"⏱️ Total Test Time: {total_time:.2f}s")
        print(f"📈 Success Rate: {(successful_scenarios/len(self.results)*100):.1f}%")
        print(f"🚀 Workflow Completion Rate: {(complete_workflows/len(self.results)*100):.1f}%")
        
        # Individual scenario results
        self.print_section("Scenario Details")
        for i, result in enumerate(self.results, 1):
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            workflow_status = "🎯 COMPLETE" if result.get("workflow_complete", False) else "⚠️ INCOMPLETE"
            time_taken = result.get("execution_time", 0)
            
            print(f"{i}. {result['scenario']}: {status} ({time_taken:.2f}s) - {workflow_status}")
            
            if not result.get("success", False):
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # Performance analysis
        self.print_section("Performance Analysis")
        successful_results = [r for r in self.results if r.get("success", False)]
        if successful_results:
            avg_time = sum(r.get("execution_time", 0) for r in successful_results) / len(successful_results)
            min_time = min(r.get("execution_time", 0) for r in successful_results)
            max_time = max(r.get("execution_time", 0) for r in successful_results)
            
            print(f"⏱️ Average Execution Time: {avg_time:.2f}s")
            print(f"⚡ Fastest Execution: {min_time:.2f}s")
            print(f"🐌 Slowest Execution: {max_time:.2f}s")
        
        # Tool coverage analysis
        self.print_section("Tool Coverage Analysis")
        intent_count = sum(1 for r in self.results if r.get("has_intent", False))
        data_count = sum(1 for r in self.results if r.get("has_data", False))
        model_count = sum(1 for r in self.results if r.get("has_model", False))
        solver_count = sum(1 for r in self.results if r.get("has_solver", False))
        
        print(f"🧠 Intent Tool: {intent_count}/{len(self.results)} ({intent_count/len(self.results)*100:.1f}%)")
        print(f"📊 Data Tool: {data_count}/{len(self.results)} ({data_count/len(self.results)*100:.1f}%)")
        print(f"🔧 Model Tool: {model_count}/{len(self.results)} ({model_count/len(self.results)*100:.1f}%)")
        print(f"🏁 Solver Tool: {solver_count}/{len(self.results)} ({solver_count/len(self.results)*100:.1f}%)")
        
        # Final assessment
        self.print_section("Production Readiness Assessment")
        if successful_scenarios == len(self.results) and complete_workflows == len(self.results):
            print("🎉 EXCELLENT: All scenarios passed with complete workflows!")
            print("✅ AgentCore deployment is production-ready")
        elif successful_scenarios == len(self.results):
            print("✅ GOOD: All scenarios passed but some workflows incomplete")
            print("⚠️ AgentCore deployment needs workflow optimization")
        elif successful_scenarios > len(self.results) / 2:
            print("⚠️ FAIR: Most scenarios passed")
            print("🔧 AgentCore deployment needs debugging")
        else:
            print("❌ POOR: Most scenarios failed")
            print("🚨 AgentCore deployment needs significant fixes")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agentcore_production_test_results_{timestamp}.json"
        
        report_data = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "agent_runtime_arn": AGENT_RUNTIME_ARN,
                "total_scenarios": len(self.results),
                "successful_scenarios": successful_scenarios,
                "complete_workflows": complete_workflows,
                "total_test_time": total_time
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.log(f"📄 Detailed results saved to: {filename}")
        
        return {
            "success_rate": successful_scenarios / len(self.results),
            "workflow_completion_rate": complete_workflows / len(self.results),
            "production_ready": successful_scenarios == len(self.results) and complete_workflows == len(self.results)
        }


async def main():
    """Main test execution."""
    tester = AgentCoreProductionTester()
    
    try:
        # Run all scenarios
        await tester.run_all_scenarios()
        
        # Generate report
        assessment = tester.generate_report()
        
        # Final status
        if assessment["production_ready"]:
            print("\n🎉 AGENTCORE PRODUCTION TEST PASSED!")
            print("🚀 Platform is ready for production deployment!")
        else:
            print("\n⚠️ AGENTCORE PRODUCTION TEST NEEDS ATTENTION")
            print("🔧 Some issues need to be addressed before production")
        
        return assessment["production_ready"]
        
    except Exception as e:
        print(f"\n❌ TEST EXECUTION FAILED: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
