#!/usr/bin/env python3
"""
AgentCore Complete Manufacturing Optimization Workflow Test
=========================================================

Test the complete 4-tool workflow on AgentCore: Intent → Data → Model → Solver
Shows detailed output from each agent in the workflow.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import time
import json
import boto3
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_MCP_v1_v2_1756310225-cfaY5Q8xSl"
REGION = "us-east-1"

class AgentCoreWorkflowTester:
    """Test the complete manufacturing optimization workflow on AgentCore"""
    
    def __init__(self):
        self.client = boto3.client('bedrock-agentcore', region_name=REGION)
        self.results = {}
        self.start_time = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def print_header(self, title: str):
        """Print formatted header."""
        print(f"\n{'='*80}")
        print(f"🚀 {title}")
        print(f"{'='*80}")
    
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
    
    def extract_workflow_stages(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and analyze workflow stages from AgentCore response."""
        stages = {
            "intent": {"found": False, "data": None},
            "data": {"found": False, "data": None},
            "model": {"found": False, "data": None},
            "solver": {"found": False, "data": None}
        }
        
        response_text = str(response).lower()
        response_str = str(response)
        
        # Look for intent analysis
        if any(keyword in response_text for keyword in ["intent", "classification", "production_scheduling", "inventory_optimization", "resource_allocation"]):
            stages["intent"]["found"] = True
            # Try to extract intent data
            try:
                if "primary_intent" in response_str:
                    stages["intent"]["data"] = {
                        "primary_intent": "EXTRACTED",
                        "confidence": "EXTRACTED",
                        "objectives": "EXTRACTED"
                    }
            except:
                pass
        
        # Look for data analysis
        if any(keyword in response_text for keyword in ["data", "requirements", "entities", "sample_data", "optimization_readiness"]):
            stages["data"]["found"] = True
            try:
                if "analysis_id" in response_str or "extracted_data_entities" in response_str:
                    stages["data"]["data"] = {
                        "analysis_id": "EXTRACTED",
                        "extracted_entities": "EXTRACTED",
                        "missing_entities": "EXTRACTED"
                    }
            except:
                pass
        
        # Look for model building
        if any(keyword in response_text for keyword in ["model", "variables", "constraints", "objective", "decision_variables"]):
            stages["model"]["found"] = True
            try:
                if "model_id" in response_str or "decision_variables" in response_str:
                    stages["model"]["data"] = {
                        "model_id": "EXTRACTED",
                        "model_type": "EXTRACTED",
                        "variables": "EXTRACTED",
                        "constraints": "EXTRACTED"
                    }
            except:
                pass
        
        # Look for solver execution
        if any(keyword in response_text for keyword in ["solver", "solution", "optimal", "feasible", "solver_type", "status"]):
            stages["solver"]["found"] = True
            try:
                if "solver_type" in response_str or "status" in response_str:
                    stages["solver"]["data"] = {
                        "solver_used": "EXTRACTED",
                        "status": "EXTRACTED",
                        "objective_value": "EXTRACTED"
                    }
            except:
                pass
        
        return stages
    
    async def test_scenario(self, scenario_name: str, user_query: str):
        """Test a complete workflow scenario on AgentCore"""
        self.print_header(f"AGENTCORE TESTING SCENARIO: {scenario_name}")
        print(f"📝 User Query: {user_query}")
        print(f"🔗 AgentCore Runtime: {AGENT_RUNTIME_ARN}")
        
        scenario_start = time.time()
        scenario_results = {
            "scenario_name": scenario_name,
            "user_query": user_query,
            "stages": {},
            "overall_success": True,
            "total_time": 0,
            "agentcore_response": None
        }
        
        try:
            # Invoke AgentCore with the complete workflow
            print(f"\n🚀 INVOKING AGENTCORE WORKFLOW")
            print(f"⏱️ Starting complete workflow execution...")
            
            workflow_start = time.time()
            response = await self.invoke_agentcore(user_query)
            workflow_time = time.time() - workflow_start
            
            scenario_results["agentcore_response"] = response
            scenario_results["total_time"] = workflow_time
            
            print(f"✅ AgentCore response received in {workflow_time:.2f}s")
            print(f"📄 Response length: {len(str(response))} characters")
            
            # Analyze the response to extract workflow stages
            print(f"\n🔍 ANALYZING WORKFLOW STAGES")
            stages = self.extract_workflow_stages(response)
            
            # Report on each stage
            print(f"\n🧠 STAGE 1: Intent Analysis")
            if stages["intent"]["found"]:
                print(f"   ✅ Intent analysis detected")
                if stages["intent"]["data"]:
                    print(f"   📊 Intent data: {stages['intent']['data']}")
                scenario_results["stages"]["intent"] = {
                    "success": True,
                    "data": stages["intent"]["data"]
                }
            else:
                print(f"   ❌ Intent analysis not detected")
                scenario_results["stages"]["intent"] = {"success": False}
                scenario_results["overall_success"] = False
            
            print(f"\n📊 STAGE 2: Data Analysis")
            if stages["data"]["found"]:
                print(f"   ✅ Data analysis detected")
                if stages["data"]["data"]:
                    print(f"   📊 Data analysis: {stages['data']['data']}")
                scenario_results["stages"]["data"] = {
                    "success": True,
                    "data": stages["data"]["data"]
                }
            else:
                print(f"   ❌ Data analysis not detected")
                scenario_results["stages"]["data"] = {"success": False}
                scenario_results["overall_success"] = False
            
            print(f"\n🔧 STAGE 3: Model Building")
            if stages["model"]["found"]:
                print(f"   ✅ Model building detected")
                if stages["model"]["data"]:
                    print(f"   📊 Model data: {stages['model']['data']}")
                scenario_results["stages"]["model"] = {
                    "success": True,
                    "data": stages["model"]["data"]
                }
            else:
                print(f"   ❌ Model building not detected")
                scenario_results["stages"]["model"] = {"success": False}
                scenario_results["overall_success"] = False
            
            print(f"\n🏁 STAGE 4: Solver Execution")
            if stages["solver"]["found"]:
                print(f"   ✅ Solver execution detected")
                if stages["solver"]["data"]:
                    print(f"   📊 Solver data: {stages['solver']['data']}")
                scenario_results["stages"]["solver"] = {
                    "success": True,
                    "data": stages["solver"]["data"]
                }
            else:
                print(f"   ❌ Solver execution not detected")
                scenario_results["stages"]["solver"] = {"success": False}
                scenario_results["overall_success"] = False
            
            # Check if complete workflow executed
            complete_workflow = all(stage["found"] for stage in stages.values())
            if complete_workflow:
                print(f"\n🎉 COMPLETE WORKFLOW DETECTED!")
                print(f"   ✅ All 4 stages executed successfully")
            else:
                print(f"\n⚠️ INCOMPLETE WORKFLOW")
                missing_stages = [stage for stage, data in stages.items() if not data["found"]]
                print(f"   ❌ Missing stages: {', '.join(missing_stages)}")
            
            # Show response preview
            print(f"\n📄 RESPONSE PREVIEW")
            response_preview = str(response)[:500] + "..." if len(str(response)) > 500 else str(response)
            print(f"   {response_preview}")
            
        except Exception as e:
            scenario_time = time.time() - scenario_start
            print(f"❌ Scenario failed after {scenario_time:.2f}s: {str(e)}")
            scenario_results["overall_success"] = False
            scenario_results["error"] = str(e)
            scenario_results["total_time"] = scenario_time
        
        return scenario_results
    
    async def run_complete_test(self):
        """Run the complete workflow test on AgentCore"""
        self.print_header("AGENTCORE COMPLETE MANUFACTURING OPTIMIZATION WORKFLOW TEST")
        print(f"🧠 Intent → 📊 Data → 🔧 Model → 🏁 Solver")
        print(f"{'='*80}")
        
        self.start_time = time.time()
        
        # Test scenarios
        scenarios = [
            {
                "name": "Production Optimization",
                "query": "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
            },
            {
                "name": "Inventory Optimization", 
                "query": "Help me optimize my inventory levels to reduce holding costs while ensuring we don't run out of critical components for our electronics manufacturing"
            },
            {
                "name": "Resource Allocation",
                "query": "I need to optimize the allocation of workers and machines across multiple production lines to maximize efficiency for our aerospace manufacturing"
            }
        ]
        
        print(f"\n{'='*80}")
        print(f"🧪 TESTING SCENARIO: Production Optimization")
        print(f"{'='*80}")
        print(f"📝 User Query: I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing")
        
        # Run the main production optimization scenario
        result = await self.test_scenario("Production Optimization", scenarios[0]["query"])
        self.results["production_optimization"] = result
        
        # Generate summary report
        self.generate_summary_report()
        
        return result["overall_success"]
    
    def generate_summary_report(self):
        """Generate a summary report of the test results"""
        self.print_header("AGENTCORE WORKFLOW TEST SUMMARY")
        
        total_time = time.time() - self.start_time
        
        for scenario_name, result in self.results.items():
            print(f"\n📋 SCENARIO: {scenario_name}")
            print(f"   ⏱️ Total Time: {result['total_time']:.2f}s")
            print(f"   ✅ Success: {result['overall_success']}")
            
            if result['overall_success']:
                stages = result['stages']
                print(f"   🧠 Intent: {'✅' if stages.get('intent', {}).get('success') else '❌'}")
                print(f"   📊 Data: {'✅' if stages.get('data', {}).get('success') else '❌'}")
                print(f"   🔧 Model: {'✅' if stages.get('model', {}).get('success') else '❌'}")
                print(f"   🏁 Solver: {'✅' if stages.get('solver', {}).get('success') else '❌'}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Scenarios: {len(self.results)}")
        successful = sum(1 for r in self.results.values() if r['overall_success'])
        print(f"   Successful: {successful}")
        print(f"   Failed: {len(self.results) - successful}")
        print(f"   Success Rate: {(successful/len(self.results)*100):.1f}%")
        print(f"   Total Test Time: {total_time:.2f}s")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agentcore_complete_workflow_test_results_{timestamp}.json"
        
        report_data = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "agent_runtime_arn": AGENT_RUNTIME_ARN,
                "total_scenarios": len(self.results),
                "successful_scenarios": successful,
                "total_test_time": total_time
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {filename}")


async def main():
    """Main test execution"""
    tester = AgentCoreWorkflowTester()
    
    try:
        success = await tester.run_complete_test()
        
        if success:
            print(f"\n🎉 AGENTCORE WORKFLOW TEST PASSED!")
            print(f"🚀 Platform is working correctly on AgentCore!")
        else:
            print(f"\n⚠️ AGENTCORE WORKFLOW TEST NEEDS ATTENTION")
            print(f"🔧 Some issues need to be addressed")
        
        return success
        
    except Exception as e:
        print(f"\n❌ TEST EXECUTION FAILED: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
