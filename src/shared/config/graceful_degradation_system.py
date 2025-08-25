"""
Graceful Degradation System for Multi-Solver Optimization
=========================================================

Implements comprehensive graceful degradation logic for solver failures,
including automatic fallback chains, alternative solver selection,
and system resilience mechanisms.

Features:
- Intelligent fallback solver selection
- Problem adaptation for alternative solvers
- Performance-based degradation decisions
- System health monitoring and recovery

Requirements: 1.4, 7.1, 7.2, 7.3, 7.4
"""

import logging
import time
import copy
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
from collections import defaultdict, deque

from .enhanced_solver_registry import enhanced_solver_registry, SolverCategory, SolverStatus
from .solver_detection_system import solver_detection_system
from .solver_configuration_manager import solver_configuration_manager

logger = logging.getLogger(__name__)


class DegradationReason(Enum):
    """Reasons for solver degradation"""
    SOLVER_UNAVAILABLE = "solver_unavailable"
    SOLVER_TIMEOUT = "solver_timeout"
    SOLVER_ERROR = "solver_error"
    SOLVER_CRASH = "solver_crash"
    MEMORY_EXHAUSTION = "memory_exhaustion"
    POOR_PERFORMANCE = "poor_performance"
    RESOURCE_LIMIT = "resource_limit"
    SYSTEM_OVERLOAD = "system_overload"


class DegradationLevel(Enum):
    """Levels of system degradation"""
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class DegradationEvent:
    """Record of a degradation event"""
    timestamp: datetime
    solver_name: str
    problem_type: str
    reason: DegradationReason
    fallback_solver: Optional[str]
    success: bool
    recovery_time: float
    impact_level: DegradationLevel
    details: Dict[str, Any]


@dataclass
class SolverHealthMetrics:
    """Health metrics for a solver"""
    solver_name: str
    success_rate: float
    average_solve_time: float
    error_rate: float
    timeout_rate: float
    crash_rate: float
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    consecutive_failures: int
    health_score: float  # 0.0 to 1.0
    status: str  # healthy, degraded, unhealthy, critical


class GracefulDegradationSystem:
    """
    Comprehensive graceful degradation system for multi-solver optimization
    
    Provides intelligent fallback mechanisms, system health monitoring,
    and automatic recovery strategies to ensure system resilience.
    """
    
    def __init__(self):
        self.registry = enhanced_solver_registry
        self.detection_system = solver_detection_system
        self.config_manager = solver_configuration_manager
        
        # Degradation tracking
        self.degradation_events: List[DegradationEvent] = []
        self.solver_health: Dict[str, SolverHealthMetrics] = {}
        self.system_health_score: float = 1.0
        self.current_degradation_level: DegradationLevel = DegradationLevel.NONE
        
        # Fallback chains and alternatives
        self.fallback_chains: Dict[str, List[str]] = {}
        self.alternative_mappings: Dict[str, Dict[str, List[str]]] = {}
        
        # Circuit breaker patterns
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.failure_thresholds = {
            "consecutive_failures": 3,
            "error_rate_threshold": 0.5,
            "timeout_rate_threshold": 0.3,
            "health_score_threshold": 0.3
        }
        
        # Performance tracking
        self.performance_window = deque(maxlen=100)  # Last 100 operations
        self.health_check_interval = timedelta(minutes=5)
        self.last_health_check = datetime.now()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize system
        self._initialize_fallback_chains()
        self._initialize_circuit_breakers()
        self._initialize_solver_health()
        
        logger.info("Graceful degradation system initialized")
    
    def _initialize_fallback_chains(self):
        """Initialize comprehensive fallback chains for different scenarios"""
        
        # Problem type-based fallback chains
        self.fallback_chains = {
            # Linear Programming fallbacks
            "linear_programming": [
                "HiGHS_LP", "GLOP", "CLP", "SCIPY_LINPROG"
            ],
            
            # Mixed-Integer Programming fallbacks
            "mixed_integer_programming": [
                "HiGHS_MIP", "SCIP", "CBC", "CVXPY_GLPK_MI", "PYOMO_CBC"
            ],
            
            # Constraint Programming fallbacks
            "constraint_programming": [
                "CP_SAT", "OR_TOOLS_ROUTING"
            ],
            
            # Nonlinear Programming fallbacks
            "nonlinear_programming": [
                "IPOPT", "CVXPY_ECOS", "SCIPY_SLSQP", "BONMIN"
            ],
            
            # Metaheuristic fallbacks
            "metaheuristic": [
                "OPTUNA", "PYSWARMS", "DEAP"
            ],
            
            # Manufacturing-specific fallbacks
            "production_scheduling": [
                "CP_SAT", "SCIP", "CBC", "HiGHS_MIP"
            ],
            
            "capacity_planning": [
                "HiGHS_LP", "GLOP", "CLP", "SCIPY_LINPROG"
            ],
            
            "resource_allocation": [
                "HiGHS_MIP", "CBC", "SCIP", "CVXPY_GLPK_MI"
            ],
            
            "routing": [
                "OR_TOOLS_ROUTING", "CP_SAT", "OPTUNA"
            ]
        }
        
        # Solver-specific alternative mappings
        self.alternative_mappings = {
            # High-performance alternatives
            "performance": {
                "GLOP": ["HiGHS_LP", "CLP"],
                "SCIP": ["HiGHS_MIP", "CBC"],
                "CP_SAT": ["SCIP", "CBC"],
                "IPOPT": ["SCIPY_SLSQP", "CVXPY_ECOS"]
            },
            
            # Memory-efficient alternatives
            "memory_efficient": {
                "SCIP": ["CBC", "HiGHS_MIP"],
                "BONMIN": ["SCIPY_SLSQP", "IPOPT"],
                "DEAP": ["PYSWARMS", "OPTUNA"]
            },
            
            # Robust alternatives (high reliability)
            "robust": {
                "HiGHS_LP": ["GLOP", "CLP"],
                "HiGHS_MIP": ["SCIP", "CBC"],
                "CP_SAT": ["SCIP"],
                "OPTUNA": ["PYSWARMS", "DEAP"]
            }
        }
    
    def _initialize_circuit_breakers(self):
        """Initialize circuit breaker patterns for each solver"""
        
        for solver_name in self.registry.solvers:
            self.circuit_breakers[solver_name] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure_time": None,
                "recovery_timeout": 300,  # 5 minutes
                "success_threshold": 3,  # Successes needed to close circuit
                "failure_threshold": 3   # Failures to open circuit
            }
    
    def _initialize_solver_health(self):
        """Initialize health metrics for all solvers"""
        
        for solver_name in self.registry.solvers:
            self.solver_health[solver_name] = SolverHealthMetrics(
                solver_name=solver_name,
                success_rate=1.0,
                average_solve_time=0.0,
                error_rate=0.0,
                timeout_rate=0.0,
                crash_rate=0.0,
                last_success=None,
                last_failure=None,
                consecutive_failures=0,
                health_score=1.0,
                status="healthy"
            )
    
    def select_solver_with_fallback(self, primary_solver: str, problem_type: str,
                                  problem_characteristics: Dict[str, Any]) -> Tuple[str, bool, str]:
        """
        Select solver with automatic fallback logic
        
        Args:
            primary_solver: Preferred primary solver
            problem_type: Type of optimization problem
            problem_characteristics: Problem characteristics for adaptation
            
        Returns:
            Tuple of (selected_solver, is_fallback, reason)
        """
        with self._lock:
            # Check if primary solver is available and healthy
            if self._is_solver_usable(primary_solver):
                return primary_solver, False, "primary_solver_available"
            
            # Get fallback options
            fallback_solvers = self._get_fallback_solvers(primary_solver, problem_type)
            
            # Select best available fallback
            for fallback_solver in fallback_solvers:
                if self._is_solver_usable(fallback_solver):
                    reason = f"fallback_from_{primary_solver}"
                    logger.info(f"Using fallback solver {fallback_solver} for {problem_type} (reason: {reason})")
                    return fallback_solver, True, reason
            
            # If no exact fallbacks, try alternative problem formulations
            alternative_solver = self._find_alternative_formulation(problem_type, problem_characteristics)
            if alternative_solver:
                reason = f"alternative_formulation_from_{primary_solver}"
                logger.warning(f"Using alternative formulation with {alternative_solver} (reason: {reason})")
                return alternative_solver, True, reason
            
            # Last resort: return any available solver
            available_solvers = self.registry.get_available_solvers()
            for solver_name in available_solvers:
                if self._is_solver_usable(solver_name):
                    reason = f"last_resort_from_{primary_solver}"
                    logger.error(f"Using last resort solver {solver_name} (reason: {reason})")
                    return solver_name, True, reason
            
            # No solvers available - critical system failure
            logger.critical("No solvers available - system in critical degradation state")
            raise RuntimeError("No optimization solvers available - system failure")
    
    def _is_solver_usable(self, solver_name: str) -> bool:
        """Check if a solver is usable (available and not circuit broken)"""
        
        # Check basic availability
        if not self.registry.check_solver_availability(solver_name):
            return False
        
        # Check circuit breaker state
        if solver_name in self.circuit_breakers:
            circuit = self.circuit_breakers[solver_name]
            
            if circuit["state"] == "open":
                # Check if recovery timeout has passed
                if (circuit["last_failure_time"] and 
                    datetime.now() - circuit["last_failure_time"] > timedelta(seconds=circuit["recovery_timeout"])):
                    # Move to half-open state
                    circuit["state"] = "half_open"
                    logger.info(f"Circuit breaker for {solver_name} moved to half-open state")
                    return True
                else:
                    return False
        
        # Check health score
        if solver_name in self.solver_health:
            health = self.solver_health[solver_name]
            if health.health_score < self.failure_thresholds["health_score_threshold"]:
                return False
        
        return True
    
    def _get_fallback_solvers(self, primary_solver: str, problem_type: str) -> List[str]:
        """Get ordered list of fallback solvers"""
        
        fallback_options = []
        
        # 1. Problem type-specific fallbacks
        if problem_type in self.fallback_chains:
            chain = self.fallback_chains[problem_type]
            fallback_options.extend([s for s in chain if s != primary_solver])
        
        # 2. Category-based fallbacks
        if primary_solver in self.registry.solvers:
            primary_category = self.registry.solvers[primary_solver].category
            category_chain = self.fallback_chains.get(primary_category.value, [])
            fallback_options.extend([s for s in category_chain if s != primary_solver and s not in fallback_options])
        
        # 3. Performance-based alternatives
        if "performance" in self.alternative_mappings:
            perf_alternatives = self.alternative_mappings["performance"].get(primary_solver, [])
            fallback_options.extend([s for s in perf_alternatives if s not in fallback_options])
        
        # 4. Robust alternatives
        if "robust" in self.alternative_mappings:
            robust_alternatives = self.alternative_mappings["robust"].get(primary_solver, [])
            fallback_options.extend([s for s in robust_alternatives if s not in fallback_options])
        
        # Sort by health score (best first)
        fallback_options.sort(key=lambda s: self.solver_health.get(s, SolverHealthMetrics("", 0, 0, 0, 0, 0, None, None, 0, 0, "")).health_score, reverse=True)
        
        return fallback_options
    
    def _find_alternative_formulation(self, problem_type: str, problem_characteristics: Dict[str, Any]) -> Optional[str]:
        """Find alternative problem formulation when direct fallbacks fail"""
        
        # Problem adaptation strategies
        adaptations = {
            "mixed_integer_programming": [
                ("linear_programming", "relax_integer_variables"),
                ("constraint_programming", "reformulate_as_cp"),
                ("metaheuristic", "use_heuristic_approach")
            ],
            
            "constraint_programming": [
                ("mixed_integer_programming", "linearize_constraints"),
                ("metaheuristic", "use_evolutionary_approach")
            ],
            
            "nonlinear_programming": [
                ("linear_programming", "linearize_objective"),
                ("mixed_integer_programming", "piecewise_linear_approximation"),
                ("metaheuristic", "use_gradient_free_method")
            ]
        }
        
        if problem_type in adaptations:
            for alt_type, adaptation_method in adaptations[problem_type]:
                if alt_type in self.fallback_chains:
                    for solver_name in self.fallback_chains[alt_type]:
                        if self._is_solver_usable(solver_name):
                            logger.info(f"Found alternative formulation: {alt_type} using {solver_name} ({adaptation_method})")
                            return solver_name
        
        return None
    
    def handle_solver_failure(self, solver_name: str, problem_type: str, 
                            failure_reason: DegradationReason, error_details: Dict[str, Any]) -> Optional[str]:
        """
        Handle solver failure and return fallback solver
        
        Args:
            solver_name: Name of the failed solver
            problem_type: Type of optimization problem
            failure_reason: Reason for the failure
            error_details: Detailed error information
            
        Returns:
            Name of fallback solver if available, None otherwise
        """
        with self._lock:
            # Record degradation event
            degradation_event = DegradationEvent(
                timestamp=datetime.now(),
                solver_name=solver_name,
                problem_type=problem_type,
                reason=failure_reason,
                fallback_solver=None,
                success=False,
                recovery_time=0.0,
                impact_level=self._assess_impact_level(failure_reason),
                details=error_details
            )
            
            # Update solver health
            self._update_solver_health(solver_name, success=False, failure_reason=failure_reason)
            
            # Update circuit breaker
            self._update_circuit_breaker(solver_name, success=False)
            
            # Find fallback solver
            try:
                fallback_solver, is_fallback, reason = self.select_solver_with_fallback(
                    solver_name, problem_type, error_details.get("problem_characteristics", {})
                )
                
                if is_fallback:
                    degradation_event.fallback_solver = fallback_solver
                    degradation_event.success = True
                    logger.info(f"Successfully found fallback solver {fallback_solver} for failed {solver_name}")
                    
                    # Update system degradation level
                    self._update_system_degradation_level()
                    
                    # Record event
                    self.degradation_events.append(degradation_event)
                    
                    return fallback_solver
                
            except RuntimeError as e:
                logger.critical(f"Failed to find fallback for {solver_name}: {e}")
                degradation_event.impact_level = DegradationLevel.CRITICAL
            
            # Record failed degradation event
            self.degradation_events.append(degradation_event)
            
            # Update system health
            self._update_system_health()
            
            return None
    
    def handle_solver_success(self, solver_name: str, solve_time: float, solution_quality: float):
        """
        Handle successful solver execution
        
        Args:
            solver_name: Name of the successful solver
            solve_time: Time taken to solve
            solution_quality: Quality of the solution
        """
        with self._lock:
            # Update solver health
            self._update_solver_health(solver_name, success=True, solve_time=solve_time, quality=solution_quality)
            
            # Update circuit breaker
            self._update_circuit_breaker(solver_name, success=True)
            
            # Update system health
            self._update_system_health()
    
    def _update_solver_health(self, solver_name: str, success: bool, failure_reason: Optional[DegradationReason] = None,
                            solve_time: Optional[float] = None, quality: Optional[float] = None):
        """Update health metrics for a solver"""
        
        if solver_name not in self.solver_health:
            self._initialize_solver_health()
        
        health = self.solver_health[solver_name]
        
        if success:
            health.last_success = datetime.now()
            health.consecutive_failures = 0
            
            if solve_time is not None:
                # Update average solve time (exponential moving average)
                alpha = 0.1
                health.average_solve_time = alpha * solve_time + (1 - alpha) * health.average_solve_time
        
        else:
            health.last_failure = datetime.now()
            health.consecutive_failures += 1
            
            # Update failure rates based on reason
            if failure_reason == DegradationReason.SOLVER_TIMEOUT:
                health.timeout_rate = min(health.timeout_rate + 0.1, 1.0)
            elif failure_reason == DegradationReason.SOLVER_CRASH:
                health.crash_rate = min(health.crash_rate + 0.1, 1.0)
            else:
                health.error_rate = min(health.error_rate + 0.1, 1.0)
        
        # Update success rate (exponential moving average)
        alpha = 0.1
        new_success = 1.0 if success else 0.0
        health.success_rate = alpha * new_success + (1 - alpha) * health.success_rate
        
        # Calculate health score
        health.health_score = self._calculate_health_score(health)
        
        # Update status
        health.status = self._determine_health_status(health)
    
    def _calculate_health_score(self, health: SolverHealthMetrics) -> float:
        """Calculate overall health score for a solver"""
        
        # Weighted combination of metrics
        weights = {
            "success_rate": 0.4,
            "error_rate": 0.2,
            "timeout_rate": 0.2,
            "crash_rate": 0.1,
            "consecutive_failures": 0.1
        }
        
        score = (
            weights["success_rate"] * health.success_rate +
            weights["error_rate"] * (1.0 - health.error_rate) +
            weights["timeout_rate"] * (1.0 - health.timeout_rate) +
            weights["crash_rate"] * (1.0 - health.crash_rate) +
            weights["consecutive_failures"] * max(0, 1.0 - health.consecutive_failures / 10.0)
        )
        
        return max(0.0, min(1.0, score))
    
    def _determine_health_status(self, health: SolverHealthMetrics) -> str:
        """Determine health status based on metrics"""
        
        if health.health_score >= 0.8:
            return "healthy"
        elif health.health_score >= 0.6:
            return "degraded"
        elif health.health_score >= 0.3:
            return "unhealthy"
        else:
            return "critical"
    
    def _update_circuit_breaker(self, solver_name: str, success: bool):
        """Update circuit breaker state for a solver"""
        
        if solver_name not in self.circuit_breakers:
            return
        
        circuit = self.circuit_breakers[solver_name]
        
        if success:
            if circuit["state"] == "half_open":
                circuit["failure_count"] = 0
                if circuit.get("success_count", 0) >= circuit["success_threshold"]:
                    circuit["state"] = "closed"
                    logger.info(f"Circuit breaker for {solver_name} closed after recovery")
                else:
                    circuit["success_count"] = circuit.get("success_count", 0) + 1
            elif circuit["state"] == "closed":
                circuit["failure_count"] = max(0, circuit["failure_count"] - 1)
        
        else:
            circuit["failure_count"] += 1
            circuit["last_failure_time"] = datetime.now()
            
            if circuit["failure_count"] >= circuit["failure_threshold"]:
                if circuit["state"] != "open":
                    circuit["state"] = "open"
                    logger.warning(f"Circuit breaker for {solver_name} opened due to repeated failures")
    
    def _assess_impact_level(self, failure_reason: DegradationReason) -> DegradationLevel:
        """Assess the impact level of a failure"""
        
        impact_mapping = {
            DegradationReason.SOLVER_UNAVAILABLE: DegradationLevel.MODERATE,
            DegradationReason.SOLVER_TIMEOUT: DegradationLevel.MINIMAL,
            DegradationReason.SOLVER_ERROR: DegradationLevel.MODERATE,
            DegradationReason.SOLVER_CRASH: DegradationLevel.SEVERE,
            DegradationReason.MEMORY_EXHAUSTION: DegradationLevel.SEVERE,
            DegradationReason.POOR_PERFORMANCE: DegradationLevel.MINIMAL,
            DegradationReason.RESOURCE_LIMIT: DegradationLevel.MODERATE,
            DegradationReason.SYSTEM_OVERLOAD: DegradationLevel.CRITICAL
        }
        
        return impact_mapping.get(failure_reason, DegradationLevel.MODERATE)
    
    def _update_system_degradation_level(self):
        """Update overall system degradation level"""
        
        # Count recent degradation events
        recent_events = [
            event for event in self.degradation_events[-20:]  # Last 20 events
            if (datetime.now() - event.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        if not recent_events:
            self.current_degradation_level = DegradationLevel.NONE
            return
        
        # Assess degradation level based on recent events
        severe_events = sum(1 for event in recent_events if event.impact_level in [DegradationLevel.SEVERE, DegradationLevel.CRITICAL])
        moderate_events = sum(1 for event in recent_events if event.impact_level == DegradationLevel.MODERATE)
        
        if severe_events >= 3:
            self.current_degradation_level = DegradationLevel.CRITICAL
        elif severe_events >= 1 or moderate_events >= 5:
            self.current_degradation_level = DegradationLevel.SEVERE
        elif moderate_events >= 2:
            self.current_degradation_level = DegradationLevel.MODERATE
        elif len(recent_events) >= 3:
            self.current_degradation_level = DegradationLevel.MINIMAL
        else:
            self.current_degradation_level = DegradationLevel.NONE
    
    def _update_system_health(self):
        """Update overall system health score"""
        
        if not self.solver_health:
            self.system_health_score = 0.0
            return
        
        # Calculate weighted average of solver health scores
        total_weight = 0
        weighted_sum = 0
        
        for solver_name, health in self.solver_health.items():
            # Weight by solver importance (based on availability and usage)
            weight = 1.0
            if self.registry.check_solver_availability(solver_name):
                weight *= 2.0  # Available solvers get higher weight
            
            weighted_sum += health.health_score * weight
            total_weight += weight
        
        self.system_health_score = weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        with self._lock:
            # Update health if needed
            if datetime.now() - self.last_health_check > self.health_check_interval:
                self._update_system_health()
                self.last_health_check = datetime.now()
            
            available_solvers = len([s for s in self.solver_health.values() if s.status in ["healthy", "degraded"]])
            total_solvers = len(self.solver_health)
            
            recent_events = [
                event for event in self.degradation_events[-10:]
                if (datetime.now() - event.timestamp).total_seconds() < 3600
            ]
            
            return {
                "system_health_score": self.system_health_score,
                "degradation_level": self.current_degradation_level.value,
                "available_solvers": available_solvers,
                "total_solvers": total_solvers,
                "availability_rate": available_solvers / total_solvers if total_solvers > 0 else 0.0,
                "recent_degradation_events": len(recent_events),
                "circuit_breakers_open": len([cb for cb in self.circuit_breakers.values() if cb["state"] == "open"]),
                "solver_health_summary": {
                    name: {
                        "status": health.status,
                        "health_score": health.health_score,
                        "success_rate": health.success_rate,
                        "consecutive_failures": health.consecutive_failures
                    }
                    for name, health in self.solver_health.items()
                },
                "last_updated": datetime.now().isoformat()
            }
    
    def get_degradation_report(self, hours: int = 24) -> Dict[str, Any]:
        """Get detailed degradation report for the specified time period"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [event for event in self.degradation_events if event.timestamp >= cutoff_time]
        
        # Group events by solver and reason
        events_by_solver = defaultdict(list)
        events_by_reason = defaultdict(list)
        
        for event in recent_events:
            events_by_solver[event.solver_name].append(event)
            events_by_reason[event.reason.value].append(event)
        
        # Calculate statistics
        total_events = len(recent_events)
        successful_fallbacks = len([e for e in recent_events if e.success])
        
        return {
            "time_period_hours": hours,
            "total_degradation_events": total_events,
            "successful_fallbacks": successful_fallbacks,
            "fallback_success_rate": successful_fallbacks / total_events if total_events > 0 else 1.0,
            "events_by_solver": {
                solver: len(events) for solver, events in events_by_solver.items()
            },
            "events_by_reason": {
                reason: len(events) for reason, events in events_by_reason.items()
            },
            "impact_distribution": {
                level.value: len([e for e in recent_events if e.impact_level == level])
                for level in DegradationLevel
            },
            "most_problematic_solvers": sorted(
                events_by_solver.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:5],
            "recommendations": self._generate_degradation_recommendations(recent_events)
        }
    
    def _generate_degradation_recommendations(self, recent_events: List[DegradationEvent]) -> List[str]:
        """Generate recommendations based on degradation patterns"""
        
        recommendations = []
        
        # Analyze patterns
        solver_failures = defaultdict(int)
        reason_counts = defaultdict(int)
        
        for event in recent_events:
            solver_failures[event.solver_name] += 1
            reason_counts[event.reason] += 1
        
        # Generate recommendations
        if reason_counts[DegradationReason.SOLVER_TIMEOUT] > 3:
            recommendations.append("Consider increasing timeout limits for frequently timing out solvers")
        
        if reason_counts[DegradationReason.MEMORY_EXHAUSTION] > 1:
            recommendations.append("Monitor system memory usage and consider using more memory-efficient solvers")
        
        if reason_counts[DegradationReason.SOLVER_CRASH] > 1:
            recommendations.append("Investigate solver crashes and consider updating solver versions")
        
        # Solver-specific recommendations
        for solver_name, failure_count in solver_failures.items():
            if failure_count > 5:
                recommendations.append(f"Consider temporarily disabling {solver_name} due to high failure rate")
        
        if not recommendations:
            recommendations.append("System is operating within normal parameters")
        
        return recommendations
    
    def reset_circuit_breaker(self, solver_name: str) -> bool:
        """
        Manually reset circuit breaker for a solver
        
        Args:
            solver_name: Name of the solver
            
        Returns:
            True if reset successfully, False otherwise
        """
        with self._lock:
            if solver_name in self.circuit_breakers:
                circuit = self.circuit_breakers[solver_name]
                circuit["state"] = "closed"
                circuit["failure_count"] = 0
                circuit["last_failure_time"] = None
                
                logger.info(f"Circuit breaker for {solver_name} manually reset")
                return True
            
            return False
    
    def force_solver_recovery(self, solver_name: str) -> bool:
        """
        Force recovery attempt for a solver
        
        Args:
            solver_name: Name of the solver
            
        Returns:
            True if recovery successful, False otherwise
        """
        try:
            # Reset circuit breaker
            self.reset_circuit_breaker(solver_name)
            
            # Reset health metrics
            if solver_name in self.solver_health:
                health = self.solver_health[solver_name]
                health.consecutive_failures = 0
                health.error_rate *= 0.5  # Reduce error rates
                health.timeout_rate *= 0.5
                health.crash_rate *= 0.5
                health.health_score = self._calculate_health_score(health)
                health.status = self._determine_health_status(health)
            
            # Test solver availability
            if self.registry.check_solver_availability(solver_name):
                logger.info(f"Solver {solver_name} recovery successful")
                return True
            else:
                logger.warning(f"Solver {solver_name} still not available after recovery attempt")
                return False
                
        except Exception as e:
            logger.error(f"Error during forced recovery of {solver_name}: {e}")
            return False


# Global degradation system instance
graceful_degradation_system = GracefulDegradationSystem()


def get_graceful_degradation_system() -> GracefulDegradationSystem:
    """Get the global graceful degradation system instance"""
    return graceful_degradation_system