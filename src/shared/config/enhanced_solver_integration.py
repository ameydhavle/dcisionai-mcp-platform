"""
Enhanced Solver Integration for Strands Architecture
===================================================

Integrates the existing solver tool with enhanced multi-solver swarm capabilities
while maintaining backward compatibility with current solver tool interfaces.

This integration layer:
1. Updates existing solver agent to use enhanced multi-solver capabilities
2. Ensures backward compatibility with current solver tool interfaces  
3. Integrates with AgentCore Memory for swarm state and performance data storage
4. Connects with AgentCore Observability for comprehensive swarm execution monitoring

Requirements: 9.1, 9.2, 9.3, 9.4
"""

import logging
import asyncio
import uuid
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import asdict

try:
    from strands import Agent
    from strands_tools import memory, retrieve, use_aws, think, use_llm
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

try:
    from ..utils.base import BaseTool, ToolExecutionError, ToolInitializationError
except ImportError:
    from tools.base import BaseTool, ToolExecutionError, ToolInitializationError

try:
    from .solver_tool import SolverTool, SolverResult, ModelSpecification
except ImportError:
    from tools.solver_tool import SolverTool, SolverResult, ModelSpecification

try:
    from .enhanced_solver_registry import EnhancedSolverRegistry
except ImportError:
    from tools.enhanced_solver_registry import EnhancedSolverRegistry

try:
    from .intelligent_solver_selector import IntelligentSolverSelector, ProblemCharacteristics
except ImportError:
    from tools.intelligent_solver_selector import IntelligentSolverSelector, ProblemCharacteristics

try:
    from .solver_swarm_orchestrator import SolverSwarmOrchestrator, SwarmPattern
except ImportError:
    from tools.solver_swarm_orchestrator import SolverSwarmOrchestrator, SwarmPattern

try:
    from .swarm_state_manager import SwarmStateManager, SwarmExecutionState
except ImportError:
    from tools.swarm_state_manager import SwarmStateManager, SwarmExecutionState

try:
    from .solution_comparator import SolutionComparator, ComparisonWeights
except ImportError:
    from tools.solution_comparator import SolutionComparator, ComparisonWeights

try:
    from .performance_analyzer import PerformanceAnalyzer
except ImportError:
    from tools.performance_analyzer import PerformanceAnalyzer

try:
    from .error_recovery_manager import ErrorRecoveryManager
except ImportError:
    from tools.error_recovery_manager import ErrorRecoveryManager

logger = logging.getLogger(__name__)


class EnhancedSolverIntegration(BaseTool):
    """
    Integration layer that enhances the existing solver tool with multi-solver
    swarm capabilities while maintaining backward compatibility.
    """
    
    def __init__(self):
        super().__init__(
            name="enhanced_solver_integration",
            description="Enhanced solver integration with multi-solver swarm capabilities",
            version="1.0.0"
        )
        
        # Legacy solver tool for backward compatibility
        self.legacy_solver_tool = SolverTool()
        
        # Enhanced multi-solver components
        self.solver_registry = EnhancedSolverRegistry()
        self.solver_selector = IntelligentSolverSelector(self.solver_registry)
        self.swarm_orchestrator = SolverSwarmOrchestrator()
        self.swarm_state_manager = SwarmStateManager()
        self.solution_comparator = SolutionComparator()
        self.performance_analyzer = PerformanceAnalyzer()
        self.error_recovery_manager = ErrorRecoveryManager()
        
        # Strands integration
        self.strands_agent = None
        self.strands_tools = {}
        
        # Configuration
        self.enable_swarm_for_critical = True
        self.enable_intelligent_selection = True
        self.enable_performance_learning = True
        self.swarm_threshold_priority = "high"  # Use swarm for high+ priority problems
        
        # Performance tracking
        self.integration_metrics = {
            "total_requests": 0,
            "swarm_requests": 0,
            "legacy_requests": 0,
            "performance_improvements": [],
            "backward_compatibility_maintained": True
        }
    
    async def initialize(self) -> bool:
        """Initialize the Enhanced Solver Integration"""
        try:
            # Initialize legacy solver tool
            legacy_init = await self.legacy_solver_tool.initialize()
            if not legacy_init:
                self.logger.warning("Legacy solver tool initialization failed")
            
            # Initialize enhanced components
            registry_init = await self._initialize_enhanced_components()
            if not registry_init:
                self.logger.error("Enhanced components initialization failed")
                return False
            
            # Initialize Strands integration
            await self._initialize_strands_integration()
            
            # Initialize AgentCore integration
            await self._initialize_agentcore_integration()
            
            self._initialized = True
            self.logger.info("Enhanced Solver Integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Enhanced Solver Integration: {e}")
            return False
    
    async def _initialize_enhanced_components(self) -> bool:
        """Initialize all enhanced multi-solver components"""
        try:
            # Initialize components in dependency order
            components = [
                ("solver_registry", self.solver_registry),
                ("solver_selector", self.solver_selector),
                ("swarm_state_manager", self.swarm_state_manager),
                ("solution_comparator", self.solution_comparator),
                ("performance_analyzer", self.performance_analyzer),
                ("error_recovery_manager", self.error_recovery_manager),
                ("swarm_orchestrator", self.swarm_orchestrator)
            ]
            
            for name, component in components:
                if hasattr(component, 'initialize'):
                    success = await component.initialize()
                    if not success:
                        self.logger.error(f"Failed to initialize {name}")
                        return False
                    self.logger.debug(f"Initialized {name} successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing enhanced components: {e}")
            return False
    
    async def _initialize_strands_integration(self):
        """Initialize Strands tools integration for enhanced capabilities"""
        if not STRANDS_AVAILABLE:
            self.logger.warning("Strands not available - enhanced features limited")
            return
        
        try:
            self.strands_agent = Agent(
                name="enhanced_solver_integration",
                system_prompt="""You are an enhanced solver integration coordinator with comprehensive multi-solver capabilities.
                
                Your responsibilities:
                1. Coordinate between legacy solver interfaces and enhanced multi-solver capabilities
                2. Make intelligent decisions about when to use swarm vs single solver approaches
                3. Monitor and analyze solver performance across different problem types
                4. Manage AgentCore Memory integration for swarm state and performance data
                5. Provide comprehensive observability and monitoring insights
                
                INTEGRATION CAPABILITIES:
                - Backward compatibility with existing solver tool interfaces
                - Intelligent solver selection based on problem analysis
                - Multi-solver swarm orchestration for critical problems
                - Real-time performance monitoring and analytics
                - AgentCore Memory integration for state management
                - Comprehensive error recovery and fallback mechanisms
                
                Always maintain backward compatibility while leveraging enhanced capabilities when beneficial.
                Store comprehensive performance data in memory for continuous learning and improvement.""",
                tools=[memory, retrieve, use_aws, think, use_llm]
            )
            
            self.strands_tools = {
                'memory': self.strands_agent.tool.memory,
                'retrieve': self.strands_agent.tool.retrieve,
                'use_aws': self.strands_agent.tool.use_aws,
                'think': self.strands_agent.tool.think,
                'use_llm': self.strands_agent.tool.use_llm
            }
            
            self.logger.info("Strands integration initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Strands integration initialization failed: {e}")
            self.strands_agent = None
            self.strands_tools = {}
    
    async def _initialize_agentcore_integration(self):
        """Initialize AgentCore Memory and Observability integration"""
        try:
            # Store integration configuration in AgentCore Memory
            if self.strands_tools.get('memory'):
                integration_config = {
                    "integration_type": "enhanced_solver_integration",
                    "components": [
                        "legacy_solver_tool",
                        "enhanced_solver_registry", 
                        "intelligent_solver_selector",
                        "solver_swarm_orchestrator",
                        "swarm_state_manager",
                        "solution_comparator",
                        "performance_analyzer",
                        "error_recovery_manager"
                    ],
                    "capabilities": [
                        "backward_compatibility",
                        "intelligent_selection",
                        "swarm_orchestration",
                        "performance_analytics",
                        "error_recovery"
                    ],
                    "agentcore_features": [
                        "memory_integration",
                        "observability_monitoring",
                        "identity_management",
                        "runtime_scaling"
                    ]
                }
                
                self.strands_tools['memory'](
                    action="store",
                    content=f"Enhanced solver integration configuration: {integration_config}",
                    metadata={
                        "type": "integration_config",
                        "component": "enhanced_solver_integration",
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            self.logger.info("AgentCore integration initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"AgentCore integration initialization failed: {e}")
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Enhanced execute method that intelligently routes between legacy and enhanced capabilities
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Track request
            self.integration_metrics["total_requests"] += 1
            
            # Determine execution strategy
            execution_strategy = await self._determine_execution_strategy(kwargs)
            
            # Store request start in AgentCore Memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Enhanced solver request started: {request_id}",
                    metadata={
                        "type": "solver_request_start",
                        "request_id": request_id,
                        "strategy": execution_strategy,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            # Execute based on strategy
            if execution_strategy == "enhanced_swarm":
                result = await self._execute_enhanced_swarm(**kwargs)
                self.integration_metrics["swarm_requests"] += 1
            elif execution_strategy == "enhanced_single":
                result = await self._execute_enhanced_single(**kwargs)
            else:  # legacy
                result = await self._execute_legacy(**kwargs)
                self.integration_metrics["legacy_requests"] += 1
            
            execution_time = time.time() - start_time
            
            # Store result in AgentCore Memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Enhanced solver request completed: {request_id}",
                    metadata={
                        "type": "solver_request_complete",
                        "request_id": request_id,
                        "strategy": execution_strategy,
                        "execution_time": execution_time,
                        "success": result.get("success", False),
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            # Add integration metadata
            result["integration_metadata"] = {
                "request_id": request_id,
                "execution_strategy": execution_strategy,
                "execution_time": execution_time,
                "enhanced_features_used": execution_strategy != "legacy",
                "backward_compatibility_maintained": True
            }
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Enhanced solver integration failed: {str(e)}"
            
            # Store error in AgentCore Memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Enhanced solver request failed: {request_id}",
                    metadata={
                        "type": "solver_request_error",
                        "request_id": request_id,
                        "error": str(e),
                        "execution_time": execution_time,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            # Attempt error recovery
            recovery_result = await self._attempt_error_recovery(kwargs, str(e))
            if recovery_result:
                return recovery_result
            
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _determine_execution_strategy(self, kwargs: Dict[str, Any]) -> str:
        """Determine the optimal execution strategy based on request characteristics"""
        try:
            # Check if enhanced features are disabled
            if not self.enable_intelligent_selection:
                return "legacy"
            
            # Analyze problem characteristics
            problem_data = kwargs.get("problem_data", {})
            priority = problem_data.get("priority", "medium")
            problem_type = problem_data.get("problem_type", "linear_programming")
            
            # Use swarm for critical/high priority problems
            if (self.enable_swarm_for_critical and 
                priority in ["critical", "high"] and
                priority >= self.swarm_threshold_priority):
                return "enhanced_swarm"
            
            # Use enhanced single solver for medium priority
            if priority in ["medium", "high"]:
                return "enhanced_single"
            
            # Use legacy for low priority or simple problems
            return "legacy"
            
        except Exception as e:
            self.logger.warning(f"Error determining execution strategy: {e}")
            return "legacy"  # Safe fallback
    
    async def _execute_enhanced_swarm(self, **kwargs) -> Dict[str, Any]:
        """Execute using enhanced multi-solver swarm capabilities"""
        try:
            problem_data = kwargs.get("problem_data", {})
            swarm_pattern = kwargs.get("swarm_pattern", "competitive")
            solver_count = kwargs.get("solver_count", 3)
            
            # Extract model_spec from problem_data for swarm orchestrator
            model_spec = problem_data.get("model_spec")
            if not model_spec:
                raise ValueError("model_spec is required in problem_data")
            
            # Use swarm orchestrator for enhanced solving
            result = await self.swarm_orchestrator.execute(
                operation="orchestrate_swarm",
                model_spec=model_spec,
                pattern=swarm_pattern,
                solver_count=solver_count,
                timeout=problem_data.get("timeout", 300)
            )
            
            # Enhance result with performance analysis
            if result.get("success") and self.enable_performance_learning:
                performance_analysis = await self.performance_analyzer.execute(
                    operation="analyze_swarm_performance",
                    swarm_result=result
                )
                result["performance_analysis"] = performance_analysis
            
            result["execution_method"] = "enhanced_swarm"
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced swarm execution failed: {e}")
            # Fallback to enhanced single solver
            return await self._execute_enhanced_single(**kwargs)
    
    async def _execute_enhanced_single(self, **kwargs) -> Dict[str, Any]:
        """Execute using enhanced single solver selection"""
        try:
            problem_data = kwargs.get("problem_data", {})
            
            # Extract model_spec from problem_data
            model_spec = problem_data.get("model_spec")
            if not model_spec:
                raise ValueError("model_spec is required in problem_data")
            
            # Use intelligent solver selection
            solver_selection = self.solver_selector.select_optimal_solver(problem_data)
            
            # Execute with selected solver using proper parameters
            result = await self.legacy_solver_tool.execute(
                operation="solve",
                model_spec=model_spec,
                solver_preference=solver_selection.primary_solver,
                timeout=problem_data.get("timeout", 300)
            )
            
            # Enhance result with selection information
            result["solver_selection"] = {
                "primary_solver": solver_selection.primary_solver,
                "backup_solvers": solver_selection.backup_solvers,
                "selection_rationale": solver_selection.selection_rationale,
                "confidence_score": solver_selection.confidence_score
            }
            
            result["execution_method"] = "enhanced_single"
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced single execution failed: {e}")
            # Fallback to legacy
            return await self._execute_legacy(**kwargs)
    
    async def _execute_legacy(self, **kwargs) -> Dict[str, Any]:
        """Execute using legacy solver tool for backward compatibility"""
        try:
            problem_data = kwargs.get("problem_data", {})
            
            # Extract model_spec from problem_data
            model_spec = problem_data.get("model_spec")
            if not model_spec:
                raise ValueError("model_spec is required in problem_data")
            
            # Execute with legacy solver using proper parameters
            result = await self.legacy_solver_tool.execute(
                operation="solve",
                model_spec=model_spec,
                timeout=problem_data.get("timeout", 300)
            )
            result["execution_method"] = "legacy"
            return result
            
        except Exception as e:
            self.logger.error(f"Legacy execution failed: {e}")
            raise ToolExecutionError(f"All execution methods failed: {str(e)}", self.name)
    
    async def _attempt_error_recovery(self, kwargs: Dict[str, Any], error: str) -> Optional[Dict[str, Any]]:
        """Attempt error recovery using the error recovery manager"""
        try:
            recovery_result = await self.error_recovery_manager.execute(
                operation="recover_from_error",
                original_request=kwargs,
                error_message=error
            )
            
            if recovery_result.get("success"):
                self.logger.info("Error recovery successful")
                return recovery_result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error recovery failed: {e}")
            return None
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status and metrics"""
        try:
            # Get component status
            component_status = {}
            components = [
                ("legacy_solver_tool", self.legacy_solver_tool),
                ("solver_registry", self.solver_registry),
                ("solver_selector", self.solver_selector),
                ("swarm_orchestrator", self.swarm_orchestrator),
                ("swarm_state_manager", self.swarm_state_manager),
                ("solution_comparator", self.solution_comparator),
                ("performance_analyzer", self.performance_analyzer),
                ("error_recovery_manager", self.error_recovery_manager)
            ]
            
            for name, component in components:
                component_status[name] = {
                    "initialized": getattr(component, '_initialized', False),
                    "available": component is not None
                }
            
            # Get solver availability
            available_solvers = []
            for solver_name in self.solver_registry.solvers:
                if self.solver_registry.check_solver_availability(solver_name):
                    available_solvers.append(solver_name)
            
            return {
                "integration_status": "active",
                "backward_compatibility": True,
                "enhanced_features_enabled": self.enable_intelligent_selection,
                "swarm_capabilities_enabled": self.enable_swarm_for_critical,
                "component_status": component_status,
                "available_solvers": available_solvers,
                "solver_count": len(available_solvers),
                "strands_integration": self.strands_agent is not None,
                "agentcore_integration": bool(self.strands_tools),
                "performance_metrics": self.integration_metrics,
                "configuration": {
                    "enable_swarm_for_critical": self.enable_swarm_for_critical,
                    "enable_intelligent_selection": self.enable_intelligent_selection,
                    "enable_performance_learning": self.enable_performance_learning,
                    "swarm_threshold_priority": self.swarm_threshold_priority
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            return {
                "integration_status": "error",
                "error": str(e)
            }
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters for enhanced solver integration"""
        try:
            # Validate required parameters
            if "problem_data" not in kwargs:
                return False
            
            problem_data = kwargs["problem_data"]
            if not isinstance(problem_data, dict):
                return False
            
            # Validate optional parameters
            if "swarm_pattern" in kwargs:
                valid_patterns = ["competitive", "collaborative", "peer_to_peer"]
                if kwargs["swarm_pattern"] not in valid_patterns:
                    return False
            
            if "solver_count" in kwargs:
                solver_count = kwargs["solver_count"]
                if not isinstance(solver_count, int) or solver_count < 1 or solver_count > 10:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation failed: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources and store final metrics"""
        try:
            # Store final integration metrics in AgentCore Memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Enhanced solver integration final metrics: {self.integration_metrics}",
                    metadata={
                        "type": "integration_metrics",
                        "component": "enhanced_solver_integration",
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            # Cleanup components
            components = [
                self.legacy_solver_tool,
                self.swarm_orchestrator,
                self.swarm_state_manager,
                self.solution_comparator,
                self.performance_analyzer,
                self.error_recovery_manager
            ]
            
            for component in components:
                if hasattr(component, 'cleanup'):
                    await component.cleanup()
            
            self.logger.info("Enhanced Solver Integration cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Factory function for creating enhanced solver integration
async def create_enhanced_solver_integration() -> EnhancedSolverIntegration:
    """Create and initialize enhanced solver integration"""
    integration = EnhancedSolverIntegration()
    await integration.initialize()
    return integration


# Backward compatibility wrapper
class EnhancedSolverTool(EnhancedSolverIntegration):
    """Backward compatibility wrapper that maintains the SolverTool interface"""
    
    def __init__(self):
        super().__init__()
        # Maintain backward compatibility by aliasing methods
        self.solve = self.execute
        self.get_solver_info = self.get_integration_status