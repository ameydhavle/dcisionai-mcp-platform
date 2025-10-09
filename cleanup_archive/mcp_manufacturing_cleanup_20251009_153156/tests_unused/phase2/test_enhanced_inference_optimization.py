#!/usr/bin/env python3
"""
Phase 2 Test Suite: Enhanced Inference Optimization
==================================================

Comprehensive testing for:
- Cross-region inference optimization
- Enhanced Gateway integration
- Performance monitoring and cost tracking
- Multi-domain tool management
"""

import asyncio
import time
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.core.inference_manager import InferenceManager, InferenceRequest
from shared.core.gateway_client import GatewayClient
from domains.manufacturing.agents.DcisionAI_Manufacturing_Agent_v2 import DcisionAI_Manufacturing_Agent_v2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Phase2TestSuite:
    """Comprehensive test suite for Phase 2 enhanced inference optimization."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.logger = logging.getLogger("Phase2TestSuite")
        self.test_results = []
        self.start_time = time.time()
        
    async def run_all_tests(self):
        """Run all Phase 2 tests."""
        self.logger.info("🚀 Starting Phase 2 Enhanced Inference Optimization Test Suite")
        
        try:
            # Test 1: Inference Manager
            await self.test_inference_manager()
            
            # Test 2: Gateway Client
            await self.test_gateway_client()
            
            # Test 3: Enhanced Manufacturing Agent
            await self.test_enhanced_manufacturing_agent()
            
            # Test 4: Cross-Region Optimization
            await self.test_cross_region_optimization()
            
            # Test 5: Performance Monitoring
            await self.test_performance_monitoring()
            
            # Test 6: Cost Tracking
            await self.test_cost_tracking()
            
            # Test 7: Health Monitoring
            await self.test_health_monitoring()
            
            # Test 8: Integration Testing
            await self.test_integration()
            
        except Exception as e:
            self.logger.error(f"❌ Test suite failed: {e}")
            self.test_results.append({
                'test': 'Test Suite',
                'status': 'FAILED',
                'error': str(e)
            })
        
        finally:
            # Generate test report
            await self.generate_test_report()
    
    async def test_inference_manager(self):
        """Test enhanced inference manager."""
        self.logger.info("🧪 Test 1: Enhanced Inference Manager")
        
        try:
            # Initialize inference manager
            inference_manager = InferenceManager()
            
            # Wait for region metrics to be initialized
            await asyncio.sleep(3)  # Allow time for background tasks to initialize metrics
            
            # Test initialization
            assert hasattr(inference_manager, 'region_metrics'), "Should have region metrics"
            assert len(inference_manager.region_metrics) > 0, "Should have initialized regions"
            
            # Test configuration loading
            assert hasattr(inference_manager, 'config'), "Should have configuration"
            assert 'inference_profiles' in inference_manager.config, "Should have inference profiles"
            
            # Test region selection
            test_request = InferenceRequest(
                request_id="test",
                domain="manufacturing",
                request_type="test",
                payload={"test": "data"}
            )
            
            selected_region = inference_manager.select_optimal_region(test_request)
            assert selected_region in ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'], \
                f"Invalid region selected: {selected_region}"
            
            # Cleanup
            await inference_manager.cleanup()
            
            self.logger.info("✅ Inference Manager tests passed")
            self.test_results.append({
                'test': 'Inference Manager',
                'status': 'PASSED',
                'details': f"Initialized with {len(inference_manager.region_metrics)} regions"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Inference Manager test failed: {e}")
            self.test_results.append({
                'test': 'Inference Manager',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def test_gateway_client(self):
        """Test enhanced Gateway client."""
        self.logger.info("🧪 Test 2: Enhanced Gateway Client")
        
        try:
            # Initialize Gateway client
            async with GatewayClient() as gateway_client:
                # Wait for region metrics to be initialized
                await asyncio.sleep(3)  # Allow time for background tasks to initialize metrics
                
                # Test tool discovery
                manufacturing_tools = await gateway_client.discover_tools(domain="manufacturing")
                assert len(manufacturing_tools) > 0, "Should discover manufacturing tools"
                
                finance_tools = await gateway_client.discover_tools(domain="finance")
                assert len(finance_tools) > 0, "Should discover finance tools"
                
                pharma_tools = await gateway_client.discover_tools(domain="pharma")
                assert len(pharma_tools) > 0, "Should discover pharma tools"
                
                # Test semantic search
                search_results = await gateway_client.discover_tools(query="optimization")
                assert len(search_results) > 0, "Should find tools via semantic search"
                
                # Test performance metrics
                performance = gateway_client.get_performance_metrics()
                assert 'tools_count' in performance, "Should have tools count"
                assert performance['tools_count'] > 0, "Should have registered tools"
                
            self.logger.info("✅ Gateway Client tests passed")
            self.test_results.append({
                'test': 'Gateway Client',
                'status': 'PASSED',
                'details': f"Discovered {len(manufacturing_tools + finance_tools + pharma_tools)} tools across all domains"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Gateway Client test failed: {e}")
            self.test_results.append({
                'test': 'Gateway Client',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def test_enhanced_manufacturing_agent(self):
        """Test enhanced manufacturing agent with inference optimization."""
        self.logger.info("🧪 Test 3: Enhanced Manufacturing Agent")
        
        try:
            # Initialize agent
            agent = DcisionAI_Manufacturing_Agent_v2()
            
            # Wait for region metrics to be initialized
            await asyncio.sleep(3)  # Allow time for background tasks to initialize metrics
            
            # Test agent capabilities
            capabilities = agent.get_capabilities()
            assert 'capabilities' in capabilities, "Should return capabilities"
            assert len(capabilities['capabilities']) > 0, "Should have at least one capability"
            
            # Test tool registration
            assert hasattr(agent, 'intent_tool'), "Should have intent tool"
            assert hasattr(agent, 'data_tool'), "Should have data tool"
            assert hasattr(agent, 'model_tool'), "Should have model tool"
            assert hasattr(agent, 'solver_tool'), "Should have solver tool"
            
            # Cleanup
            await agent.cleanup()
            
            self.logger.info("✅ Enhanced Manufacturing Agent tests passed")
            self.test_results.append({
                'test': 'Enhanced Manufacturing Agent',
                'status': 'PASSED',
                'details': f"Agent initialized with {len(capabilities['capabilities'])} capabilities"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced Manufacturing Agent test failed: {e}")
            self.test_results.append({
                'test': 'Enhanced Manufacturing Agent',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def test_cross_region_optimization(self):
        """Test cross-region inference optimization."""
        self.logger.info("🧪 Test 4: Cross-Region Optimization")
        
        try:
            # Initialize inference manager
            inference_manager = InferenceManager()
            
            # Wait for region metrics to be initialized
            await asyncio.sleep(3)  # Allow time for background tasks to initialize metrics
            
            # Test region selection for different domains
            test_requests = [
                InferenceRequest(
                    request_id="test_1",
                    domain="manufacturing",
                    request_type="intent_classification",
                    payload={"query": "test"},
                    user_location="us"
                ),
                InferenceRequest(
                    request_id="test_2",
                    domain="finance",
                    request_type="risk_assessment",
                    payload={"portfolio": "test"},
                    user_location="eu"
                ),
                InferenceRequest(
                    request_id="test_3",
                    domain="pharma",
                    request_type="drug_discovery",
                    payload={"target": "test"},
                    user_location="ap"
                )
            ]
            
            regions_used = []
            for request in test_requests:
                optimal_region = inference_manager.select_optimal_region(request)
                regions_used.append(optimal_region)
                assert optimal_region in ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'], \
                    f"Invalid region selected: {optimal_region}"
            
            # Verify different regions were selected (optimization working)
            unique_regions = set(regions_used)
            assert len(unique_regions) > 1, "Should select different regions for optimization"
            
            # Cleanup
            await inference_manager.cleanup()
            
            self.logger.info("✅ Cross-Region Optimization tests passed")
            self.test_results.append({
                'test': 'Cross-Region Optimization',
                'status': 'PASSED',
                'details': f"Selected {len(unique_regions)} different regions for optimization"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Cross-Region Optimization test failed: {e}")
            self.test_results.append({
                'test': 'Cross-Region Optimization',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def test_performance_monitoring(self):
        """Test performance monitoring capabilities."""
        self.logger.info("🧪 Test 5: Performance Monitoring")
        
        try:
            # Initialize components
            inference_manager = InferenceManager()
            async with GatewayClient() as gateway_client:
                # Wait for region metrics to be initialized
                await asyncio.sleep(3)  # Allow time for background tasks to initialize metrics
                
                # Test inference manager performance
                inference_performance = inference_manager.get_performance_summary()
                assert 'region_metrics' in inference_performance, "Should contain region metrics"
                
                # Test Gateway client performance
                gateway_performance = gateway_client.get_performance_metrics()
                assert 'request_count' in gateway_performance, "Should contain request metrics"
                assert 'tools_count' in gateway_performance, "Should contain tool metrics"
                
                # Test real-time metrics
                await asyncio.sleep(2)  # Wait for metrics to update
                updated_performance = inference_manager.get_performance_summary()
                assert 'timestamp' in updated_performance, "Should have updated timestamp"
                
            # Cleanup
            await inference_manager.cleanup()
            
            self.logger.info("✅ Performance Monitoring tests passed")
            self.test_results.append({
                'test': 'Performance Monitoring',
                'status': 'PASSED',
                'details': "Performance metrics collected and updated successfully"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Performance Monitoring test failed: {e}")
            self.test_results.append({
                'test': 'Performance Monitoring',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def test_cost_tracking(self):
        """Test cost tracking capabilities."""
        self.logger.info("🧪 Test 6: Cost Tracking")
        
        try:
            # Initialize inference manager
            inference_manager = InferenceManager()
            
            # Wait for region metrics to be initialized
            await asyncio.sleep(3)  # Allow time for background tasks to initialize metrics
            
            # Test cost calculation
            test_request = InferenceRequest(
                request_id="cost_test",
                domain="manufacturing",
                request_type="test",
                payload={"test": "data"},
                timeout=30
            )
            
            # Execute inference to test cost tracking
            result = await inference_manager.execute_inference(test_request)
            
            # Verify cost tracking
            assert hasattr(result, 'cost'), "Result should have cost attribute"
            assert isinstance(result.cost, (int, float)), "Cost should be numeric"
            assert result.cost >= 0, "Cost should be non-negative"
            
            # Cleanup
            await inference_manager.cleanup()
            
            self.logger.info("✅ Cost Tracking tests passed")
            self.test_results.append({
                'test': 'Cost Tracking',
                'status': 'PASSED',
                'details': f"Cost tracking working, sample cost: ${result.cost:.4f}"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Cost Tracking test failed: {e}")
            self.test_results.append({
                'test': 'Cost Tracking',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def test_health_monitoring(self):
        """Test health monitoring capabilities."""
        self.logger.info("🧪 Test 7: Health Monitoring")
        
        try:
            # Initialize components
            inference_manager = InferenceManager()
            async with GatewayClient() as gateway_client:
                # Wait for region metrics to be initialized
                await asyncio.sleep(3)  # Allow time for background tasks to initialize metrics
                
                # Test inference manager health
                inference_health = inference_manager.health_check()
                assert 'status' in inference_health, "Should contain health status"
                assert inference_health['status'] in ['healthy', 'degraded'], f"Unexpected health status: {inference_health['status']}"
                
                # Test Gateway client health
                gateway_health = gateway_client.health_check()
                assert 'status' in gateway_health, "Should contain health status"
                assert gateway_health['status'] in ['healthy', 'degraded'], f"Unexpected health status: {gateway_health['status']}"
                
                # Verify health details
                assert 'inference_manager' in gateway_health, "Should contain inference manager health"
                assert 'tool_registry' in gateway_health, "Should contain tool registry health"
                
            # Cleanup
            await inference_manager.cleanup()
            
            self.logger.info("✅ Health Monitoring tests passed")
            self.test_results.append({
                'test': 'Health Monitoring',
                'status': 'PASSED',
                'details': f"Inference: {inference_health['status']}, Gateway: {gateway_health['status']}"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Health Monitoring test failed: {e}")
            self.test_results.append({
                'test': 'Health Monitoring',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def test_integration(self):
        """Test integration between all components."""
        self.logger.info("🧪 Test 8: Integration Testing")
        
        try:
            # Test complete workflow with enhanced manufacturing agent
            agent = DcisionAI_Manufacturing_Agent_v2()
            
            # Wait for region metrics to be initialized
            await asyncio.sleep(3)  # Allow time for background tasks to initialize metrics
            
            # Test request processing
            test_request = {
                'query': 'Optimize production schedule to minimize costs while meeting customer demand for automotive parts manufacturing with capacity constraints of 1000 units per day',
                'user_location': 'us',
                'priority': 'normal'
            }
            
            # Execute workflow
            result = await agent.process_request(test_request)
            
            # Verify result structure
            assert 'success' in result, "Result should contain success status"
            assert 'workflow_id' in result, "Result should contain workflow ID"
            assert 'performance' in result, "Result should contain performance metrics"
            
            # Verify performance metrics
            performance = result['performance']
            assert 'total_execution_time' in performance, "Should track execution time"
            assert 'total_cost' in performance, "Should track cost"
            assert 'regions_used' in performance, "Should track regions used"
            
            # Verify regions were used
            regions_used = performance['regions_used']
            assert len(regions_used) > 0, "Should use at least one region"
            assert all(region != 'unknown' for region in regions_used), "Should not have unknown regions"
            
            # Cleanup
            await agent.cleanup()
            
            self.logger.info("✅ Integration tests passed")
            self.test_results.append({
                'test': 'Integration Testing',
                'status': 'PASSED',
                'details': f"Workflow completed in {performance['total_execution_time']:.2f}s using {len(set(regions_used))} regions"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Integration test failed: {e}")
            self.test_results.append({
                'test': 'Integration Testing',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def generate_test_report(self):
        """Generate comprehensive test report."""
        total_time = time.time() - self.start_time
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAILED'])
        
        # Generate report
        report = f"""
{'='*80}
🚀 PHASE 2 ENHANCED INFERENCE OPTIMIZATION TEST REPORT
{'='*80}

📊 Test Summary:
   Total Tests: {total_tests}
   Passed: {passed_tests} ✅
   Failed: {failed_tests} ❌
   Success Rate: {(passed_tests/total_tests*100):.1f}%
   Total Time: {total_time:.2f}s

📋 Detailed Results:
"""
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            report += f"   {status_icon} {result['test']}: {result['status']}\n"
            if 'details' in result:
                report += f"      Details: {result['details']}\n"
            if 'error' in result:
                report += f"      Error: {result['error']}\n"
            report += "\n"
        
        # Add recommendations
        if failed_tests == 0:
            report += f"""
🎉 ALL TESTS PASSED! 

Phase 2 implementation is working correctly:
✅ Cross-region inference optimization
✅ Enhanced Gateway integration  
✅ Performance monitoring and cost tracking
✅ Multi-domain tool management
✅ Health monitoring and alerting

The platform is ready for production deployment!
"""
        else:
            report += f"""
⚠️ {failed_tests} TESTS FAILED

Please review the failed tests and fix the issues before proceeding.
Focus on:
- Component initialization
- Configuration loading
- Integration between components
- Error handling and fallbacks
"""
        
        report += f"{'='*80}\n"
        
        # Print report
        print(report)
        
        # Save report to file
        report_file = project_root / "tests" / "phase2" / "test_report_phase2.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.logger.info(f"📄 Test report saved to: {report_file}")
        
        return failed_tests == 0

async def main():
    """Main test execution function."""
    test_suite = Phase2TestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎉 Phase 2 Test Suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Phase 2 Test Suite completed with failures!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
