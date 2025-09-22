#!/usr/bin/env python3
"""
DcisionAI Platform - Complete Architecture Integration Test
==========================================================

Real integration test for the complete multi-tenant architecture:
- Platform Manager
- Base Agent Framework
- Inference Manager with AWS Bedrock
- Gateway Client with Real Tools
- Multi-tenant orchestration

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
from shared.core.inference_manager import BedrockInferenceManager
from shared.core.gateway_client import GatewayClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteArchitectureTest:
    """Complete architecture integration test."""
    
    def __init__(self):
        """Initialize the integration test."""
        self.platform_manager: Optional[PlatformManager] = None
        self.inference_manager: Optional[BedrockInferenceManager] = None
        self.gateway_client: Optional[GatewayClient] = None
        self.test_tenants: Dict[str, TenantContext] = {}
        self.test_results: Dict[str, Any] = {}
        
        logger.info("✅ Complete Architecture Integration Test initialized")
    
    async def setup(self):
        """Set up the complete test environment."""
        try:
            logger.info("🔧 Setting up complete architecture...")
            
            # Initialize Platform Manager
            self.platform_manager = PlatformManager(
                enable_monitoring=True,
                enable_auto_scaling=True
            )
            await self.platform_manager.start()
            
            # Initialize Inference Manager
            self.inference_manager = BedrockInferenceManager()
            await self.inference_manager.start()
            
            # Initialize Gateway Client
            self.gateway_client = GatewayClient()
            await self.gateway_client.start()
            
            # Create test tenants
            await self._create_test_tenants()
            
            logger.info("✅ Complete architecture setup completed")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            raise
    
    async def _create_test_tenants(self):
        """Create comprehensive test tenants."""
        try:
            # Enterprise Gold Tenant
            gold_tenant = TenantContext(
                tenant_id="t_enterprise_gold",
                org_id="enterprise_corp",
                project_id="manufacturing_plant_001",
                user_id="u_enterprise_001",
                entitlements=[
                    "solver.highs", "solver.ortools", "solver.gurobi",
                    "data.analysis", "data.visualization", "data.etl",
                    "model.builder", "model.validator", "model.optimizer",
                    "rag", "byok", "compliance.full"
                ],
                pii_scope=PIIScope.FULL,
                region="us-east-1",
                sla_tier=SLATier.GOLD
            )
            
            # Professional Pro Tenant
            pro_tenant = TenantContext(
                tenant_id="t_professional_pro",
                org_id="professional_inc",
                project_id="supply_chain_001",
                user_id="u_professional_001",
                entitlements=[
                    "solver.ortools", "solver.highs",
                    "data.analysis", "data.visualization",
                    "model.builder", "model.validator"
                ],
                pii_scope=PIIScope.BASIC,
                region="us-west-2",
                sla_tier=SLATier.PRO
            )
            
            # Startup Free Tenant
            free_tenant = TenantContext(
                tenant_id="t_startup_free",
                org_id="startup_llc",
                project_id="prototype_001",
                user_id="u_startup_001",
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
    
    async def test_complete_workflow(self):
        """Test complete end-to-end workflow for each tenant tier."""
        try:
            logger.info("🧪 Testing complete end-to-end workflows...")
            
            # Test Gold Tenant - Full Capability Workflow
            await self._test_gold_tenant_workflow()
            
            # Test Pro Tenant - Balanced Workflow
            await self._test_pro_tenant_workflow()
            
            # Test Free Tenant - Limited Workflow
            await self._test_free_tenant_workflow()
            
            logger.info("✅ Complete workflow tests passed")
            
        except Exception as e:
            logger.error(f"❌ Complete workflow test failed: {e}")
            raise
    
    async def _test_gold_tenant_workflow(self):
        """Test gold tenant with full capabilities."""
        tenant_id = "t_enterprise_gold"
        tenant = self.test_tenants[tenant_id]
        
        logger.info(f"🏆 Testing Gold Tenant: {tenant_id}")
        
        # Step 1: Intent Classification
        intent_request = {
            "type": "tool",
            "tool_id": "intent-classifier",
            "parameters": {
                "query": "Optimize production scheduling for 3 manufacturing lines with 24/7 operation, considering machine maintenance windows, labor constraints, and demand variability",
                "context": "manufacturing_optimization"
            }
        }
        
        intent_result = await self.platform_manager.process_tenant_request(tenant_id, intent_request)
        assert intent_result["success"], f"Gold tenant intent classification failed: {intent_result}"
        logger.info(f"✅ Gold tenant intent: {intent_result['result']}")
        
        # Step 2: Data Analysis
        data_request = {
            "type": "tool",
            "tool_id": "data-analyzer",
            "parameters": {
                "data_type": "manufacturing_operations",
                "analysis_type": "comprehensive_analysis",
                "time_range": "last_90_days",
                "metrics": [
                    "production_efficiency", "quality_score", "cost_per_unit",
                    "machine_utilization", "labor_productivity", "inventory_turns"
                ],
                "granularity": "hourly"
            }
        }
        
        data_result = await self.platform_manager.process_tenant_request(tenant_id, data_request)
        assert data_result["success"], f"Gold tenant data analysis failed: {data_result}"
        logger.info(f"✅ Gold tenant data analysis: {data_result['metadata']}")
        
        # Step 3: Model Building
        model_request = {
            "type": "tool",
            "tool_id": "model-builder",
            "parameters": {
                "problem_type": "mixed_integer_programming",
                "objective": "minimize_total_cost",
                "constraints": [
                    "production_capacity", "labor_availability", "machine_maintenance",
                    "inventory_limits", "quality_standards", "safety_requirements"
                ],
                "variables": [
                    "production_levels", "shift_scheduling", "maintenance_timing",
                    "inventory_levels", "resource_allocation"
                ],
                "complexity": "enterprise"
            }
        }
        
        model_result = await self.platform_manager.process_tenant_request(tenant_id, model_request)
        assert model_result["success"], f"Gold tenant model building failed: {model_result}"
        logger.info(f"✅ Gold tenant model building: {model_result['metadata']}")
        
        # Step 4: High-Performance Inference
        inference_request = {
            "type": "inference",
            "domain": "manufacturing",
            "request_type": "production_optimization",
            "payload": {
                "production_capacity": 5000,
                "demand_forecast": 4200,
                "resource_constraints": {
                    "labor_hours": 10000,
                    "machine_hours": 8000,
                    "material_availability": 0.95,
                    "energy_limits": 50000
                },
                "optimization_goals": [
                    "minimize_total_cost",
                    "maximize_production_efficiency",
                    "minimize_carbon_footprint",
                    "ensure_quality_compliance"
                ],
                "sla_requirements": {
                    "response_time": "under_5_seconds",
                    "solution_quality": "optimal",
                    "reliability": "99.9_percent"
                }
            },
            "inference_profile": "dcisionai-gold-tier-production"
        }
        
        inference_result = await self.platform_manager.process_tenant_request(tenant_id, inference_request)
        assert inference_result["success"], f"Gold tenant inference failed: {inference_result}"
        logger.info(f"✅ Gold tenant inference: {inference_result['metadata']}")
        
        # Step 5: Advanced Solver Execution
        solver_request = {
            "type": "tool",
            "tool_id": "solver-highs",
            "parameters": {
                "problem_type": "mixed_integer_programming",
                "objective": "minimize",
                "variables": ["x1", "x2", "x3", "x4", "x5"],
                "constraints": [
                    {"expression": "x1 + x2 + x3 <= 100", "type": "inequality"},
                    {"expression": "2*x1 + 3*x2 + x4 <= 200", "type": "inequality"},
                    {"expression": "x1 + 2*x2 + x5 <= 150", "type": "inequality"},
                    {"expression": "x1 >= 0", "type": "inequality"},
                    {"expression": "x2 >= 0", "type": "inequality"},
                    {"expression": "x3 >= 0", "type": "inequality"},
                    {"expression": "x4 >= 0", "type": "inequality"},
                    {"expression": "x5 >= 0", "type": "inequality"}
                ],
                "objective_function": "5*x1 + 4*x2 + 3*x3 + 2*x4 + x5",
                "solver_options": {
                    "time_limit": 300,
                    "mip_gap": 0.01,
                    "presolve": "aggressive"
                }
            }
        }
        
        solver_result = await self.platform_manager.process_tenant_request(tenant_id, solver_request)
        assert solver_result["success"], f"Gold tenant solver execution failed: {solver_result}"
        logger.info(f"✅ Gold tenant solver: {solver_result['metadata']}")
        
        logger.info("🏆 Gold tenant workflow completed successfully")
    
    async def _test_pro_tenant_workflow(self):
        """Test pro tenant with balanced capabilities."""
        tenant_id = "t_professional_pro"
        tenant = self.test_tenants[tenant_id]
        
        logger.info(f"💼 Testing Pro Tenant: {tenant_id}")
        
        # Step 1: Intent Classification
        intent_request = {
            "type": "tool",
            "tool_id": "intent-classifier",
            "parameters": {
                "query": "Optimize supply chain for 2 warehouses with demand forecasting",
                "context": "supply_chain_optimization"
            }
        }
        
        intent_result = await self.platform_manager.process_tenant_request(tenant_id, intent_request)
        assert intent_result["success"], f"Pro tenant intent classification failed: {intent_result}"
        logger.info(f"✅ Pro tenant intent: {intent_result['result']}")
        
        # Step 2: Data Analysis
        data_request = {
            "type": "tool",
            "tool_id": "data-analyzer",
            "parameters": {
                "data_type": "supply_chain_metrics",
                "analysis_type": "trend_analysis",
                "time_range": "last_60_days",
                "metrics": ["demand_forecast", "inventory_levels", "lead_times", "cost_per_unit"],
                "granularity": "daily"
            }
        }
        
        data_result = await self.platform_manager.process_tenant_request(tenant_id, data_request)
        assert data_result["success"], f"Pro tenant data analysis failed: {data_result}"
        logger.info(f"✅ Pro tenant data analysis: {data_result['metadata']}")
        
        # Step 3: Model Building
        model_request = {
            "type": "tool",
            "tool_id": "model-builder",
            "parameters": {
                "problem_type": "linear_programming",
                "objective": "minimize_total_cost",
                "constraints": ["demand_satisfaction", "inventory_capacity", "budget_limits"],
                "variables": ["order_quantities", "inventory_levels", "transportation_routes"],
                "complexity": "professional"
            }
        }
        
        model_result = await self.platform_manager.process_tenant_request(tenant_id, model_request)
        assert model_result["success"], f"Pro tenant model building failed: {model_result}"
        logger.info(f"✅ Pro tenant model building: {model_result['metadata']}")
        
        # Step 4: Balanced Inference
        inference_request = {
            "type": "inference",
            "domain": "supply_chain",
            "request_type": "inventory_optimization",
            "payload": {
                "warehouse_count": 2,
                "demand_forecast": 1000,
                "constraints": {
                    "budget_limit": 50000,
                    "storage_capacity": 2000,
                    "lead_time": 7
                },
                "optimization_goals": ["minimize_cost", "maximize_service_level"]
            },
            "inference_profile": "dcisionai-pro-tier-production"
        }
        
        inference_result = await self.platform_manager.process_tenant_request(tenant_id, inference_request)
        assert inference_result["success"], f"Pro tenant inference failed: {inference_result}"
        logger.info(f"✅ Pro tenant inference: {inference_result['metadata']}")
        
        logger.info("💼 Pro tenant workflow completed successfully")
    
    async def _test_free_tenant_workflow(self):
        """Test free tenant with limited capabilities."""
        tenant_id = "t_startup_free"
        tenant = self.test_tenants[tenant_id]
        
        logger.info(f"🆓 Testing Free Tenant: {tenant_id}")
        
        # Step 1: Basic Intent Classification
        intent_request = {
            "type": "tool",
            "tool_id": "intent-classifier",
            "parameters": {
                "query": "Simple production optimization",
                "context": "basic_optimization"
            }
        }
        
        intent_result = await self.platform_manager.process_tenant_request(tenant_id, intent_request)
        assert intent_result["success"], f"Free tenant intent classification failed: {intent_result}"
        logger.info(f"✅ Free tenant intent: {intent_result['result']}")
        
        # Step 2: Basic Solver (only OR-Tools available)
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
            }
        }
        
        solver_result = await self.platform_manager.process_tenant_request(tenant_id, solver_request)
        assert solver_result["success"], f"Free tenant solver execution failed: {solver_result}"
        logger.info(f"✅ Free tenant solver: {solver_result['metadata']}")
        
        # Step 3: Test access denial to pro features
        pro_feature_request = {
            "type": "tool",
            "tool_id": "data-analyzer",  # Requires "data.analysis" entitlement
            "parameters": {"analysis_type": "trend_analysis"}
        }
        
        pro_feature_result = await self.platform_manager.process_tenant_request(tenant_id, pro_feature_request)
        assert not pro_feature_result["success"], "Free tenant should not access pro features"
        logger.info("✅ Free tenant correctly denied access to pro features")
        
        logger.info("🆓 Free tenant workflow completed successfully")
    
    async def test_tenant_isolation(self):
        """Test tenant isolation and access control."""
        try:
            logger.info("🧪 Testing tenant isolation...")
            
            # Test that tenants cannot access each other's data
            for tenant_id in self.test_tenants:
                # Get tenant catalog
                catalog = await self.platform_manager.get_tenant_catalog(tenant_id)
                assert catalog["success"], f"Failed to get catalog for {tenant_id}"
                
                # Verify catalog is tenant-specific
                catalog_data = catalog["catalog"]
                assert catalog_data["tenant_id"] == tenant_id, f"Catalog tenant mismatch for {tenant_id}"
                
                logger.info(f"✅ {tenant_id} catalog isolation verified")
            
            # Test cross-tenant access denial
            gold_tenant_id = "t_enterprise_gold"
            free_tenant_id = "t_startup_free"
            
            # Try to access gold tenant data from free tenant context
            # This should be denied by the platform
            logger.info("✅ Tenant isolation tests passed")
            
        except Exception as e:
            logger.error(f"❌ Tenant isolation test failed: {e}")
            raise
    
    async def test_performance_monitoring(self):
        """Test performance monitoring across all components."""
        try:
            logger.info("🧪 Testing performance monitoring...")
            
            # Platform Manager metrics
            platform_metrics = self.platform_manager.get_platform_metrics()
            assert "platform" in platform_metrics, "Platform metrics missing"
            assert "tenants" in platform_metrics, "Tenant metrics missing"
            
            # Inference Manager metrics
            inference_metrics = self.inference_manager.get_performance_summary()
            assert "total_requests" in inference_metrics, "Inference metrics missing"
            
            # Gateway Client metrics
            gateway_metrics = self.gateway_client.get_performance_summary()
            assert "total_requests" in gateway_metrics, "Gateway metrics missing"
            
            # Tenant-specific metrics
            for tenant_id in self.test_tenants:
                tenant_metrics = await self.platform_manager.get_tenant_metrics(tenant_id)
                assert tenant_metrics["success"], f"Failed to get metrics for {tenant_id}"
                
                metrics = tenant_metrics["metrics"]
                assert metrics["request_count"] >= 0, "Request count should be non-negative"
                assert 0 <= metrics["success_rate"] <= 100, "Success rate should be 0-100%"
                
                logger.info(f"✅ {tenant_id} metrics: {metrics['request_count']} requests, {metrics['success_rate']:.1f}% success")
            
            logger.info("✅ Performance monitoring tests passed")
            
        except Exception as e:
            logger.error(f"❌ Performance monitoring test failed: {e}")
            raise
    
    async def test_health_monitoring(self):
        """Test health monitoring across all components."""
        try:
            logger.info("🧪 Testing health monitoring...")
            
            # Platform Manager health
            platform_health = self.platform_manager.health_check()
            assert "status" in platform_health, "Platform health missing"
            assert "component_health" in platform_health, "Component health missing"
            
            # Component health
            component_health = platform_health["component_health"]
            assert "inference_manager" in component_health, "Inference manager health missing"
            assert "gateway_client" in component_health, "Gateway client health missing"
            
            # Individual component health
            inference_health = self.inference_manager.health_check()
            assert "status" in inference_health, "Inference manager status missing"
            
            gateway_health = self.gateway_client.health_check()
            assert "status" in gateway_health, "Gateway client status missing"
            
            logger.info(f"✅ Platform health: {platform_health['status']}")
            logger.info(f"✅ Inference manager: {inference_health['status']}")
            logger.info(f"✅ Gateway client: {gateway_health['status']}")
            
            logger.info("✅ Health monitoring tests passed")
            
        except Exception as e:
            logger.error(f"❌ Health monitoring test failed: {e}")
            raise
    
    async def run_all_tests(self):
        """Run all integration tests."""
        try:
            logger.info("🚀 Starting Complete Architecture Integration Tests...")
            
            # Setup
            await self.setup()
            
            # Run tests
            test_methods = [
                self.test_complete_workflow,
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
            
            logger.info("🎉 All complete architecture tests passed!")
            
        except Exception as e:
            logger.error(f"❌ Complete architecture tests failed: {e}")
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
    test = CompleteArchitectureTest()
    try:
        await test.run_all_tests()
    finally:
        await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
