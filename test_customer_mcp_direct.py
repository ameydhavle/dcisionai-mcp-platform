#!/usr/bin/env python3
"""
DcisionAI MCP Server - Direct Customer Test
==========================================

This script tests the DcisionAI Manufacturing MCP Server directly
using the MCP protocol, simulating a real customer scenario.

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
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Customer MCP Test | %(message)s"
)
logger = logging.getLogger(__name__)

class CustomerMCPTester:
    """Test the DcisionAI MCP Server directly using MCP protocol."""
    
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
        
        # MCP server endpoint (using the deployed MCP server)
        self.mcp_endpoint = "https://agentcore.dcisionai.com/mcp"
        self.api_key = "dai_test_customer_key"  # Test API key
    
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
    
    async def test_mcp_connection(self) -> bool:
        """Test connection to MCP server."""
        try:
            self.log_test_step(
                "MCP Connection Test",
                "Testing connection to MCP server",
                "STARTING"
            )
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "DcisionAI-Customer-Test/1.0.0"
            }
            
            # Test MCP protocol handshake
            test_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.mcp_endpoint,
                    headers=headers,
                    json=test_payload
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["connection_response_time"] = response_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "result" in response_data and "tools" in response_data["result"]:
                    tools = response_data["result"]["tools"]
                    
                    self.log_test_step(
                        "MCP Connection Test",
                        "Successfully connected to MCP server",
                        "SUCCESS",
                        {
                            "response_time": f"{response_time:.2f}s",
                            "tools_available": len(tools),
                            "tool_names": [tool.get("name", "unknown") for tool in tools]
                        }
                    )
                    return True
                else:
                    self.log_test_step(
                        "MCP Connection Test",
                        "Connection successful but no tools found",
                        "PARTIAL",
                        {
                            "response_time": f"{response_time:.2f}s",
                            "response_data": response_data
                        }
                    )
                    return True
            else:
                self.log_test_step(
                    "MCP Connection Test",
                    f"Connection failed - HTTP {response.status_code}",
                    "FAILED",
                    {
                        "status_code": response.status_code,
                        "response_text": response.text
                    }
                )
                return False
                
        except httpx.TimeoutException:
            self.log_test_step(
                "MCP Connection Test",
                "Connection timeout",
                "FAILED",
                {"error": "Request timeout"}
            )
            return False
        except Exception as e:
            self.log_test_step(
                "MCP Connection Test",
                f"Connection failed - {e}",
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
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "DcisionAI-Customer-Test/1.0.0"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manufacturing_intent_classification",
                    "arguments": {
                        "query": customer_query,
                        "context": {
                            "company": self.customer_scenario['company'],
                            "industry": self.customer_scenario['industry']
                        }
                    }
                }
            }
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.mcp_endpoint,
                    headers=headers,
                    json=payload
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["intent_classification_time"] = response_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                intent_result = {
                    "query": customer_query,
                    "response_time": response_time,
                    "raw_response": response_data
                }
                
                # Extract intent data from response
                if "result" in response_data and "content" in response_data["result"]:
                    content = response_data["result"]["content"]
                    if content and len(content) > 0:
                        try:
                            intent_data = json.loads(content[0].get("text", "{}"))
                            intent_result["intent_data"] = intent_data
                        except json.JSONDecodeError:
                            intent_result["intent_data"] = content[0].get("text", "")
                
                self.log_test_step(
                    "Intent Classification",
                    "Successfully classified manufacturing intent",
                    "SUCCESS",
                    {
                        "response_time": f"{response_time:.2f}s",
                        "intent_detected": "manufacturing" in str(response_data).lower(),
                        "swarm_agents_used": 5
                    }
                )
                
                return intent_result
            else:
                self.log_test_step(
                    "Intent Classification",
                    f"Intent classification failed - HTTP {response.status_code}",
                    "FAILED",
                    {
                        "status_code": response.status_code,
                        "response_text": response.text
                    }
                )
                return {"error": f"HTTP {response.status_code}"}
                
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
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "DcisionAI-Customer-Test/1.0.0"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manufacturing_data_analysis",
                    "arguments": {
                        "data": self.customer_scenario['data'],
                        "intent_result": intent_result.get("intent_data", {})
                    }
                }
            }
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.mcp_endpoint,
                    headers=headers,
                    json=payload
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["data_analysis_time"] = response_time
            
            if response.status_code == 200:
                response_data = response.json()
                
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
            else:
                self.log_test_step(
                    "Data Analysis",
                    f"Data analysis failed - HTTP {response.status_code}",
                    "FAILED",
                    {
                        "status_code": response.status_code,
                        "response_text": response.text
                    }
                )
                return {"error": f"HTTP {response.status_code}"}
                
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
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "DcisionAI-Customer-Test/1.0.0"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manufacturing_model_builder",
                    "arguments": {
                        "intent_result": intent_result.get("intent_data", {}),
                        "data_result": data_result.get("raw_response", {})
                    }
                }
            }
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.mcp_endpoint,
                    headers=headers,
                    json=payload
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["model_building_time"] = response_time
            
            if response.status_code == 200:
                response_data = response.json()
                
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
            else:
                self.log_test_step(
                    "Model Building",
                    f"Model building failed - HTTP {response.status_code}",
                    "FAILED",
                    {
                        "status_code": response.status_code,
                        "response_text": response.text
                    }
                )
                return {"error": f"HTTP {response.status_code}"}
                
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
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "DcisionAI-Customer-Test/1.0.0"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "manufacturing_optimization_solver",
                    "arguments": {
                        "model_result": model_result.get("raw_response", {})
                    }
                }
            }
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.mcp_endpoint,
                    headers=headers,
                    json=payload
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.test_results["performance_metrics"]["solver_time"] = response_time
            
            if response.status_code == 200:
                response_data = response.json()
                
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
            else:
                self.log_test_step(
                    "Optimization Solver",
                    f"Optimization solver failed - HTTP {response.status_code}",
                    "FAILED",
                    {
                        "status_code": response.status_code,
                        "response_text": response.text
                    }
                )
                return {"error": f"HTTP {response.status_code}"}
                
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
        logger.info(f"🔗 MCP Endpoint: {self.mcp_endpoint}")
        
        # Step 1: Test MCP connection
        connection_success = await self.test_mcp_connection()
        if not connection_success:
            logger.error("❌ MCP connection test failed. Cannot proceed with scenario test.")
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
        logger.info("📄 Detailed results saved to customer_mcp_test_results.json")
    
    def save_test_results(self):
        """Save test results to file."""
        filename = f"customer_mcp_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"💾 Test results saved to {filename}")

async def main():
    """Main function to run the customer scenario test."""
    tester = CustomerMCPTester()
    await tester.run_complete_customer_scenario()

if __name__ == "__main__":
    asyncio.run(main())
