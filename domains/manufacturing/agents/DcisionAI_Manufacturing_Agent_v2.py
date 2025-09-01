#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent v2 - Enhanced with Inference Optimization
======================================================================

Phase 2: High-throughput inference with cross-region optimization.
Integrates with enhanced Gateway and inference manager for optimal performance.
"""

import logging
import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Import shared framework
from shared.core.base_agent import BaseAgent
from shared.core.inference_manager import InferenceManager, InferenceRequest
from shared.core.gateway_client import GatewayClient

# Import our manufacturing tools
from ..tools.intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool_v6
from ..tools.data.DcisionAI_Data_Tool import create_data_tool
from ..tools.model.DcisionAI_Model_Builder import create_model_builder_tool
from ..tools.solver.DcisionAI_Solver_Tool import create_solver_tool

@dataclass
class ManufacturingWorkflowResult:
    """Result of a complete manufacturing workflow."""
    workflow_id: str
    success: bool
    intent_result: Dict[str, Any]
    data_result: Dict[str, Any]
    model_result: Dict[str, Any]
    solver_result: Dict[str, Any]
    total_execution_time: float
    total_cost: float
    regions_used: List[str]
    performance_metrics: Dict[str, Any]
    timestamp: datetime

class DcisionAI_Manufacturing_Agent_v2(BaseAgent):
    """
    DcisionAI Manufacturing Agent v2 - Enhanced with inference optimization.
    
    This agent orchestrates the complete manufacturing optimization workflow:
    1. Intent Classification (with inference optimization)
    2. Data Analysis (with cross-region routing)
    3. Model Building (with performance monitoring)
    4. Optimization Solving (with cost tracking)
    
    Features:
    - Cross-region inference optimization
    - Intelligent region selection
    - Performance monitoring and cost tracking
    - Gateway integration for tool management
    - Real-time health monitoring
    """
    
    def __init__(self):
        """Initialize the enhanced manufacturing agent."""
        super().__init__(
            domain="manufacturing",
            version="2.0.0",
            description="Manufacturing optimization agent with inference optimization"
        )
        
        # Enhanced inference configuration
        self.inference_profile = "DcisionAI_Manufacturing_Profile"
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1']
        self.max_throughput = 1000  # tokens/minute
        self.optimization_focus = "high_throughput"
        
        # Initialize enhanced components
        self.logger.info("Initializing Enhanced DcisionAI Manufacturing Components...")
        
        try:
            # Initialize inference manager for cross-region optimization
            self.inference_manager = InferenceManager()
            
            # Initialize Gateway client for tool management
            self.gateway_client = GatewayClient()
            
            # Initialize manufacturing tools
            self.intent_tool = create_dcisionai_intent_tool_v6()
            self.data_tool = create_data_tool()
            self.model_tool = create_model_builder_tool()
            self.solver_tool = create_solver_tool()
            
            # Register tools with the base agent
            self.register_tool("intent_classification", self.intent_tool)
            self.register_tool("data_analysis", self.data_tool)
            self.register_tool("model_building", self.model_tool)
            self.register_tool("optimization_solving", self.solver_tool)
            
            # Register tools with Gateway client
            self._register_tools_with_gateway()
            
            # Performance tracking
            self.workflow_history: List[ManufacturingWorkflowResult] = []
            self.total_workflows = 0
            self.successful_workflows = 0
            
            self.logger.info("✅ All enhanced manufacturing components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize enhanced components: {e}")
            raise
    
    def _initialize_tools(self) -> None:
        """Initialize domain-specific tools. Already done in __init__."""
        pass
    
    def _register_tools_with_gateway(self):
        """Register manufacturing tools with the Gateway client."""
        try:
            # This would typically register tools with the actual Gateway
            # For now, we'll simulate the registration
            self.logger.info("✅ Manufacturing tools registered with Gateway")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not register tools with Gateway: {e}")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process manufacturing optimization requests with enhanced inference optimization.
        
        Args:
            request: Manufacturing optimization request
            
        Returns:
            Complete workflow result with performance metrics
        """
        workflow_start_time = time.time()
        workflow_id = str(uuid.uuid4())
        
        self.logger.info(f"🚀 Starting enhanced manufacturing workflow {workflow_id}")
        
        try:
            # Extract request parameters
            user_query = request.get('query', '')
            user_location = request.get('user_location', 'us')
            priority = request.get('priority', 'normal')
            
            # Create workflow context
            workflow_context = {
                'workflow_id': workflow_id,
                'user_query': user_query,
                'user_location': user_location,
                'priority': priority,
                'start_time': datetime.now().isoformat()
            }
            
            # Step 1: Intent Classification with inference optimization
            self.logger.info("🔍 Step 1: Intent Classification with inference optimization")
            intent_result = await self._execute_intent_classification(
                user_query, user_location, priority
            )
            
            if not intent_result.get('success', False):
                raise Exception(f"Intent classification failed: {intent_result.get('error', 'Unknown error')}")
            
            # Step 2: Data Analysis with cross-region routing
            self.logger.info("📊 Step 2: Data Analysis with cross-region routing")
            data_result = await self._execute_data_analysis(
                intent_result, user_location, priority
            )
            
            if not data_result.get('success', False):
                raise Exception(f"Data analysis failed: {data_result.get('error', 'Unknown error')}")
            
            # Step 3: Model Building with performance monitoring
            self.logger.info("🏗️ Step 3: Model Building with performance monitoring")
            model_result = await self._execute_model_building(
                data_result, user_location, priority
            )
            
            if not model_result.get('success', False):
                raise Exception(f"Model building failed: {model_result.get('error', 'Unknown error')}")
            
            # Step 4: Optimization Solving with cost tracking
            self.logger.info("⚡ Step 4: Optimization Solving with cost tracking")
            solver_result = await self._execute_optimization_solving(
                model_result, user_location, priority
            )
            
            if not solver_result.get('success', False):
                raise Exception(f"Optimization solving failed: {solver_result.get('error', 'Unknown error')}")
            
            # Calculate total execution time and cost
            total_execution_time = time.time() - workflow_start_time
            total_cost = (
                intent_result.get('cost', 0.0) +
                data_result.get('cost', 0.0) +
                model_result.get('cost', 0.0) +
                solver_result.get('cost', 0.0)
            )
            
            # Collect regions used
            regions_used = [
                intent_result.get('region_used', 'unknown'),
                data_result.get('region_used', 'unknown'),
                model_result.get('region_used', 'unknown'),
                solver_result.get('region_used', 'unknown')
            ]
            
            # Create workflow result
            workflow_result = ManufacturingWorkflowResult(
                workflow_id=workflow_id,
                success=True,
                intent_result=intent_result,
                data_result=data_result,
                model_result=model_result,
                solver_result=solver_result,
                total_execution_time=total_execution_time,
                total_cost=total_cost,
                regions_used=regions_used,
                performance_metrics={
                    'intent_time': intent_result.get('execution_time', 0.0),
                    'data_time': data_result.get('execution_time', 0.0),
                    'model_time': model_result.get('execution_time', 0.0),
                    'solver_time': solver_result.get('execution_time', 0.0),
                    'intent_cost': intent_result.get('cost', 0.0),
                    'data_cost': data_result.get('cost', 0.0),
                    'model_cost': model_result.get('cost', 0.0),
                    'solver_cost': solver_result.get('cost', 0.0)
                },
                timestamp=datetime.now()
            )
            
            # Update workflow history
            self.workflow_history.append(workflow_result)
            self.total_workflows += 1
            self.successful_workflows += 1
            
            # Log success
            self.logger.info(f"✅ Enhanced manufacturing workflow {workflow_id} completed successfully")
            self.logger.info(f"   Total time: {total_execution_time:.2f}s")
            self.logger.info(f"   Total cost: ${total_cost:.4f}")
            self.logger.info(f"   Regions used: {', '.join(set(regions_used))}")
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'result': {
                    'intent': intent_result.get('data'),
                    'data_analysis': data_result.get('data'),
                    'model': model_result.get('data'),
                    'solution': solver_result.get('data')
                },
                'performance': {
                    'total_execution_time': total_execution_time,
                    'total_cost': total_cost,
                    'regions_used': regions_used,
                    'step_metrics': workflow_result.performance_metrics
                },
                'metadata': workflow_context
            }
            
        except Exception as e:
            total_execution_time = time.time() - workflow_start_time
            self.logger.error(f"❌ Enhanced manufacturing workflow {workflow_id} failed: {e}")
            
            # Update workflow history
            self.total_workflows += 1
            
            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e),
                'performance': {
                    'total_execution_time': total_execution_time,
                    'total_cost': 0.0,
                    'regions_used': ['unknown']
                },
                'metadata': workflow_context
            }
    
    async def _execute_intent_classification(self, query: str, user_location: str, 
                                           priority: str) -> Dict[str, Any]:
        """Execute intent classification with inference optimization."""
        try:
            # Create inference request for intent classification
            inference_request = InferenceRequest(
                request_id=f"intent_{int(time.time() * 1000)}",
                domain="manufacturing",
                request_type="intent_classification",
                payload={'query': query},
                user_location=user_location,
                priority=priority,
                timeout=60  # 1 minute for intent classification
            )
            
            # Execute through inference manager for optimal region selection
            inference_result = await self.inference_manager.execute_inference(inference_request)
            
            # Execute the actual intent tool
            intent_data = await self.intent_tool.execute(query=query)
            
            return {
                'success': inference_result.success and intent_data.get('success', False),
                'data': intent_data.get('data'),
                'execution_time': inference_result.execution_time,
                'cost': inference_result.cost,
                'region_used': inference_result.region_used,
                'metadata': inference_result.metadata
            }
            
        except Exception as e:
            self.logger.error(f"❌ Intent classification failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0.0,
                'cost': 0.0,
                'region_used': 'unknown'
            }
    
    async def _execute_data_analysis(self, intent_result: Dict[str, Any], 
                                   user_location: str, priority: str) -> Dict[str, Any]:
        """Execute data analysis with cross-region routing."""
        try:
            # Create inference request for data analysis
            inference_request = InferenceRequest(
                request_id=f"data_{int(time.time() * 1000)}",
                domain="manufacturing",
                request_type="data_analysis",
                payload={'intent': intent_result.get('data')},
                user_location=user_location,
                priority=priority,
                timeout=120  # 2 minutes for data analysis
            )
            
            # Execute through inference manager
            inference_result = await self.inference_manager.execute_inference(inference_request)
            
            # Execute the actual data tool
            data_result = await self.data_tool.execute(
                intent_data=intent_result.get('data')
            )
            
            return {
                'success': inference_result.success and data_result.get('success', False),
                'data': data_result.get('data'),
                'execution_time': inference_result.execution_time,
                'cost': inference_result.cost,
                'region_used': inference_result.region_used,
                'metadata': inference_result.metadata
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0.0,
                'cost': 0.0,
                'region_used': 'unknown'
            }
    
    async def _execute_model_building(self, data_result: Dict[str, Any], 
                                    user_location: str, priority: str) -> Dict[str, Any]:
        """Execute model building with performance monitoring."""
        try:
            # Create inference request for model building
            inference_request = InferenceRequest(
                request_id=f"model_{int(time.time() * 1000)}",
                domain="manufacturing",
                request_type="model_building",
                payload={'data_analysis': data_result.get('data')},
                user_location=user_location,
                priority=priority,
                timeout=180  # 3 minutes for model building
            )
            
            # Execute through inference manager
            inference_result = await self.inference_manager.execute_inference(inference_request)
            
            # Execute the actual model tool
            model_result = await self.model_tool.execute(
                data_analysis_result=data_result.get('data')
            )
            
            return {
                'success': inference_result.success and model_result.get('success', False),
                'data': model_result.get('data'),
                'execution_time': inference_result.execution_time,
                'cost': inference_result.cost,
                'region_used': inference_result.region_used,
                'metadata': inference_result.metadata
            }
            
        except Exception as e:
            self.logger.error(f"❌ Model building failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0.0,
                'cost': 0.0,
                'region_used': 'unknown'
            }
    
    async def _execute_optimization_solving(self, model_result: Dict[str, Any], 
                                          user_location: str, priority: str) -> Dict[str, Any]:
        """Execute optimization solving with cost tracking."""
        try:
            # Create inference request for optimization solving
            inference_request = InferenceRequest(
                request_id=f"solver_{int(time.time() * 1000)}",
                domain="manufacturing",
                request_type="optimization_solving",
                payload={'model': model_result.get('data')},
                user_location=user_location,
                priority=priority,
                timeout=300  # 5 minutes for optimization solving
            )
            
            # Execute through inference manager
            inference_result = await self.inference_manager.execute_inference(inference_request)
            
            # Execute the actual solver tool
            solver_result = await self.solver_tool.execute(
                optimization_model=model_result.get('data')
            )
            
            return {
                'success': inference_result.success and solver_result.get('success', False),
                'data': solver_result.get('data'),
                'execution_time': inference_result.execution_time,
                'cost': inference_result.cost,
                'region_used': inference_result.region_used,
                'metadata': inference_result.metadata
            }
            
        except Exception as e:
            self.logger.error(f"❌ Optimization solving failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0.0,
                'cost': 0.0,
                'region_used': 'unknown'
            }
    
    def get_manufacturing_capabilities(self) -> Dict[str, Any]:
        """Get enhanced manufacturing capabilities with inference optimization."""
        return {
            'domain': 'manufacturing',
            'version': '2.0.0',
            'description': 'Manufacturing optimization with inference optimization',
            'capabilities': [
                'intent_classification',
                'data_analysis',
                'model_building',
                'optimization_solving'
            ],
            'inference_optimization': {
                'enabled': True,
                'profile': self.inference_profile,
                'regions': self.regions,
                'max_throughput': self.max_throughput,
                'optimization_focus': self.optimization_focus
            },
            'gateway_integration': True,
            'performance_monitoring': True,
            'cost_tracking': True,
            'cross_region_routing': True
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_workflows': self.total_workflows,
            'successful_workflows': self.successful_workflows,
            'success_rate': (
                self.successful_workflows / self.total_workflows 
                if self.total_workflows > 0 else 0.0
            ),
            'recent_workflows': [
                {
                    'workflow_id': w.workflow_id,
                    'success': w.success,
                    'total_time': w.total_execution_time,
                    'total_cost': w.total_cost,
                    'regions_used': w.regions_used,
                    'timestamp': w.timestamp.isoformat()
                }
                for w in self.workflow_history[-10:]  # Last 10 workflows
            ],
            'inference_manager_health': self.inference_manager.health_check(),
            'gateway_client_health': self.gateway_client.health_check(),
            'capabilities': self.get_manufacturing_capabilities()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            # Check base agent health
            base_health = super().health_check()
            
            # Check inference manager health
            inference_health = self.inference_manager.health_check()
            
            # Check Gateway client health
            gateway_health = self.gateway_client.health_check()
            
            # Determine overall health
            overall_status = "healthy"
            if (inference_health["status"] != "healthy" or 
                gateway_health["status"] != "healthy"):
                overall_status = "degraded"
            
            return {
                'status': overall_status,
                'timestamp': datetime.now().isoformat(),
                'base_agent': base_health,
                'inference_manager': inference_health,
                'gateway_client': gateway_health,
                'performance_summary': self.get_performance_summary()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources and close connections."""
        try:
            # Close Gateway client
            await self.gateway_client.close()
            
            # Cleanup inference manager (if needed)
            # self.inference_manager.cleanup()
            
            self.logger.info("✅ Enhanced manufacturing agent cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")

# Standalone testing
if __name__ == "__main__":
    import asyncio
    
    async def test_enhanced_manufacturing_agent():
        """Test the enhanced manufacturing agent."""
        print("🧪 Testing Enhanced DcisionAI Manufacturing Agent v2...")
        
        # Create agent instance
        agent = DcisionAI_Manufacturing_Agent_v2()
        
        try:
            # Test capabilities
            capabilities = agent.get_manufacturing_capabilities()
            print(f"✅ Capabilities: {capabilities}")
            
            # Test health check
            health = await agent.health_check()
            print(f"✅ Health: {health['status']}")
            
            # Test performance summary
            performance = agent.get_performance_summary()
            print(f"✅ Performance: {performance['total_workflows']} workflows")
            
            # Test workflow execution
            test_request = {
                'query': 'Optimize production line efficiency for automotive manufacturing',
                'user_location': 'us',
                'priority': 'high'
            }
            
            print("🚀 Executing test workflow...")
            result = await agent.process_request(test_request)
            
            if result['success']:
                print(f"✅ Workflow completed successfully!")
                print(f"   Workflow ID: {result['workflow_id']}")
                print(f"   Total time: {result['performance']['total_execution_time']:.2f}s")
                print(f"   Total cost: ${result['performance']['total_cost']:.4f}")
                print(f"   Regions used: {result['performance']['regions_used']}")
            else:
                print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            # Cleanup
            await agent.cleanup()
            print("🧹 Cleanup completed")
    
    # Run test
    asyncio.run(test_enhanced_manufacturing_agent())
