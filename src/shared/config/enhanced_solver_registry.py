"""
Enhanced Solver Registry for Multi-Solver Swarm Optimization
===========================================================

Comprehensive solver registry with 15+ open source solvers across 5 categories:
1. Linear Programming Solvers
2. Mixed-Integer Programming Solvers  
3. Constraint Programming Solvers
4. Nonlinear Programming Solvers
5. Metaheuristic Solvers

Implements solver capability detection, registration system, configuration management,
and graceful degradation logic as required by Task 1.

Requirements: 1.1, 1.2, 1.3, 1.4
"""

import logging
import importlib
import sys
import os
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import json
import threading
import time

logger = logging.getLogger(__name__)


class SolverCategory(Enum):
    """Categories of optimization solvers"""
    LINEAR_PROGRAMMING = "linear_programming"
    MIXED_INTEGER_PROGRAMMING = "mixed_integer_programming"
    CONSTRAINT_PROGRAMMING = "constraint_programming"
    NONLINEAR_PROGRAMMING = "nonlinear_programming"
    METAHEURISTIC = "metaheuristic"


class SolverStatus(Enum):
    """Solver availability status"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class SolverCapability:
    """Comprehensive solver capability specification"""
    name: str
    category: SolverCategory
    problem_types: List[str]
    variable_types: List[str]  # continuous, integer, binary, boolean
    constraint_types: List[str]  # linear, quadratic, nonlinear, logical
    objective_types: List[str]  # linear, quadratic, nonlinear
    performance_profile: Dict[str, int]  # 1-5 rating for different aspects
    max_variables: int
    max_constraints: int
    memory_efficient: bool
    parallel_capable: bool
    supports_callbacks: bool
    license_type: str  # open_source, commercial, academic
    installation_method: str  # pip, conda, system, manual
    dependencies: List[str]
    version_info: Optional[str] = None
    last_checked: Optional[datetime] = None
    status: SolverStatus = SolverStatus.UNKNOWN
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['category'] = self.category.value
        result['status'] = self.status.value
        if self.last_checked:
            result['last_checked'] = self.last_checked.isoformat()
        return result


class EnhancedSolverRegistry:
    """
    Enhanced solver registry with comprehensive solver support and management
    
    Features:
    - 15+ open source solvers across 5 categories
    - Automatic solver detection and registration
    - Solver-specific configuration management
    - Availability checking with caching
    - Graceful degradation logic
    - Performance tracking and analytics
    """
    
    def __init__(self):
        self.solvers: Dict[str, SolverCapability] = {}
        self.availability_cache: Dict[str, bool] = {}
        self.last_availability_check: Dict[str, datetime] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.configuration_profiles: Dict[str, Dict[str, Any]] = {}
        self.fallback_chains: Dict[str, List[str]] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Cache settings
        self.cache_duration = timedelta(minutes=5)
        
        # Initialize solver definitions
        self._initialize_solver_definitions()
        
        # Perform initial availability check
        self._initial_availability_check()
        
        logger.info(f"Enhanced solver registry initialized with {len(self.solvers)} solver definitions")
    
    def _initialize_solver_definitions(self):
        """Initialize comprehensive solver capability definitions"""
        
        # ===== LINEAR PROGRAMMING SOLVERS =====
        
        # OR-Tools GLOP (Google Linear Optimization Package)
        self.solvers["GLOP"] = SolverCapability(
            name="GLOP",
            category=SolverCategory.LINEAR_PROGRAMMING,
            problem_types=["linear_programming", "resource_allocation", "capacity_planning"],
            variable_types=["continuous"],
            constraint_types=["linear"],
            objective_types=["linear"],
            performance_profile={
                "small_problems": 5,    # 1-5 rating
                "medium_problems": 4,
                "large_problems": 3,
                "memory_efficiency": 5,
                "speed": 4,
                "robustness": 4,
                "numerical_stability": 5
            },
            max_variables=1000000,
            max_constraints=500000,
            memory_efficient=True,
            parallel_capable=False,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["ortools"]
        )
        
        # COIN-OR CLP (COIN-OR Linear Programming)
        self.solvers["CLP"] = SolverCapability(
            name="CLP",
            category=SolverCategory.LINEAR_PROGRAMMING,
            problem_types=["linear_programming", "large_scale_lp"],
            variable_types=["continuous"],
            constraint_types=["linear"],
            objective_types=["linear"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 5,
                "large_problems": 5,
                "memory_efficiency": 4,
                "speed": 4,
                "robustness": 5,
                "numerical_stability": 4
            },
            max_variables=10000000,
            max_constraints=5000000,
            memory_efficient=True,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["pulp", "coinor-clp"]
        )
        
        # HiGHS Linear Programming
        self.solvers["HiGHS_LP"] = SolverCapability(
            name="HiGHS_LP",
            category=SolverCategory.LINEAR_PROGRAMMING,
            problem_types=["linear_programming", "high_performance_lp"],
            variable_types=["continuous"],
            constraint_types=["linear"],
            objective_types=["linear"],
            performance_profile={
                "small_problems": 5,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 4,
                "speed": 5,
                "robustness": 4,
                "numerical_stability": 4
            },
            max_variables=10000000,
            max_constraints=5000000,
            memory_efficient=True,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["highspy"]
        )
        
        # SciPy Linear Programming
        self.solvers["SCIPY_LINPROG"] = SolverCapability(
            name="SCIPY_LINPROG",
            category=SolverCategory.LINEAR_PROGRAMMING,
            problem_types=["linear_programming", "small_scale_lp"],
            variable_types=["continuous"],
            constraint_types=["linear"],
            objective_types=["linear"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 3,
                "large_problems": 2,
                "memory_efficiency": 4,
                "speed": 3,
                "robustness": 3,
                "numerical_stability": 4
            },
            max_variables=10000,
            max_constraints=5000,
            memory_efficient=True,
            parallel_capable=False,
            supports_callbacks=False,
            license_type="open_source",
            installation_method="pip",
            dependencies=["scipy"]
        )
        
        # ===== MIXED-INTEGER PROGRAMMING SOLVERS =====
        
        # OR-Tools SCIP (Solving Constraint Integer Programs)
        self.solvers["SCIP"] = SolverCapability(
            name="SCIP",
            category=SolverCategory.MIXED_INTEGER_PROGRAMMING,
            problem_types=["mixed_integer_programming", "constraint_programming", "production_scheduling"],
            variable_types=["continuous", "integer", "binary"],
            constraint_types=["linear", "quadratic", "logical"],
            objective_types=["linear", "quadratic"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 3,
                "speed": 4,
                "robustness": 5,
                "numerical_stability": 4
            },
            max_variables=1000000,
            max_constraints=500000,
            memory_efficient=False,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["ortools", "pyscip"]
        )
        
        # COIN-OR CBC (COIN-OR Branch and Cut)
        self.solvers["CBC"] = SolverCapability(
            name="CBC",
            category=SolverCategory.MIXED_INTEGER_PROGRAMMING,
            problem_types=["mixed_integer_programming", "scheduling", "assignment"],
            variable_types=["continuous", "integer", "binary"],
            constraint_types=["linear"],
            objective_types=["linear"],
            performance_profile={
                "small_problems": 3,
                "medium_problems": 4,
                "large_problems": 3,
                "memory_efficiency": 4,
                "speed": 3,
                "robustness": 4,
                "numerical_stability": 4
            },
            max_variables=100000,
            max_constraints=50000,
            memory_efficient=True,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["pulp", "coinor-cbc"]
        )
        
        # HiGHS Mixed-Integer Programming
        self.solvers["HiGHS_MIP"] = SolverCapability(
            name="HiGHS_MIP",
            category=SolverCategory.MIXED_INTEGER_PROGRAMMING,
            problem_types=["mixed_integer_programming", "high_performance_mip"],
            variable_types=["continuous", "integer", "binary"],
            constraint_types=["linear"],
            objective_types=["linear"],
            performance_profile={
                "small_problems": 5,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 4,
                "speed": 5,
                "robustness": 4,
                "numerical_stability": 4
            },
            max_variables=1000000,
            max_constraints=500000,
            memory_efficient=True,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["highspy"]
        )
        
        # CVXPY with GLPK_MI backend
        self.solvers["CVXPY_GLPK_MI"] = SolverCapability(
            name="CVXPY_GLPK_MI",
            category=SolverCategory.MIXED_INTEGER_PROGRAMMING,
            problem_types=["mixed_integer_programming", "convex_optimization"],
            variable_types=["continuous", "integer", "binary"],
            constraint_types=["linear", "convex"],
            objective_types=["linear", "convex"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 3,
                "large_problems": 2,
                "memory_efficiency": 3,
                "speed": 3,
                "robustness": 3,
                "numerical_stability": 4
            },
            max_variables=50000,
            max_constraints=25000,
            memory_efficient=True,
            parallel_capable=False,
            supports_callbacks=False,
            license_type="open_source",
            installation_method="pip",
            dependencies=["cvxpy", "glpk"]
        )
        
        # Pyomo with CBC backend
        self.solvers["PYOMO_CBC"] = SolverCapability(
            name="PYOMO_CBC",
            category=SolverCategory.MIXED_INTEGER_PROGRAMMING,
            problem_types=["mixed_integer_programming", "algebraic_modeling"],
            variable_types=["continuous", "integer", "binary"],
            constraint_types=["linear", "nonlinear"],
            objective_types=["linear", "nonlinear"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 4,
                "large_problems": 3,
                "memory_efficiency": 3,
                "speed": 3,
                "robustness": 4,
                "numerical_stability": 4
            },
            max_variables=100000,
            max_constraints=50000,
            memory_efficient=True,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["pyomo", "coinor-cbc"]
        )
        
        # ===== CONSTRAINT PROGRAMMING SOLVERS =====
        
        # OR-Tools CP-SAT (Constraint Programming - Satisfiability)
        self.solvers["CP_SAT"] = SolverCapability(
            name="CP_SAT",
            category=SolverCategory.CONSTRAINT_PROGRAMMING,
            problem_types=["constraint_programming", "scheduling", "assignment", "routing"],
            variable_types=["integer", "binary", "boolean"],
            constraint_types=["linear", "logical", "global_constraints"],
            objective_types=["linear"],
            performance_profile={
                "small_problems": 5,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 4,
                "speed": 5,
                "robustness": 5,
                "numerical_stability": 5
            },
            max_variables=1000000,
            max_constraints=1000000,
            memory_efficient=True,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["ortools"]
        )
        
        # OR-Tools Routing (Vehicle Routing Problems)
        self.solvers["OR_TOOLS_ROUTING"] = SolverCapability(
            name="OR_TOOLS_ROUTING",
            category=SolverCategory.CONSTRAINT_PROGRAMMING,
            problem_types=["vehicle_routing", "routing", "logistics"],
            variable_types=["integer", "binary"],
            constraint_types=["routing_constraints", "capacity_constraints"],
            objective_types=["linear"],
            performance_profile={
                "small_problems": 5,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 4,
                "speed": 4,
                "robustness": 5,
                "numerical_stability": 5
            },
            max_variables=10000,
            max_constraints=10000,
            memory_efficient=True,
            parallel_capable=False,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["ortools"]
        )
        
        # ===== NONLINEAR PROGRAMMING SOLVERS =====
        
        # COIN-OR Ipopt (Interior Point Optimizer)
        self.solvers["IPOPT"] = SolverCapability(
            name="IPOPT",
            category=SolverCategory.NONLINEAR_PROGRAMMING,
            problem_types=["nonlinear_programming", "continuous_optimization"],
            variable_types=["continuous"],
            constraint_types=["linear", "nonlinear"],
            objective_types=["linear", "nonlinear"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 4,
                "large_problems": 3,
                "memory_efficiency": 3,
                "speed": 3,
                "robustness": 4,
                "numerical_stability": 3
            },
            max_variables=100000,
            max_constraints=50000,
            memory_efficient=False,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["cyipopt", "ipopt"]
        )
        
        # SciPy SLSQP (Sequential Least Squares Programming)
        self.solvers["SCIPY_SLSQP"] = SolverCapability(
            name="SCIPY_SLSQP",
            category=SolverCategory.NONLINEAR_PROGRAMMING,
            problem_types=["nonlinear_programming", "constrained_optimization"],
            variable_types=["continuous"],
            constraint_types=["linear", "nonlinear"],
            objective_types=["linear", "nonlinear"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 3,
                "large_problems": 2,
                "memory_efficiency": 5,
                "speed": 4,
                "robustness": 3,
                "numerical_stability": 3
            },
            max_variables=10000,
            max_constraints=5000,
            memory_efficient=True,
            parallel_capable=False,
            supports_callbacks=False,
            license_type="open_source",
            installation_method="pip",
            dependencies=["scipy"]
        )
        
        # COIN-OR Bonmin (Mixed-Integer Nonlinear Programming)
        self.solvers["BONMIN"] = SolverCapability(
            name="BONMIN",
            category=SolverCategory.NONLINEAR_PROGRAMMING,
            problem_types=["mixed_integer_nonlinear_programming", "minlp"],
            variable_types=["continuous", "integer", "binary"],
            constraint_types=["linear", "nonlinear"],
            objective_types=["linear", "nonlinear"],
            performance_profile={
                "small_problems": 3,
                "medium_problems": 3,
                "large_problems": 2,
                "memory_efficiency": 2,
                "speed": 2,
                "robustness": 3,
                "numerical_stability": 3
            },
            max_variables=10000,
            max_constraints=5000,
            memory_efficient=False,
            parallel_capable=False,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="manual",
            dependencies=["pyomo", "bonmin"]
        )
        
        # CVXPY with ECOS backend
        self.solvers["CVXPY_ECOS"] = SolverCapability(
            name="CVXPY_ECOS",
            category=SolverCategory.NONLINEAR_PROGRAMMING,
            problem_types=["convex_optimization", "second_order_cone"],
            variable_types=["continuous"],
            constraint_types=["linear", "second_order_cone"],
            objective_types=["linear", "convex"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 4,
                "large_problems": 3,
                "memory_efficiency": 4,
                "speed": 4,
                "robustness": 4,
                "numerical_stability": 4
            },
            max_variables=50000,
            max_constraints=25000,
            memory_efficient=True,
            parallel_capable=False,
            supports_callbacks=False,
            license_type="open_source",
            installation_method="pip",
            dependencies=["cvxpy", "ecos"]
        )
        
        # ===== METAHEURISTIC SOLVERS =====
        
        # DEAP (Distributed Evolutionary Algorithms in Python)
        self.solvers["DEAP"] = SolverCapability(
            name="DEAP",
            category=SolverCategory.METAHEURISTIC,
            problem_types=["metaheuristic", "multi_objective", "evolutionary"],
            variable_types=["continuous", "integer", "binary", "permutation"],
            constraint_types=["penalty_based", "repair_based"],
            objective_types=["linear", "nonlinear", "multi_objective"],
            performance_profile={
                "small_problems": 3,
                "medium_problems": 4,
                "large_problems": 5,
                "memory_efficiency": 3,
                "speed": 2,
                "robustness": 4,
                "numerical_stability": 3
            },
            max_variables=1000000,
            max_constraints=1000000,
            memory_efficient=False,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["deap"]
        )
        
        # PySwarms (Particle Swarm Optimization)
        self.solvers["PYSWARMS"] = SolverCapability(
            name="PYSWARMS",
            category=SolverCategory.METAHEURISTIC,
            problem_types=["metaheuristic", "continuous_optimization", "swarm_intelligence"],
            variable_types=["continuous"],
            constraint_types=["penalty_based"],
            objective_types=["linear", "nonlinear"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 4,
                "large_problems": 5,
                "memory_efficiency": 4,
                "speed": 3,
                "robustness": 3,
                "numerical_stability": 3
            },
            max_variables=100000,
            max_constraints=100000,
            memory_efficient=True,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["pyswarms"]
        )
        
        # Optuna (Hyperparameter Optimization)
        self.solvers["OPTUNA"] = SolverCapability(
            name="OPTUNA",
            category=SolverCategory.METAHEURISTIC,
            problem_types=["metaheuristic", "hyperparameter_optimization", "bayesian_optimization"],
            variable_types=["continuous", "integer", "categorical"],
            constraint_types=["penalty_based"],
            objective_types=["linear", "nonlinear"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 4,
                "speed": 4,
                "robustness": 4,
                "numerical_stability": 4
            },
            max_variables=10000,
            max_constraints=10000,
            memory_efficient=True,
            parallel_capable=True,
            supports_callbacks=True,
            license_type="open_source",
            installation_method="pip",
            dependencies=["optuna"]
        )
        
        # Initialize fallback chains for graceful degradation
        self._initialize_fallback_chains()
        
        # Initialize default configuration profiles
        self._initialize_configuration_profiles()
    
    def _initialize_fallback_chains(self):
        """Initialize fallback chains for graceful degradation"""
        
        # Linear Programming fallback chain
        self.fallback_chains["linear_programming"] = [
            "HiGHS_LP", "GLOP", "CLP", "SCIPY_LINPROG"
        ]
        
        # Mixed-Integer Programming fallback chain
        self.fallback_chains["mixed_integer_programming"] = [
            "HiGHS_MIP", "SCIP", "CBC", "CVXPY_GLPK_MI", "PYOMO_CBC"
        ]
        
        # Constraint Programming fallback chain
        self.fallback_chains["constraint_programming"] = [
            "CP_SAT", "OR_TOOLS_ROUTING"
        ]
        
        # Nonlinear Programming fallback chain
        self.fallback_chains["nonlinear_programming"] = [
            "IPOPT", "CVXPY_ECOS", "SCIPY_SLSQP", "BONMIN"
        ]
        
        # Metaheuristic fallback chain
        self.fallback_chains["metaheuristic"] = [
            "OPTUNA", "PYSWARMS", "DEAP"
        ]
        
        # Problem-specific fallback chains
        self.fallback_chains["production_scheduling"] = [
            "CP_SAT", "SCIP", "CBC"
        ]
        
        self.fallback_chains["capacity_planning"] = [
            "HiGHS_LP", "GLOP", "CLP"
        ]
        
        self.fallback_chains["routing"] = [
            "OR_TOOLS_ROUTING", "CP_SAT"
        ]
    
    def _initialize_configuration_profiles(self):
        """Initialize default configuration profiles for different problem types"""
        
        # Manufacturing-specific configurations
        self.configuration_profiles["production_scheduling"] = {
            "CP_SAT": {
                "max_time_in_seconds": 300,
                "num_search_workers": 4,
                "log_search_progress": True,
                "use_fixed_search": False
            },
            "SCIP": {
                "limits/time": 300,
                "parallel/maxnthreads": 4,
                "display/verblevel": 2,
                "heuristics/emphasis": "aggressive"
            }
        }
        
        self.configuration_profiles["capacity_planning"] = {
            "HiGHS_LP": {
                "time_limit": 60,
                "presolve": "on",
                "parallel": "on",
                "log_to_console": True
            },
            "GLOP": {
                "max_time_in_seconds": 60,
                "use_preprocessing": True,
                "use_dual_simplex": True
            }
        }
        
        self.configuration_profiles["resource_allocation"] = {
            "HiGHS_LP": {
                "time_limit": 30,
                "presolve": "on",
                "simplex_strategy": "dual"
            },
            "CLP": {
                "maximumSeconds": 30,
                "presolve": "on",
                "dualSimplex": True
            }
        }
    
    def _initial_availability_check(self):
        """Perform initial availability check for all solvers"""
        logger.info("Performing initial solver availability check...")
        
        available_count = 0
        for solver_name in self.solvers:
            if self.check_solver_availability(solver_name):
                available_count += 1
        
        logger.info(f"Initial availability check complete: {available_count}/{len(self.solvers)} solvers available")
    
    def check_solver_availability(self, solver_name: str) -> bool:
        """
        Check if a solver is available and functional
        
        Args:
            solver_name: Name of the solver to check
            
        Returns:
            True if solver is available, False otherwise
        """
        with self._lock:
            # Check cache first
            if solver_name in self.availability_cache:
                last_check = self.last_availability_check.get(solver_name)
                if last_check and (datetime.now() - last_check) < self.cache_duration:
                    return self.availability_cache[solver_name]
            
            # Perform availability check
            available = self._perform_availability_check(solver_name)
            
            # Update cache
            self.availability_cache[solver_name] = available
            self.last_availability_check[solver_name] = datetime.now()
            
            # Update solver status
            if solver_name in self.solvers:
                self.solvers[solver_name].status = SolverStatus.AVAILABLE if available else SolverStatus.UNAVAILABLE
                self.solvers[solver_name].last_checked = datetime.now()
            
            return available
    
    def _perform_availability_check(self, solver_name: str) -> bool:
        """Perform actual availability check for a specific solver"""
        
        if solver_name not in self.solvers:
            return False
        
        solver_capability = self.solvers[solver_name]
        
        try:
            # Check based on solver type and dependencies
            if solver_name == "GLOP":
                from ortools.linear_solver import pywraplp
                test_solver = pywraplp.Solver.CreateSolver('GLOP')
                available = test_solver is not None
                if available:
                    solver_capability.version_info = "OR-Tools"
            
            elif solver_name == "CLP":
                import pulp
                available = pulp.COIN_CMD().available()
                if available:
                    solver_capability.version_info = pulp.__version__
            
            elif solver_name == "HiGHS_LP" or solver_name == "HiGHS_MIP":
                import highspy
                test_highs = highspy.Highs()
                available = True
                solver_capability.version_info = highspy.__version__
            
            elif solver_name == "SCIPY_LINPROG" or solver_name == "SCIPY_SLSQP":
                from scipy.optimize import linprog, minimize
                available = True
                import scipy
                solver_capability.version_info = scipy.__version__
            
            elif solver_name == "SCIP":
                from pyscip import Model
                test_model = Model("test")
                available = True
                solver_capability.version_info = "PySCIP"
            
            elif solver_name == "CBC":
                import pulp
                available = pulp.PULP_CBC_CMD().available()
                if available:
                    solver_capability.version_info = pulp.__version__
            
            elif solver_name == "CP_SAT":
                from ortools.sat.python import cp_model
                test_model = cp_model.CpModel()
                available = True
                solver_capability.version_info = "OR-Tools"
            
            elif solver_name == "OR_TOOLS_ROUTING":
                from ortools.constraint_solver import routing_enums_pb2
                from ortools.constraint_solver import pywrapcp
                available = True
                solver_capability.version_info = "OR-Tools"
            
            elif solver_name == "IPOPT":
                import cyipopt
                available = True
                solver_capability.version_info = cyipopt.__version__
            
            elif solver_name == "BONMIN":
                import pyomo.environ as pyo
                available = pyo.SolverFactory('bonmin').available()
                if available:
                    solver_capability.version_info = pyo.__version__
            
            elif solver_name == "CVXPY_GLPK_MI" or solver_name == "CVXPY_ECOS":
                import cvxpy as cp
                backend = "GLPK_MI" if "GLPK" in solver_name else "ECOS"
                available = backend in cp.installed_solvers()
                if available:
                    solver_capability.version_info = cp.__version__
            
            elif solver_name == "PYOMO_CBC":
                import pyomo.environ as pyo
                available = pyo.SolverFactory('cbc').available()
                if available:
                    solver_capability.version_info = pyo.__version__
            
            elif solver_name == "DEAP":
                from deap import base, creator, tools, algorithms
                available = True
                import deap
                solver_capability.version_info = deap.__version__
            
            elif solver_name == "PYSWARMS":
                import pyswarms as ps
                available = True
                solver_capability.version_info = ps.__version__
            
            elif solver_name == "OPTUNA":
                import optuna
                available = True
                solver_capability.version_info = optuna.__version__
            
            else:
                available = False
            
            if available:
                solver_capability.error_message = None
                logger.debug(f"Solver {solver_name} is available (version: {solver_capability.version_info})")
            else:
                solver_capability.error_message = "Solver not available"
                logger.debug(f"Solver {solver_name} is not available")
            
            return available
            
        except ImportError as e:
            solver_capability.error_message = f"Import error: {str(e)}"
            logger.debug(f"Solver {solver_name} unavailable due to import error: {e}")
            return False
        except Exception as e:
            solver_capability.error_message = f"Error: {str(e)}"
            logger.error(f"Error checking availability for solver {solver_name}: {e}")
            return False
    
    def get_available_solvers(self, category: Optional[SolverCategory] = None) -> List[str]:
        """
        Get list of available solvers, optionally filtered by category
        
        Args:
            category: Optional category filter
            
        Returns:
            List of available solver names
        """
        available = []
        
        for solver_name, solver_capability in self.solvers.items():
            if category and solver_capability.category != category:
                continue
            
            if self.check_solver_availability(solver_name):
                available.append(solver_name)
        
        return available
    
    def get_compatible_solvers(self, problem_type: str, problem_size: str = "medium") -> List[str]:
        """
        Get list of compatible solvers for given problem type and size
        
        Args:
            problem_type: Type of optimization problem
            problem_size: Problem size category (small, medium, large)
            
        Returns:
            List of compatible solver names, sorted by suitability
        """
        compatible = []
        
        for solver_name, solver_capability in self.solvers.items():
            if (problem_type in solver_capability.problem_types and 
                self.check_solver_availability(solver_name)):
                
                # Consider performance profile for problem size
                size_score = solver_capability.performance_profile.get(f"{problem_size}_problems", 3)
                if size_score >= 3:  # Minimum acceptable performance
                    compatible.append((solver_name, size_score))
        
        # Sort by performance score (descending)
        compatible.sort(key=lambda x: x[1], reverse=True)
        
        return [solver_name for solver_name, _ in compatible]
    
    def get_fallback_solvers(self, primary_solver: str, problem_type: str) -> List[str]:
        """
        Get fallback solvers for graceful degradation
        
        Args:
            primary_solver: Primary solver that failed
            problem_type: Type of optimization problem
            
        Returns:
            List of fallback solver names
        """
        # Get fallback chain for problem type
        fallback_chain = self.fallback_chains.get(problem_type, [])
        
        # Remove primary solver from chain and filter by availability
        fallbacks = []
        for solver_name in fallback_chain:
            if solver_name != primary_solver and self.check_solver_availability(solver_name):
                fallbacks.append(solver_name)
        
        # If no specific fallback chain, use category-based fallback
        if not fallbacks and primary_solver in self.solvers:
            primary_category = self.solvers[primary_solver].category
            category_fallbacks = self.fallback_chains.get(primary_category.value, [])
            
            for solver_name in category_fallbacks:
                if solver_name != primary_solver and self.check_solver_availability(solver_name):
                    fallbacks.append(solver_name)
        
        return fallbacks
    
    def get_solver_configuration(self, solver_name: str, problem_type: str) -> Dict[str, Any]:
        """
        Get solver-specific configuration for a problem type
        
        Args:
            solver_name: Name of the solver
            problem_type: Type of optimization problem
            
        Returns:
            Configuration dictionary
        """
        # Get problem-specific configuration
        problem_config = self.configuration_profiles.get(problem_type, {})
        solver_config = problem_config.get(solver_name, {})
        
        # Add default configuration based on solver capability
        if solver_name in self.solvers:
            solver_capability = self.solvers[solver_name]
            
            # Add default timeout based on problem complexity
            if "timeout" not in solver_config and "time_limit" not in solver_config:
                if solver_capability.category == SolverCategory.METAHEURISTIC:
                    solver_config["timeout"] = 300  # 5 minutes for metaheuristics
                else:
                    solver_config["timeout"] = 60   # 1 minute for exact solvers
            
            # Add parallel configuration if supported
            if solver_capability.parallel_capable and "parallel" not in solver_config:
                solver_config["parallel"] = True
                solver_config["num_threads"] = 4
        
        return solver_config
    
    def record_solver_performance(self, solver_name: str, execution_time: float, 
                                 solution_quality: float, problem_characteristics: Dict[str, Any]):
        """
        Record solver performance for future optimization
        
        Args:
            solver_name: Name of the solver
            execution_time: Time taken to solve
            solution_quality: Quality score of the solution
            problem_characteristics: Characteristics of the problem solved
        """
        with self._lock:
            performance_record = {
                "solver_name": solver_name,
                "execution_time": execution_time,
                "solution_quality": solution_quality,
                "problem_characteristics": problem_characteristics,
                "timestamp": datetime.now().isoformat()
            }
            
            self.performance_history[solver_name].append(performance_record)
            
            # Keep only recent history (last 100 records per solver)
            if len(self.performance_history[solver_name]) > 100:
                self.performance_history[solver_name] = self.performance_history[solver_name][-100:]
    
    def get_solver_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive solver registry statistics
        
        Returns:
            Dictionary with solver statistics
        """
        stats = {
            "total_solvers": len(self.solvers),
            "available_solvers": len([s for s in self.solvers if self.check_solver_availability(s)]),
            "solvers_by_category": {},
            "availability_by_category": {},
            "performance_summary": {}
        }
        
        # Count by category
        for solver_name, solver_capability in self.solvers.items():
            category = solver_capability.category.value
            
            if category not in stats["solvers_by_category"]:
                stats["solvers_by_category"][category] = 0
                stats["availability_by_category"][category] = 0
            
            stats["solvers_by_category"][category] += 1
            
            if self.check_solver_availability(solver_name):
                stats["availability_by_category"][category] += 1
        
        # Performance summary
        for solver_name, history in self.performance_history.items():
            if history:
                execution_times = [record["execution_time"] for record in history]
                quality_scores = [record["solution_quality"] for record in history]
                
                stats["performance_summary"][solver_name] = {
                    "total_runs": len(history),
                    "avg_execution_time": sum(execution_times) / len(execution_times),
                    "avg_solution_quality": sum(quality_scores) / len(quality_scores),
                    "last_run": history[-1]["timestamp"]
                }
        
        return stats
    
    def export_registry(self) -> Dict[str, Any]:
        """
        Export complete registry for serialization
        
        Returns:
            Dictionary representation of the registry
        """
        return {
            "solvers": {name: capability.to_dict() for name, capability in self.solvers.items()},
            "fallback_chains": self.fallback_chains,
            "configuration_profiles": self.configuration_profiles,
            "performance_history": dict(self.performance_history),
            "statistics": self.get_solver_statistics(),
            "export_timestamp": datetime.now().isoformat()
        }
    
    def refresh_availability(self):
        """Force refresh of all solver availability checks"""
        logger.info("Refreshing solver availability...")
        
        with self._lock:
            # Clear cache
            self.availability_cache.clear()
            self.last_availability_check.clear()
            
            # Re-check all solvers
            available_count = 0
            for solver_name in self.solvers:
                if self.check_solver_availability(solver_name):
                    available_count += 1
        
        logger.info(f"Availability refresh complete: {available_count}/{len(self.solvers)} solvers available")


# Global registry instance
enhanced_solver_registry = EnhancedSolverRegistry()


def get_solver_registry() -> EnhancedSolverRegistry:
    """Get the global enhanced solver registry instance"""
    return enhanced_solver_registry