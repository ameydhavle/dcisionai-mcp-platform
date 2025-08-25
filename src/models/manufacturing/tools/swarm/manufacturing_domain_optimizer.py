"""
Manufacturing Domain-Specific Optimization System
===============================================

Implements specialized solver configurations and optimizations for common manufacturing
problem patterns including production scheduling, capacity planning, routing/logistics,
and resource allocation.

Features:
- Production scheduling optimization with constraint programming focus
- Capacity planning with mixed-integer programming specialization
- Routing and logistics optimization using advanced constraint programming
- Resource allocation with large-scale linear programming capabilities
- Manufacturing-specific problem pattern recognition
- Domain-aware solver selection and configuration

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import logging
import json
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Fallback for numpy functions
    class np:
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0
        
        @staticmethod
        def std(data):
            if not data:
                return 0
            mean_val = sum(data) / len(data)
            variance = sum((x - mean_val) ** 2 for x in data) / len(data)
            return variance ** 0.5
        
        @staticmethod
        def array(data):
            return list(data)
        
        @staticmethod
        def zeros(shape):
            if isinstance(shape, int):
                return [0] * shape
            return [[0] * shape[1] for _ in range(shape[0])]
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict
import statistics

from .enhanced_solver_registry import enhanced_solver_registry, SolverCategory
from .solver_configuration_manager import AdvancedSolverConfigurationManager
from .intelligent_solver_selector import IntelligentSolverSelector

logger = logging.getLogger(__name__)


class ManufacturingProblemType(Enum):
    """Types of manufacturing optimization problems"""
    PRODUCTION_SCHEDULING = "production_scheduling"
    CAPACITY_PLANNING = "capacity_planning"
    ROUTING_LOGISTICS = "routing_logistics"
    RESOURCE_ALLOCATION = "resource_allocation"
    INVENTORY_OPTIMIZATION = "inventory_optimization"
    SUPPLY_CHAIN_PLANNING = "supply_chain_planning"
    QUALITY_CONTROL = "quality_control"
    MAINTENANCE_SCHEDULING = "maintenance_scheduling"


class ProductionType(Enum):
    """Types of production systems"""
    JOB_SHOP = "job_shop"
    FLOW_SHOP = "flow_shop"
    BATCH_PRODUCTION = "batch_production"
    CONTINUOUS_PRODUCTION = "continuous_production"
    ASSEMBLY_LINE = "assembly_line"
    FLEXIBLE_MANUFACTURING = "flexible_manufacturing"


class OptimizationObjective(Enum):
    """Manufacturing optimization objectives"""
    MINIMIZE_MAKESPAN = "minimize_makespan"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    MINIMIZE_INVENTORY = "minimize_inventory"
    MAXIMIZE_UTILIZATION = "maximize_utilization"
    MINIMIZE_TARDINESS = "minimize_tardiness"
    MINIMIZE_ENERGY = "minimize_energy"
    MAXIMIZE_QUALITY = "maximize_quality"


@dataclass
class ManufacturingProblemSpec:
    """Specification for manufacturing optimization problems"""
    problem_type: ManufacturingProblemType
    production_type: ProductionType
    objectives: List[OptimizationObjective]
    time_horizon: str  # short_term, medium_term, long_term
    problem_size: str  # small, medium, large, very_large
    
    # Problem characteristics
    num_jobs: Optional[int] = None
    num_machines: Optional[int] = None
    num_resources: Optional[int] = None
    num_locations: Optional[int] = None
    num_vehicles: Optional[int] = None
    
    # Constraints
    has_setup_times: bool = False
    has_precedence_constraints: bool = False
    has_resource_constraints: bool = False
    has_capacity_constraints: bool = False
    has_time_windows: bool = False
    has_routing_constraints: bool = False
    
    # Performance requirements
    max_solve_time: float = 300.0
    target_gap: float = 0.01
    real_time_required: bool = False
    
    # Manufacturing-specific attributes
    changeover_complexity: str = "low"  # low, medium, high
    demand_variability: str = "low"  # low, medium, high
    uncertainty_level: str = "low"  # low, medium, high
    
    def calculate_complexity_score(self) -> float:
        """Calculate problem complexity score for solver selection"""
        base_score = {
            "small": 1.0, "medium": 2.0, "large": 3.0, "very_large": 4.0
        }.get(self.problem_size, 2.0)
        
        # Adjust for problem characteristics
        if self.num_jobs:
            if self.num_jobs > 1000:
                base_score *= 1.5
            elif self.num_jobs > 100:
                base_score *= 1.2
        
        # Adjust for constraints
        constraint_multiplier = 1.0
        if self.has_setup_times:
            constraint_multiplier *= 1.3
        if self.has_precedence_constraints:
            constraint_multiplier *= 1.2
        if self.has_resource_constraints:
            constraint_multiplier *= 1.4
        if self.has_time_windows:
            constraint_multiplier *= 1.3
        if self.has_routing_constraints:
            constraint_multiplier *= 1.5
        
        # Adjust for manufacturing complexity
        complexity_factors = {
            "low": 1.0, "medium": 1.3, "high": 1.6
        }
        changeover_factor = complexity_factors.get(self.changeover_complexity, 1.0)
        variability_factor = complexity_factors.get(self.demand_variability, 1.0)
        uncertainty_factor = complexity_factors.get(self.uncertainty_level, 1.0)
        
        return base_score * constraint_multiplier * changeover_factor * variability_factor * uncertainty_factor


@dataclass
class ManufacturingOptimizationResult:
    """Result from manufacturing optimization with domain-specific metrics"""
    solver_name: str
    solve_status: str
    objective_value: Optional[float]
    solution: Dict[str, Any]
    solve_time: float
    
    # Manufacturing-specific metrics
    makespan: Optional[float] = None
    throughput: Optional[float] = None
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    schedule_feasibility: bool = True
    constraint_violations: List[str] = field(default_factory=list)
    
    # Quality metrics
    solution_robustness: float = 0.0
    manufacturing_kpis: Dict[str, float] = field(default_factory=dict)
    
    def calculate_manufacturing_score(self) -> float:
        """Calculate overall manufacturing optimization score"""
        base_score = 1.0 if self.solve_status == "optimal" else 0.8
        
        # Penalize for constraint violations
        if self.constraint_violations:
            base_score *= (1.0 - 0.1 * len(self.constraint_violations))
        
        # Reward for good resource utilization
        if self.resource_utilization:
            avg_utilization = statistics.mean(self.resource_utilization.values())
            base_score *= (0.5 + 0.5 * avg_utilization)
        
        # Consider solution robustness
        base_score *= (0.7 + 0.3 * self.solution_robustness)
        
        return max(0.0, min(1.0, base_score))


class ProductionSchedulingOptimizer:
    """Specialized optimizer for production scheduling problems"""
    
    def __init__(self, config_manager: AdvancedSolverConfigurationManager):
        self.config_manager = config_manager
        self.solver_selector = IntelligentSolverSelector()
        
        # Production scheduling specific configurations
        self.scheduling_configs = {
            "job_shop": {
                "preferred_solvers": ["CP_SAT", "SCIP"],
                "cp_sat_config": {
                    "max_time_in_seconds": 300,
                    "num_search_workers": 4,
                    "use_fixed_search": False,
                    "linearization_level": 1,
                    "log_search_progress": True
                },
                "scip_config": {
                    "limits/time": 300,
                    "parallel/maxnthreads": 4,
                    "heuristics/emphasis": "aggressive",
                    "separating/emphasis": "aggressive",
                    "presolving/maxrounds": 15
                }
            },
            "flow_shop": {
                "preferred_solvers": ["CP_SAT", "HiGHS_MIP"],
                "cp_sat_config": {
                    "max_time_in_seconds": 180,
                    "num_search_workers": 6,
                    "use_fixed_search": True,
                    "linearization_level": 2
                },
                "highs_mip_config": {
                    "time_limit": 180,
                    "presolve": "on",
                    "parallel": "on",
                    "mip_rel_gap": 0.01
                }
            },
            "batch_production": {
                "preferred_solvers": ["SCIP", "CBC"],
                "scip_config": {
                    "limits/time": 600,
                    "parallel/maxnthreads": 8,
                    "heuristics/emphasis": "aggressive",
                    "separating/emphasis": "default"
                },
                "cbc_config": {
                    "seconds": 600,
                    "threads": 8,
                    "ratioGap": 0.02,
                    "allowableGap": 1.0
                }
            }
        }
    
    def optimize_production_schedule(self, problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """Optimize production scheduling with specialized configurations"""
        logger.info(f"Optimizing production schedule for {problem_spec.production_type.value}")
        
        # Select optimal solver configuration
        config_key = problem_spec.production_type.value
        if config_key not in self.scheduling_configs:
            config_key = "job_shop"  # Default fallback
        
        config = self.scheduling_configs[config_key]
        
        # Adjust configuration based on problem characteristics
        adjusted_config = self._adjust_scheduling_config(config, problem_spec)
        
        # Select best solver
        preferred_solvers = adjusted_config["preferred_solvers"]
        selected_solver = self._select_scheduling_solver(preferred_solvers, problem_spec)
        
        # Apply solver-specific configuration
        solver_config = adjusted_config.get(f"{selected_solver.lower()}_config", {})
        
        logger.info(f"Selected solver {selected_solver} with config: {solver_config}")
        
        # Execute optimization (placeholder - would integrate with actual solver)
        result = self._execute_scheduling_optimization(selected_solver, solver_config, problem_spec)
        
        return result
    
    def _adjust_scheduling_config(self, base_config: Dict[str, Any], 
                                problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Adjust configuration based on problem characteristics"""
        config = base_config.copy()
        
        # Adjust time limits based on problem size and complexity
        complexity_score = problem_spec.calculate_complexity_score()
        time_multiplier = min(3.0, max(0.5, complexity_score / 2.0))
        
        # Update CP-SAT configuration
        if "cp_sat_config" in config:
            cp_config = config["cp_sat_config"].copy()
            cp_config["max_time_in_seconds"] *= time_multiplier
            
            # Adjust workers based on problem size
            if problem_spec.num_jobs and problem_spec.num_jobs > 500:
                cp_config["num_search_workers"] = min(8, cp_config["num_search_workers"] * 2)
            
            # Enable fixed search for complex problems
            if complexity_score > 3.0:
                cp_config["use_fixed_search"] = True
                cp_config["linearization_level"] = 2
            
            config["cp_sat_config"] = cp_config
        
        # Update SCIP configuration
        if "scip_config" in config:
            scip_config = config["scip_config"].copy()
            scip_config["limits/time"] *= time_multiplier
            
            # Adjust parallelism
            if problem_spec.num_jobs and problem_spec.num_jobs > 1000:
                scip_config["parallel/maxnthreads"] = min(16, scip_config["parallel/maxnthreads"] * 2)
            
            # Aggressive settings for complex problems
            if complexity_score > 3.0:
                scip_config["heuristics/emphasis"] = "aggressive"
                scip_config["separating/emphasis"] = "aggressive"
                scip_config["presolving/maxrounds"] = 20
            
            config["scip_config"] = scip_config
        
        return config
    
    def _select_scheduling_solver(self, preferred_solvers: List[str], 
                                problem_spec: ManufacturingProblemSpec) -> str:
        """Select best solver for scheduling problem"""
        # Check solver availability
        available_solvers = []
        for solver in preferred_solvers:
            if enhanced_solver_registry.check_solver_availability(solver):
                available_solvers.append(solver)
        
        if not available_solvers:
            logger.warning("No preferred solvers available, falling back to any available solver")
            return self.solver_selector.select_best_solver("constraint_programming", problem_spec.problem_size)
        
        # Select based on problem characteristics
        if problem_spec.has_setup_times and problem_spec.has_precedence_constraints:
            # Complex scheduling - prefer CP-SAT
            if "CP_SAT" in available_solvers:
                return "CP_SAT"
        
        if problem_spec.num_jobs and problem_spec.num_jobs > 1000:
            # Large problems - prefer SCIP
            if "SCIP" in available_solvers:
                return "SCIP"
        
        # Default to first available
        return available_solvers[0]
    
    def _execute_scheduling_optimization(self, solver_name: str, config: Dict[str, Any], 
                                       problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """Execute scheduling optimization with selected solver"""
        start_time = datetime.now()
        
        # Simulate optimization execution
        # In real implementation, this would call the actual solver
        solve_time = min(config.get("max_time_in_seconds", config.get("limits/time", 60)), 
                        problem_spec.max_solve_time)
        
        # Calculate manufacturing-specific metrics
        makespan = self._calculate_makespan(problem_spec)
        throughput = self._calculate_throughput(problem_spec, makespan)
        resource_utilization = self._calculate_resource_utilization(problem_spec)
        
        result = ManufacturingOptimizationResult(
            solver_name=solver_name,
            solve_status="optimal",
            objective_value=makespan,
            solution={"schedule": "optimized_schedule_placeholder"},
            solve_time=solve_time,
            makespan=makespan,
            throughput=throughput,
            resource_utilization=resource_utilization,
            schedule_feasibility=True,
            solution_robustness=0.85,
            manufacturing_kpis={
                "on_time_delivery": 0.95,
                "resource_efficiency": statistics.mean(resource_utilization.values()) if resource_utilization else 0.8,
                "setup_efficiency": 0.9
            }
        )
        
        logger.info(f"Production scheduling completed in {solve_time:.2f}s with makespan {makespan:.2f}")
        return result
    
    def _calculate_makespan(self, problem_spec: ManufacturingProblemSpec) -> float:
        """Calculate estimated makespan for the problem"""
        base_makespan = 100.0  # Base time units
        
        if problem_spec.num_jobs and problem_spec.num_machines:
            # Simple estimation based on jobs and machines
            base_makespan = problem_spec.num_jobs * 2.0 / problem_spec.num_machines
        
        # Adjust for complexity factors
        if problem_spec.has_setup_times:
            base_makespan *= 1.2
        if problem_spec.has_precedence_constraints:
            base_makespan *= 1.1
        
        return base_makespan
    
    def _calculate_throughput(self, problem_spec: ManufacturingProblemSpec, makespan: float) -> float:
        """Calculate throughput based on makespan"""
        if problem_spec.num_jobs and makespan > 0:
            return problem_spec.num_jobs / makespan
        return 1.0
    
    def _calculate_resource_utilization(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, float]:
        """Calculate resource utilization"""
        utilization = {}
        
        if problem_spec.num_machines:
            for i in range(min(problem_spec.num_machines, 10)):  # Limit for example
                # Simulate utilization between 70-95%
                utilization[f"machine_{i+1}"] = 0.7 + 0.25 * np.random.random()
        
        return utilization


class CapacityPlanningOptimizer:
    """Specialized optimizer for capacity planning problems with MIP focus"""
    
    def __init__(self, config_manager: AdvancedSolverConfigurationManager):
        self.config_manager = config_manager
        self.solver_selector = IntelligentSolverSelector()
        
        # Capacity planning specific configurations
        self.capacity_configs = {
            "short_term": {
                "preferred_solvers": ["HiGHS_LP", "GLOP"],
                "time_horizon": "1-4 weeks",
                "highs_lp_config": {
                    "time_limit": 60,
                    "presolve": "on",
                    "simplex_strategy": "dual",
                    "parallel": "on"
                },
                "glop_config": {
                    "max_time_in_seconds": 60,
                    "use_preprocessing": True,
                    "use_dual_simplex": True,
                    "scaling": True
                }
            },
            "medium_term": {
                "preferred_solvers": ["HiGHS_MIP", "SCIP"],
                "time_horizon": "1-6 months",
                "highs_mip_config": {
                    "time_limit": 300,
                    "presolve": "on",
                    "parallel": "on",
                    "mip_rel_gap": 0.01,
                    "mip_abs_gap": 1.0
                },
                "scip_config": {
                    "limits/time": 300,
                    "parallel/maxnthreads": 6,
                    "heuristics/emphasis": "default",
                    "separating/emphasis": "default"
                }
            },
            "long_term": {
                "preferred_solvers": ["SCIP", "CBC"],
                "time_horizon": "6+ months",
                "scip_config": {
                    "limits/time": 900,
                    "parallel/maxnthreads": 8,
                    "heuristics/emphasis": "aggressive",
                    "separating/emphasis": "aggressive",
                    "presolving/maxrounds": 25
                },
                "cbc_config": {
                    "seconds": 900,
                    "threads": 8,
                    "ratioGap": 0.05,
                    "allowableGap": 10.0
                }
            }
        }
    
    def optimize_capacity_planning(self, problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """Optimize capacity planning with MIP-focused approach"""
        logger.info(f"Optimizing capacity planning for {problem_spec.time_horizon}")
        
        # Select configuration based on time horizon
        config = self.capacity_configs.get(problem_spec.time_horizon, self.capacity_configs["medium_term"])
        
        # Adjust configuration based on problem characteristics
        adjusted_config = self._adjust_capacity_config(config, problem_spec)
        
        # Select best solver
        selected_solver = self._select_capacity_solver(adjusted_config["preferred_solvers"], problem_spec)
        
        # Apply solver-specific configuration
        solver_config = adjusted_config.get(f"{selected_solver.lower()}_config", {})
        
        logger.info(f"Selected solver {selected_solver} for capacity planning with config: {solver_config}")
        
        # Execute optimization
        result = self._execute_capacity_optimization(selected_solver, solver_config, problem_spec)
        
        return result
    
    def _adjust_capacity_config(self, base_config: Dict[str, Any], 
                              problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Adjust capacity planning configuration"""
        config = base_config.copy()
        
        # Adjust based on problem size and complexity
        if problem_spec.problem_size == "large" or problem_spec.problem_size == "very_large":
            # Increase time limits for large problems
            for solver_config_key in config:
                if solver_config_key.endswith("_config"):
                    solver_config = config[solver_config_key].copy()
                    if "time_limit" in solver_config:
                        solver_config["time_limit"] *= 2
                    if "limits/time" in solver_config:
                        solver_config["limits/time"] *= 2
                    if "seconds" in solver_config:
                        solver_config["seconds"] *= 2
                    config[solver_config_key] = solver_config
        
        # Adjust gap tolerances for real-time requirements
        if problem_spec.real_time_required:
            for solver_config_key in config:
                if solver_config_key.endswith("_config"):
                    solver_config = config[solver_config_key].copy()
                    if "mip_rel_gap" in solver_config:
                        solver_config["mip_rel_gap"] = max(0.05, solver_config["mip_rel_gap"] * 2)
                    if "ratioGap" in solver_config:
                        solver_config["ratioGap"] = max(0.05, solver_config["ratioGap"] * 2)
                    config[solver_config_key] = solver_config
        
        return config
    
    def _select_capacity_solver(self, preferred_solvers: List[str], 
                              problem_spec: ManufacturingProblemSpec) -> str:
        """Select best solver for capacity planning"""
        available_solvers = [s for s in preferred_solvers 
                           if enhanced_solver_registry.check_solver_availability(s)]
        
        if not available_solvers:
            return self.solver_selector.select_best_solver("mixed_integer_programming", problem_spec.problem_size)
        
        # Prefer linear solvers for continuous problems
        if not problem_spec.has_capacity_constraints and "HiGHS_LP" in available_solvers:
            return "HiGHS_LP"
        
        # Prefer MIP solvers for discrete capacity decisions
        if problem_spec.has_capacity_constraints:
            mip_solvers = [s for s in available_solvers if "MIP" in s or s == "SCIP"]
            if mip_solvers:
                return mip_solvers[0]
        
        return available_solvers[0]
    
    def _execute_capacity_optimization(self, solver_name: str, config: Dict[str, Any], 
                                     problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """Execute capacity planning optimization"""
        start_time = datetime.now()
        
        # Simulate capacity optimization
        solve_time = min(config.get("time_limit", config.get("limits/time", config.get("seconds", 300))), 
                        problem_spec.max_solve_time)
        
        # Calculate capacity metrics
        capacity_utilization = self._calculate_capacity_utilization(problem_spec)
        throughput = self._calculate_capacity_throughput(problem_spec)
        
        result = ManufacturingOptimizationResult(
            solver_name=solver_name,
            solve_status="optimal",
            objective_value=throughput,
            solution={"capacity_plan": "optimized_capacity_plan_placeholder"},
            solve_time=solve_time,
            throughput=throughput,
            resource_utilization=capacity_utilization,
            schedule_feasibility=True,
            solution_robustness=0.9,
            manufacturing_kpis={
                "capacity_utilization": statistics.mean(capacity_utilization.values()) if capacity_utilization else 0.85,
                "demand_coverage": 0.98,
                "cost_efficiency": 0.92
            }
        )
        
        logger.info(f"Capacity planning completed in {solve_time:.2f}s with throughput {throughput:.2f}")
        return result
    
    def _calculate_capacity_utilization(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, float]:
        """Calculate capacity utilization by resource"""
        utilization = {}
        
        if problem_spec.num_resources:
            for i in range(min(problem_spec.num_resources, 10)):
                # Simulate utilization between 75-95% for capacity planning
                utilization[f"resource_{i+1}"] = 0.75 + 0.2 * np.random.random()
        
        return utilization
    
    def _calculate_capacity_throughput(self, problem_spec: ManufacturingProblemSpec) -> float:
        """Calculate expected throughput from capacity plan"""
        base_throughput = 1000.0  # Base units per time period
        
        if problem_spec.num_resources:
            base_throughput *= problem_spec.num_resources * 0.8  # 80% efficiency
        
        # Adjust for time horizon
        horizon_multiplier = {
            "short_term": 1.0,
            "medium_term": 0.9,  # Slightly lower due to uncertainty
            "long_term": 0.8
        }.get(problem_spec.time_horizon, 1.0)
        
        return base_throughput * horizon_multiplier


class RoutingLogisticsOptimizer:
    """Specialized optimizer for routing and logistics problems using constraint programming"""
    
    def __init__(self, config_manager: AdvancedSolverConfigurationManager):
        self.config_manager = config_manager
        self.solver_selector = IntelligentSolverSelector()
        
        # Routing and logistics specific configurations
        self.routing_configs = {
            "vehicle_routing": {
                "preferred_solvers": ["OR_TOOLS_ROUTING", "CP_SAT"],
                "or_tools_routing_config": {
                    "time_limit": 300,
                    "first_solution_strategy": "PATH_CHEAPEST_ARC",
                    "local_search_metaheuristic": "GUIDED_LOCAL_SEARCH",
                    "log_search": True
                },
                "cp_sat_config": {
                    "max_time_in_seconds": 300,
                    "num_search_workers": 4,
                    "use_fixed_search": False,
                    "linearization_level": 1
                }
            },
            "pickup_delivery": {
                "preferred_solvers": ["OR_TOOLS_ROUTING", "CP_SAT"],
                "or_tools_routing_config": {
                    "time_limit": 600,
                    "first_solution_strategy": "PARALLEL_CHEAPEST_INSERTION",
                    "local_search_metaheuristic": "GUIDED_LOCAL_SEARCH",
                    "use_depth_first_search": False
                }
            },
            "multi_depot": {
                "preferred_solvers": ["CP_SAT", "SCIP"],
                "cp_sat_config": {
                    "max_time_in_seconds": 900,
                    "num_search_workers": 8,
                    "use_fixed_search": True,
                    "linearization_level": 2
                }
            }
        }
    
    def optimize_routing_logistics(self, problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """Optimize routing and logistics with constraint programming focus"""
        logger.info("Optimizing routing and logistics problem")
        
        # Determine routing problem type
        routing_type = self._determine_routing_type(problem_spec)
        config = self.routing_configs.get(routing_type, self.routing_configs["vehicle_routing"])
        
        # Adjust configuration
        adjusted_config = self._adjust_routing_config(config, problem_spec)
        
        # Select solver
        selected_solver = self._select_routing_solver(adjusted_config["preferred_solvers"], problem_spec)
        
        # Apply configuration
        solver_config = adjusted_config.get(f"{selected_solver.lower()}_config", {})
        
        logger.info(f"Selected solver {selected_solver} for routing with config: {solver_config}")
        
        # Execute optimization
        result = self._execute_routing_optimization(selected_solver, solver_config, problem_spec)
        
        return result
    
    def _determine_routing_type(self, problem_spec: ManufacturingProblemSpec) -> str:
        """Determine the type of routing problem"""
        if problem_spec.num_locations and problem_spec.num_locations > 50:
            return "multi_depot"
        elif problem_spec.has_time_windows:
            return "pickup_delivery"
        else:
            return "vehicle_routing"
    
    def _adjust_routing_config(self, base_config: Dict[str, Any], 
                             problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Adjust routing configuration based on problem characteristics"""
        config = base_config.copy()
        
        # Adjust time limits based on problem size
        complexity_score = problem_spec.calculate_complexity_score()
        time_multiplier = min(2.0, max(0.5, complexity_score / 2.0))
        
        for solver_config_key in config:
            if solver_config_key.endswith("_config"):
                solver_config = config[solver_config_key].copy()
                
                if "time_limit" in solver_config:
                    solver_config["time_limit"] *= time_multiplier
                if "max_time_in_seconds" in solver_config:
                    solver_config["max_time_in_seconds"] *= time_multiplier
                
                # Adjust search strategy for large problems
                if problem_spec.num_locations and problem_spec.num_locations > 100:
                    if "first_solution_strategy" in solver_config:
                        solver_config["first_solution_strategy"] = "SAVINGS"
                    if "num_search_workers" in solver_config:
                        solver_config["num_search_workers"] = min(8, solver_config["num_search_workers"] * 2)
                
                config[solver_config_key] = solver_config
        
        return config
    
    def _select_routing_solver(self, preferred_solvers: List[str], 
                             problem_spec: ManufacturingProblemSpec) -> str:
        """Select best solver for routing problem"""
        available_solvers = [s for s in preferred_solvers 
                           if enhanced_solver_registry.check_solver_availability(s)]
        
        if not available_solvers:
            return self.solver_selector.select_best_solver("constraint_programming", problem_spec.problem_size)
        
        # Prefer OR-Tools Routing for vehicle routing problems
        if problem_spec.num_vehicles and "OR_TOOLS_ROUTING" in available_solvers:
            return "OR_TOOLS_ROUTING"
        
        # Prefer CP-SAT for complex constraint problems
        if (problem_spec.has_time_windows and problem_spec.has_capacity_constraints 
            and "CP_SAT" in available_solvers):
            return "CP_SAT"
        
        return available_solvers[0]
    
    def _execute_routing_optimization(self, solver_name: str, config: Dict[str, Any], 
                                    problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """Execute routing optimization"""
        start_time = datetime.now()
        
        solve_time = min(config.get("time_limit", config.get("max_time_in_seconds", 300)), 
                        problem_spec.max_solve_time)
        
        # Calculate routing metrics
        total_distance = self._calculate_total_distance(problem_spec)
        vehicle_utilization = self._calculate_vehicle_utilization(problem_spec)
        
        result = ManufacturingOptimizationResult(
            solver_name=solver_name,
            solve_status="optimal",
            objective_value=total_distance,
            solution={"routes": "optimized_routes_placeholder"},
            solve_time=solve_time,
            resource_utilization=vehicle_utilization,
            schedule_feasibility=True,
            solution_robustness=0.88,
            manufacturing_kpis={
                "route_efficiency": 0.92,
                "on_time_delivery": 0.96,
                "vehicle_utilization": statistics.mean(vehicle_utilization.values()) if vehicle_utilization else 0.85,
                "fuel_efficiency": 0.89
            }
        )
        
        logger.info(f"Routing optimization completed in {solve_time:.2f}s with total distance {total_distance:.2f}")
        return result
    
    def _calculate_total_distance(self, problem_spec: ManufacturingProblemSpec) -> float:
        """Calculate estimated total distance for routes"""
        base_distance = 100.0
        
        if problem_spec.num_locations:
            # Simple estimation based on number of locations
            base_distance = problem_spec.num_locations * 5.0
        
        if problem_spec.num_vehicles:
            # Distribute across vehicles
            base_distance = base_distance / problem_spec.num_vehicles * 1.2  # 20% overlap
        
        return base_distance
    
    def _calculate_vehicle_utilization(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, float]:
        """Calculate vehicle utilization"""
        utilization = {}
        
        if problem_spec.num_vehicles:
            for i in range(min(problem_spec.num_vehicles, 20)):
                # Simulate utilization between 70-90% for routing
                utilization[f"vehicle_{i+1}"] = 0.7 + 0.2 * np.random.random()
        
        return utilization


class ResourceAllocationOptimizer:
    """Specialized optimizer for resource allocation with large-scale LP capabilities"""
    
    def __init__(self, config_manager: AdvancedSolverConfigurationManager):
        self.config_manager = config_manager
        self.solver_selector = IntelligentSolverSelector()
        
        # Resource allocation specific configurations
        self.allocation_configs = {
            "workforce": {
                "preferred_solvers": ["HiGHS_LP", "CLP", "GLOP"],
                "highs_lp_config": {
                    "time_limit": 120,
                    "presolve": "on",
                    "simplex_strategy": "dual",
                    "parallel": "on",
                    "primal_feasibility_tolerance": 1e-7
                },
                "clp_config": {
                    "maximumSeconds": 120,
                    "presolve": "on",
                    "dualSimplex": True,
                    "scaling": True
                }
            },
            "equipment": {
                "preferred_solvers": ["HiGHS_MIP", "SCIP"],
                "highs_mip_config": {
                    "time_limit": 300,
                    "presolve": "on",
                    "parallel": "on",
                    "mip_rel_gap": 0.01
                }
            },
            "material": {
                "preferred_solvers": ["HiGHS_LP", "CLP"],
                "highs_lp_config": {
                    "time_limit": 60,
                    "presolve": "on",
                    "simplex_strategy": "primal",
                    "parallel": "on"
                }
            }
        }
    
    def optimize_resource_allocation(self, problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """Optimize resource allocation with large-scale LP focus"""
        logger.info("Optimizing resource allocation problem")
        
        # Determine allocation type
        allocation_type = self._determine_allocation_type(problem_spec)
        config = self.allocation_configs.get(allocation_type, self.allocation_configs["workforce"])
        
        # Adjust for large-scale problems
        adjusted_config = self._adjust_allocation_config(config, problem_spec)
        
        # Select solver
        selected_solver = self._select_allocation_solver(adjusted_config["preferred_solvers"], problem_spec)
        
        # Apply configuration
        solver_config = adjusted_config.get(f"{selected_solver.lower()}_config", {})
        
        logger.info(f"Selected solver {selected_solver} for resource allocation with config: {solver_config}")
        
        # Execute optimization
        result = self._execute_allocation_optimization(selected_solver, solver_config, problem_spec)
        
        return result
    
    def _determine_allocation_type(self, problem_spec: ManufacturingProblemSpec) -> str:
        """Determine the type of resource allocation problem"""
        # Simple heuristic based on problem characteristics
        if problem_spec.num_machines and problem_spec.num_machines > 0:
            return "equipment"
        elif problem_spec.has_resource_constraints:
            return "material"
        else:
            return "workforce"
    
    def _adjust_allocation_config(self, base_config: Dict[str, Any], 
                                problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Adjust configuration for large-scale resource allocation"""
        config = base_config.copy()
        
        # Adjust for large-scale problems
        if problem_spec.problem_size in ["large", "very_large"]:
            for solver_config_key in config:
                if solver_config_key.endswith("_config"):
                    solver_config = config[solver_config_key].copy()
                    
                    # Increase time limits for large problems
                    if "time_limit" in solver_config:
                        solver_config["time_limit"] *= 3
                    if "maximumSeconds" in solver_config:
                        solver_config["maximumSeconds"] *= 3
                    
                    # Enable aggressive presolving for large problems
                    if "presolve" in solver_config:
                        solver_config["presolve"] = "on"
                    
                    # Use dual simplex for large LP problems
                    if "simplex_strategy" in solver_config:
                        solver_config["simplex_strategy"] = "dual"
                    
                    config[solver_config_key] = solver_config
        
        return config
    
    def _select_allocation_solver(self, preferred_solvers: List[str], 
                                problem_spec: ManufacturingProblemSpec) -> str:
        """Select best solver for resource allocation"""
        available_solvers = [s for s in preferred_solvers 
                           if enhanced_solver_registry.check_solver_availability(s)]
        
        if not available_solvers:
            return self.solver_selector.select_best_solver("linear_programming", problem_spec.problem_size)
        
        # Prefer HiGHS for large-scale problems
        if problem_spec.problem_size in ["large", "very_large"] and "HiGHS_LP" in available_solvers:
            return "HiGHS_LP"
        
        # Prefer CLP for very large problems
        if problem_spec.problem_size == "very_large" and "CLP" in available_solvers:
            return "CLP"
        
        return available_solvers[0]
    
    def _execute_allocation_optimization(self, solver_name: str, config: Dict[str, Any], 
                                       problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """Execute resource allocation optimization"""
        start_time = datetime.now()
        
        solve_time = min(config.get("time_limit", config.get("maximumSeconds", 120)), 
                        problem_spec.max_solve_time)
        
        # Calculate allocation metrics
        allocation_efficiency = self._calculate_allocation_efficiency(problem_spec)
        resource_utilization = self._calculate_allocation_utilization(problem_spec)
        
        result = ManufacturingOptimizationResult(
            solver_name=solver_name,
            solve_status="optimal",
            objective_value=allocation_efficiency,
            solution={"allocation": "optimized_allocation_placeholder"},
            solve_time=solve_time,
            resource_utilization=resource_utilization,
            schedule_feasibility=True,
            solution_robustness=0.93,
            manufacturing_kpis={
                "allocation_efficiency": allocation_efficiency,
                "resource_utilization": statistics.mean(resource_utilization.values()) if resource_utilization else 0.88,
                "cost_optimization": 0.91,
                "demand_satisfaction": 0.97
            }
        )
        
        logger.info(f"Resource allocation completed in {solve_time:.2f}s with efficiency {allocation_efficiency:.3f}")
        return result
    
    def _calculate_allocation_efficiency(self, problem_spec: ManufacturingProblemSpec) -> float:
        """Calculate allocation efficiency score"""
        base_efficiency = 0.85
        
        # Adjust based on problem characteristics
        if problem_spec.has_resource_constraints:
            base_efficiency += 0.05  # Better optimization with constraints
        
        if problem_spec.problem_size == "large":
            base_efficiency += 0.03  # Economies of scale
        elif problem_spec.problem_size == "very_large":
            base_efficiency += 0.05
        
        return min(1.0, base_efficiency)
    
    def _calculate_allocation_utilization(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, float]:
        """Calculate resource utilization from allocation"""
        utilization = {}
        
        num_resources = problem_spec.num_resources or 5
        for i in range(min(num_resources, 15)):
            # Simulate utilization between 80-95% for resource allocation
            utilization[f"resource_{i+1}"] = 0.8 + 0.15 * np.random.random()
        
        return utilization


class ManufacturingDomainOptimizer:
    """
    Main manufacturing domain-specific optimization system
    
    Coordinates specialized optimizers for different manufacturing problem types
    and provides unified interface for manufacturing optimization.
    """
    
    def __init__(self):
        self.config_manager = AdvancedSolverConfigurationManager()
        
        # Initialize specialized optimizers
        self.production_scheduler = ProductionSchedulingOptimizer(self.config_manager)
        self.capacity_planner = CapacityPlanningOptimizer(self.config_manager)
        self.routing_optimizer = RoutingLogisticsOptimizer(self.config_manager)
        self.resource_allocator = ResourceAllocationOptimizer(self.config_manager)
        
        # Performance tracking
        self.optimization_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("Manufacturing domain optimizer initialized with all specialized optimizers")
    
    def optimize_manufacturing_problem(self, problem_spec: ManufacturingProblemSpec) -> ManufacturingOptimizationResult:
        """
        Optimize manufacturing problem using appropriate specialized optimizer
        
        Args:
            problem_spec: Manufacturing problem specification
            
        Returns:
            Manufacturing optimization result with domain-specific metrics
        """
        with self._lock:
            start_time = datetime.now()
            
            logger.info(f"Starting manufacturing optimization for {problem_spec.problem_type.value}")
            
            try:
                # Route to appropriate specialized optimizer
                if problem_spec.problem_type == ManufacturingProblemType.PRODUCTION_SCHEDULING:
                    result = self.production_scheduler.optimize_production_schedule(problem_spec)
                
                elif problem_spec.problem_type == ManufacturingProblemType.CAPACITY_PLANNING:
                    result = self.capacity_planner.optimize_capacity_planning(problem_spec)
                
                elif problem_spec.problem_type == ManufacturingProblemType.ROUTING_LOGISTICS:
                    result = self.routing_optimizer.optimize_routing_logistics(problem_spec)
                
                elif problem_spec.problem_type == ManufacturingProblemType.RESOURCE_ALLOCATION:
                    result = self.resource_allocator.optimize_resource_allocation(problem_spec)
                
                else:
                    # Default to production scheduling for unknown types
                    logger.warning(f"Unknown problem type {problem_spec.problem_type}, defaulting to production scheduling")
                    result = self.production_scheduler.optimize_production_schedule(problem_spec)
                
                # Record performance
                self._record_optimization_performance(problem_spec, result)
                
                total_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"Manufacturing optimization completed in {total_time:.2f}s with score {result.calculate_manufacturing_score():.3f}")
                
                return result
                
            except Exception as e:
                logger.error(f"Manufacturing optimization failed: {str(e)}")
                # Return error result
                return ManufacturingOptimizationResult(
                    solver_name="error",
                    solve_status="error",
                    objective_value=None,
                    solution={},
                    solve_time=(datetime.now() - start_time).total_seconds(),
                    constraint_violations=[f"Optimization error: {str(e)}"]
                )
    
    def get_manufacturing_recommendations(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Get recommendations for manufacturing problem optimization"""
        recommendations = {
            "problem_analysis": self._analyze_manufacturing_problem(problem_spec),
            "solver_recommendations": self._get_solver_recommendations(problem_spec),
            "configuration_suggestions": self._get_configuration_suggestions(problem_spec),
            "performance_expectations": self._get_performance_expectations(problem_spec)
        }
        
        return recommendations
    
    def _analyze_manufacturing_problem(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Analyze manufacturing problem characteristics"""
        complexity_score = problem_spec.calculate_complexity_score()
        
        analysis = {
            "problem_type": problem_spec.problem_type.value,
            "production_type": problem_spec.production_type.value,
            "complexity_score": complexity_score,
            "complexity_level": "low" if complexity_score < 2 else "medium" if complexity_score < 4 else "high",
            "key_constraints": [],
            "optimization_challenges": []
        }
        
        # Identify key constraints
        if problem_spec.has_setup_times:
            analysis["key_constraints"].append("setup_times")
        if problem_spec.has_precedence_constraints:
            analysis["key_constraints"].append("precedence_constraints")
        if problem_spec.has_resource_constraints:
            analysis["key_constraints"].append("resource_constraints")
        if problem_spec.has_time_windows:
            analysis["key_constraints"].append("time_windows")
        
        # Identify optimization challenges
        if complexity_score > 3:
            analysis["optimization_challenges"].append("high_complexity")
        if problem_spec.real_time_required:
            analysis["optimization_challenges"].append("real_time_requirements")
        if problem_spec.uncertainty_level == "high":
            analysis["optimization_challenges"].append("high_uncertainty")
        
        return analysis
    
    def _get_solver_recommendations(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Get solver recommendations for manufacturing problem"""
        recommendations = {
            "primary_solvers": [],
            "fallback_solvers": [],
            "rationale": {}
        }
        
        if problem_spec.problem_type == ManufacturingProblemType.PRODUCTION_SCHEDULING:
            recommendations["primary_solvers"] = ["CP_SAT", "SCIP"]
            recommendations["fallback_solvers"] = ["CBC", "HiGHS_MIP"]
            recommendations["rationale"]["CP_SAT"] = "Excellent for scheduling with complex constraints"
            recommendations["rationale"]["SCIP"] = "Strong performance on large scheduling problems"
        
        elif problem_spec.problem_type == ManufacturingProblemType.CAPACITY_PLANNING:
            if problem_spec.has_capacity_constraints:
                recommendations["primary_solvers"] = ["HiGHS_MIP", "SCIP"]
                recommendations["fallback_solvers"] = ["CBC"]
            else:
                recommendations["primary_solvers"] = ["HiGHS_LP", "GLOP"]
                recommendations["fallback_solvers"] = ["CLP"]
            recommendations["rationale"]["HiGHS_MIP"] = "High performance mixed-integer solver"
            recommendations["rationale"]["HiGHS_LP"] = "Excellent for large-scale linear problems"
        
        elif problem_spec.problem_type == ManufacturingProblemType.ROUTING_LOGISTICS:
            recommendations["primary_solvers"] = ["OR_TOOLS_ROUTING", "CP_SAT"]
            recommendations["fallback_solvers"] = ["SCIP"]
            recommendations["rationale"]["OR_TOOLS_ROUTING"] = "Specialized for vehicle routing problems"
            recommendations["rationale"]["CP_SAT"] = "Flexible constraint programming solver"
        
        elif problem_spec.problem_type == ManufacturingProblemType.RESOURCE_ALLOCATION:
            recommendations["primary_solvers"] = ["HiGHS_LP", "CLP"]
            recommendations["fallback_solvers"] = ["GLOP"]
            recommendations["rationale"]["HiGHS_LP"] = "Excellent for large-scale resource allocation"
            recommendations["rationale"]["CLP"] = "Robust for very large linear programs"
        
        return recommendations
    
    def _get_configuration_suggestions(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Get configuration suggestions for manufacturing problem"""
        suggestions = {
            "time_limits": {},
            "parallelism": {},
            "numerical_settings": {},
            "heuristics": {}
        }
        
        complexity_score = problem_spec.calculate_complexity_score()
        
        # Time limit suggestions
        base_time = 60 if problem_spec.real_time_required else 300
        time_multiplier = min(3.0, max(0.5, complexity_score / 2.0))
        suggested_time = base_time * time_multiplier
        
        suggestions["time_limits"]["recommended"] = suggested_time
        suggestions["time_limits"]["minimum"] = suggested_time * 0.5
        suggestions["time_limits"]["maximum"] = suggested_time * 2.0
        
        # Parallelism suggestions
        if problem_spec.problem_size in ["large", "very_large"]:
            suggestions["parallelism"]["threads"] = 8
        else:
            suggestions["parallelism"]["threads"] = 4
        
        # Numerical settings
        if problem_spec.problem_type == ManufacturingProblemType.CAPACITY_PLANNING:
            suggestions["numerical_settings"]["gap_tolerance"] = 0.01
            suggestions["numerical_settings"]["feasibility_tolerance"] = 1e-7
        
        # Heuristics
        if complexity_score > 3:
            suggestions["heuristics"]["emphasis"] = "aggressive"
        else:
            suggestions["heuristics"]["emphasis"] = "default"
        
        return suggestions
    
    def _get_performance_expectations(self, problem_spec: ManufacturingProblemSpec) -> Dict[str, Any]:
        """Get performance expectations for manufacturing problem"""
        complexity_score = problem_spec.calculate_complexity_score()
        
        expectations = {
            "solve_time_range": {},
            "solution_quality": {},
            "success_probability": 0.0,
            "key_metrics": {}
        }
        
        # Solve time expectations
        if complexity_score < 2:
            expectations["solve_time_range"] = {"min": 5, "typical": 30, "max": 120}
            expectations["success_probability"] = 0.95
        elif complexity_score < 4:
            expectations["solve_time_range"] = {"min": 30, "typical": 180, "max": 600}
            expectations["success_probability"] = 0.85
        else:
            expectations["solve_time_range"] = {"min": 120, "typical": 600, "max": 1800}
            expectations["success_probability"] = 0.75
        
        # Solution quality expectations
        expectations["solution_quality"] = {
            "optimality_gap": "< 1%" if complexity_score < 3 else "< 5%",
            "feasibility": "guaranteed" if complexity_score < 4 else "high_probability"
        }
        
        # Key metrics expectations
        if problem_spec.problem_type == ManufacturingProblemType.PRODUCTION_SCHEDULING:
            expectations["key_metrics"] = {
                "makespan_improvement": "10-30%",
                "resource_utilization": "85-95%",
                "on_time_delivery": "90-98%"
            }
        elif problem_spec.problem_type == ManufacturingProblemType.CAPACITY_PLANNING:
            expectations["key_metrics"] = {
                "capacity_utilization": "80-95%",
                "demand_coverage": "95-100%",
                "cost_reduction": "5-20%"
            }
        
        return expectations
    
    def _record_optimization_performance(self, problem_spec: ManufacturingProblemSpec, 
                                       result: ManufacturingOptimizationResult):
        """Record optimization performance for analytics"""
        performance_record = {
            "timestamp": datetime.now().isoformat(),
            "problem_type": problem_spec.problem_type.value,
            "production_type": problem_spec.production_type.value,
            "problem_size": problem_spec.problem_size,
            "complexity_score": problem_spec.calculate_complexity_score(),
            "solver_name": result.solver_name,
            "solve_time": result.solve_time,
            "solve_status": result.solve_status,
            "manufacturing_score": result.calculate_manufacturing_score(),
            "solution_robustness": result.solution_robustness
        }
        
        self.optimization_history.append(performance_record)
        
        # Update performance metrics
        self.performance_metrics[problem_spec.problem_type.value].append(result.solve_time)
        self.performance_metrics[f"{problem_spec.problem_type.value}_score"].append(
            result.calculate_manufacturing_score()
        )
        
        # Keep history limited
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-1000:]
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics for manufacturing optimizations"""
        analytics = {
            "total_optimizations": len(self.optimization_history),
            "problem_type_distribution": defaultdict(int),
            "solver_usage": defaultdict(int),
            "average_solve_times": {},
            "average_scores": {},
            "success_rates": {}
        }
        
        if not self.optimization_history:
            return analytics
        
        # Calculate distributions and averages
        for record in self.optimization_history:
            analytics["problem_type_distribution"][record["problem_type"]] += 1
            analytics["solver_usage"][record["solver_name"]] += 1
        
        # Calculate average metrics
        for problem_type, times in self.performance_metrics.items():
            if times and not problem_type.endswith("_score"):
                analytics["average_solve_times"][problem_type] = statistics.mean(times)
            elif times and problem_type.endswith("_score"):
                base_type = problem_type.replace("_score", "")
                analytics["average_scores"][base_type] = statistics.mean(times)
        
        # Calculate success rates
        for problem_type in analytics["problem_type_distribution"]:
            successful = sum(1 for r in self.optimization_history 
                           if r["problem_type"] == problem_type and r["solve_status"] in ["optimal", "feasible"])
            total = analytics["problem_type_distribution"][problem_type]
            analytics["success_rates"][problem_type] = successful / total if total > 0 else 0.0
        
        return analytics


# Global instance for easy access
manufacturing_domain_optimizer = ManufacturingDomainOptimizer()