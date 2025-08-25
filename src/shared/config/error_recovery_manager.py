"""
Error Recovery Manager for Multi-Solver Swarm Optimization
=========================================================

Comprehensive error handling and recovery system providing:
- ErrorRecoveryManager class for comprehensive error handling
- Automatic retry logic with alternative solver fallback
- Circuit breaker patterns for resource protection and system stability
- Partial result recovery and checkpoint-based resumption capabilities

Requirements: 7.1, 7.2, 7.3, 7.4
"""

import logging
import asyncio
import time
import threading
import uuid
import json
import pickle
import os
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import traceback

try:
    from strands import Agent
    from strands_tools import memory, retrieve, use_aws, think, use_llm
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

from ..utils.base import BaseTool, ToolExecutionError, ToolInitializationError
from .solver_tool import SolverResult, ModelSpecification
from .enhanced_solver_registry import EnhancedSolverRegistry
from .intelligent_solver_selector import IntelligentSolverSelector

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur in solver operations"""
    SOLVER_UNAVAILABLE = "solver_unavailable"
    SOLVER_EXECUTION_FAILURE = "solver_execution_failure"
    TIMEOUT = "timeout"
    MEMORY_EXHAUSTION = "memory_exhaustion"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    DATA_ERROR = "data_error"
    SWARM_COORDINATION_FAILURE = "swarm_coordination_failure"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStrategy(Enum):
    """Available recovery strategies"""
    RETRY_SAME_SOLVER = "retry_same_solver"
    RETRY_WITH_FALLBACK_CONFIG = "retry_with_fallback_config"
    SWITCH_TO_ALTERNATIVE_SOLVER = "switch_to_alternative_solver"
    PARTIAL_RESULT_RECOVERY = "partial_result_recovery"
    CHECKPOINT_RESUMPTION = "checkpoint_resumption"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    CIRCUIT_BREAKER_ACTIVATION = "circuit_breaker_activation"
    ABORT_OPERATION = "abort_operation"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class ErrorContext:
    """Context information for error analysis and recovery"""
    error_id: str
    error_type: ErrorType
    error_message: str
    exception: Optional[Exception]
    timestamp: datetime
    
    # Operation context
    operation: str
    solver_name: Optional[str]
    problem_id: Optional[str]
    swarm_id: Optional[str]
    
    # Error details
    stack_trace: str
    error_data: Dict[str, Any]
    
    # Recovery context
    retry_count: int = 0
    max_retries: int = 3
    recovery_attempts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['error_type'] = self.error_type.value
        result['timestamp'] = self.timestamp.isoformat()
        result['exception'] = str(self.exception) if self.exception else None
        return result


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5      # Number of failures to open circuit
    recovery_timeout: int = 60      # Seconds before attempting recovery
    success_threshold: int = 3      # Successful calls to close circuit
    monitoring_window: int = 300    # Seconds for failure rate calculation


@dataclass
class CircuitBreaker:
    """Circuit breaker for resource protection"""
    name: str
    config: CircuitBreakerConfig
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    
    # State tracking
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    
    # Monitoring
    recent_failures: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_successes: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def record_success(self):
        """Record successful operation"""
        now = datetime.now()
        self.success_count += 1
        self.last_success_time = now
        self.recent_successes.append(now)
        
        # Reset failure count on success
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit breaker {self.name} closed after recovery")
    
    def record_failure(self):
        """Record failed operation"""
        now = datetime.now()
        self.failure_count += 1
        self.last_failure_time = now
        self.recent_failures.append(now)
        
        # Check if circuit should open
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker {self.name} opened due to {self.failure_count} failures")
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Return to open state on failure during recovery
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker {self.name} returned to open state")
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        now = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (self.last_failure_time and 
                (now - self.last_failure_time).total_seconds() >= self.config.recovery_timeout):
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info(f"Circuit breaker {self.name} entering half-open state")
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def get_failure_rate(self) -> float:
        """Calculate recent failure rate"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.config.monitoring_window)
        
        recent_failures = sum(1 for f in self.recent_failures if f >= window_start)
        recent_successes = sum(1 for s in self.recent_successes if s >= window_start)
        
        total_operations = recent_failures + recent_successes
        if total_operations == 0:
            return 0.0
        
        return recent_failures / total_operations


@dataclass
class Checkpoint:
    """Checkpoint for resuming operations"""
    checkpoint_id: str
    operation: str
    timestamp: datetime
    
    # State data
    problem_data: Dict[str, Any]
    solver_state: Dict[str, Any]
    intermediate_results: List[SolverResult]
    progress: float
    
    # Recovery metadata
    solver_name: str
    swarm_id: Optional[str]
    configuration: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['intermediate_results'] = [asdict(r) for r in self.intermediate_results]
        return result


class ErrorRecoveryManager(BaseTool):
    """
    Comprehensive error handling and recovery system for multi-solver operations.
    Provides automatic retry logic, circuit breaker patterns, and checkpoint-based recovery.
    """
    
    def __init__(self):
        super().__init__(
            name="error_recovery_manager",
            description="Comprehensive error handling and recovery system for solver operations",
            version="1.0.0"
        )
        
        # Core components
        self.solver_registry = EnhancedSolverRegistry()
        self.solver_selector = IntelligentSolverSelector(self.solver_registry)
        
        # Circuit breakers for different resources
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Error tracking
        self.error_history: List[ErrorContext] = []
        self.recovery_statistics = defaultdict(int)
        
        # Checkpoints
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.checkpoint_storage_path = "data/checkpoints"
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Strands integration
        self.strands_agent = None
        self.strands_tools = {}
        
        # Configuration
        self.max_error_history = 1000
        self.default_retry_config = {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "exponential_backoff": True,
            "jitter": True
        }
        
        # Recovery strategies mapping
        self.error_recovery_strategies = {
            ErrorType.SOLVER_UNAVAILABLE: [
                RecoveryStrategy.SWITCH_TO_ALTERNATIVE_SOLVER,
                RecoveryStrategy.GRACEFUL_DEGRADATION
            ],
            ErrorType.SOLVER_EXECUTION_FAILURE: [
                RecoveryStrategy.RETRY_WITH_FALLBACK_CONFIG,
                RecoveryStrategy.SWITCH_TO_ALTERNATIVE_SOLVER,
                RecoveryStrategy.PARTIAL_RESULT_RECOVERY
            ],
            ErrorType.TIMEOUT: [
                RecoveryStrategy.CHECKPOINT_RESUMPTION,
                RecoveryStrategy.RETRY_WITH_FALLBACK_CONFIG,
                RecoveryStrategy.SWITCH_TO_ALTERNATIVE_SOLVER
            ],
            ErrorType.MEMORY_EXHAUSTION: [
                RecoveryStrategy.CIRCUIT_BREAKER_ACTIVATION,
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.SWITCH_TO_ALTERNATIVE_SOLVER
            ],
            ErrorType.RESOURCE_EXHAUSTION: [
                RecoveryStrategy.CIRCUIT_BREAKER_ACTIVATION,
                RecoveryStrategy.GRACEFUL_DEGRADATION
            ],
            ErrorType.SWARM_COORDINATION_FAILURE: [
                RecoveryStrategy.PARTIAL_RESULT_RECOVERY,
                RecoveryStrategy.GRACEFUL_DEGRADATION
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize the Error Recovery Manager"""
        try:
            # Initialize Strands integration
            await self._initialize_strands_integration()
            
            # Initialize circuit breakers
            await self._initialize_circuit_breakers()
            
            # Initialize checkpoint storage
            await self._initialize_checkpoint_storage()
            
            # Load error recovery configuration
            await self._load_recovery_configuration()
            
            self._initialized = True
            self.logger.info("Error Recovery Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Error Recovery Manager: {e}")
            return False
    
    async def _initialize_strands_integration(self):
        """Initialize Strands tools integration"""
        if not STRANDS_AVAILABLE:
            self.logger.warning("Strands not available - using fallback implementation")
            return
        
        try:
            self.strands_agent = Agent(
                name="error_recovery_manager",
                system_prompt="""You are an error recovery expert specializing in multi-solver optimization system resilience.
                
                Your expertise includes:
                1. Analyzing error patterns and root causes in solver operations
                2. Implementing intelligent recovery strategies based on error types
                3. Managing circuit breaker patterns for resource protection
                4. Coordinating checkpoint-based recovery for long-running operations
                5. Providing detailed error analysis and recovery recommendations
                
                ERROR RECOVERY STRATEGIES:
                
                Solver Unavailable:
                - Switch to alternative solver with similar capabilities
                - Graceful degradation to available solvers
                - Update solver availability status
                
                Solver Execution Failure:
                - Retry with fallback configuration parameters
                - Switch to alternative solver if retries fail
                - Recover partial results if available
                
                Timeout Errors:
                - Resume from checkpoint if available
                - Retry with adjusted time limits
                - Switch to faster solver alternatives
                
                Resource Exhaustion:
                - Activate circuit breaker for resource protection
                - Implement graceful degradation
                - Queue operations for later execution
                
                Swarm Coordination Failure:
                - Recover partial results from successful solvers
                - Fall back to single solver execution
                - Maintain best available solution
                
                Always store error context and recovery actions in memory for learning and pattern analysis.
                Provide detailed recovery rationale and confidence assessments.""",
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
            self.logger.warning(f"Strands tools initialization failed: {e}")
            self.strands_agent = None
            self.strands_tools = {}
    
    async def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for different resources"""
        try:
            # Circuit breaker configurations for different resources
            breaker_configs = {
                "solver_execution": CircuitBreakerConfig(
                    failure_threshold=5,
                    recovery_timeout=60,
                    success_threshold=3,
                    monitoring_window=300
                ),
                "memory_usage": CircuitBreakerConfig(
                    failure_threshold=3,
                    recovery_timeout=120,
                    success_threshold=2,
                    monitoring_window=600
                ),
                "swarm_coordination": CircuitBreakerConfig(
                    failure_threshold=4,
                    recovery_timeout=90,
                    success_threshold=2,
                    monitoring_window=300
                ),
                "network_operations": CircuitBreakerConfig(
                    failure_threshold=6,
                    recovery_timeout=30,
                    success_threshold=3,
                    monitoring_window=180
                )
            }
            
            # Create circuit breakers
            for name, config in breaker_configs.items():
                self.circuit_breakers[name] = CircuitBreaker(name=name, config=config)
            
            self.logger.info(f"Initialized {len(self.circuit_breakers)} circuit breakers")
            
        except Exception as e:
            self.logger.error(f"Error initializing circuit breakers: {e}")
    
    async def _initialize_checkpoint_storage(self):
        """Initialize checkpoint storage system"""
        try:
            # Create checkpoint directory if it doesn't exist
            os.makedirs(self.checkpoint_storage_path, exist_ok=True)
            
            # Load existing checkpoints
            await self._load_existing_checkpoints()
            
            self.logger.info(f"Checkpoint storage initialized at {self.checkpoint_storage_path}")
            
        except Exception as e:
            self.logger.error(f"Error initializing checkpoint storage: {e}")
    
    async def _load_existing_checkpoints(self):
        """Load existing checkpoints from storage"""
        try:
            checkpoint_files = [
                f for f in os.listdir(self.checkpoint_storage_path)
                if f.endswith('.checkpoint')
            ]
            
            for checkpoint_file in checkpoint_files:
                try:
                    file_path = os.path.join(self.checkpoint_storage_path, checkpoint_file)
                    with open(file_path, 'rb') as f:
                        checkpoint_data = pickle.load(f)
                        checkpoint = Checkpoint(**checkpoint_data)
                        self.checkpoints[checkpoint.checkpoint_id] = checkpoint
                except Exception as e:
                    self.logger.warning(f"Failed to load checkpoint {checkpoint_file}: {e}")
            
            self.logger.info(f"Loaded {len(self.checkpoints)} existing checkpoints")
            
        except Exception as e:
            self.logger.error(f"Error loading existing checkpoints: {e}")
    
    async def _load_recovery_configuration(self):
        """Load error recovery configuration"""
        if self.strands_tools.get('memory'):
            try:
                # Try to retrieve previous configuration
                config_result = self.strands_tools['memory'](
                    action="retrieve",
                    query="error recovery configuration strategies circuit breaker"
                )
                
                if config_result and 'content' in config_result:
                    self.logger.info("Loaded error recovery configuration from memory")
                
            except Exception as e:
                self.logger.warning(f"Could not load recovery configuration: {e}")
        
        # Store default configuration
        if self.strands_tools.get('memory'):
            try:
                config_data = {
                    "default_retry_config": self.default_retry_config,
                    "error_recovery_strategies": {
                        error_type.value: [strategy.value for strategy in strategies]
                        for error_type, strategies in self.error_recovery_strategies.items()
                    },
                    "circuit_breaker_configs": {
                        name: asdict(breaker.config)
                        for name, breaker in self.circuit_breakers.items()
                    }
                }
                
                self.strands_tools['memory'](
                    action="store",
                    content=f"Error recovery configuration: {json.dumps(config_data)}",
                    metadata={"type": "recovery_config", "component": "error_recovery_manager"}
                )
                
            except Exception as e:
                self.logger.warning(f"Could not store recovery configuration: {e}")
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute error recovery operations"""
        operation = kwargs.get("operation", "handle_error")
        
        if operation == "handle_error":
            return await self._handle_error(**kwargs)
        elif operation == "create_checkpoint":
            return await self._create_checkpoint(**kwargs)
        elif operation == "resume_from_checkpoint":
            return await self._resume_from_checkpoint(**kwargs)
        elif operation == "check_circuit_breaker":
            return await self._check_circuit_breaker(**kwargs)
        elif operation == "get_error_statistics":
            return await self._get_error_statistics(**kwargs)
        elif operation == "analyze_error_patterns":
            return await self._analyze_error_patterns(**kwargs)
        else:
            raise ToolExecutionError(f"Unknown operation: {operation}", self.name)
    
    async def _handle_error(self,
                           error: Exception,
                           operation_name: Optional[str] = None,
                           solver_name: Optional[str] = None,
                           problem_data: Optional[Dict[str, Any]] = None,
                           swarm_id: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """Handle error with comprehensive recovery strategies"""
        start_time = time.time()
        
        try:
            # Create error context
            # Remove operation_name from kwargs to avoid duplicate parameter
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'operation_name'}
            error_context = self._create_error_context(
                error, operation_name or "unknown_operation", solver_name, problem_data, swarm_id, **filtered_kwargs
            )
            
            # Store error in history
            with self._lock:
                self.error_history.append(error_context)
                if len(self.error_history) > self.max_error_history:
                    self.error_history = self.error_history[-self.max_error_history:]
            
            # Determine recovery strategies
            recovery_strategies = self._determine_recovery_strategies(error_context)
            
            # Execute recovery strategies
            recovery_result = await self._execute_recovery_strategies(
                error_context, recovery_strategies, problem_data
            )
            
            # Update circuit breakers
            await self._update_circuit_breakers(error_context, recovery_result["success"])
            
            # Store recovery result in memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Error recovery completed: {error_context.error_id}",
                    metadata={
                        "type": "error_recovery",
                        "error_id": error_context.error_id,
                        "error_type": error_context.error_type.value,
                        "recovery_success": recovery_result["success"],
                        "strategies_used": recovery_result.get("strategies_used", [])
                    }
                )
            
            execution_time = time.time() - start_time
            
            return {
                "success": recovery_result["success"],
                "error_context": error_context.to_dict(),
                "recovery_result": recovery_result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error recovery failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _create_error_context(self,
                             error: Exception,
                             operation: str,
                             solver_name: Optional[str] = None,
                             problem_data: Optional[Dict[str, Any]] = None,
                             swarm_id: Optional[str] = None,
                             **kwargs) -> ErrorContext:
        """Create comprehensive error context"""
        error_id = str(uuid.uuid4())
        error_type = self._classify_error(error)
        
        return ErrorContext(
            error_id=error_id,
            error_type=error_type,
            error_message=str(error),
            exception=error,
            timestamp=datetime.now(),
            operation=operation,
            solver_name=solver_name,
            problem_id=problem_data.get("problem_id") if problem_data else None,
            swarm_id=swarm_id,
            stack_trace=traceback.format_exc(),
            error_data=kwargs,
            retry_count=kwargs.get("retry_count", 0),
            max_retries=kwargs.get("max_retries", self.default_retry_config["max_retries"])
        )
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type based on exception characteristics"""
        error_str = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        # Classification rules
        if "solver not available" in error_str or "solver not found" in error_str:
            return ErrorType.SOLVER_UNAVAILABLE
        elif "timeout" in error_str or "time limit" in error_str:
            return ErrorType.TIMEOUT
        elif "memory" in error_str or "out of memory" in error_str:
            return ErrorType.MEMORY_EXHAUSTION
        elif "resource" in error_str or "limit exceeded" in error_str:
            return ErrorType.RESOURCE_EXHAUSTION
        elif "network" in error_str or "connection" in error_str:
            return ErrorType.NETWORK_ERROR
        elif "configuration" in error_str or "parameter" in error_str:
            return ErrorType.CONFIGURATION_ERROR
        elif "data" in error_str or "invalid input" in error_str:
            return ErrorType.DATA_ERROR
        elif "swarm" in error_str or "coordination" in error_str:
            return ErrorType.SWARM_COORDINATION_FAILURE
        elif "execution" in error_str or "solver" in error_str:
            return ErrorType.SOLVER_EXECUTION_FAILURE
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def _determine_recovery_strategies(self, error_context: ErrorContext) -> List[RecoveryStrategy]:
        """Determine appropriate recovery strategies for error type"""
        base_strategies = self.error_recovery_strategies.get(
            error_context.error_type, 
            [RecoveryStrategy.GRACEFUL_DEGRADATION]
        )
        
        # Adjust strategies based on context
        strategies = list(base_strategies)
        
        # Add retry strategy if not exceeded max retries
        if error_context.retry_count < error_context.max_retries:
            if RecoveryStrategy.RETRY_SAME_SOLVER not in strategies:
                strategies.insert(0, RecoveryStrategy.RETRY_SAME_SOLVER)
        
        # Add checkpoint resumption if available
        if error_context.swarm_id and error_context.swarm_id in self.checkpoints:
            if RecoveryStrategy.CHECKPOINT_RESUMPTION not in strategies:
                strategies.insert(0, RecoveryStrategy.CHECKPOINT_RESUMPTION)
        
        return strategies
    
    async def _execute_recovery_strategies(self,
                                         error_context: ErrorContext,
                                         strategies: List[RecoveryStrategy],
                                         problem_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute recovery strategies in order until one succeeds"""
        strategies_used = []
        last_error = None
        
        for strategy in strategies:
            try:
                strategies_used.append(strategy.value)
                self.logger.info(f"Attempting recovery strategy: {strategy.value}")
                
                result = await self._execute_single_recovery_strategy(
                    strategy, error_context, problem_data
                )
                
                if result["success"]:
                    self.recovery_statistics[strategy.value] += 1
                    return {
                        "success": True,
                        "strategy_used": strategy.value,
                        "strategies_used": strategies_used,
                        "result": result,
                        "recovery_data": result.get("recovery_data")
                    }
                
                last_error = result.get("error")
                
            except Exception as e:
                self.logger.error(f"Recovery strategy {strategy.value} failed: {e}")
                last_error = str(e)
        
        # All strategies failed
        return {
            "success": False,
            "strategies_used": strategies_used,
            "error": last_error or "All recovery strategies failed"
        }
    
    async def _execute_single_recovery_strategy(self,
                                              strategy: RecoveryStrategy,
                                              error_context: ErrorContext,
                                              problem_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a single recovery strategy"""
        if strategy == RecoveryStrategy.RETRY_SAME_SOLVER:
            return await self._retry_same_solver(error_context, problem_data)
        elif strategy == RecoveryStrategy.RETRY_WITH_FALLBACK_CONFIG:
            return await self._retry_with_fallback_config(error_context, problem_data)
        elif strategy == RecoveryStrategy.SWITCH_TO_ALTERNATIVE_SOLVER:
            return await self._switch_to_alternative_solver(error_context, problem_data)
        elif strategy == RecoveryStrategy.PARTIAL_RESULT_RECOVERY:
            return await self._recover_partial_results(error_context)
        elif strategy == RecoveryStrategy.CHECKPOINT_RESUMPTION:
            return await self._resume_from_checkpoint_strategy(error_context)
        elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
            return await self._graceful_degradation(error_context, problem_data)
        elif strategy == RecoveryStrategy.CIRCUIT_BREAKER_ACTIVATION:
            return await self._activate_circuit_breaker(error_context)
        else:
            return {"success": False, "error": f"Unknown recovery strategy: {strategy.value}"}
    
    async def _retry_same_solver(self,
                               error_context: ErrorContext,
                               problem_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Retry with the same solver using exponential backoff"""
        try:
            if error_context.retry_count >= error_context.max_retries:
                return {"success": False, "error": "Max retries exceeded"}
            
            # Calculate delay with exponential backoff
            delay = self._calculate_retry_delay(error_context.retry_count)
            
            self.logger.info(f"Retrying solver {error_context.solver_name} after {delay}s delay")
            await asyncio.sleep(delay)
            
            # Update retry count
            error_context.retry_count += 1
            error_context.recovery_attempts.append(f"retry_attempt_{error_context.retry_count}")
            
            return {
                "success": True,
                "recovery_data": {
                    "strategy": "retry_same_solver",
                    "retry_count": error_context.retry_count,
                    "delay": delay
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _retry_with_fallback_config(self,
                                        error_context: ErrorContext,
                                        problem_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Retry with fallback configuration parameters"""
        try:
            if not error_context.solver_name:
                return {"success": False, "error": "No solver specified for fallback config"}
            
            # Generate fallback configuration
            fallback_config = self._generate_fallback_config(error_context)
            
            self.logger.info(f"Retrying {error_context.solver_name} with fallback configuration")
            
            return {
                "success": True,
                "recovery_data": {
                    "strategy": "retry_with_fallback_config",
                    "fallback_config": fallback_config,
                    "original_solver": error_context.solver_name
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _switch_to_alternative_solver(self,
                                          error_context: ErrorContext,
                                          problem_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Switch to alternative solver with similar capabilities"""
        try:
            if not problem_data:
                return {"success": False, "error": "No problem data for solver selection"}
            
            # Get alternative solver
            alternative_solver = await self._select_alternative_solver(
                error_context.solver_name, problem_data
            )
            
            if not alternative_solver:
                return {"success": False, "error": "No alternative solver available"}
            
            self.logger.info(f"Switching from {error_context.solver_name} to {alternative_solver}")
            
            return {
                "success": True,
                "recovery_data": {
                    "strategy": "switch_to_alternative_solver",
                    "original_solver": error_context.solver_name,
                    "alternative_solver": alternative_solver
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _recover_partial_results(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Recover partial results from failed operation"""
        try:
            # Check for partial results in error context
            partial_results = error_context.error_data.get("partial_results", [])
            
            if not partial_results:
                return {"success": False, "error": "No partial results available"}
            
            # Validate and process partial results
            valid_results = []
            for result in partial_results:
                if isinstance(result, SolverResult) and result.objective_value is not None:
                    valid_results.append(result)
            
            if not valid_results:
                return {"success": False, "error": "No valid partial results"}
            
            # Select best partial result
            best_result = min(valid_results, key=lambda r: r.objective_value or float('inf'))
            
            self.logger.info(f"Recovered {len(valid_results)} partial results, best: {best_result.objective_value}")
            
            return {
                "success": True,
                "recovery_data": {
                    "strategy": "partial_result_recovery",
                    "partial_results_count": len(valid_results),
                    "best_result": asdict(best_result),
                    "recovery_quality": "partial"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _resume_from_checkpoint_strategy(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Resume operation from checkpoint"""
        try:
            if not error_context.swarm_id:
                return {"success": False, "error": "No swarm ID for checkpoint recovery"}
            
            checkpoint = self.checkpoints.get(error_context.swarm_id)
            if not checkpoint:
                return {"success": False, "error": "No checkpoint available"}
            
            # Validate checkpoint age
            checkpoint_age = (datetime.now() - checkpoint.timestamp).total_seconds()
            if checkpoint_age > 3600:  # 1 hour
                return {"success": False, "error": "Checkpoint too old"}
            
            self.logger.info(f"Resuming from checkpoint {checkpoint.checkpoint_id}")
            
            return {
                "success": True,
                "recovery_data": {
                    "strategy": "checkpoint_resumption",
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "checkpoint_progress": checkpoint.progress,
                    "intermediate_results": len(checkpoint.intermediate_results)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _graceful_degradation(self,
                                  error_context: ErrorContext,
                                  problem_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Implement graceful degradation strategy"""
        try:
            degradation_options = []
            
            # Reduce problem complexity
            if problem_data:
                degradation_options.append("reduce_problem_complexity")
            
            # Use simplified solver
            if error_context.solver_name:
                degradation_options.append("use_simplified_solver")
            
            # Return approximate solution
            degradation_options.append("approximate_solution")
            
            selected_option = degradation_options[0] if degradation_options else "no_operation"
            
            self.logger.info(f"Applying graceful degradation: {selected_option}")
            
            return {
                "success": True,
                "recovery_data": {
                    "strategy": "graceful_degradation",
                    "degradation_type": selected_option,
                    "quality_impact": "reduced"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _activate_circuit_breaker(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Activate circuit breaker for resource protection"""
        try:
            # Determine appropriate circuit breaker
            breaker_name = self._get_circuit_breaker_for_error(error_context.error_type)
            
            if breaker_name not in self.circuit_breakers:
                return {"success": False, "error": f"No circuit breaker for {breaker_name}"}
            
            breaker = self.circuit_breakers[breaker_name]
            breaker.record_failure()
            
            self.logger.warning(f"Circuit breaker {breaker_name} activated due to {error_context.error_type.value}")
            
            return {
                "success": True,
                "recovery_data": {
                    "strategy": "circuit_breaker_activation",
                    "breaker_name": breaker_name,
                    "breaker_state": breaker.state.value,
                    "failure_count": breaker.failure_count
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay with exponential backoff and jitter"""
        base_delay = self.default_retry_config["base_delay"]
        max_delay = self.default_retry_config["max_delay"]
        
        if self.default_retry_config["exponential_backoff"]:
            delay = base_delay * (2 ** retry_count)
        else:
            delay = base_delay
        
        delay = min(delay, max_delay)
        
        # Add jitter if enabled
        if self.default_retry_config["jitter"]:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def _generate_fallback_config(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Generate fallback configuration based on error type"""
        fallback_config = {}
        
        if error_context.error_type == ErrorType.TIMEOUT:
            fallback_config.update({
                "time_limit": 300,  # 5 minutes
                "early_termination": True,
                "solution_limit": 1
            })
        elif error_context.error_type == ErrorType.MEMORY_EXHAUSTION:
            fallback_config.update({
                "memory_limit": "1GB",
                "presolve": True,
                "cuts": "off"
            })
        elif error_context.error_type == ErrorType.SOLVER_EXECUTION_FAILURE:
            fallback_config.update({
                "tolerances": "relaxed",
                "algorithm": "dual_simplex",
                "scaling": True
            })
        
        return fallback_config
    
    async def _select_alternative_solver(self,
                                       failed_solver: Optional[str],
                                       problem_data: Dict[str, Any]) -> Optional[str]:
        """Select alternative solver with similar capabilities"""
        try:
            # Use intelligent solver selector to find alternatives
            selection_result = self.solver_selector.select_optimal_solver(problem_data)
            
            # Get list of suitable solvers excluding the failed one
            suitable_solvers = [
                solver for solver in selection_result.backup_solvers
                if solver != failed_solver
            ]
            
            if selection_result.primary_solver != failed_solver:
                suitable_solvers.insert(0, selection_result.primary_solver)
            
            return suitable_solvers[0] if suitable_solvers else None
            
        except Exception as e:
            self.logger.error(f"Error selecting alternative solver: {e}")
            return None
    
    def _get_circuit_breaker_for_error(self, error_type: ErrorType) -> str:
        """Get appropriate circuit breaker name for error type"""
        error_breaker_mapping = {
            ErrorType.SOLVER_EXECUTION_FAILURE: "solver_execution",
            ErrorType.MEMORY_EXHAUSTION: "memory_usage",
            ErrorType.RESOURCE_EXHAUSTION: "memory_usage",
            ErrorType.SWARM_COORDINATION_FAILURE: "swarm_coordination",
            ErrorType.NETWORK_ERROR: "network_operations"
        }
        
        return error_breaker_mapping.get(error_type, "solver_execution")
    
    async def _update_circuit_breakers(self, error_context: ErrorContext, recovery_success: bool):
        """Update circuit breaker states based on recovery result"""
        try:
            breaker_name = self._get_circuit_breaker_for_error(error_context.error_type)
            
            if breaker_name in self.circuit_breakers:
                breaker = self.circuit_breakers[breaker_name]
                
                if recovery_success:
                    breaker.record_success()
                else:
                    breaker.record_failure()
            
        except Exception as e:
            self.logger.error(f"Error updating circuit breakers: {e}")
    
    async def _create_checkpoint(self,
                               operation: str,
                               problem_data: Dict[str, Any],
                               solver_state: Dict[str, Any],
                               intermediate_results: List[SolverResult],
                               progress: float,
                               solver_name: str,
                               swarm_id: Optional[str] = None,
                               **kwargs) -> Dict[str, Any]:
        """Create checkpoint for operation resumption"""
        try:
            checkpoint_id = str(uuid.uuid4())
            
            checkpoint = Checkpoint(
                checkpoint_id=checkpoint_id,
                operation=operation,
                timestamp=datetime.now(),
                problem_data=problem_data,
                solver_state=solver_state,
                intermediate_results=intermediate_results,
                progress=progress,
                solver_name=solver_name,
                swarm_id=swarm_id,
                configuration=kwargs
            )
            
            # Store checkpoint in memory
            with self._lock:
                self.checkpoints[checkpoint_id] = checkpoint
            
            # Persist checkpoint to disk
            await self._persist_checkpoint(checkpoint)
            
            # Store in Strands memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Checkpoint created: {checkpoint_id}",
                    metadata={
                        "type": "checkpoint_creation",
                        "checkpoint_id": checkpoint_id,
                        "operation": operation,
                        "progress": progress,
                        "swarm_id": swarm_id
                    }
                )
            
            self.logger.info(f"Created checkpoint {checkpoint_id} for {operation}")
            
            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "progress": progress,
                "timestamp": checkpoint.timestamp.isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to create checkpoint: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _persist_checkpoint(self, checkpoint: Checkpoint):
        """Persist checkpoint to disk storage"""
        try:
            file_path = os.path.join(
                self.checkpoint_storage_path,
                f"{checkpoint.checkpoint_id}.checkpoint"
            )
            
            with open(file_path, 'wb') as f:
                pickle.dump(checkpoint.to_dict(), f)
            
        except Exception as e:
            self.logger.error(f"Failed to persist checkpoint {checkpoint.checkpoint_id}: {e}")
    
    async def _resume_from_checkpoint(self, checkpoint_id: str, **kwargs) -> Dict[str, Any]:
        """Resume operation from checkpoint"""
        try:
            if checkpoint_id not in self.checkpoints:
                raise ToolExecutionError(f"Checkpoint {checkpoint_id} not found", self.name)
            
            checkpoint = self.checkpoints[checkpoint_id]
            
            # Validate checkpoint age
            checkpoint_age = (datetime.now() - checkpoint.timestamp).total_seconds()
            if checkpoint_age > 3600:  # 1 hour
                raise ToolExecutionError(f"Checkpoint {checkpoint_id} is too old", self.name)
            
            self.logger.info(f"Resuming operation from checkpoint {checkpoint_id}")
            
            return {
                "success": True,
                "checkpoint": checkpoint.to_dict(),
                "resume_data": {
                    "operation": checkpoint.operation,
                    "progress": checkpoint.progress,
                    "intermediate_results": len(checkpoint.intermediate_results),
                    "solver_name": checkpoint.solver_name
                }
            }
            
        except Exception as e:
            error_msg = f"Failed to resume from checkpoint: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _check_circuit_breaker(self, breaker_name: str, **kwargs) -> Dict[str, Any]:
        """Check circuit breaker status"""
        try:
            if breaker_name not in self.circuit_breakers:
                raise ToolExecutionError(f"Circuit breaker {breaker_name} not found", self.name)
            
            breaker = self.circuit_breakers[breaker_name]
            
            return {
                "success": True,
                "breaker_name": breaker_name,
                "state": breaker.state.value,
                "can_execute": breaker.can_execute(),
                "failure_count": breaker.failure_count,
                "success_count": breaker.success_count,
                "failure_rate": breaker.get_failure_rate(),
                "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None,
                "last_success": breaker.last_success_time.isoformat() if breaker.last_success_time else None
            }
            
        except Exception as e:
            error_msg = f"Failed to check circuit breaker: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _get_error_statistics(self, **kwargs) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        try:
            with self._lock:
                total_errors = len(self.error_history)
                
                if total_errors == 0:
                    return {
                        "success": True,
                        "total_errors": 0,
                        "error_types": {},
                        "recovery_statistics": dict(self.recovery_statistics),
                        "circuit_breaker_status": {}
                    }
                
                # Error type distribution
                error_type_counts = defaultdict(int)
                for error in self.error_history:
                    error_type_counts[error.error_type.value] += 1
                
                # Recent errors (last 24 hours)
                recent_cutoff = datetime.now() - timedelta(hours=24)
                recent_errors = [
                    error for error in self.error_history
                    if error.timestamp >= recent_cutoff
                ]
                
                # Circuit breaker status
                circuit_breaker_status = {}
                for name, breaker in self.circuit_breakers.items():
                    circuit_breaker_status[name] = {
                        "state": breaker.state.value,
                        "failure_count": breaker.failure_count,
                        "success_count": breaker.success_count,
                        "failure_rate": breaker.get_failure_rate()
                    }
                
                return {
                    "success": True,
                    "total_errors": total_errors,
                    "recent_errors": len(recent_errors),
                    "error_types": dict(error_type_counts),
                    "recovery_statistics": dict(self.recovery_statistics),
                    "circuit_breaker_status": circuit_breaker_status,
                    "checkpoints_available": len(self.checkpoints)
                }
            
        except Exception as e:
            error_msg = f"Failed to get error statistics: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _analyze_error_patterns(self, **kwargs) -> Dict[str, Any]:
        """Analyze error patterns and provide insights"""
        try:
            if not self.strands_tools.get('use_llm'):
                return {"success": False, "error": "LLM not available for pattern analysis"}
            
            # Prepare error data for analysis
            error_summary = await self._get_error_statistics()
            
            # Generate analysis using Strands LLM
            analysis_prompt = f"""
            Analyze the following error patterns from a multi-solver optimization system:
            
            Error Statistics:
            {json.dumps(error_summary['data'] if error_summary['success'] else {}, indent=2)}
            
            Recent Error History:
            {json.dumps([error.to_dict() for error in self.error_history[-10:]], indent=2)}
            
            Provide insights on:
            1. Most common error patterns and their root causes
            2. Recovery strategy effectiveness
            3. Circuit breaker performance
            4. Recommendations for system improvements
            5. Preventive measures to reduce error rates
            
            Focus on actionable insights for system reliability improvement.
            """
            
            analysis_result = self.strands_tools['use_llm'](
                prompt=analysis_prompt,
                model="claude-3-sonnet-20240229"
            )
            
            return {
                "success": True,
                "error_analysis": analysis_result,
                "statistics": error_summary,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to analyze error patterns: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate error recovery parameters"""
        operation = kwargs.get("operation", "handle_error")
        
        if operation == "handle_error":
            return (
                "error" in kwargs and
                ("operation_name" in kwargs or "operation" in kwargs)
            )
        elif operation == "create_checkpoint":
            return (
                ("operation_name" in kwargs or "operation" in kwargs) and
                "problem_data" in kwargs and
                "solver_state" in kwargs and
                "progress" in kwargs and
                "solver_name" in kwargs
            )
        elif operation == "resume_from_checkpoint":
            return "checkpoint_id" in kwargs
        elif operation == "check_circuit_breaker":
            return "breaker_name" in kwargs
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup error recovery resources"""
        try:
            # Clean up old checkpoints
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            with self._lock:
                expired_checkpoints = [
                    checkpoint_id for checkpoint_id, checkpoint in self.checkpoints.items()
                    if checkpoint.timestamp < cutoff_time
                ]
                
                for checkpoint_id in expired_checkpoints:
                    del self.checkpoints[checkpoint_id]
                    
                    # Remove checkpoint file
                    try:
                        file_path = os.path.join(
                            self.checkpoint_storage_path,
                            f"{checkpoint_id}.checkpoint"
                        )
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        self.logger.warning(f"Failed to remove checkpoint file {checkpoint_id}: {e}")
            
            self.logger.info(f"Cleaned up {len(expired_checkpoints)} expired checkpoints")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")