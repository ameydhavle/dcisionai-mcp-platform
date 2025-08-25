"""
Swarm State Management System
============================

Comprehensive state management system for multi-solver swarm execution including:
- SwarmExecutionState class for tracking swarm execution progress
- Swarm lifecycle management (initialization, execution, termination)
- Real-time progress monitoring and status updates for all participating solvers
- Swarm result aggregation and intermediate result collection

Requirements: 3.2, 3.5, 5.3
"""

import logging
import asyncio
import uuid
import time
import threading
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from collections import defaultdict, deque
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from strands import Agent
    from strands_tools import memory, retrieve, use_aws
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

from ..utils.base import BaseTool, ToolExecutionError, ToolInitializationError
from .solver_tool import SolverResult

logger = logging.getLogger(__name__)


class SwarmStatus(Enum):
    """Swarm execution status states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class SolverStatus(Enum):
    """Individual solver status states"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class SwarmPattern(Enum):
    """Available swarm coordination patterns"""
    COMPETITIVE = "competitive"
    COLLABORATIVE = "collaborative"
    PEER_TO_PEER = "peer_to_peer"


@dataclass
class SolverProgress:
    """Progress tracking for individual solver"""
    solver_id: str
    status: SolverStatus
    progress_percentage: float = 0.0
    current_iteration: int = 0
    total_iterations: Optional[int] = None
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    last_update: datetime = field(default_factory=datetime.now)
    
    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    objective_value: Optional[float] = None
    
    # Status messages
    status_message: str = ""
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['status'] = self.status.value
        result['last_update'] = self.last_update.isoformat()
        if self.start_time:
            result['start_time'] = self.start_time.isoformat()
        if self.estimated_completion:
            result['estimated_completion'] = self.estimated_completion.isoformat()
        return result


@dataclass
class SwarmResourceUsage:
    """Resource usage tracking for swarm execution"""
    total_cpu_time: float = 0.0
    peak_memory_usage: float = 0.0
    current_memory_usage: float = 0.0
    parallel_efficiency: float = 0.0
    
    # Per-solver resource usage
    solver_cpu_usage: Dict[str, float] = field(default_factory=dict)
    solver_memory_usage: Dict[str, float] = field(default_factory=dict)
    
    # System resource limits
    max_cpu_cores: int = field(default_factory=lambda: os.cpu_count() or 1)
    max_memory_gb: float = field(default_factory=lambda: psutil.virtual_memory().total / (1024**3) if PSUTIL_AVAILABLE else 8.0)
    
    def update_resource_usage(self, solver_id: str, cpu_percent: float, memory_mb: float):
        """Update resource usage for a specific solver"""
        self.solver_cpu_usage[solver_id] = cpu_percent
        self.solver_memory_usage[solver_id] = memory_mb
        
        # Update totals
        self.current_memory_usage = sum(self.solver_memory_usage.values()) / 1024  # Convert to GB
        self.peak_memory_usage = max(self.peak_memory_usage, self.current_memory_usage)
        
        # Calculate parallel efficiency
        total_cpu_usage = sum(self.solver_cpu_usage.values())
        active_solvers = len([usage for usage in self.solver_cpu_usage.values() if usage > 0])
        if active_solvers > 0:
            self.parallel_efficiency = total_cpu_usage / (active_solvers * 100.0)


@dataclass
class SwarmExecutionState:
    """Enhanced state management for swarm execution"""
    
    # Basic identification
    swarm_id: str
    problem_id: str
    pattern: SwarmPattern
    
    # Execution metadata
    start_time: datetime
    end_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    timeout: Optional[float] = None
    
    # Status tracking
    status: SwarmStatus = SwarmStatus.INITIALIZING
    status_message: str = ""
    
    # Participating solvers
    solver_agents: List[str] = field(default_factory=list)
    solver_progress: Dict[str, SolverProgress] = field(default_factory=dict)
    
    # Results management
    completed_results: List[SolverResult] = field(default_factory=list)
    intermediate_results: Dict[str, List[SolverResult]] = field(default_factory=dict)
    best_result: Optional[SolverResult] = None
    comparison_analysis: Optional[Dict[str, Any]] = None
    
    # Resource usage
    resource_usage: SwarmResourceUsage = field(default_factory=SwarmResourceUsage)
    
    # Configuration
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Event history
    event_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Callbacks for real-time updates
    progress_callbacks: List[Callable] = field(default_factory=list)
    
    def add_event(self, event_type: str, message: str, solver_id: Optional[str] = None, **kwargs):
        """Add event to history"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "solver_id": solver_id,
            **kwargs
        }
        self.event_history.append(event)
        
        # Trigger callbacks
        for callback in self.progress_callbacks:
            try:
                callback(self, event)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
    
    def update_solver_progress(self, solver_id: str, progress: float, **kwargs):
        """Update progress for a specific solver"""
        if solver_id not in self.solver_progress:
            self.solver_progress[solver_id] = SolverProgress(
                solver_id=solver_id,
                status=SolverStatus.RUNNING
            )
        
        solver_progress = self.solver_progress[solver_id]
        solver_progress.progress_percentage = progress
        solver_progress.last_update = datetime.now()
        
        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(solver_progress, key):
                setattr(solver_progress, key, value)
        
        # Add progress event
        self.add_event(
            "progress_update",
            f"Solver {solver_id} progress: {progress:.1f}%",
            solver_id=solver_id,
            progress=progress
        )
    
    def update_solver_status(self, solver_id: str, status: SolverStatus, message: str = ""):
        """Update status for a specific solver"""
        if solver_id not in self.solver_progress:
            self.solver_progress[solver_id] = SolverProgress(
                solver_id=solver_id,
                status=status
            )
        else:
            self.solver_progress[solver_id].status = status
        
        self.solver_progress[solver_id].status_message = message
        self.solver_progress[solver_id].last_update = datetime.now()
        
        # Add status event
        self.add_event(
            "status_update",
            f"Solver {solver_id} status: {status.value} - {message}",
            solver_id=solver_id,
            status=status.value
        )
    
    def add_intermediate_result(self, solver_id: str, result: SolverResult):
        """Add intermediate result from a solver"""
        if solver_id not in self.intermediate_results:
            self.intermediate_results[solver_id] = []
        
        self.intermediate_results[solver_id].append(result)
        
        # Add result event
        self.add_event(
            "intermediate_result",
            f"Intermediate result from {solver_id}: {result.objective_value}",
            solver_id=solver_id,
            objective_value=result.objective_value
        )
    
    def add_completed_result(self, result: SolverResult):
        """Add completed result from a solver"""
        self.completed_results.append(result)
        
        # Update solver status
        if result.solver_name:
            self.update_solver_status(
                result.solver_name,
                SolverStatus.COMPLETED,
                f"Completed with status: {result.solve_status}"
            )
        
        # Add completion event
        self.add_event(
            "solver_completed",
            f"Solver {result.solver_name} completed with objective: {result.objective_value}",
            solver_id=result.solver_name,
            objective_value=result.objective_value,
            solve_status=result.solve_status
        )
    
    def get_overall_progress(self) -> float:
        """Calculate overall swarm progress"""
        if not self.solver_progress:
            return 0.0
        
        total_progress = sum(sp.progress_percentage for sp in self.solver_progress.values())
        return total_progress / len(self.solver_progress)
    
    def get_active_solvers(self) -> List[str]:
        """Get list of currently active solvers"""
        return [
            solver_id for solver_id, progress in self.solver_progress.items()
            if progress.status in [SolverStatus.INITIALIZING, SolverStatus.RUNNING]
        ]
    
    def get_completed_solvers(self) -> List[str]:
        """Get list of completed solvers"""
        return [
            solver_id for solver_id, progress in self.solver_progress.items()
            if progress.status == SolverStatus.COMPLETED
        ]
    
    def get_failed_solvers(self) -> List[str]:
        """Get list of failed solvers"""
        return [
            solver_id for solver_id, progress in self.solver_progress.items()
            if progress.status in [SolverStatus.FAILED, SolverStatus.TIMEOUT, SolverStatus.CANCELLED]
        ]
    
    def is_complete(self) -> bool:
        """Check if swarm execution is complete"""
        if not self.solver_progress:
            return False
        
        return all(
            progress.status in [SolverStatus.COMPLETED, SolverStatus.FAILED, 
                              SolverStatus.TIMEOUT, SolverStatus.CANCELLED]
            for progress in self.solver_progress.values()
        )
    
    def get_execution_time(self) -> float:
        """Get total execution time"""
        end_time = self.end_time or datetime.now()
        return (end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            "swarm_id": self.swarm_id,
            "problem_id": self.problem_id,
            "pattern": self.pattern.value,
            "status": self.status.value,
            "status_message": self.status_message,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "timeout": self.timeout,
            "solver_agents": self.solver_agents,
            "solver_progress": {k: v.to_dict() for k, v in self.solver_progress.items()},
            "completed_results": [asdict(r) for r in self.completed_results],
            "intermediate_results": {
                k: [asdict(r) for r in v] for k, v in self.intermediate_results.items()
            },
            "best_result": asdict(self.best_result) if self.best_result else None,
            "comparison_analysis": self.comparison_analysis,
            "resource_usage": asdict(self.resource_usage),
            "configuration": self.configuration,
            "event_history": self.event_history,
            "overall_progress": self.get_overall_progress(),
            "execution_time": self.get_execution_time(),
            "active_solvers": self.get_active_solvers(),
            "completed_solvers": self.get_completed_solvers(),
            "failed_solvers": self.get_failed_solvers(),
            "is_complete": self.is_complete()
        }
        return result


class SwarmStateManager(BaseTool):
    """
    Comprehensive swarm state management system providing:
    - Swarm lifecycle management
    - Real-time progress monitoring
    - Result aggregation and analysis
    - Resource usage tracking
    """
    
    def __init__(self):
        super().__init__(
            name="swarm_state_manager",
            description="Comprehensive state management for multi-solver swarm execution",
            version="1.0.0"
        )
        
        # Active swarms
        self.active_swarms: Dict[str, SwarmExecutionState] = {}
        self.swarm_history: List[SwarmExecutionState] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Monitoring
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        self._shutdown_event = asyncio.Event()
        
        # Strands integration
        self.strands_agent = None
        self.strands_tools = {}
        
        # Performance tracking
        self.performance_metrics = defaultdict(list)
        
        # Configuration
        self.max_history_size = 1000
        self.monitoring_interval = 1.0  # seconds
        self.resource_monitoring_enabled = True
    
    async def initialize(self) -> bool:
        """Initialize the Swarm State Manager"""
        try:
            # Initialize Strands integration
            await self._initialize_strands_integration()
            
            # Start background monitoring
            await self._start_background_monitoring()
            
            self._initialized = True
            self.logger.info("Swarm State Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Swarm State Manager: {e}")
            return False
    
    async def _initialize_strands_integration(self):
        """Initialize Strands tools integration"""
        if not STRANDS_AVAILABLE:
            self.logger.warning("Strands not available - using fallback implementation")
            return
        
        try:
            self.strands_agent = Agent(
                name="swarm_state_manager",
                system_prompt="""You are a swarm state management expert responsible for tracking and coordinating multi-solver swarm execution.
                
                Your responsibilities:
                1. Monitor swarm execution progress and status
                2. Track resource usage and performance metrics
                3. Aggregate and analyze solver results
                4. Provide real-time updates on swarm execution
                5. Manage swarm lifecycle from initialization to completion
                
                Use memory to store swarm state and execution history for analysis and learning.""",
                tools=[memory, retrieve, use_aws]
            )
            
            self.strands_tools = {
                'memory': self.strands_agent.tool.memory,
                'retrieve': self.strands_agent.tool.retrieve,
                'use_aws': self.strands_agent.tool.use_aws
            }
            
            self.logger.info("Strands integration initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Strands tools initialization failed: {e}")
            self.strands_agent = None
            self.strands_tools = {}
    
    async def _start_background_monitoring(self):
        """Start background monitoring tasks"""
        try:
            # Start resource monitoring task
            if self.resource_monitoring_enabled:
                monitoring_task = asyncio.create_task(self._resource_monitoring_loop())
                self._monitoring_tasks["resource_monitor"] = monitoring_task
            
            self.logger.info("Background monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start background monitoring: {e}")
    
    async def _resource_monitoring_loop(self):
        """Background loop for monitoring resource usage"""
        while not self._shutdown_event.is_set():
            try:
                with self._lock:
                    for swarm_id, swarm_state in self.active_swarms.items():
                        await self._update_resource_usage(swarm_state)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in resource monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _update_resource_usage(self, swarm_state: SwarmExecutionState):
        """Update resource usage for a swarm"""
        try:
            if not PSUTIL_AVAILABLE:
                return
            
            # Get system resource usage
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            
            # Update resource usage (simplified - in real implementation would track per-solver)
            for solver_id in swarm_state.get_active_solvers():
                # Simulate per-solver resource tracking
                solver_cpu = cpu_percent / len(swarm_state.get_active_solvers()) if swarm_state.get_active_solvers() else 0
                solver_memory = memory_info.used / (1024**2) / len(swarm_state.get_active_solvers()) if swarm_state.get_active_solvers() else 0
                
                swarm_state.resource_usage.update_resource_usage(solver_id, solver_cpu, solver_memory)
            
        except Exception as e:
            self.logger.error(f"Error updating resource usage: {e}")
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute swarm state management operations"""
        operation = kwargs.get("operation", "create_swarm")
        
        if operation == "create_swarm":
            return await self._create_swarm(**kwargs)
        elif operation == "update_progress":
            return await self._update_solver_progress(**kwargs)
        elif operation == "add_result":
            return await self._add_solver_result(**kwargs)
        elif operation == "get_status":
            return await self._get_swarm_status(**kwargs)
        elif operation == "monitor_swarm":
            return await self._monitor_swarm(**kwargs)
        elif operation == "terminate_swarm":
            return await self._terminate_swarm(**kwargs)
        elif operation == "get_history":
            return await self._get_swarm_history(**kwargs)
        else:
            raise ToolExecutionError(f"Unknown operation: {operation}", self.name)
    
    async def _create_swarm(self, 
                           problem_id: str,
                           solver_agents: List[str],
                           pattern: str = "competitive",
                           timeout: Optional[float] = None,
                           configuration: Optional[Dict[str, Any]] = None,
                           **kwargs) -> Dict[str, Any]:
        """Create a new swarm execution state"""
        try:
            swarm_id = str(uuid.uuid4())
            
            # Create swarm execution state
            swarm_state = SwarmExecutionState(
                swarm_id=swarm_id,
                problem_id=problem_id,
                pattern=SwarmPattern(pattern),
                start_time=datetime.now(),
                timeout=timeout,
                solver_agents=solver_agents,
                configuration=configuration or {}
            )
            
            # Initialize solver progress
            for solver_id in solver_agents:
                swarm_state.solver_progress[solver_id] = SolverProgress(
                    solver_id=solver_id,
                    status=SolverStatus.PENDING
                )
            
            # Store in active swarms
            with self._lock:
                self.active_swarms[swarm_id] = swarm_state
            
            # Add creation event
            swarm_state.add_event(
                "swarm_created",
                f"Swarm created with {len(solver_agents)} solvers",
                pattern=pattern,
                solver_count=len(solver_agents)
            )
            
            # Store in Strands memory if available
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Swarm created: {swarm_id}",
                    metadata={
                        "type": "swarm_creation",
                        "swarm_id": swarm_id,
                        "problem_id": problem_id,
                        "pattern": pattern,
                        "solver_count": len(solver_agents)
                    }
                )
            
            self.logger.info(f"Created swarm {swarm_id} with {len(solver_agents)} solvers")
            
            return {
                "success": True,
                "swarm_id": swarm_id,
                "status": swarm_state.status.value,
                "solver_count": len(solver_agents),
                "pattern": pattern
            }
            
        except Exception as e:
            error_msg = f"Failed to create swarm: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _update_solver_progress(self,
                                    swarm_id: str,
                                    solver_id: str,
                                    progress: float,
                                    status: Optional[str] = None,
                                    **kwargs) -> Dict[str, Any]:
        """Update progress for a specific solver"""
        try:
            with self._lock:
                if swarm_id not in self.active_swarms:
                    raise ToolExecutionError(f"Swarm {swarm_id} not found", self.name)
                
                swarm_state = self.active_swarms[swarm_id]
            
            # Update progress
            swarm_state.update_solver_progress(solver_id, progress, **kwargs)
            
            # Update status if provided
            if status:
                swarm_state.update_solver_status(
                    solver_id,
                    SolverStatus(status),
                    kwargs.get("status_message", "")
                )
            
            # Store progress update in memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Progress update: {solver_id} at {progress}%",
                    metadata={
                        "type": "progress_update",
                        "swarm_id": swarm_id,
                        "solver_id": solver_id,
                        "progress": progress
                    }
                )
            
            return {
                "success": True,
                "swarm_id": swarm_id,
                "solver_id": solver_id,
                "progress": progress,
                "overall_progress": swarm_state.get_overall_progress()
            }
            
        except Exception as e:
            error_msg = f"Failed to update solver progress: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _add_solver_result(self,
                               swarm_id: str,
                               result: SolverResult,
                               is_intermediate: bool = False,
                               **kwargs) -> Dict[str, Any]:
        """Add solver result to swarm state"""
        try:
            with self._lock:
                if swarm_id not in self.active_swarms:
                    raise ToolExecutionError(f"Swarm {swarm_id} not found", self.name)
                
                swarm_state = self.active_swarms[swarm_id]
            
            if is_intermediate:
                swarm_state.add_intermediate_result(result.solver_name, result)
            else:
                swarm_state.add_completed_result(result)
                
                # Update best result if this is better
                if (swarm_state.best_result is None or 
                    (result.objective_value is not None and 
                     swarm_state.best_result.objective_value is not None and
                     result.objective_value < swarm_state.best_result.objective_value)):
                    swarm_state.best_result = result
                    swarm_state.add_event(
                        "new_best_result",
                        f"New best result from {result.solver_name}: {result.objective_value}",
                        solver_id=result.solver_name,
                        objective_value=result.objective_value
                    )
            
            # Check if swarm is complete
            if swarm_state.is_complete():
                await self._complete_swarm(swarm_state)
            
            return {
                "success": True,
                "swarm_id": swarm_id,
                "result_type": "intermediate" if is_intermediate else "final",
                "solver_id": result.solver_name,
                "objective_value": result.objective_value,
                "is_complete": swarm_state.is_complete()
            }
            
        except Exception as e:
            error_msg = f"Failed to add solver result: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _complete_swarm(self, swarm_state: SwarmExecutionState):
        """Complete swarm execution"""
        try:
            swarm_state.status = SwarmStatus.COMPLETED
            swarm_state.end_time = datetime.now()
            swarm_state.status_message = "Swarm execution completed successfully"
            
            # Generate comparison analysis
            swarm_state.comparison_analysis = self._generate_comparison_analysis(swarm_state)
            
            # Add completion event
            swarm_state.add_event(
                "swarm_completed",
                f"Swarm completed with {len(swarm_state.completed_results)} results",
                execution_time=swarm_state.get_execution_time(),
                result_count=len(swarm_state.completed_results)
            )
            
            # Move to history
            with self._lock:
                if swarm_state.swarm_id in self.active_swarms:
                    del self.active_swarms[swarm_state.swarm_id]
                
                self.swarm_history.append(swarm_state)
                
                # Maintain history size limit
                if len(self.swarm_history) > self.max_history_size:
                    self.swarm_history = self.swarm_history[-self.max_history_size:]
            
            # Store completion in memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Swarm completed: {swarm_state.swarm_id}",
                    metadata={
                        "type": "swarm_completion",
                        "swarm_id": swarm_state.swarm_id,
                        "execution_time": swarm_state.get_execution_time(),
                        "result_count": len(swarm_state.completed_results),
                        "best_objective": swarm_state.best_result.objective_value if swarm_state.best_result else None
                    }
                )
            
            self.logger.info(f"Swarm {swarm_state.swarm_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error completing swarm: {e}")
    
    def _generate_comparison_analysis(self, swarm_state: SwarmExecutionState) -> Dict[str, Any]:
        """Generate comparison analysis of swarm results"""
        try:
            if not swarm_state.completed_results:
                return {"error": "No completed results to analyze"}
            
            results = swarm_state.completed_results
            
            analysis = {
                "total_solvers": len(swarm_state.solver_agents),
                "completed_solvers": len(results),
                "success_rate": len(results) / len(swarm_state.solver_agents),
                "execution_time": swarm_state.get_execution_time(),
                "pattern": swarm_state.pattern.value,
                "solver_performance": {},
                "quality_metrics": {},
                "resource_efficiency": {}
            }
            
            # Analyze individual solver performance
            for result in results:
                solver_name = result.solver_name
                analysis["solver_performance"][solver_name] = {
                    "status": result.solve_status,
                    "objective_value": result.objective_value,
                    "execution_time": result.execution_time,
                    "iterations": getattr(result, 'iterations', 0)
                }
            
            # Quality metrics
            objective_values = [r.objective_value for r in results if r.objective_value is not None]
            if objective_values:
                analysis["quality_metrics"] = {
                    "best_objective": min(objective_values),
                    "worst_objective": max(objective_values),
                    "average_objective": sum(objective_values) / len(objective_values),
                    "objective_range": max(objective_values) - min(objective_values)
                }
            
            # Resource efficiency
            analysis["resource_efficiency"] = {
                "peak_memory_usage": swarm_state.resource_usage.peak_memory_usage,
                "parallel_efficiency": swarm_state.resource_usage.parallel_efficiency,
                "total_cpu_time": swarm_state.resource_usage.total_cpu_time
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error generating comparison analysis: {e}")
            return {"error": str(e)}
    
    async def _get_swarm_status(self, swarm_id: str, **kwargs) -> Dict[str, Any]:
        """Get current status of a swarm"""
        try:
            with self._lock:
                # Check active swarms first
                if swarm_id in self.active_swarms:
                    swarm_state = self.active_swarms[swarm_id]
                    return {
                        "success": True,
                        "swarm_state": swarm_state.to_dict(),
                        "is_active": True
                    }
                
                # Check history
                for swarm_state in self.swarm_history:
                    if swarm_state.swarm_id == swarm_id:
                        return {
                            "success": True,
                            "swarm_state": swarm_state.to_dict(),
                            "is_active": False
                        }
            
            raise ToolExecutionError(f"Swarm {swarm_id} not found", self.name)
            
        except Exception as e:
            error_msg = f"Failed to get swarm status: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _monitor_swarm(self, swarm_id: str, **kwargs) -> Dict[str, Any]:
        """Get real-time monitoring data for a swarm"""
        try:
            with self._lock:
                if swarm_id not in self.active_swarms:
                    raise ToolExecutionError(f"Active swarm {swarm_id} not found", self.name)
                
                swarm_state = self.active_swarms[swarm_id]
            
            # Get recent events
            recent_events = swarm_state.event_history[-10:] if swarm_state.event_history else []
            
            monitoring_data = {
                "swarm_id": swarm_id,
                "status": swarm_state.status.value,
                "overall_progress": swarm_state.get_overall_progress(),
                "execution_time": swarm_state.get_execution_time(),
                "active_solvers": swarm_state.get_active_solvers(),
                "completed_solvers": swarm_state.get_completed_solvers(),
                "failed_solvers": swarm_state.get_failed_solvers(),
                "solver_progress": {k: v.to_dict() for k, v in swarm_state.solver_progress.items()},
                "resource_usage": asdict(swarm_state.resource_usage),
                "recent_events": recent_events,
                "intermediate_results_count": sum(len(results) for results in swarm_state.intermediate_results.values()),
                "completed_results_count": len(swarm_state.completed_results),
                "best_objective": swarm_state.best_result.objective_value if swarm_state.best_result else None
            }
            
            return {
                "success": True,
                "monitoring_data": monitoring_data
            }
            
        except Exception as e:
            error_msg = f"Failed to monitor swarm: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _terminate_swarm(self, swarm_id: str, reason: str = "user_requested", **kwargs) -> Dict[str, Any]:
        """Terminate a running swarm"""
        try:
            with self._lock:
                if swarm_id not in self.active_swarms:
                    raise ToolExecutionError(f"Active swarm {swarm_id} not found", self.name)
                
                swarm_state = self.active_swarms[swarm_id]
            
            # Update status
            swarm_state.status = SwarmStatus.CANCELLED
            swarm_state.end_time = datetime.now()
            swarm_state.status_message = f"Terminated: {reason}"
            
            # Update all active solvers to cancelled
            for solver_id in swarm_state.get_active_solvers():
                swarm_state.update_solver_status(solver_id, SolverStatus.CANCELLED, reason)
            
            # Add termination event
            swarm_state.add_event(
                "swarm_terminated",
                f"Swarm terminated: {reason}",
                reason=reason
            )
            
            # Move to history
            with self._lock:
                del self.active_swarms[swarm_id]
                self.swarm_history.append(swarm_state)
            
            self.logger.info(f"Swarm {swarm_id} terminated: {reason}")
            
            return {
                "success": True,
                "swarm_id": swarm_id,
                "reason": reason,
                "execution_time": swarm_state.get_execution_time()
            }
            
        except Exception as e:
            error_msg = f"Failed to terminate swarm: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _get_swarm_history(self, limit: int = 50, **kwargs) -> Dict[str, Any]:
        """Get swarm execution history"""
        try:
            with self._lock:
                history = self.swarm_history[-limit:] if limit > 0 else self.swarm_history
            
            history_data = [
                {
                    "swarm_id": swarm.swarm_id,
                    "problem_id": swarm.problem_id,
                    "pattern": swarm.pattern.value,
                    "status": swarm.status.value,
                    "start_time": swarm.start_time.isoformat(),
                    "end_time": swarm.end_time.isoformat() if swarm.end_time else None,
                    "execution_time": swarm.get_execution_time(),
                    "solver_count": len(swarm.solver_agents),
                    "completed_results": len(swarm.completed_results),
                    "best_objective": swarm.best_result.objective_value if swarm.best_result else None
                }
                for swarm in history
            ]
            
            return {
                "success": True,
                "history": history_data,
                "total_count": len(self.swarm_history),
                "returned_count": len(history_data)
            }
            
        except Exception as e:
            error_msg = f"Failed to get swarm history: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate swarm state management parameters"""
        try:
            operation = kwargs.get("operation", "create_swarm")
            
            if operation == "create_swarm":
                problem_id = kwargs.get("problem_id")
                if not problem_id or not isinstance(problem_id, str):
                    self.logger.error("Invalid problem_id parameter")
                    return False
                
                solver_agents = kwargs.get("solver_agents")
                if not solver_agents or not isinstance(solver_agents, list) or len(solver_agents) == 0:
                    self.logger.error("Invalid solver_agents parameter")
                    return False
                
                pattern = kwargs.get("pattern", "competitive")
                if pattern not in ["competitive", "collaborative", "peer_to_peer"]:
                    self.logger.error(f"Invalid pattern: {pattern}")
                    return False
            
            elif operation in ["update_progress", "add_result", "get_status", "monitor_swarm", "terminate_swarm"]:
                swarm_id = kwargs.get("swarm_id")
                if not swarm_id or not isinstance(swarm_id, str):
                    self.logger.error("Invalid swarm_id parameter")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            # Set shutdown event
            self._shutdown_event.set()
            
            # Cancel monitoring tasks
            for task_name, task in self._monitoring_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Clear active swarms
            with self._lock:
                self.active_swarms.clear()
            
            self.logger.info("Swarm State Manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")