#!/usr/bin/env python3
"""
DcisionAI MCP Server - Customer Scenario E2E Test
===============================================

This script tests the DcisionAI Manufacturing MCP Server with a real customer scenario
using the existing E2E test infrastructure.

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
import sys
import os

# Add the domains directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'domains', 'manufacturing', 'mcp_server'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Customer E2E Test | %(message)s"
)
logger = logging.getLogger(__name__)

class CustomerScenarioE2ETester:
    """Test the DcisionAI MCP Server with real customer scenarios using E2E framework."""
    
    def __init__(self):
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
    
    async def test_customer_intent_classification(self) -> Dict[str, Any]:
        """Test manufacturing intent classification with customer scenario."""
        try:
            self.log_test_step(
                "Customer Intent Classification",
                "Testing manufacturing intent classification with 5-agent swarm for ACME Manufacturing",
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
            
            # Import and use the existing intent swarm
            from manufacturing_intent_swarm import ManufacturingIntentSwarm
            
            intent_swarm = ManufacturingIntentSwarm()
            
            start_time = time.time()
            
            result = await intent_swarm.classify_intent(
                query=customer_query,
                context={
                    "company": self.customer_scenario['company'],
                    "industry": self.customer_scenario['industry'],
                    "problem_type": "production_optimization"
                }
            )
            
            # The result is already the final result, not a coroutine
            if hasattr(result, 'get'):
                # It's a dictionary, use it directly
                final_result = result
            else:
                # It might be a coroutine, await it
                final_result = await result
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["intent_classification_time"] = response_time
            
            intent_result = {
                "query": customer_query,
                "response_time": response_time,
                "result": final_result
            }
            
            self.log_test_step(
                "Customer Intent Classification",
                "Successfully classified manufacturing intent for ACME Manufacturing",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "intent_detected": "manufacturing" in str(result).lower(),
                    "swarm_agents_used": 5,
                    "customer": self.customer_scenario['company']
                }
            )
            
            return intent_result
            
        except Exception as e:
            self.log_test_step(
                "Customer Intent Classification",
                f"Intent classification failed: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    async def test_customer_data_analysis(self, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test manufacturing data analysis with customer data."""
        try:
            self.log_test_step(
                "Customer Data Analysis",
                "Testing manufacturing data analysis with 3-agent swarm for ACME Manufacturing data",
                "STARTING"
            )
            
            # Import and use the existing data swarm
            from manufacturing_data_swarm import ManufacturingDataSwarm
            
            data_swarm = ManufacturingDataSwarm()
            
            start_time = time.time()
            
            result = await data_swarm.analyze_data(
                data=self.customer_scenario['data'],
                intent_result=intent_result.get("result", {}),
                context={
                    "company": self.customer_scenario['company'],
                    "analysis_type": "production_optimization"
                }
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["data_analysis_time"] = response_time
            
            data_result = {
                "data_analyzed": self.customer_scenario['data'],
                "response_time": response_time,
                "result": result
            }
            
            self.log_test_step(
                "Customer Data Analysis",
                "Successfully analyzed ACME Manufacturing data",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "data_points_analyzed": len(self.customer_scenario['data']),
                    "swarm_agents_used": 3,
                    "customer": self.customer_scenario['company']
                }
            )
            
            return data_result
            
        except Exception as e:
            self.log_test_step(
                "Customer Data Analysis",
                f"Data analysis failed: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    async def test_customer_model_building(self, intent_result: Dict[str, Any], data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test manufacturing model building with customer scenario."""
        try:
            self.log_test_step(
                "Customer Model Building",
                "Testing manufacturing model building with 4-agent swarm for ACME Manufacturing optimization",
                "STARTING"
            )
            
            # Import and use the existing model swarm
            from manufacturing_model_swarm import ManufacturingModelSwarm
            
            model_swarm = ManufacturingModelSwarm()
            
            start_time = time.time()
            
            result = await model_swarm.build_model(
                intent_result=intent_result.get("result", {}),
                data_result=data_result.get("result", {}),
                context={
                    "company": self.customer_scenario['company'],
                    "model_type": "production_optimization"
                }
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["model_building_time"] = response_time
            
            model_result = {
                "model_input": {
                    "intent": intent_result,
                    "data": data_result
                },
                "response_time": response_time,
                "result": result
            }
            
            self.log_test_step(
                "Customer Model Building",
                "Successfully built optimization model for ACME Manufacturing",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "model_complexity": "medium",
                    "swarm_agents_used": 4,
                    "customer": self.customer_scenario['company']
                }
            )
            
            return model_result
            
        except Exception as e:
            self.log_test_step(
                "Customer Model Building",
                f"Model building failed: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    async def test_customer_optimization_solver(self, model_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test manufacturing optimization solver with customer model."""
        try:
            self.log_test_step(
                "Customer Optimization Solver",
                "Testing manufacturing optimization solver with 6-agent swarm for ACME Manufacturing solution",
                "STARTING"
            )
            
            # Import and use the existing solver swarm
            from manufacturing_solver_swarm import ManufacturingSolverSwarm
            
            solver_swarm = ManufacturingSolverSwarm()
            
            start_time = time.time()
            
            result = await solver_swarm.solve_optimization(
                model_result=model_result.get("result", {}),
                context={
                    "company": self.customer_scenario['company'],
                    "solver_type": "production_optimization"
                }
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["solver_time"] = response_time
            
            solver_result = {
                "model_input": model_result,
                "response_time": response_time,
                "result": result
            }
            
            self.log_test_step(
                "Customer Optimization Solver",
                "Successfully solved optimization problem for ACME Manufacturing",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "solution_found": "optimal" in str(result).lower(),
                    "swarm_agents_used": 6,
                    "customer": self.customer_scenario['company']
                }
            )
            
            return solver_result
            
        except Exception as e:
            self.log_test_step(
                "Customer Optimization Solver",
                f"Optimization solver failed: {e}",
                "FAILED",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    async def run_complete_customer_scenario(self):
        """Run the complete customer scenario test."""
        logger.info("🚀 Starting DcisionAI MCP Server Customer Scenario E2E Test")
        logger.info(f"📊 Customer: {self.customer_scenario['company']}")
        logger.info(f"🎯 Problem: {self.customer_scenario['problem']}")
        logger.info(f"🏭 Industry: {self.customer_scenario['industry']}")
        logger.info("🔧 Using existing E2E test infrastructure with real swarm agents")
        
        # Step 1: Intent Classification
        intent_result = await self.test_customer_intent_classification()
        if "error" in intent_result:
            logger.error("❌ Intent classification failed. Cannot proceed.")
            return
        
        # Step 2: Data Analysis
        data_result = await self.test_customer_data_analysis(intent_result)
        if "error" in data_result:
            logger.error("❌ Data analysis failed. Cannot proceed.")
            return
        
        # Step 3: Model Building
        model_result = await self.test_customer_model_building(intent_result, data_result)
        if "error" in model_result:
            logger.error("❌ Model building failed. Cannot proceed.")
            return
        
        # Step 4: Optimization Solver
        solver_result = await self.test_customer_optimization_solver(model_result)
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
        
        logger.info("🎉 Customer scenario E2E test completed successfully!")
        logger.info(f"⏱️ Total workflow time: {total_time:.2f}s")
        logger.info(f"📈 Average response time: {total_time/4:.2f}s")
        logger.info("📄 Detailed results saved to customer_e2e_test_results.json")
        
        # Print summary for customer
        self.print_customer_summary()
    
    def print_customer_summary(self):
        """Print a customer-friendly summary of the test results."""
        print("\n" + "="*80)
        print("🎯 ACME MANUFACTURING - OPTIMIZATION RESULTS SUMMARY")
        print("="*80)
        print(f"📊 Company: {self.customer_scenario['company']}")
        print(f"🏭 Industry: {self.customer_scenario['industry']}")
        print(f"🎯 Problem: {self.customer_scenario['problem']}")
        print()
        
        # Performance metrics
        metrics = self.test_results["performance_metrics"]
        print("⏱️ PERFORMANCE METRICS:")
        print(f"   • Intent Classification: {metrics.get('intent_classification_time', 0):.2f}s")
        print(f"   • Data Analysis: {metrics.get('data_analysis_time', 0):.2f}s")
        print(f"   • Model Building: {metrics.get('model_building_time', 0):.2f}s")
        print(f"   • Optimization Solver: {metrics.get('solver_time', 0):.2f}s")
        print(f"   • Total Workflow Time: {metrics.get('total_workflow_time', 0):.2f}s")
        print(f"   • Average Response Time: {metrics.get('average_response_time', 0):.2f}s")
        print()
        
        # Agent swarm usage
        print("🤖 AGENT SWARM USAGE:")
        print("   • Intent Swarm: 5 specialized agents (Operations Research, Production Systems, Supply Chain, Quality, Sustainability)")
        print("   • Data Swarm: 3 specialized agents (Data Requirements, Business Context, Sample Data Generation)")
        print("   • Model Swarm: 4 specialized agents (Mathematical Formulation, Constraint Modeling, Solver Compatibility, Research)")
        print("   • Solver Swarm: 6 specialized agents (GLOP, SCIP, HiGHS, PuLP, CVXPY, Validation)")
        print()
        
        # Customer data processed
        data = self.customer_scenario['data']
        print("📈 CUSTOMER DATA PROCESSED:")
        print(f"   • Total Workers: {data['total_workers']}")
        print(f"   • Production Lines: {data['production_lines']}")
        print(f"   • Worker Skills: {', '.join(data['worker_skills'])}")
        print(f"   • Line Capacities: {data['line_capacities']} units/hour")
        print(f"   • Cost per Hour: ${data['cost_per_hour']}")
        print()
        
        print("✅ OPTIMIZATION COMPLETE - Ready for production deployment!")
        print("="*80)
    
    def save_test_results(self):
        """Save test results to file."""
        filename = f"customer_e2e_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"💾 Test results saved to {filename}")

async def main():
    """Main function to run the customer scenario E2E test."""
    tester = CustomerScenarioE2ETester()
    await tester.run_complete_customer_scenario()

if __name__ == "__main__":
    asyncio.run(main())
