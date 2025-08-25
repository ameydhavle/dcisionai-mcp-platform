"""
Multi-Solver Registry Integration Module
=======================================

Integrates all components of the enhanced solver registry system:
- Enhanced Solver Registry (15+ solvers across 5 categories)
- Solver Detection and Registration System
- Solver Configuration Management
- Graceful Degradation System

Provides unified interface for multi-solver swarm optimization.

Requirements: 1.1, 1.2, 1.3, 1.4
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from .enhanced_solver_registry import enhanced_solver_registry, SolverCategory
from .solver_detection_system import solver_detection_system
from .solver_configuration_manager import solver_configuration_manager
from .graceful_degradation_system import graceful_degradation_system, DegradationReason

logger = logging.getLogger(__name__)


@dataclass
class SolverSelectionResult:
    """Result of solver selection process"""
    selected_solver: str
    is_fallback: bool
    fallback_reason: Optional[str]
    configuration: Dict[str, Any]
    alternatives: List[str]
    confidence_score: float
    selection_time: float


@dataclass
class MultiSolverRegistryStatus:
    """Comprehensive status of the multi-solver registry system"""
    total_registered_solvers: int
    available_solvers: int
    healthy_solvers: int
    degraded_solvers: int
    unavailable_solvers: int
    system_health_score: float
    degradation_level: str
    last_discovery_time: Optional[datetime]
    circuit_breakers_open: int
    recent_failures: int
    solver_categories: Dict[str, Dict[str, int]]


class MultiSolverRegistryIntegration:
    """
    Unified interface for the multi-solver registry system
    
    Integrates all components to provide comprehensive solver management,
    selection, configuration, and degradation handling.
    """
    
    def __init__(self):
        self.registry = enhanced_solver_registry
        self.detection_system = solver_detection_system
        self.config_manager = solver_configuration_manager
        self.degradation_system = graceful_degradation_system
        
        # System initialization
        self._initialized = False
        self._initialization_time = None
        
        logger.info("Multi-solver registry integration initialized")
    
    async def initialize_system(self, perform_discovery: bool = True) -> Dict[str, Any]:
        """
        Initialize the complete multi-solver registry system
        
        Args:
            perform_discovery: Whether to perform initial solver discovery
            
        Returns:
            Initialization results and system status
        """
        start_time = time.time()
        
        try:
            logger.info("Initializing multi-solver registry system...")
            
            initialization_results = {
                "success": False,
                "initialization_time": 0.0,
                "discovery_results": {},
                "system_status": {},
                "errors": []
            }
            
            # Perform solver discovery if requested
            if perform_discovery:
                logger.info("Performing comprehensive solver discovery...")
                discovery_results = self.detection_system.discover_all_solvers()
                initialization_results["discovery_results"] = {
                    name: result.found for name, result in discovery_results.items()
                }
                
                # Log discovery summary
                found_count = sum(1 for result in discovery_results.values() if result.found)
                total_count = len(discovery_results)
                logger.info(f"Solver discovery complete: {found_count}/{total_count} solvers found")
            
            # Get system status
            system_status = await self.get_system_status()
            initialization_results["system_status"] = system_status
            
            # Mark as initialized
            self._initialized = True
            self._initialization_time = datetime.now()
            
            initialization_results["success"] = True
            initialization_results["initialization_time"] = time.time() - start_time
            
            logger.info(f"Multi-solver registry system initialized successfully in {initialization_results['initialization_time']:.2f}s")
            
            return initialization_results
            
        except Exception as e:
            error_msg = f"Failed to initialize multi-solver registry system: {str(e)}"
            logger.error(error_msg)
            
            return {
                "success": False,
                "initialization_time": time.time() - start_time,
                "error": error_msg,
                "system_status": {}
            }
    
    async def select_optimal_solver(self, problem_type: str, problem_characteristics: Dict[str, Any],
                                  solver_preference: Optional[str] = None) -> SolverSelectionResult:
        """
        Select optimal solver with comprehensive fallback logic
        
        Args:
            problem_type: Type of optimization problem
            problem_characteristics: Characteristics of the specific problem
            solver_preference: Preferred solver (optional)
            
        Returns:
            Solver selection result with configuration and alternatives
        """
        start_time = time.time()
        
        try:
            # Determine primary solver
            if solver_preference:
                primary_solver = solver_preference
            else:
                primary_solver = self._select_best_solver_for_problem(problem_type, problem_characteristics)
            
            # Use degradation system for intelligent selection with fallback
            selected_solver, is_fallback, fallback_reason = self.degradation_system.select_solver_with_fallback(
                primary_solver, problem_type, problem_characteristics
            )
            
            # Get optimized configuration
            configuration = self.config_manager.optimize_configuration(
                selected_solver, problem_type, problem_characteristics
            )
            
            # Get alternative solvers
            alternatives = self.registry.get_compatible_solvers(problem_type)
            alternatives = [s for s in alternatives if s != selected_solver][:3]  # Top 3 alternatives
            
            # Calculate confidence score
            confidence_score = self._calculate_selection_confidence(
                selected_solver, problem_type, is_fallback
            )
            
            selection_time = time.time() - start_time
            
            result = SolverSelectionResult(
                selected_solver=selected_solver,
                is_fallback=is_fallback,
                fallback_reason=fallback_reason if is_fallback else None,
                configuration=configuration,
                alternatives=alternatives,
                confidence_score=confidence_score,
                selection_time=selection_time
            )
            
            logger.info(f"Selected solver {selected_solver} for {problem_type} "
                       f"(fallback: {is_fallback}, confidence: {confidence_score:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in solver selection: {str(e)}")
            raise RuntimeError(f"Solver selection failed: {str(e)}")
    
    def _select_best_solver_for_problem(self, problem_type: str, problem_characteristics: Dict[str, Any]) -> str:
        """Select the best solver for a problem based on characteristics"""
        
        # Get compatible solvers
        problem_size = self._categorize_problem_size(problem_characteristics)
        compatible_solvers = self.registry.get_compatible_solvers(problem_type, problem_size)
        
        if not compatible_solvers:
            raise ValueError(f"No compatible solvers found for problem type: {problem_type}")
        
        # Score solvers based on multiple criteria
        solver_scores = {}
        
        for solver_name in compatible_solvers:
            score = self._score_solver_for_problem(solver_name, problem_type, problem_characteristics)
            solver_scores[solver_name] = score
        
        # Return highest scoring solver
        best_solver = max(solver_scores, key=solver_scores.get)
        logger.debug(f"Best solver for {problem_type}: {best_solver} (score: {solver_scores[best_solver]:.3f})")
        
        return best_solver
    
    def _categorize_problem_size(self, problem_characteristics: Dict[str, Any]) -> str:
        """Categorize problem size based on characteristics"""
        
        num_variables = problem_characteristics.get("num_variables", 0)
        num_constraints = problem_characteristics.get("num_constraints", 0)
        
        # Simple size categorization
        if num_variables <= 100 and num_constraints <= 50:
            return "small"
        elif num_variables <= 10000 and num_constraints <= 5000:
            return "medium"
        else:
            return "large"
    
    def _score_solver_for_problem(self, solver_name: str, problem_type: str, 
                                problem_characteristics: Dict[str, Any]) -> float:
        """Score a solver for a specific problem"""
        
        if solver_name not in self.registry.solvers:
            return 0.0
        
        solver_capability = self.registry.solvers[solver_name]
        
        # Base score from performance profile
        problem_size = self._categorize_problem_size(problem_characteristics)
        base_score = solver_capability.performance_profile.get(f"{problem_size}_problems", 3) / 5.0
        
        # Health score from degradation system
        health_score = 1.0
        if solver_name in self.degradation_system.solver_health:
            health_score = self.degradation_system.solver_health[solver_name].health_score
        
        # Availability bonus
        availability_bonus = 0.2 if self.registry.check_solver_availability(solver_name) else 0.0
        
        # Problem type match bonus
        type_match_bonus = 0.1 if problem_type in solver_capability.problem_types else 0.0
        
        # Combine scores
        total_score = (
            0.4 * base_score +
            0.3 * health_score +
            0.2 * availability_bonus +
            0.1 * type_match_bonus
        )
        
        return total_score
    
    def _calculate_selection_confidence(self, solver_name: str, problem_type: str, is_fallback: bool) -> float:
        """Calculate confidence score for solver selection"""
        
        base_confidence = 0.5 if is_fallback else 0.8
        
        # Adjust based on solver health
        if solver_name in self.degradation_system.solver_health:
            health = self.degradation_system.solver_health[solver_name]
            health_factor = health.health_score
            base_confidence *= health_factor
        
        # Adjust based on problem type match
        if solver_name in self.registry.solvers:
            solver_capability = self.registry.solvers[solver_name]
            if problem_type in solver_capability.problem_types:
                base_confidence *= 1.2
        
        return min(1.0, base_confidence)
    
    async def handle_solver_execution_result(self, solver_name: str, problem_type: str,
                                           configuration: Dict[str, Any], 
                                           execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle solver execution result and update system state
        
        Args:
            solver_name: Name of the executed solver
            problem_type: Type of optimization problem
            configuration: Configuration used
            execution_result: Result of solver execution
            
        Returns:
            Updated system information
        """
        try:
            success = execution_result.get("success", False)
            solve_time = execution_result.get("solve_time", 0.0)
            solution_quality = execution_result.get("solution_quality", 0.0)
            
            if success:
                # Handle successful execution
                self.degradation_system.handle_solver_success(solver_name, solve_time, solution_quality)
                
                # Record performance for configuration optimization
                self.config_manager.record_performance(
                    solver_name, problem_type, configuration, execution_result
                )
                
                logger.debug(f"Recorded successful execution for {solver_name}: {solve_time:.3f}s")
                
            else:
                # Handle failure
                error_details = execution_result.get("error_details", {})
                failure_reason = self._determine_failure_reason(execution_result)
                
                fallback_solver = self.degradation_system.handle_solver_failure(
                    solver_name, problem_type, failure_reason, error_details
                )
                
                logger.warning(f"Handled failure for {solver_name}, fallback: {fallback_solver}")
                
                return {
                    "success": False,
                    "fallback_solver": fallback_solver,
                    "failure_reason": failure_reason.value,
                    "system_status": await self.get_system_status()
                }
            
            return {
                "success": True,
                "system_status": await self.get_system_status()
            }
            
        except Exception as e:
            logger.error(f"Error handling solver execution result: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_failure_reason(self, execution_result: Dict[str, Any]) -> DegradationReason:
        """Determine the reason for solver failure"""
        
        error_type = execution_result.get("error_type", "")
        error_message = execution_result.get("error", "")
        
        if "timeout" in error_message.lower() or "time limit" in error_message.lower():
            return DegradationReason.SOLVER_TIMEOUT
        elif "memory" in error_message.lower() or "out of memory" in error_message.lower():
            return DegradationReason.MEMORY_EXHAUSTION
        elif "crash" in error_message.lower() or "segmentation fault" in error_message.lower():
            return DegradationReason.SOLVER_CRASH
        elif "not available" in error_message.lower() or "not found" in error_message.lower():
            return DegradationReason.SOLVER_UNAVAILABLE
        else:
            return DegradationReason.SOLVER_ERROR
    
    async def get_system_status(self) -> MultiSolverRegistryStatus:
        """Get comprehensive system status"""
        
        # Get basic registry statistics
        registry_stats = self.registry.get_solver_statistics()
        
        # Get degradation system status
        degradation_status = self.degradation_system.get_system_status()
        
        # Count solvers by health status
        healthy_solvers = len([
            h for h in self.degradation_system.solver_health.values() 
            if h.status == "healthy"
        ])
        
        degraded_solvers = len([
            h for h in self.degradation_system.solver_health.values() 
            if h.status == "degraded"
        ])
        
        unavailable_solvers = registry_stats["total_solvers"] - registry_stats["available_solvers"]
        
        # Categorize solvers by category and status
        solver_categories = {}
        for category in SolverCategory:
            category_solvers = [
                name for name, capability in self.registry.solvers.items()
                if capability.category == category
            ]
            
            solver_categories[category.value] = {
                "total": len(category_solvers),
                "available": len([s for s in category_solvers if self.registry.check_solver_availability(s)]),
                "healthy": len([
                    s for s in category_solvers 
                    if s in self.degradation_system.solver_health and 
                    self.degradation_system.solver_health[s].status == "healthy"
                ])
            }
        
        return MultiSolverRegistryStatus(
            total_registered_solvers=registry_stats["total_solvers"],
            available_solvers=registry_stats["available_solvers"],
            healthy_solvers=healthy_solvers,
            degraded_solvers=degraded_solvers,
            unavailable_solvers=unavailable_solvers,
            system_health_score=degradation_status["system_health_score"],
            degradation_level=degradation_status["degradation_level"],
            last_discovery_time=self._initialization_time,
            circuit_breakers_open=degradation_status["circuit_breakers_open"],
            recent_failures=degradation_status["recent_degradation_events"],
            solver_categories=solver_categories
        )
    
    async def refresh_system(self) -> Dict[str, Any]:
        """Refresh the entire system (discovery, health checks, etc.)"""
        
        start_time = time.time()
        
        try:
            logger.info("Refreshing multi-solver registry system...")
            
            # Refresh solver availability
            self.registry.refresh_availability()
            
            # Perform new discovery
            discovery_results = self.detection_system.discover_all_solvers()
            
            # Get updated system status
            system_status = await self.get_system_status()
            
            refresh_time = time.time() - start_time
            
            logger.info(f"System refresh completed in {refresh_time:.2f}s")
            
            return {
                "success": True,
                "refresh_time": refresh_time,
                "discovery_results": {
                    name: result.found for name, result in discovery_results.items()
                },
                "system_status": asdict(system_status)
            }
            
        except Exception as e:
            logger.error(f"Error during system refresh: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "refresh_time": time.time() - start_time
            }
    
    def get_solver_recommendations(self, problem_type: str, 
                                 problem_characteristics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get solver recommendations for a problem"""
        
        recommendations = []
        
        # Get compatible solvers with scores
        compatible_solvers = self.registry.get_compatible_solvers(problem_type)
        
        for solver_name in compatible_solvers[:5]:  # Top 5 recommendations
            score = self._score_solver_for_problem(solver_name, problem_type, problem_characteristics)
            
            # Get solver info
            solver_capability = self.registry.solvers.get(solver_name)
            health = self.degradation_system.solver_health.get(solver_name)
            
            recommendation = {
                "solver_name": solver_name,
                "suitability_score": score,
                "category": solver_capability.category.value if solver_capability else "unknown",
                "health_status": health.status if health else "unknown",
                "health_score": health.health_score if health else 0.0,
                "available": self.registry.check_solver_availability(solver_name),
                "reasons": []
            }
            
            # Add recommendation reasons
            if score > 0.8:
                recommendation["reasons"].append("Excellent match for problem type")
            elif score > 0.6:
                recommendation["reasons"].append("Good match for problem type")
            
            if health and health.health_score > 0.9:
                recommendation["reasons"].append("Excellent reliability")
            elif health and health.health_score > 0.7:
                recommendation["reasons"].append("Good reliability")
            
            if solver_capability and solver_capability.memory_efficient:
                recommendation["reasons"].append("Memory efficient")
            
            if solver_capability and solver_capability.parallel_capable:
                recommendation["reasons"].append("Supports parallel execution")
            
            recommendations.append(recommendation)
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return recommendations
    
    def export_system_configuration(self) -> Dict[str, Any]:
        """Export complete system configuration and state"""
        
        return {
            "registry_export": self.registry.export_registry(),
            "configuration_export": self.config_manager.export_configurations(),
            "degradation_report": self.degradation_system.get_degradation_report(24),
            "discovery_summary": self.detection_system.get_discovery_summary(),
            "system_metadata": {
                "initialized": self._initialized,
                "initialization_time": self._initialization_time.isoformat() if self._initialization_time else None,
                "export_timestamp": datetime.now().isoformat()
            }
        }


# Global integration instance
multi_solver_registry = MultiSolverRegistryIntegration()


def get_multi_solver_registry() -> MultiSolverRegistryIntegration:
    """Get the global multi-solver registry integration instance"""
    return multi_solver_registry


# Convenience functions for external use
async def initialize_multi_solver_system(perform_discovery: bool = True) -> Dict[str, Any]:
    """Initialize the multi-solver registry system"""
    return await multi_solver_registry.initialize_system(perform_discovery)


async def select_solver_for_problem(problem_type: str, problem_characteristics: Dict[str, Any],
                                   solver_preference: Optional[str] = None) -> SolverSelectionResult:
    """Select optimal solver for a problem"""
    return await multi_solver_registry.select_optimal_solver(
        problem_type, problem_characteristics, solver_preference
    )


def get_solver_recommendations_for_problem(problem_type: str, 
                                         problem_characteristics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get solver recommendations for a problem"""
    return multi_solver_registry.get_solver_recommendations(problem_type, problem_characteristics)


async def get_multi_solver_system_status() -> MultiSolverRegistryStatus:
    """Get comprehensive system status"""
    return await multi_solver_registry.get_system_status()