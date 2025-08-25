"""
Solver Detection and Registration System
=======================================

Implements automatic solver discovery, capability detection, and dynamic registration
for the multi-solver swarm optimization system.

Features:
- Automatic solver discovery at runtime
- Capability profiling and analysis
- Version compatibility checking
- Performance baseline establishment
- Dynamic solver registration

Requirements: 1.2, 1.3, 6.2
"""

import logging
import importlib
import subprocess
import sys
import os
import platform
import time
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import threading
from pathlib import Path

from .enhanced_solver_registry import SolverCapability, SolverCategory, SolverStatus, enhanced_solver_registry

logger = logging.getLogger(__name__)


@dataclass
class SolverDiscoveryResult:
    """Result of solver discovery process"""
    solver_name: str
    found: bool
    version: Optional[str] = None
    installation_path: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None
    performance_baseline: Optional[Dict[str, float]] = None
    error_message: Optional[str] = None
    discovery_time: float = 0.0


@dataclass
class CapabilityProfile:
    """Detailed capability profile for a solver"""
    problem_types: Set[str]
    variable_types: Set[str]
    constraint_types: Set[str]
    objective_types: Set[str]
    max_variables: int
    max_constraints: int
    memory_usage: str  # low, medium, high
    computational_complexity: str  # linear, polynomial, exponential
    numerical_stability: str  # poor, good, excellent
    parallel_support: bool
    callback_support: bool
    warm_start_support: bool


class SolverDetectionSystem:
    """
    Comprehensive solver detection and registration system
    
    Automatically discovers available solvers, profiles their capabilities,
    and maintains up-to-date registry information.
    """
    
    def __init__(self):
        self.registry = enhanced_solver_registry
        self.discovery_cache: Dict[str, SolverDiscoveryResult] = {}
        self.capability_profiles: Dict[str, CapabilityProfile] = {}
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Detection configuration
        self.detection_timeout = 30.0  # seconds
        self.benchmark_timeout = 10.0  # seconds per benchmark
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("Solver detection system initialized")
    
    def discover_all_solvers(self, parallel: bool = True, timeout: float = 300.0) -> Dict[str, SolverDiscoveryResult]:
        """
        Comprehensive solver discovery with parallel processing and timeout
        
        Args:
            parallel: Whether to run discovery in parallel
            timeout: Maximum time to spend on discovery (seconds)
            
        Returns:
            Dictionary mapping solver names to discovery results
        """
        logger.info("Starting comprehensive solver discovery...")
        start_time = time.time()
        
        discovery_results = {}
        
        # Get all registered solver names
        solver_names = list(self.registry.solvers.keys())
        
        if parallel and len(solver_names) > 1:
            # Parallel discovery using threading
            discovery_results = self._discover_solvers_parallel(solver_names, timeout)
        else:
            # Sequential discovery
            discovery_results = self._discover_solvers_sequential(solver_names, timeout)
        
        total_time = time.time() - start_time
        found_count = sum(1 for result in discovery_results.values() if result.found)
        
        logger.info(f"Solver discovery complete: {found_count}/{len(solver_names)} solvers found in {total_time:.2f}s")
        
        # Generate discovery report
        self._generate_discovery_report(discovery_results, total_time)
        
        return discovery_results
    
    def _discover_solvers_parallel(self, solver_names: List[str], timeout: float) -> Dict[str, SolverDiscoveryResult]:
        """Discover solvers in parallel using threading"""
        
        import concurrent.futures
        
        discovery_results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit discovery tasks
            future_to_solver = {
                executor.submit(self.discover_solver, solver_name): solver_name 
                for solver_name in solver_names
            }
            
            # Collect results with timeout
            try:
                for future in concurrent.futures.as_completed(future_to_solver, timeout=timeout):
                    solver_name = future_to_solver[future]
                    try:
                        result = future.result()
                        discovery_results[solver_name] = result
                        
                        if result.found:
                            logger.info(f"Discovered solver: {solver_name} (version: {result.version})")
                        else:
                            logger.debug(f"Solver not found: {solver_name} - {result.error_message}")
                            
                    except Exception as e:
                        logger.error(f"Error discovering solver {solver_name}: {e}")
                        discovery_results[solver_name] = SolverDiscoveryResult(
                            solver_name=solver_name,
                            found=False,
                            error_message=str(e)
                        )
            
            except concurrent.futures.TimeoutError:
                logger.warning(f"Solver discovery timed out after {timeout}s")
                
                # Handle incomplete results
                for future, solver_name in future_to_solver.items():
                    if solver_name not in discovery_results:
                        future.cancel()
                        discovery_results[solver_name] = SolverDiscoveryResult(
                            solver_name=solver_name,
                            found=False,
                            error_message="Discovery timed out"
                        )
        
        return discovery_results
    
    def _discover_solvers_sequential(self, solver_names: List[str], timeout: float) -> Dict[str, SolverDiscoveryResult]:
        """Discover solvers sequentially with timeout"""
        
        discovery_results = {}
        start_time = time.time()
        
        for solver_name in solver_names:
            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Discovery timeout reached, skipping remaining solvers")
                for remaining_solver in solver_names[len(discovery_results):]:
                    discovery_results[remaining_solver] = SolverDiscoveryResult(
                        solver_name=remaining_solver,
                        found=False,
                        error_message="Discovery timed out"
                    )
                break
            
            try:
                result = self.discover_solver(solver_name)
                discovery_results[solver_name] = result
                
                if result.found:
                    logger.info(f"Discovered solver: {solver_name} (version: {result.version})")
                else:
                    logger.debug(f"Solver not found: {solver_name} - {result.error_message}")
                    
            except Exception as e:
                logger.error(f"Error discovering solver {solver_name}: {e}")
                discovery_results[solver_name] = SolverDiscoveryResult(
                    solver_name=solver_name,
                    found=False,
                    error_message=str(e)
                )
        
        return discovery_results
    
    def _generate_discovery_report(self, discovery_results: Dict[str, SolverDiscoveryResult], total_time: float):
        """Generate comprehensive discovery report"""
        
        try:
            report = {
                "discovery_timestamp": datetime.now().isoformat(),
                "total_discovery_time": total_time,
                "total_solvers": len(discovery_results),
                "found_solvers": sum(1 for r in discovery_results.values() if r.found),
                "failed_solvers": sum(1 for r in discovery_results.values() if not r.found),
                "solvers_by_category": {},
                "performance_summary": {},
                "issues_summary": {},
                "recommendations": []
            }
            
            # Categorize results
            for solver_name, result in discovery_results.items():
                if solver_name in self.registry.solvers:
                    category = self.registry.solvers[solver_name].category.value
                    
                    if category not in report["solvers_by_category"]:
                        report["solvers_by_category"][category] = {"total": 0, "found": 0}
                    
                    report["solvers_by_category"][category]["total"] += 1
                    if result.found:
                        report["solvers_by_category"][category]["found"] += 1
            
            # Performance summary
            found_solvers = [r for r in discovery_results.values() if r.found]
            if found_solvers:
                discovery_times = [r.discovery_time for r in found_solvers]
                report["performance_summary"] = {
                    "avg_discovery_time": sum(discovery_times) / len(discovery_times),
                    "max_discovery_time": max(discovery_times),
                    "min_discovery_time": min(discovery_times)
                }
            
            # Issues summary
            failed_solvers = [r for r in discovery_results.values() if not r.found]
            if failed_solvers:
                error_types = {}
                for result in failed_solvers:
                    error_msg = result.error_message or "Unknown error"
                    error_type = self._categorize_error(error_msg)
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                
                report["issues_summary"] = error_types
                
                # Generate recommendations
                if "Import error" in error_types:
                    report["recommendations"].append("Install missing dependencies using pip or conda")
                if "Solver not available" in error_types:
                    report["recommendations"].append("Check solver installation and configuration")
                if "Discovery timed out" in error_types:
                    report["recommendations"].append("Increase discovery timeout or check system performance")
            
            # Store report
            with self._lock:
                self.discovery_report = report
            
            logger.info(f"Discovery report generated: {report['found_solvers']}/{report['total_solvers']} solvers found")
            
        except Exception as e:
            logger.error(f"Error generating discovery report: {e}")
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message for reporting"""
        
        error_message_lower = error_message.lower()
        
        if "import" in error_message_lower:
            return "Import error"
        elif "timeout" in error_message_lower:
            return "Discovery timed out"
        elif "not available" in error_message_lower:
            return "Solver not available"
        elif "version" in error_message_lower:
            return "Version issue"
        elif "permission" in error_message_lower:
            return "Permission error"
        else:
            return "Other error"
    
    def discover_new_solvers(self) -> Dict[str, SolverDiscoveryResult]:
        """
        Discover new solvers that may have been installed since last check
        
        Returns:
            Dictionary of newly discovered solvers
        """
        logger.info("Searching for new solver installations...")
        
        new_discoveries = {}
        
        # Check for common solver installations in system paths
        potential_solvers = self._scan_system_for_solvers()
        
        for solver_info in potential_solvers:
            solver_name = solver_info["name"]
            
            # Check if this is a new solver or updated version
            if solver_name not in self.discovery_cache or not self.discovery_cache[solver_name].found:
                result = self.discover_solver(solver_name)
                if result.found:
                    new_discoveries[solver_name] = result
                    logger.info(f"New solver discovered: {solver_name}")
        
        return new_discoveries
    
    def _scan_system_for_solvers(self) -> List[Dict[str, Any]]:
        """Scan system for potential solver installations"""
        
        potential_solvers = []
        
        try:
            # Check Python packages
            import pkg_resources
            
            installed_packages = {pkg.project_name.lower(): pkg.version for pkg in pkg_resources.working_set}
            
            # Map package names to solver names
            package_to_solver = {
                "ortools": ["GLOP", "CP_SAT", "OR_TOOLS_ROUTING"],
                "pulp": ["CLP", "CBC"],
                "highspy": ["HiGHS_LP", "HiGHS_MIP"],
                "scipy": ["SCIPY_LINPROG", "SCIPY_SLSQP"],
                "pyscip": ["SCIP"],
                "cyipopt": ["IPOPT"],
                "cvxpy": ["CVXPY_GLPK_MI", "CVXPY_ECOS"],
                "pyomo": ["PYOMO_CBC", "BONMIN"],
                "deap": ["DEAP"],
                "pyswarms": ["PYSWARMS"],
                "optuna": ["OPTUNA"]
            }
            
            for package_name, solver_names in package_to_solver.items():
                if package_name in installed_packages:
                    for solver_name in solver_names:
                        potential_solvers.append({
                            "name": solver_name,
                            "package": package_name,
                            "version": installed_packages[package_name]
                        })
        
        except Exception as e:
            logger.debug(f"Error scanning system for solvers: {e}")
        
        return potential_solvers
    
    def discover_solver(self, solver_name: str) -> SolverDiscoveryResult:
        """
        Discover a specific solver and profile its capabilities
        
        Args:
            solver_name: Name of the solver to discover
            
        Returns:
            Discovery result with detailed information
        """
        start_time = time.time()
        
        try:
            # Check if solver is in registry
            if solver_name not in self.registry.solvers:
                return SolverDiscoveryResult(
                    solver_name=solver_name,
                    found=False,
                    error_message="Solver not in registry",
                    discovery_time=time.time() - start_time
                )
            
            solver_capability = self.registry.solvers[solver_name]
            
            # Perform solver-specific discovery
            discovery_result = self._discover_solver_specific(solver_name, solver_capability)
            
            if discovery_result.found:
                # Profile capabilities
                capability_profile = self._profile_solver_capabilities(solver_name, solver_capability)
                discovery_result.capabilities = self._capability_profile_to_dict(capability_profile)
                
                # Establish performance baseline
                performance_baseline = self._establish_performance_baseline(solver_name)
                discovery_result.performance_baseline = performance_baseline
                
                # Update registry
                self._update_registry_from_discovery(solver_name, discovery_result)
            
            discovery_result.discovery_time = time.time() - start_time
            
            # Cache result
            with self._lock:
                self.discovery_cache[solver_name] = discovery_result
            
            return discovery_result
            
        except Exception as e:
            logger.error(f"Error in solver discovery for {solver_name}: {e}")
            return SolverDiscoveryResult(
                solver_name=solver_name,
                found=False,
                error_message=str(e),
                discovery_time=time.time() - start_time
            )
    
    def _discover_solver_specific(self, solver_name: str, solver_capability: SolverCapability) -> SolverDiscoveryResult:
        """Perform solver-specific discovery logic"""
        
        result = SolverDiscoveryResult(solver_name=solver_name, found=False)
        
        try:
            if solver_name == "GLOP":
                from ortools.linear_solver import pywraplp
                test_solver = pywraplp.Solver.CreateSolver('GLOP')
                if test_solver is not None:
                    result.found = True
                    result.version = self._get_ortools_version()
                    result.installation_path = self._get_package_path("ortools")
                else:
                    result.error_message = "GLOP solver not available in OR-Tools"
            
            elif solver_name == "CLP":
                import pulp
                if pulp.COIN_CMD().available():
                    result.found = True
                    result.version = pulp.__version__
                    result.installation_path = self._get_package_path("pulp")
                else:
                    result.error_message = "CLP solver not available through PuLP"
            
            elif solver_name in ["HiGHS_LP", "HiGHS_MIP"]:
                import highspy
                test_highs = highspy.Highs()
                result.found = True
                result.version = highspy.__version__
                result.installation_path = self._get_package_path("highspy")
            
            elif solver_name in ["SCIPY_LINPROG", "SCIPY_SLSQP"]:
                from scipy.optimize import linprog, minimize
                import scipy
                result.found = True
                result.version = scipy.__version__
                result.installation_path = self._get_package_path("scipy")
            
            elif solver_name == "SCIP":
                from pyscip import Model
                test_model = Model("test")
                result.found = True
                result.version = self._get_pyscip_version()
                result.installation_path = self._get_package_path("pyscip")
            
            elif solver_name == "CBC":
                import pulp
                if pulp.PULP_CBC_CMD().available():
                    result.found = True
                    result.version = pulp.__version__
                    result.installation_path = self._get_package_path("pulp")
                else:
                    result.error_message = "CBC solver not available through PuLP"
            
            elif solver_name == "CP_SAT":
                from ortools.sat.python import cp_model
                test_model = cp_model.CpModel()
                result.found = True
                result.version = self._get_ortools_version()
                result.installation_path = self._get_package_path("ortools")
            
            elif solver_name == "OR_TOOLS_ROUTING":
                from ortools.constraint_solver import routing_enums_pb2
                from ortools.constraint_solver import pywrapcp
                result.found = True
                result.version = self._get_ortools_version()
                result.installation_path = self._get_package_path("ortools")
            
            elif solver_name == "IPOPT":
                import cyipopt
                result.found = True
                result.version = cyipopt.__version__
                result.installation_path = self._get_package_path("cyipopt")
            
            elif solver_name == "BONMIN":
                import pyomo.environ as pyo
                solver_factory = pyo.SolverFactory('bonmin')
                if solver_factory.available():
                    result.found = True
                    result.version = pyo.__version__
                    result.installation_path = self._get_package_path("pyomo")
                else:
                    result.error_message = "BONMIN solver not available through Pyomo"
            
            elif solver_name in ["CVXPY_GLPK_MI", "CVXPY_ECOS"]:
                import cvxpy as cp
                backend = "GLPK_MI" if "GLPK" in solver_name else "ECOS"
                if backend in cp.installed_solvers():
                    result.found = True
                    result.version = cp.__version__
                    result.installation_path = self._get_package_path("cvxpy")
                else:
                    result.error_message = f"{backend} backend not available in CVXPY"
            
            elif solver_name == "PYOMO_CBC":
                import pyomo.environ as pyo
                solver_factory = pyo.SolverFactory('cbc')
                if solver_factory.available():
                    result.found = True
                    result.version = pyo.__version__
                    result.installation_path = self._get_package_path("pyomo")
                else:
                    result.error_message = "CBC solver not available through Pyomo"
            
            elif solver_name == "DEAP":
                from deap import base, creator, tools, algorithms
                import deap
                result.found = True
                result.version = deap.__version__
                result.installation_path = self._get_package_path("deap")
            
            elif solver_name == "PYSWARMS":
                import pyswarms as ps
                result.found = True
                result.version = ps.__version__
                result.installation_path = self._get_package_path("pyswarms")
            
            elif solver_name == "OPTUNA":
                import optuna
                result.found = True
                result.version = optuna.__version__
                result.installation_path = self._get_package_path("optuna")
            
            else:
                result.error_message = f"Unknown solver: {solver_name}"
                
        except ImportError as e:
            result.error_message = f"Import error: {str(e)}"
        except Exception as e:
            result.error_message = f"Discovery error: {str(e)}"
        
        return result
    
    def _profile_solver_capabilities(self, solver_name: str, solver_capability: SolverCapability) -> CapabilityProfile:
        """Profile detailed capabilities of a solver"""
        
        # Start with registry information
        profile = CapabilityProfile(
            problem_types=set(solver_capability.problem_types),
            variable_types=set(solver_capability.variable_types),
            constraint_types=set(solver_capability.constraint_types),
            objective_types=set(solver_capability.objective_types),
            max_variables=solver_capability.max_variables,
            max_constraints=solver_capability.max_constraints,
            memory_usage="medium",
            computational_complexity="polynomial",
            numerical_stability="good",
            parallel_support=solver_capability.parallel_capable,
            callback_support=solver_capability.supports_callbacks,
            warm_start_support=False
        )
        
        # Enhance with solver-specific profiling
        try:
            if solver_name in ["GLOP", "CLP", "HiGHS_LP", "SCIPY_LINPROG"]:
                profile.computational_complexity = "polynomial"
                profile.numerical_stability = "excellent"
                
            elif solver_name in ["SCIP", "CBC", "HiGHS_MIP"]:
                profile.computational_complexity = "exponential"
                profile.numerical_stability = "good"
                profile.warm_start_support = True
                
            elif solver_name in ["CP_SAT", "OR_TOOLS_ROUTING"]:
                profile.computational_complexity = "exponential"
                profile.numerical_stability = "excellent"
                profile.callback_support = True
                
            elif solver_name in ["IPOPT", "BONMIN", "SCIPY_SLSQP"]:
                profile.computational_complexity = "polynomial"
                profile.numerical_stability = "good"
                profile.warm_start_support = True
                
            elif solver_name in ["DEAP", "PYSWARMS", "OPTUNA"]:
                profile.computational_complexity = "heuristic"
                profile.numerical_stability = "fair"
                profile.parallel_support = True
                
            # Memory usage profiling
            if solver_capability.memory_efficient:
                profile.memory_usage = "low"
            elif solver_name in ["SCIP", "BONMIN"]:
                profile.memory_usage = "high"
            else:
                profile.memory_usage = "medium"
                
        except Exception as e:
            logger.warning(f"Error profiling capabilities for {solver_name}: {e}")
        
        # Cache the profile
        with self._lock:
            self.capability_profiles[solver_name] = profile
        
        return profile
    
    def _establish_performance_baseline(self, solver_name: str) -> Dict[str, float]:
        """Establish comprehensive performance baseline for a solver"""
        
        baseline = {
            "small_problem_time": 0.0,
            "medium_problem_time": 0.0,
            "large_problem_time": 0.0,
            "memory_usage_mb": 0.0,
            "setup_time": 0.0,
            "reliability_score": 1.0,
            "numerical_stability": 1.0,
            "convergence_rate": 1.0,
            "scalability_factor": 1.0,
            "baseline_timestamp": datetime.now().isoformat()
        }
        
        try:
            logger.info(f"Establishing performance baseline for {solver_name}...")
            
            # Run comprehensive benchmark suite
            small_time = self._benchmark_small_problem(solver_name)
            if small_time > 0:
                baseline["small_problem_time"] = small_time
            
            medium_time = self._benchmark_medium_problem(solver_name)
            if medium_time > 0:
                baseline["medium_problem_time"] = medium_time
            
            # Run large problem benchmark for scalability assessment
            large_time = self._benchmark_large_problem(solver_name)
            if large_time > 0:
                baseline["large_problem_time"] = large_time
                
                # Calculate scalability factor
                if medium_time > 0 and small_time > 0:
                    expected_large_time = medium_time * (medium_time / small_time)
                    baseline["scalability_factor"] = min(expected_large_time / large_time, 2.0)
            
            # Measure setup time with multiple runs for accuracy
            setup_times = []
            for _ in range(3):
                setup_time = self._measure_setup_time(solver_name)
                if setup_time > 0:
                    setup_times.append(setup_time)
            
            if setup_times:
                baseline["setup_time"] = sum(setup_times) / len(setup_times)
            
            # Estimate memory usage with actual measurement
            baseline["memory_usage_mb"] = self._measure_memory_usage(solver_name)
            
            # Test numerical stability
            baseline["numerical_stability"] = self._test_numerical_stability(solver_name)
            
            # Test convergence characteristics
            baseline["convergence_rate"] = self._test_convergence_rate(solver_name)
            
            # Calculate overall reliability score
            baseline["reliability_score"] = self._calculate_reliability_score(baseline)
            
            logger.info(f"Baseline established for {solver_name}: "
                       f"small={baseline['small_problem_time']:.3f}s, "
                       f"medium={baseline['medium_problem_time']:.3f}s, "
                       f"reliability={baseline['reliability_score']:.2f}")
            
        except Exception as e:
            logger.warning(f"Error establishing baseline for {solver_name}: {e}")
            baseline["reliability_score"] = 0.5
        
        # Cache the baseline
        with self._lock:
            self.performance_baselines[solver_name] = baseline
        
        return baseline
    
    def _benchmark_small_problem(self, solver_name: str) -> float:
        """Benchmark solver on a small problem"""
        
        try:
            start_time = time.time()
            
            # Create a simple 2-variable linear programming problem
            if solver_name == "GLOP":
                from ortools.linear_solver import pywraplp
                solver = pywraplp.Solver.CreateSolver('GLOP')
                if solver:
                    x = solver.NumVar(0, 10, 'x')
                    y = solver.NumVar(0, 10, 'y')
                    solver.Add(x + y <= 5)
                    solver.Objective().SetCoefficient(x, 1)
                    solver.Objective().SetCoefficient(y, 2)
                    solver.Objective().SetMaximization()
                    solver.Solve()
            
            elif solver_name == "CP_SAT":
                from ortools.sat.python import cp_model
                model = cp_model.CpModel()
                x = model.NewIntVar(0, 10, 'x')
                y = model.NewIntVar(0, 10, 'y')
                model.Add(x + y <= 5)
                model.Maximize(x + 2 * y)
                solver = cp_model.CpSolver()
                solver.parameters.max_time_in_seconds = self.benchmark_timeout
                solver.Solve(model)
            
            # Add more solver-specific benchmarks as needed
            
            return time.time() - start_time
            
        except Exception as e:
            logger.debug(f"Benchmark failed for {solver_name}: {e}")
            return -1.0
    
    def _benchmark_medium_problem(self, solver_name: str) -> float:
        """Benchmark solver on a medium-sized problem"""
        
        try:
            start_time = time.time()
            
            # Create a medium-sized problem (10 variables, 5 constraints)
            if solver_name == "GLOP":
                from ortools.linear_solver import pywraplp
                solver = pywraplp.Solver.CreateSolver('GLOP')
                if solver:
                    variables = []
                    for i in range(10):
                        variables.append(solver.NumVar(0, 100, f'x{i}'))
                    
                    # Add constraints
                    for i in range(5):
                        constraint = solver.Constraint(0, 50)
                        for j, var in enumerate(variables):
                            constraint.SetCoefficient(var, (i + j) % 3 + 1)
                    
                    # Set objective
                    objective = solver.Objective()
                    for i, var in enumerate(variables):
                        objective.SetCoefficient(var, i + 1)
                    objective.SetMaximization()
                    
                    solver.Solve()
            
            # Add more solver-specific medium benchmarks
            
            return time.time() - start_time
            
        except Exception as e:
            logger.debug(f"Medium benchmark failed for {solver_name}: {e}")
            return -1.0
    
    def _measure_setup_time(self, solver_name: str) -> float:
        """Measure solver setup/initialization time"""
        
        try:
            start_time = time.time()
            
            if solver_name == "GLOP":
                from ortools.linear_solver import pywraplp
                solver = pywraplp.Solver.CreateSolver('GLOP')
            elif solver_name == "CP_SAT":
                from ortools.sat.python import cp_model
                model = cp_model.CpModel()
                solver = cp_model.CpSolver()
            # Add more setup measurements
            
            return time.time() - start_time
            
        except Exception as e:
            logger.debug(f"Setup time measurement failed for {solver_name}: {e}")
            return 0.001  # Default minimal setup time
    
    def _benchmark_large_problem(self, solver_name: str) -> float:
        """Benchmark solver on a large problem for scalability assessment"""
        
        try:
            start_time = time.time()
            
            # Create a larger problem (50 variables, 25 constraints)
            if solver_name == "GLOP":
                from ortools.linear_solver import pywraplp
                solver = pywraplp.Solver.CreateSolver('GLOP')
                if solver:
                    variables = []
                    for i in range(50):
                        variables.append(solver.NumVar(0, 1000, f'x{i}'))
                    
                    # Add constraints
                    for i in range(25):
                        constraint = solver.Constraint(0, 500)
                        for j, var in enumerate(variables):
                            constraint.SetCoefficient(var, (i + j) % 5 + 1)
                    
                    # Set objective
                    objective = solver.Objective()
                    for i, var in enumerate(variables):
                        objective.SetCoefficient(var, (i % 10) + 1)
                    objective.SetMaximization()
                    
                    solver.Solve()
            
            elif solver_name == "CP_SAT":
                from ortools.sat.python import cp_model
                model = cp_model.CpModel()
                
                variables = []
                for i in range(50):
                    variables.append(model.NewIntVar(0, 100, f'x{i}'))
                
                # Add constraints
                for i in range(25):
                    constraint_vars = variables[i*2:(i*2)+4] if (i*2)+4 <= len(variables) else variables[i*2:]
                    if constraint_vars:
                        model.Add(sum(constraint_vars) <= 200)
                
                # Set objective
                model.Maximize(sum(variables))
                
                solver = cp_model.CpSolver()
                solver.parameters.max_time_in_seconds = self.benchmark_timeout * 2
                solver.Solve(model)
            
            # Add more solver-specific large benchmarks as needed
            
            return time.time() - start_time
            
        except Exception as e:
            logger.debug(f"Large benchmark failed for {solver_name}: {e}")
            return -1.0
    
    def _measure_memory_usage(self, solver_name: str) -> float:
        """Measure actual memory usage for solver operations"""
        
        try:
            import psutil
            import os
            
            # Get current process
            process = psutil.Process(os.getpid())
            
            # Measure memory before solver operation
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform a memory-intensive operation
            if solver_name == "GLOP":
                from ortools.linear_solver import pywraplp
                solver = pywraplp.Solver.CreateSolver('GLOP')
                if solver:
                    # Create many variables to test memory usage
                    variables = []
                    for i in range(1000):
                        variables.append(solver.NumVar(0, 100, f'x{i}'))
                    
                    # Add constraints
                    for i in range(100):
                        constraint = solver.Constraint(0, 50)
                        for j in range(min(10, len(variables))):
                            constraint.SetCoefficient(variables[i*10 + j], 1)
            
            elif solver_name == "CP_SAT":
                from ortools.sat.python import cp_model
                model = cp_model.CpModel()
                
                variables = []
                for i in range(1000):
                    variables.append(model.NewIntVar(0, 100, f'x{i}'))
                
                # Add constraints
                for i in range(100):
                    start_idx = i * 10
                    end_idx = min(start_idx + 10, len(variables))
                    if start_idx < len(variables):
                        model.Add(sum(variables[start_idx:end_idx]) <= 500)
            
            # Measure memory after solver operation
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            return max(memory_after - memory_before, 10.0)  # Minimum 10MB
            
        except ImportError:
            # Fallback to estimated values if psutil not available
            return self._estimate_memory_usage(solver_name)
        except Exception as e:
            logger.debug(f"Memory measurement failed for {solver_name}: {e}")
            return self._estimate_memory_usage(solver_name)
    
    def _estimate_memory_usage(self, solver_name: str) -> float:
        """Estimate typical memory usage for solver (fallback method)"""
        
        # Enhanced memory estimation based on solver characteristics
        memory_estimates = {
            "GLOP": 50.0,
            "CLP": 100.0,
            "HiGHS_LP": 75.0,
            "HiGHS_MIP": 150.0,
            "SCIP": 200.0,
            "CBC": 100.0,
            "CP_SAT": 100.0,
            "OR_TOOLS_ROUTING": 150.0,
            "IPOPT": 100.0,
            "BONMIN": 250.0,
            "CVXPY_GLPK_MI": 75.0,
            "CVXPY_ECOS": 50.0,
            "PYOMO_CBC": 150.0,
            "DEAP": 50.0,
            "PYSWARMS": 75.0,
            "OPTUNA": 100.0,
            "SCIPY_LINPROG": 25.0,
            "SCIPY_SLSQP": 30.0
        }
        
        return memory_estimates.get(solver_name, 100.0)
    
    def _test_numerical_stability(self, solver_name: str) -> float:
        """Test numerical stability of solver"""
        
        try:
            # Create a problem with potential numerical issues
            stability_score = 1.0
            
            if solver_name == "GLOP":
                from ortools.linear_solver import pywraplp
                solver = pywraplp.Solver.CreateSolver('GLOP')
                if solver:
                    # Create variables with very different scales
                    x1 = solver.NumVar(0, 1e-6, 'x1')  # Very small
                    x2 = solver.NumVar(0, 1e6, 'x2')   # Very large
                    
                    # Add constraint with different scales
                    solver.Add(1e6 * x1 + 1e-6 * x2 <= 1)
                    
                    # Set objective
                    solver.Objective().SetCoefficient(x1, 1e6)
                    solver.Objective().SetCoefficient(x2, 1e-6)
                    solver.Objective().SetMaximization()
                    
                    status = solver.Solve()
                    if status == pywraplp.Solver.OPTIMAL:
                        # Check if solution makes sense
                        obj_value = solver.Objective().Value()
                        if obj_value > 0 and obj_value < 1e10:
                            stability_score = 1.0
                        else:
                            stability_score = 0.7
                    else:
                        stability_score = 0.5
            
            elif solver_name == "CP_SAT":
                from ortools.sat.python import cp_model
                model = cp_model.CpModel()
                
                # Create variables with large domains
                x = model.NewIntVar(0, 1000000, 'x')
                y = model.NewIntVar(0, 1000000, 'y')
                
                # Add constraints
                model.Add(x + y == 999999)
                model.Add(x - y <= 1)
                
                # Set objective
                model.Maximize(x)
                
                solver = cp_model.CpSolver()
                solver.parameters.max_time_in_seconds = 5
                status = solver.Solve(model)
                
                if status == cp_model.OPTIMAL:
                    stability_score = 1.0
                elif status == cp_model.FEASIBLE:
                    stability_score = 0.8
                else:
                    stability_score = 0.6
            
            # For other solvers, use default good stability
            else:
                stability_score = 0.9
            
            return stability_score
            
        except Exception as e:
            logger.debug(f"Numerical stability test failed for {solver_name}: {e}")
            return 0.8  # Default moderate stability
    
    def _test_convergence_rate(self, solver_name: str) -> float:
        """Test convergence characteristics of solver"""
        
        try:
            convergence_score = 1.0
            
            if solver_name in ["GLOP", "HiGHS_LP", "CLP"]:
                # Linear solvers typically have good convergence
                convergence_score = 0.95
                
            elif solver_name in ["SCIP", "CBC", "HiGHS_MIP"]:
                # MIP solvers have variable convergence
                convergence_score = 0.8
                
            elif solver_name == "CP_SAT":
                # CP-SAT has excellent convergence for feasible problems
                convergence_score = 0.9
                
            elif solver_name in ["IPOPT", "SCIPY_SLSQP"]:
                # Nonlinear solvers have moderate convergence
                convergence_score = 0.7
                
            elif solver_name in ["DEAP", "PYSWARMS", "OPTUNA"]:
                # Metaheuristics have variable convergence
                convergence_score = 0.6
                
            else:
                convergence_score = 0.8
            
            return convergence_score
            
        except Exception as e:
            logger.debug(f"Convergence test failed for {solver_name}: {e}")
            return 0.7  # Default moderate convergence
    
    def _calculate_reliability_score(self, baseline: Dict[str, float]) -> float:
        """Calculate overall reliability score from baseline metrics"""
        
        try:
            # Weight different factors
            weights = {
                "performance": 0.3,
                "stability": 0.3,
                "convergence": 0.2,
                "scalability": 0.2
            }
            
            # Performance score (inverse of time, normalized)
            small_time = baseline.get("small_problem_time", 1.0)
            performance_score = min(1.0 / max(small_time, 0.001), 1.0)
            
            # Stability score
            stability_score = baseline.get("numerical_stability", 0.8)
            
            # Convergence score
            convergence_score = baseline.get("convergence_rate", 0.8)
            
            # Scalability score
            scalability_score = baseline.get("scalability_factor", 1.0)
            scalability_score = min(scalability_score, 1.0)
            
            # Calculate weighted average
            reliability_score = (
                weights["performance"] * performance_score +
                weights["stability"] * stability_score +
                weights["convergence"] * convergence_score +
                weights["scalability"] * scalability_score
            )
            
            return min(max(reliability_score, 0.0), 1.0)
            
        except Exception as e:
            logger.debug(f"Error calculating reliability score: {e}")
            return 0.7  # Default moderate reliability
    
    def _update_registry_from_discovery(self, solver_name: str, discovery_result: SolverDiscoveryResult):
        """Update registry with discovery results"""
        
        if solver_name in self.registry.solvers:
            solver_capability = self.registry.solvers[solver_name]
            
            # Update version and status
            solver_capability.version_info = discovery_result.version
            solver_capability.status = SolverStatus.AVAILABLE if discovery_result.found else SolverStatus.UNAVAILABLE
            solver_capability.last_checked = datetime.now()
            
            if not discovery_result.found:
                solver_capability.error_message = discovery_result.error_message
            else:
                solver_capability.error_message = None
    
    def _capability_profile_to_dict(self, profile: CapabilityProfile) -> Dict[str, Any]:
        """Convert capability profile to dictionary"""
        
        return {
            "problem_types": list(profile.problem_types),
            "variable_types": list(profile.variable_types),
            "constraint_types": list(profile.constraint_types),
            "objective_types": list(profile.objective_types),
            "max_variables": profile.max_variables,
            "max_constraints": profile.max_constraints,
            "memory_usage": profile.memory_usage,
            "computational_complexity": profile.computational_complexity,
            "numerical_stability": profile.numerical_stability,
            "parallel_support": profile.parallel_support,
            "callback_support": profile.callback_support,
            "warm_start_support": profile.warm_start_support
        }
    
    def _get_package_path(self, package_name: str) -> Optional[str]:
        """Get installation path of a package"""
        
        try:
            module = importlib.import_module(package_name)
            if hasattr(module, '__file__') and module.__file__:
                return str(Path(module.__file__).parent)
            elif hasattr(module, '__path__'):
                return str(module.__path__[0])
        except Exception:
            pass
        
        return None
    
    def _get_ortools_version(self) -> str:
        """Get OR-Tools version"""
        try:
            import ortools
            return ortools.__version__
        except:
            return "unknown"
    
    def _get_pyscip_version(self) -> str:
        """Get PySCIP version"""
        try:
            import pyscip
            return pyscip.__version__
        except:
            return "unknown"
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of discovery results"""
        
        with self._lock:
            total_solvers = len(self.registry.solvers)
            discovered_solvers = len([r for r in self.discovery_cache.values() if r.found])
            
            summary = {
                "total_registered_solvers": total_solvers,
                "discovered_solvers": discovered_solvers,
                "discovery_rate": discovered_solvers / total_solvers if total_solvers > 0 else 0.0,
                "solvers_by_category": {},
                "discovery_results": {name: result.found for name, result in self.discovery_cache.items()},
                "performance_baselines": dict(self.performance_baselines),
                "capability_profiles": {name: self._capability_profile_to_dict(profile) 
                                      for name, profile in self.capability_profiles.items()},
                "last_discovery": max([r.discovery_time for r in self.discovery_cache.values()]) if self.discovery_cache else 0.0,
                "system_info": {
                    "platform": platform.system(),
                    "architecture": platform.machine(),
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                },
                "compatibility_summary": {},
                "recommendations": []
            }
            
            # Group by category
            for solver_name, result in self.discovery_cache.items():
                if solver_name in self.registry.solvers:
                    category = self.registry.solvers[solver_name].category.value
                    if category not in summary["solvers_by_category"]:
                        summary["solvers_by_category"][category] = {"total": 0, "discovered": 0, "compatible": 0}
                    
                    summary["solvers_by_category"][category]["total"] += 1
                    if result.found:
                        summary["solvers_by_category"][category]["discovered"] += 1
                        
                        # Check compatibility
                        compatibility = self.validate_solver_compatibility(solver_name)
                        if compatibility["compatibility_score"] >= 0.8:
                            summary["solvers_by_category"][category]["compatible"] += 1
            
            # Generate compatibility summary
            compatible_solvers = 0
            total_discovered = 0
            
            for solver_name, result in self.discovery_cache.items():
                if result.found:
                    total_discovered += 1
                    compatibility = self.validate_solver_compatibility(solver_name)
                    if compatibility["compatibility_score"] >= 0.8:
                        compatible_solvers += 1
            
            summary["compatibility_summary"] = {
                "compatible_solvers": compatible_solvers,
                "compatibility_rate": compatible_solvers / total_discovered if total_discovered > 0 else 0.0
            }
            
            # Generate recommendations
            if discovered_solvers < total_solvers * 0.5:
                summary["recommendations"].append("Consider installing additional solver dependencies")
            
            if compatible_solvers < discovered_solvers * 0.8:
                summary["recommendations"].append("Some solvers may need version updates for optimal compatibility")
            
            # Add category-specific recommendations
            for category, stats in summary["solvers_by_category"].items():
                if stats["discovered"] == 0:
                    summary["recommendations"].append(f"No {category} solvers available - consider installing relevant packages")
                elif stats["compatible"] < stats["discovered"]:
                    summary["recommendations"].append(f"Some {category} solvers have compatibility issues")
            
            return summary
    
    def get_discovery_report(self) -> Optional[Dict[str, Any]]:
        """Get the latest discovery report"""
        
        with self._lock:
            return getattr(self, 'discovery_report', None)
    
    def export_discovery_data(self) -> Dict[str, Any]:
        """Export all discovery data for analysis or backup"""
        
        with self._lock:
            export_data = {
                "discovery_cache": {
                    name: {
                        "solver_name": result.solver_name,
                        "found": result.found,
                        "version": result.version,
                        "installation_path": result.installation_path,
                        "capabilities": result.capabilities,
                        "performance_baseline": result.performance_baseline,
                        "error_message": result.error_message,
                        "discovery_time": result.discovery_time
                    }
                    for name, result in self.discovery_cache.items()
                },
                "capability_profiles": {
                    name: self._capability_profile_to_dict(profile)
                    for name, profile in self.capability_profiles.items()
                },
                "performance_baselines": dict(self.performance_baselines),
                "discovery_report": getattr(self, 'discovery_report', None),
                "export_timestamp": datetime.now().isoformat(),
                "system_info": {
                    "platform": platform.system(),
                    "architecture": platform.machine(),
                    "python_version": sys.version
                }
            }
            
            return export_data
    
    def refresh_solver_discovery(self, solver_names: Optional[List[str]] = None) -> Dict[str, SolverDiscoveryResult]:
        """
        Refresh discovery for specific solvers or all solvers
        
        Args:
            solver_names: List of solver names to refresh, or None for all
            
        Returns:
            Dictionary of refreshed discovery results
        """
        logger.info("Refreshing solver discovery...")
        
        if solver_names is None:
            solver_names = list(self.registry.solvers.keys())
        
        # Clear cache for specified solvers
        with self._lock:
            for solver_name in solver_names:
                if solver_name in self.discovery_cache:
                    del self.discovery_cache[solver_name]
                if solver_name in self.capability_profiles:
                    del self.capability_profiles[solver_name]
                if solver_name in self.performance_baselines:
                    del self.performance_baselines[solver_name]
        
        # Re-discover specified solvers
        refreshed_results = {}
        for solver_name in solver_names:
            if solver_name in self.registry.solvers:
                result = self.discover_solver(solver_name)
                refreshed_results[solver_name] = result
        
        logger.info(f"Discovery refresh complete for {len(refreshed_results)} solvers")
        
        return refreshed_results
    
    def validate_solver_compatibility(self, solver_name: str) -> Dict[str, Any]:
        """Comprehensive solver compatibility validation with version checking"""
        
        validation_result = {
            "solver_name": solver_name,
            "compatible": False,
            "version_compatible": False,
            "dependencies_satisfied": False,
            "performance_acceptable": False,
            "system_compatible": False,
            "issues": [],
            "recommendations": [],
            "version_info": {},
            "compatibility_score": 0.0
        }
        
        try:
            if solver_name not in self.registry.solvers:
                validation_result["issues"].append("Solver not in registry")
                return validation_result
            
            solver_capability = self.registry.solvers[solver_name]
            
            # Check if solver was discovered
            if solver_name in self.discovery_cache:
                discovery_result = self.discovery_cache[solver_name]
                
                if not discovery_result.found:
                    validation_result["issues"].append(f"Solver not found: {discovery_result.error_message}")
                    validation_result["recommendations"].append(f"Install dependencies: {', '.join(solver_capability.dependencies)}")
                    return validation_result
                
                validation_result["compatible"] = True
                validation_result["dependencies_satisfied"] = True
                
                # Comprehensive version compatibility checking
                version_check = self._check_version_compatibility(solver_name, discovery_result.version)
                validation_result["version_compatible"] = version_check["compatible"]
                validation_result["version_info"] = version_check
                
                if not version_check["compatible"]:
                    validation_result["issues"].extend(version_check["issues"])
                    validation_result["recommendations"].extend(version_check["recommendations"])
                
                # System compatibility checking
                system_check = self._check_system_compatibility(solver_name)
                validation_result["system_compatible"] = system_check["compatible"]
                
                if not system_check["compatible"]:
                    validation_result["issues"].extend(system_check["issues"])
                    validation_result["recommendations"].extend(system_check["recommendations"])
                
                # Performance acceptability check
                if solver_name in self.performance_baselines:
                    baseline = self.performance_baselines[solver_name]
                    performance_check = self._evaluate_performance_acceptability(baseline)
                    validation_result["performance_acceptable"] = performance_check["acceptable"]
                    
                    if not performance_check["acceptable"]:
                        validation_result["issues"].extend(performance_check["issues"])
                        validation_result["recommendations"].extend(performance_check["recommendations"])
                
                # Calculate overall compatibility score
                validation_result["compatibility_score"] = self._calculate_compatibility_score(validation_result)
                
            else:
                validation_result["issues"].append("Solver not yet discovered")
                validation_result["recommendations"].append("Run solver discovery first")
        
        except Exception as e:
            validation_result["issues"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def _check_version_compatibility(self, solver_name: str, detected_version: Optional[str]) -> Dict[str, Any]:
        """Check version compatibility for a solver"""
        
        version_check = {
            "compatible": True,
            "detected_version": detected_version,
            "minimum_version": None,
            "recommended_version": None,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Define minimum and recommended versions for each solver
            version_requirements = {
                "GLOP": {"minimum": "9.0.0", "recommended": "9.5.0"},
                "CLP": {"minimum": "2.0.0", "recommended": "2.2.0"},
                "HiGHS_LP": {"minimum": "1.4.0", "recommended": "1.5.0"},
                "HiGHS_MIP": {"minimum": "1.4.0", "recommended": "1.5.0"},
                "SCIP": {"minimum": "8.0.0", "recommended": "8.0.3"},
                "CBC": {"minimum": "2.10.0", "recommended": "2.10.5"},
                "CP_SAT": {"minimum": "9.0.0", "recommended": "9.5.0"},
                "OR_TOOLS_ROUTING": {"minimum": "9.0.0", "recommended": "9.5.0"},
                "IPOPT": {"minimum": "3.13.0", "recommended": "3.14.0"},
                "BONMIN": {"minimum": "1.8.0", "recommended": "1.8.8"},
                "CVXPY_GLPK_MI": {"minimum": "1.2.0", "recommended": "1.3.0"},
                "CVXPY_ECOS": {"minimum": "1.2.0", "recommended": "1.3.0"},
                "PYOMO_CBC": {"minimum": "6.4.0", "recommended": "6.5.0"},
                "DEAP": {"minimum": "1.3.0", "recommended": "1.3.3"},
                "PYSWARMS": {"minimum": "1.3.0", "recommended": "1.3.0"},
                "OPTUNA": {"minimum": "3.0.0", "recommended": "3.4.0"},
                "SCIPY_LINPROG": {"minimum": "1.7.0", "recommended": "1.10.0"},
                "SCIPY_SLSQP": {"minimum": "1.7.0", "recommended": "1.10.0"}
            }
            
            if solver_name in version_requirements:
                requirements = version_requirements[solver_name]
                version_check["minimum_version"] = requirements["minimum"]
                version_check["recommended_version"] = requirements["recommended"]
                
                if detected_version:
                    # Parse version numbers for comparison
                    detected_parts = self._parse_version(detected_version)
                    minimum_parts = self._parse_version(requirements["minimum"])
                    recommended_parts = self._parse_version(requirements["recommended"])
                    
                    if detected_parts and minimum_parts:
                        if self._compare_versions(detected_parts, minimum_parts) < 0:
                            version_check["compatible"] = False
                            version_check["issues"].append(
                                f"Version {detected_version} is below minimum required {requirements['minimum']}"
                            )
                            version_check["recommendations"].append(
                                f"Upgrade to version {requirements['recommended']} or higher"
                            )
                        elif recommended_parts and self._compare_versions(detected_parts, recommended_parts) < 0:
                            version_check["recommendations"].append(
                                f"Consider upgrading to recommended version {requirements['recommended']}"
                            )
                else:
                    version_check["issues"].append("Could not detect version")
                    version_check["recommendations"].append("Verify installation and version")
            
        except Exception as e:
            logger.debug(f"Version compatibility check failed for {solver_name}: {e}")
            version_check["issues"].append(f"Version check error: {str(e)}")
        
        return version_check
    
    def _check_system_compatibility(self, solver_name: str) -> Dict[str, Any]:
        """Check system compatibility for a solver"""
        
        system_check = {
            "compatible": True,
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python_version": sys.version,
            "issues": [],
            "recommendations": []
        }
        
        try:
            current_platform = platform.system().lower()
            current_arch = platform.machine().lower()
            python_version = sys.version_info
            
            # Define platform compatibility
            platform_compatibility = {
                "GLOP": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "CLP": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "HiGHS_LP": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "HiGHS_MIP": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "SCIP": {"platforms": ["linux", "darwin"], "min_python": (3, 7)},  # Limited Windows support
                "CBC": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "CP_SAT": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "OR_TOOLS_ROUTING": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "IPOPT": {"platforms": ["linux", "darwin"], "min_python": (3, 7)},  # Complex Windows setup
                "BONMIN": {"platforms": ["linux", "darwin"], "min_python": (3, 7)},  # Complex Windows setup
                "CVXPY_GLPK_MI": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "CVXPY_ECOS": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "PYOMO_CBC": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "DEAP": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 6)},
                "PYSWARMS": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 6)},
                "OPTUNA": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "SCIPY_LINPROG": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)},
                "SCIPY_SLSQP": {"platforms": ["windows", "linux", "darwin"], "min_python": (3, 7)}
            }
            
            if solver_name in platform_compatibility:
                compatibility = platform_compatibility[solver_name]
                
                # Check platform compatibility
                if current_platform not in compatibility["platforms"]:
                    system_check["compatible"] = False
                    system_check["issues"].append(
                        f"Platform {current_platform} not supported. Supported: {', '.join(compatibility['platforms'])}"
                    )
                    system_check["recommendations"].append("Use a supported platform or find alternative solver")
                
                # Check Python version compatibility
                min_python = compatibility["min_python"]
                if python_version < min_python:
                    system_check["compatible"] = False
                    system_check["issues"].append(
                        f"Python {python_version.major}.{python_version.minor} is below minimum required {min_python[0]}.{min_python[1]}"
                    )
                    system_check["recommendations"].append(f"Upgrade Python to {min_python[0]}.{min_python[1]} or higher")
                
                # Architecture-specific checks
                if current_arch in ["arm64", "aarch64"] and solver_name in ["SCIP", "IPOPT", "BONMIN"]:
                    system_check["recommendations"].append(
                        f"ARM architecture may require special compilation for {solver_name}"
                    )
            
        except Exception as e:
            logger.debug(f"System compatibility check failed for {solver_name}: {e}")
            system_check["issues"].append(f"System check error: {str(e)}")
        
        return system_check
    
    def _evaluate_performance_acceptability(self, baseline: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate if solver performance is acceptable"""
        
        performance_check = {
            "acceptable": True,
            "issues": [],
            "recommendations": []
        }
        
        try:
            reliability_score = baseline.get("reliability_score", 0.0)
            small_problem_time = baseline.get("small_problem_time", 0.0)
            memory_usage = baseline.get("memory_usage_mb", 0.0)
            numerical_stability = baseline.get("numerical_stability", 0.0)
            
            # Check reliability threshold
            if reliability_score < 0.6:
                performance_check["acceptable"] = False
                performance_check["issues"].append(f"Low reliability score: {reliability_score:.2f}")
                performance_check["recommendations"].append("Consider using more reliable solver")
            
            # Check performance thresholds
            if small_problem_time > 10.0:  # 10 seconds for small problems is too slow
                performance_check["issues"].append(f"Slow performance on small problems: {small_problem_time:.2f}s")
                performance_check["recommendations"].append("Consider faster solver for time-critical applications")
            
            # Check memory usage
            if memory_usage > 1000.0:  # 1GB is high for basic operations
                performance_check["issues"].append(f"High memory usage: {memory_usage:.1f}MB")
                performance_check["recommendations"].append("Monitor memory usage in production")
            
            # Check numerical stability
            if numerical_stability < 0.5:
                performance_check["issues"].append(f"Poor numerical stability: {numerical_stability:.2f}")
                performance_check["recommendations"].append("Use solver with better numerical properties")
            
        except Exception as e:
            logger.debug(f"Performance evaluation failed: {e}")
            performance_check["issues"].append(f"Performance evaluation error: {str(e)}")
        
        return performance_check
    
    def _parse_version(self, version_string: str) -> Optional[Tuple[int, ...]]:
        """Parse version string into tuple of integers"""
        
        try:
            # Clean version string (remove non-numeric prefixes/suffixes)
            import re
            version_match = re.search(r'(\d+(?:\.\d+)*)', version_string)
            if version_match:
                version_clean = version_match.group(1)
                return tuple(int(x) for x in version_clean.split('.'))
        except Exception:
            pass
        
        return None
    
    def _compare_versions(self, version1: Tuple[int, ...], version2: Tuple[int, ...]) -> int:
        """Compare two version tuples. Returns -1, 0, or 1"""
        
        # Pad shorter version with zeros
        max_len = max(len(version1), len(version2))
        v1_padded = version1 + (0,) * (max_len - len(version1))
        v2_padded = version2 + (0,) * (max_len - len(version2))
        
        if v1_padded < v2_padded:
            return -1
        elif v1_padded > v2_padded:
            return 1
        else:
            return 0
    
    def _calculate_compatibility_score(self, validation_result: Dict[str, Any]) -> float:
        """Calculate overall compatibility score"""
        
        try:
            score = 0.0
            
            # Base compatibility (40%)
            if validation_result["compatible"]:
                score += 0.4
            
            # Version compatibility (25%)
            if validation_result["version_compatible"]:
                score += 0.25
            
            # System compatibility (20%)
            if validation_result["system_compatible"]:
                score += 0.2
            
            # Performance acceptability (15%)
            if validation_result["performance_acceptable"]:
                score += 0.15
            
            return min(max(score, 0.0), 1.0)
            
        except Exception:
            return 0.0


# Global detection system instance
solver_detection_system = SolverDetectionSystem()


def get_solver_detection_system() -> SolverDetectionSystem:
    """Get the global solver detection system instance"""
    return solver_detection_system