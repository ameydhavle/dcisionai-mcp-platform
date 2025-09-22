#!/usr/bin/env python3
"""
DcisionAI Platform - Platform Manager Integration Test
=====================================================

Real integration test for the Platform Manager with:
- Multi-tenant orchestration
- Real tool execution
- AWS Bedrock integration
- Performance monitoring

NO MOCKS - Production code only.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from platform_core.orchestrator.platform_manager import PlatformManager
from shared.core.base_agent import TenantContext, SLATier, PIIScope

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformManagerIntegrationTest:
    """Real integration test for Platform Manager."""
    
    def __init__(self):
        """Initialize the integration test."""
        self.platform_manager: Optional[PlatformManager] = None
        self.test_tenants: Dict[str, TenantContext] = {}
        self.test_results: Dict[str, Any] = {}
        
        logger.info("✅ Platform Manager Integration Test initialized")
    
    async def setup(self):
        """Set up the test environment."""
        try:
            logger.info("🔧 Setting up Platform Manager...")
            
            # Initialize Platform Manager
            self.platform_manager = PlatformManager(
                enable_monitoring=True,
                enable_auto_scaling=True
            )
            
            # Start the platform
            await self.platform_manager.start()
            
            # Create test tenants
            await self._create_test_tenants()
            
            logger.info("✅ Test environment setup completed")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            raise
    
    async def _create_test_tenants(self):
        """Create test tenants for integration testing."""
        try:
            # Gold tier tenant (enterprise)
            gold_tenant = TenantContext(
                tenant_id="t_gold_test",
                org_id="gold_org",
                project_id="gold_project",
                user_id="u_gold_001",
                entitlements=["solver.highs", "solver.ortools", "data.analysis", "model.builder", "rag", "byok"],
                pii_scope=PIIScope.FULL,
                region="us-east-1",
                sla_tier=SLATier.GOLD
            )
            
            # Pro tier tenant
            pro_tenant = TenantContext(
                tenant_id="t_pro_test",
                org_id="pro_org",
                project_id="pro_project",
                user_id="u_pro_001",
                entitlements=["solver.ortools", "data.analysis", "model.builder"],
                pii_scope=PIIScope.BASIC,
                region="us-west-2",
                sla_tier=SLATier.PRO
            )
            
            # Free tier tenant
            free_tenant = TenantContext(
                tenant_id="t_free_test",
                org_id="free_org",
                project_id="free_project",
                user_id="u_free_001",
                entitlements=["solver.ortools"],
                pii_scope=PIIScope.NONE,
                region="us-east-1",
                sla_tier=SLATier.FREE
            )
            
            # Register tenants
            tenants = [gold_tenant, pro_tenant, free_tenant]
            for tenant in tenants:
                success = await self.platform_manager.register_tenant(tenant)
                if success:
                    self.test_tenants[tenant.tenant_id] = tenant
                    logger.info(f"✅ Tenant {tenant.tenant_id} registered")
                else:
                    logger.error(f"❌ Failed to register tenant {tenant.tenant_id}")
            
            logger.info(f"✅ Created {len(self.test_tenants)} test tenants")
            
        except Exception as e:
            logger.error(f"❌ Failed to create test tenants: {e}")
            raise
    
    async def test_tenant_registration(self):
        """Test tenant registration and validation."""
        try:
            logger.info("🧪 Testing tenant registration...")
            
            # Test invalid tenant (missing entitlements)
            invalid_tenant = TenantContext(
                tenant_id="t_invalid",
                org_id="invalid_org",
                project_id="invalid_project",
                user_id="u_invalid_001",
                entitlements=[],  # No entitlements
                pii_scope=PIIScope.NONE,
                region="us-east-1",
                sla_tier=SLATier.FREE
            )
            
            success = await self.platform_manager.register_tenant(invalid_tenant)
            assert not success, "Should reject tenant without entitlements"
            
            # Test duplicate registration
            duplicate_tenant = self.test_tenants["t_gold_test"]
            success = await self.platform_manager.register_tenant(duplicate_tenant)
            assert not success, "Should reject duplicate tenant registration"
            
            logger.info("✅ Tenant registration tests passed")
            
        except Exception as e:
            logger.error(f"❌ Tenant registration test failed: {e}")
            raise
    
    async def test_tool_execution(self):
        """Test real tool execution through the platform."""
        try:
            logger.info("🧪 Testing tool execution...")
            
            # Test solver tool execution
            solver_request = {
                "type": "tool",
                "tool_id": "solver-ortools",
                "parameters": {
                    "problem_type": "linear_programming",
                    "objective": "minimize",
                    "variables": ["x1", "x2"],
                    "constraints": [
                        {"expression": "x1 + x2 <= 10", "type": "inequality"},
                        {"expression": "x1 >= 0", "type": "inequality"},
                        {"expression": "x2 >= 0", "type": "inequality"}
                    ],
                    "objective_function": "2*x1 + 3*x2"
                },
                "priority": "high",
                "timeout": 120
            }
            
            # Execute for gold tenant
            gold_result = await self.platform_manager.process_tenant_request(
                "t_gold_test", solver_request
            )
            
            assert gold_result["success"], f"Gold tenant solver execution failed: {gold_result}"
            logger.info(f"✅ Gold tenant solver execution: {gold_result['metadata']}")
            
            # Test data analysis tool
            data_request = {
                "type": "tool",
                "tool_id": "data-analyzer",
                "parameters": {
                    "data_type": "manufacturing_metrics",
                    "analysis_type": "trend_analysis",
                    "time_range": "last_30_days",
                    "metrics": ["production_efficiency", "quality_score", "cost_per_unit"]
                },
                "priority": "normal",
                "timeout": 60
            }
            
            pro_result = await self.platform_manager.process_tenant_request(
                "t_pro_test", data_request
            )
            
            assert pro_result["success"], f"Pro tenant data analysis failed: {pro_result}"
            logger.info(f"✅ Pro tenant data analysis: {pro_result['metadata']}")
            
            logger.info("✅ Tool execution tests passed")
            
        except Exception as e:
            logger.error(f"❌ Tool execution test failed: {e}")
            raise
    
    async def test_inference_execution(self):
        """Test inference execution through AWS Bedrock."""
        try:
            logger.info("🧪 Testing inference execution...")
            
            # Test manufacturing optimization inference
            inference_request = {
                "type": "inference",
                "domain": "manufacturing",
                "request_type": "production_optimization",
                "payload": {
                    "production_capacity": 1000,
                    "demand_forecast": 800,
                    "resource_constraints": {
                        "labor_hours": 2000,
                        "machine_hours": 1500,
                        "material_availability": 0.9
                    },
                    "optimization_goals": ["minimize_cost", "maximize_efficiency"]
                },
                "inference_profile": "dcisionai-manufacturing-latency"
            }
            
            # Execute for gold tenant
            gold_inference = await self.platform_manager.process_tenant_request(
                "t_gold_test", inference_request
            )
            
            assert gold_inference["success"], f"Gold tenant inference failed: {gold_inference}"
            logger.info(f"✅ Gold tenant inference: {gold_inference['metadata']}")
            
            logger.info("✅ Inference execution tests passed")
            
        except Exception as e:
            logger.error(f"❌ Inference execution test failed: {e}")
            raise
    
    async def test_tenant_isolation(self):
        """Test tenant isolation and access control."""
        try:
            logger.info("🧪 Testing tenant isolation...")
            
            # Test that free tenant cannot access pro features
            pro_feature_request = {
                "type": "tool",
                "tool_id": "data-analyzer",  # Requires "data.analysis" entitlement
                "parameters": {"analysis_type": "trend_analysis"},
                "priority": "normal",
                "timeout": 60
            }
            
            free_result = await self.platform_manager.process_tenant_request(
                "t_free_test", pro_feature_request
            )
            
            # Free tenant should not have access to data analysis
            assert not free_result["success"], "Free tenant should not access pro features"
            logger.info("✅ Free tenant correctly denied access to pro features")
            
            # Test that gold tenant can access all features
            gold_catalog = await self.platform_manager.get_tenant_catalog("t_gold_test")
            assert gold_catalog["success"], "Gold tenant catalog access failed"
            
            catalog = gold_catalog["catalog"]
            assert catalog["total_tools"] > 0, "Gold tenant should have access to tools"
            logger.info(f"✅ Gold tenant has access to {catalog['total_tools']} tools")
            
            logger.info("✅ Tenant isolation tests passed")
            
        except Exception as e:
            logger.error(f"❌ Tenant isolation test failed: {e}")
            raise
    
    async def test_performance_monitoring(self):
        """Test performance monitoring and metrics."""
        try:
            logger.info("🧪 Testing performance monitoring...")
            
            # Get platform metrics
            platform_metrics = self.platform_manager.get_platform_metrics()
            assert "platform" in platform_metrics, "Platform metrics missing"
            assert "tenants" in platform_metrics, "Tenant metrics missing"
            
            # Check tenant metrics
            for tenant_id in self.test_tenants:
                tenant_metrics = await self.platform_manager.get_tenant_metrics(tenant_id)
                assert tenant_metrics["success"], f"Failed to get metrics for {tenant_id}"
                
                metrics = tenant_metrics["metrics"]
                assert metrics["request_count"] >= 0, "Request count should be non-negative"
                assert 0 <= metrics["success_rate"] <= 100, "Success rate should be 0-100%"
                
                logger.info(f"✅ {tenant_id} metrics: {metrics['request_count']} requests, {metrics['success_rate']:.1f}% success")
            
            # Get platform status
            platform_status = self.platform_manager.get_platform_status()
            assert "status" in platform_status, "Platform status missing"
            assert platform_status["status"] in ["operational", "degraded", "maintenance"], "Invalid platform status"
            
            logger.info(f"✅ Platform status: {platform_status['status']}")
            logger.info("✅ Performance monitoring tests passed")
            
        except Exception as e:
            logger.error(f"❌ Performance monitoring test failed: {e}")
            raise
    
    async def test_health_monitoring(self):
        """Test health monitoring and component status."""
        try:
            logger.info("🧪 Testing health monitoring...")
            
            # Get comprehensive health check
            health_status = self.platform_manager.health_check()
            assert "status" in health_status, "Health status missing"
            assert "component_health" in health_status, "Component health missing"
            
            # Check component health
            component_health = health_status["component_health"]
            assert "inference_manager" in component_health, "Inference manager health missing"
            assert "gateway_client" in component_health, "Gateway client health missing"
            
            # Check inference manager health
            inference_health = component_health["inference_manager"]
            if inference_health and inference_health != "not_initialized":
                assert "status" in inference_health, "Inference manager status missing"
                logger.info(f"✅ Inference manager: {inference_health['status']}")
            
            # Check gateway client health
            gateway_health = component_health["gateway_client"]
            if gateway_health and gateway_health != "not_initialized":
                assert "status" in gateway_health, "Gateway client status missing"
                logger.info(f"✅ Gateway client: {gateway_health['status']}")
            
            logger.info("✅ Health monitoring tests passed")
            
        except Exception as e:
            logger.error(f"❌ Health monitoring test failed: {e}")
            raise
    
    async def run_all_tests(self):
        """Run all integration tests."""
        try:
            logger.info("🚀 Starting Platform Manager Integration Tests...")
            
            # Setup
            await self.setup()
            
            # Run tests
            test_methods = [
                self.test_tenant_registration,
                self.test_tool_execution,
                self.test_inference_execution,
                self.test_tenant_isolation,
                self.test_performance_monitoring,
                self.test_health_monitoring
            ]
            
            for test_method in test_methods:
                try:
                    await test_method()
                    logger.info(f"✅ {test_method.__name__} passed")
                except Exception as e:
                    logger.error(f"❌ {test_method.__name__} failed: {e}")
                    raise
            
            logger.info("🎉 All integration tests passed!")
            
        except Exception as e:
            logger.error(f"❌ Integration tests failed: {e}")
            raise
        
        finally:
            # Cleanup
            if self.platform_manager:
                await self.platform_manager.cleanup()
    
    async def cleanup(self):
        """Cleanup test resources."""
        try:
            if self.platform_manager:
                await self.platform_manager.cleanup()
            logger.info("✅ Test cleanup completed")
        except Exception as e:
            logger.error(f"❌ Test cleanup failed: {e}")

async def main():
    """Main test execution."""
    test = PlatformManagerIntegrationTest()
    try:
        await test.run_all_tests()
    finally:
        await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
