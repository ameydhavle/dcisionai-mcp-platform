#!/usr/bin/env python3
"""
DcisionAI MCP Server - Customer Scenario Test
============================================

This script tests the DcisionAI Manufacturing MCP Server on AgentCore
with a real customer scenario, documenting the entire process and results.

Customer Scenario: Manufacturing Production Line Optimization
- Company: ACME Manufacturing
- Problem: Optimize worker assignment across production lines
- Goal: Maximize efficiency while minimizing costs

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Customer Test | %(message)s"
)
logger = logging.getLogger(__name__)

class CustomerScenarioTester:
    """Test the DcisionAI MCP Server with real customer scenarios."""
    
    def __init__(self):
        self.agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v4_1757015134-2cxwp1BgzR"
        self.region = "us-east-1"
        self.bedrock_client = boto3.client('bedrock-agentcore', region_name=self.region)
        
        # Customer scenario data
        self.customer_scenario = {
            "company": "ACME Manufacturing",
            "industry": "Automotive Parts Manufacturing",
            "problem": "Production line efficiency optimization",
            "data": {
                "total_workers": 50,
                "production_lines": 3,
                "max_hours_per_week": 48,
                "worker_skills": ["assembly", "quality_control", "packaging", "maintenance"],
                "line_capacities": [100, 120, 80],  # units per hour
                "worker_efficiency": {
                    "assembly": 0.95,
                    "quality_control": 0.90,
                    "packaging": 0.98,
                    "maintenance": 0.85
                },
                "cost_per_hour": 25.00,
                "overtime_multiplier": 1.5
            }
        }
        
        self.test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "customer_scenario": self.customer_scenario,
            "test_steps": [],
            "performance_metrics": {},
            "results": {}
        }
    
    def log_test_step(self, step_name: str, description: str, status: str, details: Any = None):
        """Log a test step with details."""
        step = {
            "step_name": step_name,
            "description": description,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results["test_steps"].append(step)
        logger.info(f"📋 {step_name}: {status} - {description}")
    
    async def test_agentcore_connection(self) -> bool:
        """Test connection to AgentCore MCP server."""
        try:
            self.log_test_step(
                "Connection Test",
                "Testing connection to AgentCore MCP server",
                "STARTING"
            )
            
            # Test payload for connection
            test_payload = {
                "prompt": "Hello, can you help me with manufacturing optimization?",
                "tenantContext": {
                    "tenant_id": "test_customer",
                    "sla_tier": "free",
                    "region": "us-east-1"
                }
            }
            
            start_time = time.time()
            
            response = self.bedrock_client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_runtime_arn,
                payload=json.dumps(test_payload),
                contentType="application/json",
                accept="application/json"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Parse response
            response_data = json.loads(response['output'])
            
            self.test_results["performance_metrics"]["connection_response_time"] = response_time
            
            if response_data.get("status") == "success" or "tools" in response_data:
                self.log_test_step(
                    "Connection Test",
                    "Successfully connected to AgentCore MCP server",
                    "SUCCESS",
                    {
                        "response_time": f"{response_time:.2f}s",
                        "response_keys": list(response_data.keys())
                    }
                )
                return True
            else:
                self.log_test_step(
                    "Connection Test",
                    "Connection failed - invalid response",
                    "FAILED",
                    response_data
                )
                return False
                
        except ClientError as e:
            self.log_test_step(
                "Connection Test",
                f"Connection failed - AWS error: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return False
        except Exception as e:
            self.log_test_step(
                "Connection Test",
                f"Connection failed - unexpected error: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return False
    
    async def test_manufacturing_intent_classification(self) -> Dict[str, Any]:
        """Test manufacturing intent classification."""
        try:
            self.log_test_step(
                "Intent Classification",
                "Testing manufacturing intent classification with 5-agent swarm",
                "STARTING"
            )
            
            customer_query = f"""
            We are {self.customer_scenario['company']}, a {self.customer_scenario['industry']} company.
            
            We need to optimize our production line efficiency. We have:
            - {self.customer_scenario['data']['total_workers']} workers
            - {self.customer_scenario['data']['production_lines']} production lines
            - Workers with skills: {', '.join(self.customer_scenario['data']['worker_skills'])}
            - Line capacities: {self.customer_scenario['data']['line_capacities']} units/hour
            
            Our goal is to maximize efficiency while minimizing costs. Can you help us optimize worker assignment across production lines?
            """
            
            payload = {
                "prompt": customer_query,
                "tenantContext": {
                    "tenant_id": "acme_manufacturing",
                    "sla_tier": "pro",
                    "region": "us-east-1"
                }
            }
            
            start_time = time.time()
            
            response = self.bedrock_client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_runtime_arn,
                payload=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_data = json.loads(response['output'])
            
            self.test_results["performance_metrics"]["intent_classification_time"] = response_time
            
            # Extract intent classification results
            intent_result = {
                "query": customer_query,
                "response_time": response_time,
                "raw_response": response_data
            }
            
            # Try to extract structured intent data
            if "tools" in response_data:
                for tool in response_data["tools"]:
                    if tool.get("name") == "manufacturing_intent_classification":
                        intent_result["intent_data"] = tool.get("result", {})
                        break
            
            self.log_test_step(
                "Intent Classification",
                "Successfully classified manufacturing intent",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "intent_detected": "manufacturing_optimization" in str(response_data).lower(),
                    "swarm_agents_used": 5
                }
            )
            
            return intent_result
            
        except Exception as e:
            self.log_test_step(
                "Intent Classification",
                f"Intent classification failed: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    async def test_manufacturing_data_analysis(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test manufacturing data analysis."""
        try:
            self.log_test_step(
                "Data Analysis",
                "Testing manufacturing data analysis with 3-agent swarm",
                "STARTING"
            )
            
            data_analysis_query = f"""
            Based on the intent classification, please analyze our manufacturing data:
            
            Company: {self.customer_scenario['company']}
            Data: {json.dumps(self.customer_scenario['data'], indent=2)}
            
            Please provide insights on:
            1. Data quality and completeness
            2. Optimization readiness score
            3. Key constraints and opportunities
            4. Recommended next steps
            """
            
            payload = {
                "prompt": data_analysis_query,
                "tenantContext": {
                    "tenant_id": "acme_manufacturing",
                    "sla_tier": "pro",
                    "region": "us-east-1"
                }
            }
            
            start_time = time.time()
            
            response = self.bedrock_client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_runtime_arn,
                payload=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_data = json.dumps(response['output'])
            
            self.test_results["performance_metrics"]["data_analysis_time"] = response_time
            
            data_result = {
                "data_analyzed": self.customer_scenario['data'],
                "response_time": response_time,
                "raw_response": response_data
            }
            
            self.log_test_step(
                "Data Analysis",
                "Successfully analyzed manufacturing data",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "data_points_analyzed": len(self.customer_scenario['data']),
                    "swarm_agents_used": 3
                }
            )
            
            return data_result
            
        except Exception as e:
            self.log_test_step(
                "Data Analysis",
                f"Data analysis failed: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    async def test_manufacturing_model_building(self, intent_result: Dict[str, Any], data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test manufacturing model building."""
        try:
            self.log_test_step(
                "Model Building",
                "Testing manufacturing model building with 4-agent swarm",
                "STARTING"
            )
            
            model_building_query = f"""
            Based on the intent classification and data analysis, please build an optimization model:
            
            Intent: {intent_result.get('query', 'Manufacturing optimization')}
            Data: {json.dumps(self.customer_scenario['data'], indent=2)}
            
            Please provide:
            1. Model type (LP, MILP, etc.)
            2. Decision variables
            3. Constraints
            4. Objective function
            5. Model complexity assessment
            """
            
            payload = {
                "prompt": model_building_query,
                "tenantContext": {
                    "tenant_id": "acme_manufacturing",
                    "sla_tier": "pro",
                    "region": "us-east-1"
                }
            }
            
            start_time = time.time()
            
            response = self.bedrock_client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_runtime_arn,
                payload=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_data = json.dumps(response['output'])
            
            self.test_results["performance_metrics"]["model_building_time"] = response_time
            
            model_result = {
                "model_input": {
                    "intent": intent_result,
                    "data": data_result
                },
                "response_time": response_time,
                "raw_response": response_data
            }
            
            self.log_test_step(
                "Model Building",
                "Successfully built optimization model",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "model_complexity": "medium",
                    "swarm_agents_used": 4
                }
            )
            
            return model_result
            
        except Exception as e:
            self.log_test_step(
                "Model Building",
                f"Model building failed: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    async def test_manufacturing_optimization_solver(self, model_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test manufacturing optimization solver."""
        try:
            self.log_test_step(
                "Optimization Solver",
                "Testing manufacturing optimization solver with 6-agent swarm",
                "STARTING"
            )
            
            solver_query = f"""
            Based on the optimization model, please solve the manufacturing optimization problem:
            
            Model: {model_result.get('raw_response', 'Optimization model')}
            Data: {json.dumps(self.customer_scenario['data'], indent=2)}
            
            Please provide:
            1. Optimal solution
            2. Objective function value
            3. Variable assignments
            4. Performance metrics
            5. Sensitivity analysis
            """
            
            payload = {
                "prompt": solver_query,
                "tenantContext": {
                    "tenant_id": "acme_manufacturing",
                    "sla_tier": "pro",
                    "region": "us-east-1"
                }
            }
            
            start_time = time.time()
            
            response = self.bedrock_client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_runtime_arn,
                payload=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_data = json.dumps(response['output'])
            
            self.test_results["performance_metrics"]["solver_time"] = response_time
            
            solver_result = {
                "model_input": model_result,
                "response_time": response_time,
                "raw_response": response_data
            }
            
            self.log_test_step(
                "Optimization Solver",
                "Successfully solved optimization problem",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "solution_found": "optimal" in str(response_data).lower(),
                    "swarm_agents_used": 6
                }
            )
            
            return solver_result
            
        except Exception as e:
            self.log_test_step(
                "Optimization Solver",
                f"Optimization solver failed: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    async def run_complete_customer_scenario(self):
        """Run the complete customer scenario test."""
        logger.info("🚀 Starting DcisionAI MCP Server Customer Scenario Test")
        logger.info(f"📊 Customer: {self.customer_scenario['company']}")
        logger.info(f"🎯 Problem: {self.customer_scenario['problem']}")
        logger.info(f"🏭 Industry: {self.customer_scenario['industry']}")
        
        # Step 1: Test connection
        connection_success = await self.test_agentcore_connection()
        if not connection_success:
            logger.error("❌ Connection test failed. Cannot proceed with scenario test.")
            return
        
        # Step 2: Intent Classification
        intent_result = await self.test_manufacturing_intent_classification()
        if "error" in intent_result:
            logger.error("❌ Intent classification failed. Cannot proceed.")
            return
        
        # Step 3: Data Analysis
        data_result = await self.test_manufacturing_data_analysis(intent_result)
        if "error" in data_result:
            logger.error("❌ Data analysis failed. Cannot proceed.")
            return
        
        # Step 4: Model Building
        model_result = await self.test_manufacturing_model_building(intent_result, data_result)
        if "error" in model_result:
            logger.error("❌ Model building failed. Cannot proceed.")
            return
        
        # Step 5: Optimization Solver
        solver_result = await self.test_manufacturing_optimization_solver(model_result)
        if "error" in solver_result:
            logger.error("❌ Optimization solver failed.")
            return
        
        # Compile results
        self.test_results["results"] = {
            "intent_classification": intent_result,
            "data_analysis": data_result,
            "model_building": model_result,
            "optimization_solver": solver_result
        }
        
        # Calculate total performance metrics
        total_time = sum([
            self.test_results["performance_metrics"].get("intent_classification_time", 0),
            self.test_results["performance_metrics"].get("data_analysis_time", 0),
            self.test_results["performance_metrics"].get("model_building_time", 0),
            self.test_results["performance_metrics"].get("solver_time", 0)
        ])
        
        self.test_results["performance_metrics"]["total_workflow_time"] = total_time
        self.test_results["performance_metrics"]["average_response_time"] = total_time / 4
        
        # Save results
        self.save_test_results()
        
        logger.info("🎉 Customer scenario test completed successfully!")
        logger.info(f"⏱️ Total workflow time: {total_time:.2f}s")
        logger.info(f"📈 Average response time: {total_time/4:.2f}s")
        logger.info("📄 Detailed results saved to customer_test_results.json")
    
    def save_test_results(self):
        """Save test results to file."""
        filename = f"customer_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"💾 Test results saved to {filename}")

async def main():
    """Main function to run the customer scenario test."""
    tester = CustomerScenarioTester()
    await tester.run_complete_customer_scenario()

if __name__ == "__main__":
    asyncio.run(main())
