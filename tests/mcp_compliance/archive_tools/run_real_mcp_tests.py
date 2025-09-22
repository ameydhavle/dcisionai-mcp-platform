#!/usr/bin/env python3
"""
Real MCP Server Compliance Testing
=================================

Comprehensive test runner for connecting to the real DcisionAI MCP server
and running all compliance tests with real protocol validation.

This script:
1. Connects to the actual MCP server
2. Runs comprehensive compliance tests
3. Validates real protocol behavior
4. Generates detailed compliance reports
5. Provides performance metrics and recommendations
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mcp_compliance.config import MCPComplianceConfig, load_environment_config
from tests.mcp_compliance.mcp_compliance_tester import MCPComplianceTester
from tests.mcp_compliance.mcp_compliance_validator import MCPComplianceValidator

# Setup logger
logger = logging.getLogger(__name__)


class RealMCPComplianceTester:
    """
    Real MCP server compliance tester.
    
    Connects to actual MCP servers and runs comprehensive compliance tests
    to validate protocol implementation and server behavior.
    """
    
    def __init__(self, config: MCPComplianceConfig):
        """
        Initialize real MCP compliance tester.
        
        Args:
            config: MCP compliance configuration
        """
        self.config = config
        self.test_config = config.get_test_config()
        
        # Initialize components
        self.tester = MCPComplianceTester(
            server_url=self.test_config["server_url"],
            auth_token=self.test_config["auth_token"],
            timeout=self.test_config["timeout"],
            max_retries=self.test_config["max_retries"]
        )
        
        self.validator = MCPComplianceValidator()
        
        # Setup logging
        self._setup_logging()
        
        # Test results storage
        self.test_results: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        logger.info(f"🚀 Real MCP Compliance Tester initialized")
        logger.info(f"📡 Server: {self.test_config['server_config']['name']}")
        logger.info(f"🔗 URL: {self.test_config['server_url']}")
    
    def _setup_logging(self) -> None:
        """Setup comprehensive logging."""
        # Create logs directory
        logs_dir = Path(self.test_config["output_dir"]) / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup file logging
        timestamp = int(time.time())
        log_file = logs_dir / f"real_mcp_compliance_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger.info(f"📝 Logging to: {log_file}")
    
    async def run_comprehensive_compliance_test(self) -> Dict[str, Any]:
        """
        Run comprehensive compliance test against real MCP server.
        
        Returns:
            Complete test results and compliance report
        """
        logger.info("🚀 Starting Comprehensive MCP Compliance Testing")
        logger.info(f"🎯 Target: {self.test_config['server_config']['name']}")
        
        start_time = time.time()
        
        try:
            # Step 1: Server connectivity test
            logger.info("🔍 Step 1: Testing Server Connectivity")
            connectivity_result = await self._test_server_connectivity()
            
            if not connectivity_result["success"]:
                logger.error(f"❌ Server connectivity failed: {connectivity_result['error']}")
                return {
                    "status": "FAILED",
                    "error": "Server connectivity failed",
                    "details": connectivity_result,
                    "execution_time": time.time() - start_time
                }
            
            # Step 2: Protocol compliance testing
            logger.info("🔍 Step 2: Testing Protocol Compliance")
            protocol_results = await self._test_protocol_compliance()
            
            # Step 3: Tool and resource testing
            logger.info("🔍 Step 3: Testing Tools and Resources")
            tool_results = await self._test_tools_and_resources()
            
            # Step 4: Security and authentication testing
            logger.info("🔍 Step 4: Testing Security and Authentication")
            security_results = await self._test_security_and_auth()
            
            # Step 5: Performance and resilience testing
            logger.info("🔍 Step 5: Testing Performance and Resilience")
            performance_results = await self._test_performance_and_resilience()
            
            # Step 6: Compliance validation
            logger.info("🔍 Step 6: Validating Compliance Requirements")
            compliance_report = await self._validate_compliance()
            
            # Step 7: Generate comprehensive report
            logger.info("🔍 Step 7: Generating Comprehensive Report")
            final_report = await self._generate_comprehensive_report(
                connectivity_result,
                protocol_results,
                tool_results,
                security_results,
                performance_results,
                compliance_report
            )
            
            execution_time = time.time() - start_time
            logger.info(f"✅ Comprehensive MCP Compliance Testing completed in {execution_time:.2f}s")
            
            return final_report
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Comprehensive testing failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def _test_server_connectivity(self) -> Dict[str, Any]:
        """Test basic server connectivity."""
        try:
            logger.info("🔗 Testing server connectivity...")
            
            # Test WebSocket connection
            websocket_score = await self.tester._test_websocket_connection()
            logger.info(f"   WebSocket connection: {websocket_score:.2%}")
            
            # Test HTTP connection (if supported)
            http_score = 0.0
            if self.test_config["server_config"]["supports_http"]:
                http_score = await self.tester._test_http_connection()
                logger.info(f"   HTTP connection: {http_score:.2%}")
            
            # Test connection resilience
            resilience_score = await self.tester._test_connection_resilience()
            logger.info(f"   Connection resilience: {resilience_score:.2%}")
            
            # Calculate overall connectivity score
            if self.test_config["server_config"]["supports_http"]:
                connectivity_score = (websocket_score + http_score + resilience_score) / 3
            else:
                connectivity_score = (websocket_score + resilience_score) / 2
            
            success = connectivity_score >= 0.7
            
            return {
                "success": success,
                "score": connectivity_score,
                "websocket_score": websocket_score,
                "http_score": http_score,
                "resilience_score": resilience_score,
                "details": {
                    "supports_websocket": self.test_config["server_config"]["supports_websocket"],
                    "supports_http": self.test_config["server_config"]["supports_http"]
                }
            }
            
        except Exception as e:
            logger.error(f"Connectivity test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    async def _test_protocol_compliance(self) -> Dict[str, Any]:
        """Test MCP protocol compliance."""
        try:
            logger.info("📋 Testing MCP protocol compliance...")
            
            # Test protocol version
            version_info = await self.tester._get_protocol_version()
            logger.info(f"   Protocol version: {version_info['version']}")
            logger.info(f"   Supported versions: {version_info['supported_versions']}")
            
            # Test message format
            message_format_score = await self.tester._test_message_format()
            logger.info(f"   Message format: {message_format_score:.2%}")
            
            # Test parameter validation
            param_validation_score = await self.tester._test_parameter_validation()
            logger.info(f"   Parameter validation: {param_validation_score:.2%}")
            
            # Calculate overall protocol score
            protocol_score = (message_format_score + param_validation_score) / 2
            
            return {
                "success": protocol_score >= 0.8,
                "score": protocol_score,
                "version_info": version_info,
                "message_format_score": message_format_score,
                "param_validation_score": param_validation_score,
                "details": {
                    "expected_version": self.test_config["server_config"]["expected_protocol_version"],
                    "actual_version": version_info["version"]
                }
            }
            
        except Exception as e:
            logger.error(f"Protocol compliance test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    async def _test_tools_and_resources(self) -> Dict[str, Any]:
        """Test tools and resources functionality."""
        try:
            logger.info("🛠️ Testing tools and resources...")
            
            # Test tool management
            tool_management_score = await self.tester._test_tool_management()
            logger.info(f"   Tool management: {tool_management_score:.2%}")
            
            # Test resource management
            resource_management_score = await self.tester._test_resource_management()
            logger.info(f"   Resource management: {resource_management_score:.2%}")
            
            # Test prompt management
            prompt_management_score = await self.tester._test_prompt_management()
            logger.info(f"   Prompt management: {prompt_management_score:.2%}")
            
            # Calculate overall functionality score
            functionality_score = (tool_management_score + resource_management_score + prompt_management_score) / 3
            
            return {
                "success": functionality_score >= 0.6,
                "score": functionality_score,
                "tool_management_score": tool_management_score,
                "resource_management_score": resource_management_score,
                "prompt_management_score": prompt_management_score,
                "details": {
                    "expected_tools": self.test_config["server_config"]["expected_tools"]
                }
            }
            
        except Exception as e:
            logger.error(f"Tools and resources test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    async def _test_security_and_auth(self) -> Dict[str, Any]:
        """Test security and authentication features."""
        try:
            logger.info("🔒 Testing security and authentication...")
            
            # Test authentication
            auth_score = await self.tester._test_authentication()
            logger.info(f"   Authentication: {auth_score:.2%}")
            
            # Test security features
            security_score = await self.tester._test_security_features()
            logger.info(f"   Security features: {security_score:.2%}")
            
            # Test rate limiting
            rate_limit_score = await self.tester._test_rate_limiting()
            logger.info(f"   Rate limiting: {rate_limit_score:.2%}")
            
            # Calculate overall security score
            security_overall_score = (auth_score + security_score + rate_limit_score) / 3
            
            return {
                "success": security_overall_score >= 0.7,
                "score": security_overall_score,
                "auth_score": auth_score,
                "security_score": security_score,
                "rate_limit_score": rate_limit_score,
                "details": {
                    "auth_required": self.test_config["server_config"]["auth_required"],
                    "rate_limiting": self.test_config["server_config"]["rate_limiting"]
                }
            }
            
        except Exception as e:
            logger.error(f"Security and auth test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    async def _test_performance_and_resilience(self) -> Dict[str, Any]:
        """Test performance and resilience features."""
        try:
            logger.info("⚡ Testing performance and resilience...")
            
            # Test error handling
            error_handling_score = await self.tester._test_error_handling()
            logger.info(f"   Error handling: {error_handling_score:.2%}")
            
            # Test resilience
            resilience_score = await self.tester._test_resilience()
            logger.info(f"   Resilience: {resilience_score:.2%}")
            
            # Test performance (connection times, response times)
            performance_score = await self._test_performance_metrics()
            logger.info(f"   Performance: {performance_score:.2%}")
            
            # Calculate overall performance score
            performance_overall_score = (error_handling_score + resilience_score + performance_score) / 3
            
            return {
                "success": performance_overall_score >= 0.6,
                "score": performance_overall_score,
                "error_handling_score": error_handling_score,
                "resilience_score": resilience_score,
                "performance_score": performance_score,
                "details": {
                    "circuit_breaker": self.test_config["server_config"]["circuit_breaker"],
                    "health_checks": self.test_config["server_config"]["health_checks"]
                }
            }
            
        except Exception as e:
            logger.error(f"Performance and resilience test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    async def _test_performance_metrics(self) -> float:
        """Test performance metrics."""
        try:
            # Test response times for basic operations
            start_time = time.time()
            
            # Test tool listing response time
            tools = await self.tester._list_tools()
            tool_listing_time = time.time() - start_time
            
            # Test basic tool execution time
            if tools:
                start_time = time.time()
                tool_exec_score = await self.tester._test_tool_execution()
                tool_execution_time = time.time() - start_time
            else:
                tool_exec_score = 0.0
                tool_execution_time = 0.0
            
            # Score based on response times
            score = 1.0
            if tool_listing_time > 5.0:  # More than 5 seconds
                score -= 0.3
            elif tool_listing_time > 2.0:  # More than 2 seconds
                score -= 0.1
            
            if tool_execution_time > 10.0:  # More than 10 seconds
                score -= 0.3
            elif tool_execution_time > 5.0:  # More than 5 seconds
                score -= 0.1
            
            # Store performance metrics
            self.performance_metrics = {
                "tool_listing_time": tool_listing_time,
                "tool_execution_time": tool_execution_time,
                "tool_count": len(tools) if tools else 0
            }
            
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"Performance metrics test failed: {e}")
            return 0.0
    
    async def _validate_compliance(self) -> Dict[str, Any]:
        """Validate compliance requirements."""
        try:
            logger.info("✅ Validating compliance requirements...")
            
            # Run the full compliance test suite
            test_report = await self.tester.run_full_compliance_test()
            
            # Validate against requirements
            validation_report = self.validator.validate_compliance(
                [asdict(result) for result in test_report.test_results]
            )
            
            return {
                "success": validation_report.certification_status in ["COMPLIANT", "MOSTLY_COMPLIANT"],
                "certification_status": validation_report.certification_status,
                "overall_score": validation_report.overall_score,
                "total_requirements": validation_report.total_requirements,
                "passed_requirements": validation_report.passed_requirements,
                "failed_requirements": validation_report.failed_requirements,
                "recommendations": validation_report.recommendations,
                "test_results": [asdict(result) for result in test_report.test_results]
            }
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "certification_status": "FAILED",
                "overall_score": 0.0
            }
    
    async def _generate_comprehensive_report(
        self,
        connectivity_result: Dict[str, Any],
        protocol_results: Dict[str, Any],
        tool_results: Dict[str, Any],
        security_results: Dict[str, Any],
        performance_results: Dict[str, Any],
        compliance_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        try:
            logger.info("📊 Generating comprehensive report...")
            
            # Calculate overall success
            all_tests = [
                connectivity_result,
                protocol_results,
                tool_results,
                security_results,
                performance_results
            ]
            
            successful_tests = sum(1 for test in all_tests if test.get("success", False))
            total_tests = len(all_tests)
            overall_success_rate = successful_tests / total_tests
            
            # Calculate weighted score
            weights = {
                "connectivity": 0.20,
                "protocol": 0.25,
                "tools": 0.25,
                "security": 0.20,
                "performance": 0.10
            }
            
            weighted_score = (
                connectivity_result.get("score", 0.0) * weights["connectivity"] +
                protocol_results.get("score", 0.0) * weights["protocol"] +
                tool_results.get("score", 0.0) * weights["tools"] +
                security_results.get("score", 0.0) * weights["security"] +
                performance_results.get("score", 0.0) * weights["performance"]
            )
            
            # Determine overall status
            if overall_success_rate >= 0.8 and weighted_score >= 0.8:
                overall_status = "PASSED"
            elif overall_success_rate >= 0.6 and weighted_score >= 0.6:
                overall_status = "PARTIAL"
            else:
                overall_status = "FAILED"
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                connectivity_result,
                protocol_results,
                tool_results,
                security_results,
                performance_results,
                compliance_report
            )
            
            comprehensive_report = {
                "status": "COMPLETED",
                "overall_status": overall_status,
                "overall_success_rate": overall_success_rate,
                "weighted_score": weighted_score,
                "certification_status": compliance_report.get("certification_status", "UNKNOWN"),
                "compliance_score": compliance_report.get("overall_score", 0.0),
                "test_results": {
                    "connectivity": connectivity_result,
                    "protocol": protocol_results,
                    "tools": tool_results,
                    "security": security_results,
                    "performance": performance_results
                },
                "compliance_details": compliance_report,
                "performance_metrics": self.performance_metrics,
                "recommendations": recommendations,
                "server_info": {
                    "name": self.test_config["server_config"]["name"],
                    "url": self.test_config["server_url"],
                    "expected_tools": self.test_config["server_config"]["expected_tools"],
                    "expected_protocol": self.test_config["server_config"]["expected_protocol_version"]
                },
                "test_config": {
                    "timeout": self.test_config["timeout"],
                    "max_retries": self.test_config["max_retries"],
                    "parallel_tests": self.test_config["parallel_tests"]
                }
            }
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {
                "status": "FAILED",
                "error": f"Report generation failed: {str(e)}"
            }
    
    def _generate_recommendations(
        self,
        connectivity_result: Dict[str, Any],
        protocol_results: Dict[str, Any],
        tool_results: Dict[str, Any],
        security_results: Dict[str, Any],
        performance_results: Dict[str, Any],
        compliance_report: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Connectivity recommendations
        if connectivity_result.get("score", 0.0) < 0.8:
            recommendations.append("Improve server connectivity and response times")
        
        # Protocol recommendations
        if protocol_results.get("score", 0.0) < 0.8:
            recommendations.append("Enhance MCP protocol compliance and message handling")
        
        # Tools recommendations
        if tool_results.get("score", 0.0) < 0.8:
            recommendations.append("Improve tool and resource management functionality")
        
        # Security recommendations
        if security_results.get("score", 0.0) < 0.8:
            recommendations.append("Strengthen authentication and security features")
        
        # Performance recommendations
        if performance_results.get("score", 0.0) < 0.8:
            recommendations.append("Optimize performance and implement resilience patterns")
        
        # Compliance recommendations
        if compliance_report.get("overall_score", 0.0) < 0.9:
            recommendations.append("Address compliance gaps to achieve full certification")
        
        # Add specific recommendations from compliance report
        if "recommendations" in compliance_report:
            recommendations.extend(compliance_report["recommendations"])
        
        if not recommendations:
            recommendations.append("All tests passed - maintain current standards")
        
        return recommendations
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print formatted test summary."""
        print("\n" + "="*80)
        print("🏆 REAL MCP SERVER COMPLIANCE TESTING SUMMARY")
        print("="*80)
        
        # Server Information
        server_info = report.get("server_info", {})
        print(f"\n📡 SERVER INFORMATION:")
        print(f"   Name: {server_info.get('name', 'Unknown')}")
        print(f"   URL: {server_info.get('url', 'Unknown')}")
        print(f"   Expected Protocol: {server_info.get('expected_protocol', 'Unknown')}")
        
        # Overall Results
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Status: {report.get('overall_status', 'Unknown')}")
        print(f"   Success Rate: {report.get('overall_success_rate', 0):.1%}")
        print(f"   Weighted Score: {report.get('weighted_score', 0):.1%}")
        print(f"   Certification: {report.get('certification_status', 'Unknown')}")
        print(f"   Compliance Score: {report.get('compliance_score', 0):.1%}")
        
        # Test Results
        test_results = report.get("test_results", {})
        print(f"\n🧪 TEST RESULTS:")
        for test_name, result in test_results.items():
            status_icon = "✅" if result.get("success", False) else "❌"
            score = result.get("score", 0.0)
            print(f"   {test_name.title()}: {status_icon} {score:.1%}")
        
        # Performance Metrics
        performance = report.get("performance_metrics", {})
        if performance:
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Tool Listing Time: {performance.get('tool_listing_time', 0):.2f}s")
            print(f"   Tool Execution Time: {performance.get('tool_execution_time', 0):.2f}s")
            print(f"   Available Tools: {performance.get('tool_count', 0)}")
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)


async def main():
    """Main entry point for real MCP compliance testing."""
    print("🚀 Real MCP Server Compliance Testing")
    print("="*60)
    
    # Load configuration
    config = MCPComplianceConfig()
    
    # Validate configuration
    if not config.validate_config():
        print("❌ Configuration validation failed. Please check your environment variables.")
        sys.exit(1)
    
    # Print configuration
    config.print_config()
    
    try:
        # Initialize tester
        tester = RealMCPComplianceTester(config)
        
        # Run comprehensive compliance test
        results = await tester.run_comprehensive_compliance_test()
        
        if results["status"] == "COMPLETED":
            # Print summary
            tester.print_summary(results)
            
            # Save detailed report
            output_dir = Path(config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = int(time.time())
            report_file = output_dir / f"real_mcp_compliance_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n📄 Detailed report saved to: {report_file}")
            
            # Exit with appropriate code
            if results["overall_status"] == "PASSED":
                print("\n🎉 Real MCP Compliance Testing PASSED!")
                sys.exit(0)
            elif results["overall_status"] == "PARTIAL":
                print("\n⚠️ Real MCP Compliance Testing PARTIAL - Some issues found")
                sys.exit(1)
            else:
                print("\n❌ Real MCP Compliance Testing FAILED")
                sys.exit(1)
        else:
            print(f"\n❌ Real MCP Compliance Testing FAILED: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Check for environment argument
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
        print(f"🔧 Loading environment configuration: {env_name}")
        load_environment_config(env_name)
    
    # Run the main function
    asyncio.run(main())
