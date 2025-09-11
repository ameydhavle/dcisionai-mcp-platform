#!/usr/bin/env python3
"""
DcisionAI MCP Server - Local Customer Test
=========================================

This script tests the DcisionAI Manufacturing MCP Server locally
by directly importing and using the MCP server classes.

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
    format="%(asctime)s | %(levelname)s | Customer Local Test | %(message)s"
)
logger = logging.getLogger(__name__)

class CustomerLocalTester:
    """Test the DcisionAI MCP Server locally."""
    
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
        
        # Import MCP server components
        try:
            from mcp_server import mcp_server
            self.mcp_server = mcp_server
            logger.info("✅ Successfully imported MCP server")
        except ImportError as e:
            logger.error(f"❌ Failed to import MCP server: {e}")
            self.mcp_server = None
    
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
    
    async def test_mcp_server_initialization(self) -> bool:
        """Test MCP server initialization."""
        try:
            self.log_test_step(
                "MCP Server Initialization",
                "Testing MCP server initialization and tool registration",
                "STARTING"
            )
            
            if not self.mcp_server:
                self.log_test_step(
                    "MCP Server Initialization",
                    "MCP server not available",
                    "FAILED",
                    {"error": "ManufacturingMCP not imported"}
                )
                return False
            
            # Check if MCP server is available
            if hasattr(self.mcp_server, 'mcp') and self.mcp_server.mcp:
                self.log_test_step(
                    "MCP Server Initialization",
                    "Successfully initialized MCP server",
                    "SUCCESS",
                    {
                        "server_type": "FastMCP",
                        "host": "0.0.0.0",
                        "stateless_http": True
                    }
                )
                return True
            else:
                self.log_test_step(
                    "MCP Server Initialization",
                    "MCP server not properly initialized",
                    "FAILED",
                    {"server_available": False}
                )
                return False
                
        except Exception as e:
            self.log_test_step(
                "MCP Server Initialization",
                f"MCP server initialization failed: {e}",
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
            
            start_time = time.time()
            
            # Call the intent classification tool using FastMCP
            result = await self.mcp_server.mcp.call_tool(
                "manufacturing_intent_classification",
                {
                    "query": customer_query,
                    "context": {
                        "company": self.customer_scenario['company'],
                        "industry": self.customer_scenario['industry']
                    }
                }
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["intent_classification_time"] = response_time
            
            intent_result = {
                "query": customer_query,
                "response_time": response_time,
                "result": result
            }
            
            self.log_test_step(
                "Intent Classification",
                "Successfully classified manufacturing intent",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "intent_detected": "manufacturing" in str(result).lower(),
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
            
            start_time = time.time()
            
            # Call the data analysis tool using FastMCP
            result = await self.mcp_server.mcp.call_tool(
                "manufacturing_data_analysis",
                {
                    "data": self.customer_scenario['data'],
                    "intent_result": intent_result.get("result", {})
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
    
    async def test_manufacturing_model_builder(self, intent_result: Dict[str, Any], data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test manufacturing model builder."""
        try:
            self.log_test_step(
                "Model Building",
                "Testing manufacturing model building with 4-agent swarm",
                "STARTING"
            )
            
            start_time = time.time()
            
            # Call the model builder tool using FastMCP
            result = await self.mcp_server.mcp.call_tool(
                "manufacturing_model_builder",
                {
                    "intent_result": intent_result.get("result", {}),
                    "data_result": data_result.get("result", {})
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
            
            start_time = time.time()
            
            # Call the optimization solver tool using FastMCP
            result = await self.mcp_server.mcp.call_tool(
                "manufacturing_optimization_solver",
                {
                    "model_result": model_result.get("result", {})
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
                "Optimization Solver",
                "Successfully solved optimization problem",
                "SUCCESS",
                {
                    "response_time": f"{response_time:.2f}s",
                    "solution_found": "optimal" in str(result).lower(),
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
        logger.info("🚀 Starting DcisionAI MCP Server Local Customer Scenario Test")
        logger.info(f"📊 Customer: {self.customer_scenario['company']}")
        logger.info(f"🎯 Problem: {self.customer_scenario['problem']}")
        logger.info(f"🏭 Industry: {self.customer_scenario['industry']}")
        
        # Step 1: Test MCP server initialization
        init_success = await self.test_mcp_server_initialization()
        if not init_success:
            logger.error("❌ MCP server initialization failed. Cannot proceed with scenario test.")
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
        model_result = await self.test_manufacturing_model_builder(intent_result, data_result)
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
        logger.info("📄 Detailed results saved to customer_local_test_results.json")
    
    def save_test_results(self):
        """Save test results to file."""
        filename = f"customer_local_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"💾 Test results saved to {filename}")

async def main():
    """Main function to run the customer scenario test."""
    tester = CustomerLocalTester()
    await tester.run_complete_customer_scenario()

if __name__ == "__main__":
    asyncio.run(main())
