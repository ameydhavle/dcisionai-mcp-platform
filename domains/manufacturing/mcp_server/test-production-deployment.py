#!/usr/bin/env python3
"""
Production Deployment Test for DcisionAI Manufacturing MCP Server

This script tests the production deployment on AWS AgentCore to ensure all features are working correctly.
"""

import asyncio
import json
import logging
import time
import requests
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Production Test | %(message)s"
)
logger = logging.getLogger(__name__)

class ProductionTester:
    """Test the production deployment on AWS AgentCore."""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, message: str, duration: float = 0.0):
        """Log test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message} ({duration:.2f}s)")
    
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint."""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.endpoint}/health", timeout=30)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("overall_status") == "healthy":
                    self.log_test_result(
                        "Health Check",
                        True,
                        f"All components healthy: {health_data.get('overall_status')}",
                        duration
                    )
                    return True
                else:
                    self.log_test_result(
                        "Health Check",
                        False,
                        f"Unhealthy status: {health_data.get('overall_status')}",
                        duration
                    )
                    return False
            else:
                self.log_test_result(
                    "Health Check",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Health Check",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_health_summary(self) -> bool:
        """Test the health summary endpoint."""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.endpoint}/health/summary", timeout=30)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                summary_data = response.json()
                self.log_test_result(
                    "Health Summary",
                    True,
                    f"Summary available: {summary_data.get('overall_status')}",
                    duration
                )
                return True
            else:
                self.log_test_result(
                    "Health Summary",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Health Summary",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_mcp_tools_list(self) -> bool:
        """Test MCP tools list endpoint."""
        start_time = time.time()
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            response = requests.post(
                f"{self.endpoint}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    expected_tools = [
                        "manufacturing_intent_classification",
                        "manufacturing_data_analysis", 
                        "manufacturing_model_builder",
                        "manufacturing_optimization_solver",
                        "manufacturing_health_check"
                    ]
                    
                    available_tools = [tool["name"] for tool in tools]
                    missing_tools = set(expected_tools) - set(available_tools)
                    
                    if not missing_tools:
                        self.log_test_result(
                            "MCP Tools List",
                            True,
                            f"All {len(tools)} tools available",
                            duration
                        )
                        return True
                    else:
                        self.log_test_result(
                            "MCP Tools List",
                            False,
                            f"Missing tools: {missing_tools}",
                            duration
                        )
                        return False
                else:
                    self.log_test_result(
                        "MCP Tools List",
                        False,
                        "Invalid response format",
                        duration
                    )
                    return False
            else:
                self.log_test_result(
                    "MCP Tools List",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "MCP Tools List",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_intent_classification(self) -> bool:
        """Test intent classification with swarm."""
        start_time = time.time()
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manufacturing_intent_classification",
                    "arguments": {
                        "query": "Optimize production scheduling for 3 lines with 45 workers"
                    }
                }
            }
            
            response = requests.post(
                f"{self.endpoint}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # Longer timeout for swarm processing
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    content = data["result"]["content"][0]["text"]
                    result_data = json.loads(content)
                    
                    if result_data.get("status") != "error":
                        self.log_test_result(
                            "Intent Classification",
                            True,
                            f"Intent: {result_data.get('intent', 'unknown')}, Confidence: {result_data.get('confidence', 0)}",
                            duration
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Intent Classification",
                            False,
                            f"Error: {result_data.get('error', 'Unknown error')}",
                            duration
                        )
                        return False
                else:
                    self.log_test_result(
                        "Intent Classification",
                        False,
                        "Invalid response format",
                        duration
                    )
                    return False
            else:
                self.log_test_result(
                    "Intent Classification",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Intent Classification",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_data_analysis(self) -> bool:
        """Test data analysis with swarm."""
        start_time = time.time()
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manufacturing_data_analysis",
                    "arguments": {
                        "data": {
                            "query": "Analyze data requirements for inventory optimization"
                        },
                        "intent_result": {
                            "intent": "INVENTORY_OPTIMIZATION",
                            "confidence": 0.9,
                            "entities": ["inventory", "optimization"]
                        },
                        "analysis_type": "comprehensive"
                    }
                }
            }
            
            response = requests.post(
                f"{self.endpoint}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    content = data["result"]["content"][0]["text"]
                    result_data = json.loads(content)
                    
                    if result_data.get("status") != "error":
                        entities = len(result_data.get("extracted_data_entities", []))
                        self.log_test_result(
                            "Data Analysis",
                            True,
                            f"Extracted {entities} data entities",
                            duration
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Data Analysis",
                            False,
                            f"Error: {result_data.get('error', 'Unknown error')}",
                            duration
                        )
                        return False
                else:
                    self.log_test_result(
                        "Data Analysis",
                        False,
                        "Invalid response format",
                        duration
                    )
                    return False
            else:
                self.log_test_result(
                    "Data Analysis",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Data Analysis",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_model_builder(self) -> bool:
        """Test model builder with swarm."""
        start_time = time.time()
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manufacturing_model_builder",
                    "arguments": {
                        "intent_result": {
                            "intent": "PRODUCTION_SCHEDULING",
                            "confidence": 0.9
                        },
                        "data_result": {
                            "extracted_data_entities": ["production_capacity", "demand_forecast"],
                            "sample_data_generated": {
                                "production_capacity": {"Line_A": 100, "Line_B": 150},
                                "demand_forecast": {"Product_A": 500, "Product_B": 300}
                            }
                        }
                    }
                }
            }
            
            response = requests.post(
                f"{self.endpoint}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    content = data["result"]["content"][0]["text"]
                    result_data = json.loads(content)
                    
                    if result_data.get("status") != "error":
                        variables = len(result_data.get("decision_variables", []))
                        constraints = len(result_data.get("constraints", []))
                        self.log_test_result(
                            "Model Builder",
                            True,
                            f"Built model with {variables} variables and {constraints} constraints",
                            duration
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Model Builder",
                            False,
                            f"Error: {result_data.get('error', 'Unknown error')}",
                            duration
                        )
                        return False
                else:
                    self.log_test_result(
                        "Model Builder",
                        False,
                        "Invalid response format",
                        duration
                    )
                    return False
            else:
                self.log_test_result(
                    "Model Builder",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Model Builder",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_solver_optimization(self) -> bool:
        """Test solver optimization with swarm."""
        start_time = time.time()
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "manufacturing_optimization_solver",
                    "arguments": {
                        "model_result": {
                            "model_type": "LINEAR_PROGRAMMING",
                            "decision_variables": [
                                {"name": "x1", "variable_type": "continuous", "bounds": {"lower": 0.0, "upper": 100.0}},
                                {"name": "x2", "variable_type": "continuous", "bounds": {"lower": 0.0, "upper": 150.0}}
                            ],
                            "constraints": [
                                {"name": "capacity", "expression": "x1 + x2 <= 200", "sense": "<=", "rhs_value": "200"}
                            ],
                            "objective_functions": [
                                {"name": "minimize_cost", "expression": "25*x1 + 30*x2", "sense": "minimize"}
                            ]
                        }
                    }
                }
            }
            
            response = requests.post(
                f"{self.endpoint}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    content = data["result"]["content"][0]["text"]
                    result_data = json.loads(content)
                    
                    if result_data.get("status") != "error":
                        solvers = len(result_data.get("solver_recommendations", []))
                        self.log_test_result(
                            "Solver Optimization",
                            True,
                            f"Generated {solvers} solver recommendations",
                            duration
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Solver Optimization",
                            False,
                            f"Error: {result_data.get('error', 'Unknown error')}",
                            duration
                        )
                        return False
                else:
                    self.log_test_result(
                        "Solver Optimization",
                        False,
                        "Invalid response format",
                        duration
                    )
                    return False
            else:
                self.log_test_result(
                    "Solver Optimization",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Solver Optimization",
                False,
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive production test suite."""
        logger.info("🧪 Starting comprehensive production test suite...")
        logger.info(f"Testing endpoint: {self.endpoint}")
        
        # Run all tests
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Health Summary", self.test_health_summary),
            ("MCP Tools List", self.test_mcp_tools_list),
            ("Intent Classification", self.test_intent_classification),
            ("Data Analysis", self.test_data_analysis),
            ("Model Builder", self.test_model_builder),
            ("Solver Optimization", self.test_solver_optimization)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"Running {test_name}...")
            if test_func():
                passed_tests += 1
            time.sleep(2)  # Brief pause between tests
        
        # Calculate results
        success_rate = (passed_tests / total_tests) * 100
        overall_status = "PASS" if success_rate >= 80 else "FAIL"
        
        summary = {
            "overall_status": overall_status,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
            "endpoint": self.endpoint
        }
        
        logger.info(f"🎯 Test Summary: {overall_status}")
        logger.info(f"   Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        logger.info(f"   Passed Tests: {passed_tests}")
        logger.info(f"   Failed Tests: {total_tests - passed_tests}")
        
        return summary

def main():
    """Main test function."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test-production-deployment.py <endpoint>")
        print("Example: python test-production-deployment.py https://your-agentcore-endpoint.com")
        sys.exit(1)
    
    endpoint = sys.argv[1]
    
    # Create tester and run tests
    tester = ProductionTester(endpoint)
    results = tester.run_comprehensive_test()
    
    # Save results
    with open("production-test-results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("📄 Test results saved to production-test-results.json")
    
    # Exit with appropriate code
    if results["overall_status"] == "PASS":
        logger.info("🎉 Production deployment test PASSED!")
        sys.exit(0)
    else:
        logger.error("❌ Production deployment test FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
