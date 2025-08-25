"""
Solver Tool with Competitive Swarm Intelligence and Open Source Solver Integration
Supports 15+ open source solvers across 5 categories with competitive agent selection
"""

import logging
import asyncio
import json
import uuid
import time
import statistics
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import concurrent.futures
import threading

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# AgentCore SDK imports for production deployment
try:
    from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
    AGENTCORE_AVAILABLE = True
except ImportError:
    AGENTCORE_AVAILABLE = False
    print("AgentCore SDK not available - using fallback implementation")

try:
    from strands import Agent
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

from ..utils.base import BaseTool, ToolExecutionError, ToolInitializationError

# Import AdaptiveManufacturingSwarms
try:
    from adaptive_manufacturing_swarms import AdaptiveManufacturingSwarms
    ADAPTIVE_SWARMS_AVAILABLE = True
except ImportError:
    ADAPTIVE_SWARMS_AVAILABLE = False
    class AdaptiveManufacturingSwarms:
        @classmethod
        def create_competitive_model_swarm(cls):
            """Create a basic competitive model swarm"""
            return AdaptiveSwarmTool()
        
        @classmethod
        def create_manufacturing_swarm(cls, swarm_type="competitive"):
            """Create a manufacturing swarm"""
            return AdaptiveSwarmTool()

# Define AdaptiveSwarmTool locally if not available
try:
    from tools.swarm.adaptive_swarm import AdaptiveSwarmTool, SwarmPerformanceMetrics
except ImportError:
    class AdaptiveSwarmTool:
        def __init__(self):
            self.initialized = False
            self.performance_metrics = SwarmPerformanceMetrics()
        
        async def initialize(self):
            """Initialize the swarm tool"""
            self.initialized = True
            return True
        
        async def execute(self, **kwargs):
            """Execute swarm operations - basic implementation"""
            if not self.initialized:
                await self.initialize()
            
            # Return basic swarm result
            return {
                "success": True,
                "swarm_type": kwargs.get("swarm_type", "competitive"),
                "agents": [],
                "performance": {},
                "message": "Basic swarm implementation - production swarm not available"
            }
    
    class SwarmPerformanceMetrics:
        def __init__(self):
            self.metrics = {}
        
        def record_competitive_performance(self, agent_name, solver_name, execution_time, objective_value, solve_status):
            """Record performance metrics for competitive solving"""
            if agent_name not in self.metrics:
                self.metrics[agent_name] = []
            
            self.metrics[agent_name].append({
                "solver_name": solver_name,
                "execution_time": execution_time,
                "objective_value": objective_value,
                "solve_status": solve_status,
                "timestamp": time.time()
            })
        
        def get_performance_summary(self):
            """Get performance summary"""
            return self.metrics

logger = logging.getLogger(__name__)


@dataclass
class SolverResult:
    """Standardized solver result format"""
    solve_status: str
    objective_value: Optional[float]
    solution: Dict[str, float]
    solver_info: Dict[str, Any]
    solution_quality: Dict[str, Any]
    metadata: Dict[str, Any]
    execution_time: float
    solver_name: str
    
    def __post_init__(self):
        if self.solution_quality is None:
            self.solution_quality = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ModelSpecification:
    """Universal model specification for solver input"""
    problem_type: str
    variables: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    objective: Dict[str, Any]
    solver_hints: Dict[str, Any]
    metadata: Dict[str, Any]
    model_id: str = None
    
    def __post_init__(self):
        if self.model_id is None:
            self.model_id = str(uuid.uuid4())
        if self.solver_hints is None:
            self.solver_hints = {}
        if self.metadata is None:
            self.metadata = {}


class SolverCategory(Enum):
    """Categories of optimization solvers"""
    LINEAR_PROGRAMMING = "linear_programming"
    MIXED_INTEGER = "mixed_integer_programming"
    CONSTRAINT_PROGRAMMING = "constraint_programming"
    NONLINEAR_PROGRAMMING = "nonlinear_programming"
    METAHEURISTIC = "metaheuristic"


class SolverStatus(Enum):
    """Solver execution status"""
    OPTIMAL = "optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNBOUNDED = "unbounded"
    TIME_LIMIT = "time_limit"
    ERROR = "error"
    NOT_SOLVED = "not_solved"


class SolverCapability:
    """Solver capability definition"""
    def __init__(self, name: str, category: SolverCategory, 
                 problem_types: List[str], performance_profile: Dict[str, Any]):
        self.name = name
        self.category = category
        self.problem_types = problem_types
        self.performance_profile = performance_profile
        self.available = False
        self.version = None


class SolverRegistry:
    """Registry for managing available solvers and their capabilities"""
    
    def __init__(self):
        self.solvers = {}
        self.performance_history = defaultdict(list)
        self.availability_cache = {}
        self.last_availability_check = {}
        self._initialize_solver_definitions()
    
    def _initialize_solver_definitions(self):
        """Initialize solver capability definitions"""
        # Linear Programming Solvers
        self.solvers["GLOP"] = SolverCapability(
            name="GLOP",
            category=SolverCategory.LINEAR_PROGRAMMING,
            problem_types=["linear_programming"],
            performance_profile={
                "small_problems": 5,  # 1-5 rating
                "medium_problems": 4,
                "large_problems": 3,
                "memory_efficiency": 5,
                "speed": 4,
                "robustness": 4
            }
        )
        
        self.solvers["CLP"] = SolverCapability(
            name="CLP",
            category=SolverCategory.LINEAR_PROGRAMMING,
            problem_types=["linear_programming"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 5,
                "large_problems": 5,
                "memory_efficiency": 4,
                "speed": 4,
                "robustness": 5
            }
        )
        
        self.solvers["HiGHS"] = SolverCapability(
            name="HiGHS",
            category=SolverCategory.LINEAR_PROGRAMMING,
            problem_types=["linear_programming", "mixed_integer_programming"],
            performance_profile={
                "small_problems": 5,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 4,
                "speed": 5,
                "robustness": 4
            }
        )
        
        # Mixed Integer Programming Solvers
        self.solvers["SCIP"] = SolverCapability(
            name="SCIP",
            category=SolverCategory.MIXED_INTEGER,
            problem_types=["mixed_integer_programming", "constraint_programming"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 3,
                "speed": 4,
                "robustness": 5
            }
        )
        
        self.solvers["CBC"] = SolverCapability(
            name="CBC",
            category=SolverCategory.MIXED_INTEGER,
            problem_types=["mixed_integer_programming"],
            performance_profile={
                "small_problems": 3,
                "medium_problems": 4,
                "large_problems": 3,
                "memory_efficiency": 4,
                "speed": 3,
                "robustness": 4
            }
        )
        
        # Constraint Programming Solvers
        self.solvers["CP-SAT"] = SolverCapability(
            name="CP-SAT",
            category=SolverCategory.CONSTRAINT_PROGRAMMING,
            problem_types=["constraint_programming", "scheduling"],
            performance_profile={
                "small_problems": 5,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 4,
                "speed": 5,
                "robustness": 5
            }
        )
        
        # Nonlinear Programming Solvers
        self.solvers["Ipopt"] = SolverCapability(
            name="Ipopt",
            category=SolverCategory.NONLINEAR_PROGRAMMING,
            problem_types=["nonlinear_programming"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 4,
                "large_problems": 3,
                "memory_efficiency": 3,
                "speed": 3,
                "robustness": 4
            }
        )
        
        self.solvers["SLSQP"] = SolverCapability(
            name="SLSQP",
            category=SolverCategory.NONLINEAR_PROGRAMMING,
            problem_types=["nonlinear_programming"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 3,
                "large_problems": 2,
                "memory_efficiency": 5,
                "speed": 4,
                "robustness": 3
            }
        )
        
        # Metaheuristic Solvers
        self.solvers["DEAP"] = SolverCapability(
            name="DEAP",
            category=SolverCategory.METAHEURISTIC,
            problem_types=["metaheuristic", "multi_objective"],
            performance_profile={
                "small_problems": 3,
                "medium_problems": 4,
                "large_problems": 5,
                "memory_efficiency": 3,
                "speed": 2,
                "robustness": 4
            }
        )
        
        self.solvers["PySwarms"] = SolverCapability(
            name="PySwarms",
            category=SolverCategory.METAHEURISTIC,
            problem_types=["metaheuristic", "continuous_optimization"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 4,
                "large_problems": 5,
                "memory_efficiency": 4,
                "speed": 3,
                "robustness": 3
            }
        )
        
        self.solvers["Optuna"] = SolverCapability(
            name="Optuna",
            category=SolverCategory.METAHEURISTIC,
            problem_types=["metaheuristic", "hyperparameter_optimization"],
            performance_profile={
                "small_problems": 4,
                "medium_problems": 5,
                "large_problems": 4,
                "memory_efficiency": 4,
                "speed": 4,
                "robustness": 4
            }
        )
    
    def check_solver_availability(self, solver_name: str) -> bool:
        """Check if a solver is available and functional"""
        # Check cache first
        if solver_name in self.availability_cache:
            last_check = self.last_availability_check.get(solver_name)
            if last_check and (datetime.utcnow() - last_check).seconds < 300:  # 5 min cache
                return self.availability_cache[solver_name]
        
        try:
            available = False
            
            if solver_name == "GLOP":
                try:
                    from ortools.linear_solver import pywraplp
                    test_solver = pywraplp.Solver.CreateSolver('GLOP')
                    available = test_solver is not None
                except ImportError:
                    available = False
            
            elif solver_name == "CLP":
                try:
                    import pulp
                    # Test CLP availability through PuLP
                    available = pulp.COIN_CMD().available()
                except ImportError:
                    available = False
            
            elif solver_name == "HiGHS":
                try:
                    import highspy
                    test_highs = highspy.Highs()
                    available = True
                except ImportError:
                    available = False
            
            elif solver_name == "SCIP":
                try:
                    from pyscipopt import Model
                    test_model = Model("test")
                    available = True
                except ImportError:
                    available = False
            
            elif solver_name == "CBC":
                try:
                    import pulp
                    # Check for CBC solver availability
                    try:
                        # Use PULP_CBC_CMD which is available
                        cbc_solver = pulp.PULP_CBC_CMD()
                        available = cbc_solver.available()
                    except Exception as e:
                        self.logger.debug(f"CBC solver check failed: {e}")
                        available = False
                except ImportError:
                    available = False
            
            elif solver_name == "CP-SAT":
                try:
                    from ortools.sat.python import cp_model
                    test_model = cp_model.CpModel()
                    available = True
                except ImportError:
                    available = False
            
            elif solver_name == "Ipopt":
                try:
                    import cyipopt
                    available = True
                except ImportError:
                    available = False
            
            elif solver_name == "SLSQP":
                try:
                    from scipy.optimize import minimize
                    available = True
                except ImportError:
                    available = False
            
            elif solver_name == "DEAP":
                try:
                    from deap import base, creator, tools, algorithms
                    available = True
                except ImportError:
                    available = False
            
            elif solver_name == "PySwarms":
                try:
                    import pyswarms as ps
                    available = True
                except ImportError:
                    available = False
            
            elif solver_name == "Optuna":
                try:
                    import optuna
                    available = True
                except ImportError:
                    available = False
            
            # Update cache
            self.availability_cache[solver_name] = available
            self.last_availability_check[solver_name] = datetime.utcnow()
            
            if solver_name in self.solvers:
                self.solvers[solver_name].available = available
            
            return available
            
        except Exception as e:
            logger.error(f"Error checking availability for solver {solver_name}: {e}")
            self.availability_cache[solver_name] = False
            return False
    
    def get_compatible_solvers(self, problem_type: str, problem_size: str = "medium") -> List[str]:
        """Get list of compatible solvers for given problem type and size"""
        compatible = []
        
        for solver_name, solver_capability in self.solvers.items():
            if (problem_type in solver_capability.problem_types and 
                self.check_solver_availability(solver_name)):
                
                # Consider performance profile for problem size
                size_score = solver_capability.performance_profile.get(f"{problem_size}_problems", 3)
                if size_score >= 3:  # Minimum acceptable performance
                    compatible.append(solver_name)
        
        # Sort by performance for the given problem size
        compatible.sort(key=lambda x: self.solvers[x].performance_profile.get(f"{problem_size}_problems", 0), 
                       reverse=True)
        
        return compatible
    
    def record_solver_performance(self, solver_name: str, execution_time: float, 
                                 solution_quality: float, problem_characteristics: Dict[str, Any]):
        """Record solver performance for future optimization"""
        performance_record = {
            "solver_name": solver_name,
            "execution_time": execution_time,
            "solution_quality": solution_quality,
            "problem_characteristics": problem_characteristics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.performance_history[solver_name].append(performance_record)
        
        # Keep only recent history (last 100 records per solver)
        if len(self.performance_history[solver_name]) > 100:
            self.performance_history[solver_name] = self.performance_history[solver_name][-100:]


class ModelConverter:
    """Converts universal model specification to solver-specific formats"""
    
    @staticmethod
    def parse_bounds(bounds_str: str) -> Tuple[float, float]:
        """Parse bounds string like '[0, inf]' to tuple"""
        bounds_str = bounds_str.strip('[]')
        parts = bounds_str.split(',')
        
        lower = float(parts[0].strip()) if parts[0].strip() != '-inf' else float('-inf')
        upper = float(parts[1].strip()) if parts[1].strip() != 'inf' else float('inf')
        
        return lower, upper
    
    @staticmethod
    def to_ortools_lp(model_spec: ModelSpecification, solver_name: str = "GLOP"):
        """Convert to OR-Tools linear solver format"""
        try:
            from ortools.linear_solver import pywraplp
            
            solver = pywraplp.Solver.CreateSolver(solver_name)
            if not solver:
                raise ToolExecutionError(f"Could not create {solver_name} solver", "solver_tool")
            
            # Convert variables
            variables = {}
            for var_spec in model_spec.variables:
                bounds = ModelConverter.parse_bounds(var_spec['bounds'])
                lb = bounds[0] if bounds[0] != float('-inf') else -solver.infinity()
                ub = bounds[1] if bounds[1] != float('inf') else solver.infinity()
                
                if var_spec['type'] == 'continuous':
                    variables[var_spec['name']] = solver.NumVar(lb, ub, var_spec['name'])
                elif var_spec['type'] == 'integer':
                    variables[var_spec['name']] = solver.IntVar(int(lb), int(ub), var_spec['name'])
                elif var_spec['type'] == 'binary':
                    variables[var_spec['name']] = solver.BoolVar(var_spec['name'])
            
            # Convert constraints
            for constraint_spec in model_spec.constraints:
                if constraint_spec['type'] == 'linear':
                    # Parse constraint expression and create constraint
                    coefficients = constraint_spec.get('coefficients', {})
                    rhs = constraint_spec.get('rhs', 0)
                    sense = constraint_spec.get('sense', '<=')
                    
                    if sense == '<=':
                        constraint = solver.Constraint(-solver.infinity(), rhs)
                    elif sense == '>=':
                        constraint = solver.Constraint(rhs, solver.infinity())
                    elif sense == '=':
                        constraint = solver.Constraint(rhs, rhs)
                    
                    for var_name, coeff in coefficients.items():
                        if var_name in variables:
                            constraint.SetCoefficient(variables[var_name], coeff)
            
            # Convert objective
            objective = solver.Objective()
            obj_coefficients = model_spec.objective.get('coefficients', {})
            
            for var_name, coeff in obj_coefficients.items():
                if var_name in variables:
                    objective.SetCoefficient(variables[var_name], coeff)
            
            if model_spec.objective['type'] == 'maximize':
                objective.SetMaximization()
            else:
                objective.SetMinimization()
            
            return solver, variables
            
        except Exception as e:
            logger.error(f"Error converting model to OR-Tools format: {e}")
            raise ToolExecutionError(f"Model conversion failed: {str(e)}", "solver_tool")
    
    @staticmethod
    def to_scip_mip(model_spec: ModelSpecification):
        """Convert to SCIP MIP format"""
        try:
            from pyscipopt import Model
            
            model = Model("optimization_model")
            
            # Convert variables
            variables = {}
            for var_spec in model_spec.variables:
                bounds = ModelConverter.parse_bounds(var_spec['bounds'])
                
                vtype = 'C' if var_spec['type'] == 'continuous' else 'I' if var_spec['type'] == 'integer' else 'B'
                
                if var_spec['type'] == 'binary':
                    bounds = (0, 1)
                
                lb = bounds[0] if bounds[0] != float('-inf') else None
                ub = bounds[1] if bounds[1] != float('inf') else None
                
                variables[var_spec['name']] = model.addVar(
                    var_spec['name'], vtype=vtype, lb=lb, ub=ub
                )
            
            # Convert constraints
            for constraint_spec in model_spec.constraints:
                if constraint_spec['type'] == 'linear':
                    coefficients = constraint_spec.get('coefficients', {})
                    rhs = constraint_spec.get('rhs', 0)
                    sense = constraint_spec.get('sense', '<=')
                    
                    expr = sum(coeff * variables[var_name] 
                             for var_name, coeff in coefficients.items() 
                             if var_name in variables)
                    
                    if sense == '<=':
                        model.addCons(expr <= rhs)
                    elif sense == '>=':
                        model.addCons(expr >= rhs)
                    elif sense == '=':
                        model.addCons(expr == rhs)
            
            # Convert objective
            obj_coefficients = model_spec.objective.get('coefficients', {})
            obj_expr = sum(coeff * variables[var_name] 
                          for var_name, coeff in obj_coefficients.items() 
                          if var_name in variables)
            
            sense = "maximize" if model_spec.objective['type'] == 'maximize' else "minimize"
            model.setObjective(obj_expr, sense)
            
            return model, variables
            
        except Exception as e:
            logger.error(f"Error converting model to SCIP format: {e}")
            raise ToolExecutionError(f"SCIP model conversion failed: {str(e)}", "solver_tool")
    
    @staticmethod
    def to_cp_sat(model_spec: ModelSpecification):
        """Convert to OR-Tools CP-SAT format"""
        try:
            from ortools.sat.python import cp_model
            
            model = cp_model.CpModel()
            
            # Convert variables (CP-SAT only handles integers and booleans)
            variables = {}
            for var_spec in model_spec.variables:
                bounds = ModelConverter.parse_bounds(var_spec['bounds'])
                
                if var_spec['type'] in ['integer', 'continuous']:
                    # CP-SAT treats continuous as integer
                    variables[var_spec['name']] = model.NewIntVar(
                        int(bounds[0]) if bounds[0] != float('-inf') else -1000000,
                        int(bounds[1]) if bounds[1] != float('inf') else 1000000,
                        var_spec['name']
                    )
                elif var_spec['type'] in ['binary', 'boolean']:
                    variables[var_spec['name']] = model.NewBoolVar(var_spec['name'])
            
            # Convert constraints
            for constraint_spec in model_spec.constraints:
                if constraint_spec['type'] == 'linear':
                    coefficients = constraint_spec.get('coefficients', {})
                    rhs = constraint_spec.get('rhs', 0)
                    sense = constraint_spec.get('sense', '<=')
                    
                    expr = sum(coeff * variables[var_name] 
                             for var_name, coeff in coefficients.items() 
                             if var_name in variables)
                    
                    if sense == '<=':
                        model.Add(expr <= rhs)
                    elif sense == '>=':
                        model.Add(expr >= rhs)
                    elif sense == '=':
                        model.Add(expr == rhs)
            
            # Convert objective
            obj_coefficients = model_spec.objective.get('coefficients', {})
            obj_expr = sum(coeff * variables[var_name] 
                          for var_name, coeff in obj_coefficients.items() 
                          if var_name in variables)
            
            if model_spec.objective['type'] == 'maximize':
                model.Maximize(obj_expr)
            else:
                model.Minimize(obj_expr)
            
            return model, variables
            
        except Exception as e:
            logger.error(f"Error converting model to CP-SAT format: {e}")
            raise ToolExecutionError(f"CP-SAT model conversion failed: {str(e)}", "solver_tool")


class ResultStandardizer:
    """Standardizes solver results to universal format"""
    
    @staticmethod
    def from_ortools(solver, variables, model_spec: ModelSpecification, execution_time: float, solver_name: str) -> SolverResult:
        """Convert OR-Tools result to standard format"""
        try:
            from ortools.linear_solver import pywraplp
            
            status_map = {
                pywraplp.Solver.OPTIMAL: SolverStatus.OPTIMAL.value,
                pywraplp.Solver.FEASIBLE: SolverStatus.FEASIBLE.value,
                pywraplp.Solver.INFEASIBLE: SolverStatus.INFEASIBLE.value,
                pywraplp.Solver.UNBOUNDED: SolverStatus.UNBOUNDED.value,
                pywraplp.Solver.ABNORMAL: SolverStatus.ERROR.value,
                pywraplp.Solver.NOT_SOLVED: SolverStatus.NOT_SOLVED.value
            }
            
            solve_status = solver.Solve()
            
            return SolverResult(
                solve_status=status_map.get(solve_status, SolverStatus.ERROR.value),
                objective_value=solver.Objective().Value() if solve_status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE] else None,
                solution={name: var.solution_value() for name, var in variables.items()} if solve_status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE] else {},
                solver_info={
                    "solver_name": solver_name,
                    "solve_time": solver.wall_time() / 1000.0,
                    "iterations": solver.iterations(),
                    "termination_reason": status_map.get(solve_status, "unknown")
                },
                solution_quality={
                    "optimality_gap": 0.0 if solve_status == pywraplp.Solver.OPTIMAL else None,
                    "feasibility_check": "passed" if solve_status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE] else "failed"
                },
                metadata={
                    "model_id": model_spec.model_id,
                    "solve_timestamp": datetime.utcnow().isoformat()
                },
                execution_time=execution_time,
                solver_name=solver_name
            )
            
        except Exception as e:
            logger.error(f"Error standardizing OR-Tools result: {e}")
            return SolverResult(
                solve_status=SolverStatus.ERROR.value,
                objective_value=None,
                solution={},
                solver_info={"solver_name": solver_name, "error": str(e)},
                solution_quality={},
                metadata={"model_id": model_spec.model_id},
                execution_time=execution_time,
                solver_name=solver_name
            )
    
    @staticmethod
    def from_scip(model, variables, model_spec: ModelSpecification, execution_time: float) -> SolverResult:
        """Convert SCIP result to standard format"""
        try:
            status_map = {
                "optimal": SolverStatus.OPTIMAL.value,
                "feasible": SolverStatus.FEASIBLE.value,
                "infeasible": SolverStatus.INFEASIBLE.value,
                "unbounded": SolverStatus.UNBOUNDED.value,
                "timelimit": SolverStatus.TIME_LIMIT.value
            }
            
            status = model.getStatus()
            
            return SolverResult(
                solve_status=status_map.get(status, SolverStatus.ERROR.value),
                objective_value=model.getObjVal() if status in ["optimal", "feasible"] else None,
                solution={name: model.getVal(var) for name, var in variables.items()} if status in ["optimal", "feasible"] else {},
                solver_info={
                    "solver_name": "SCIP",
                    "solve_time": model.getSolvingTime(),
                    "nodes": model.getNNodes(),
                    "gap": model.getGap() if status == "feasible" else 0.0
                },
                solution_quality={
                    "optimality_gap": model.getGap() if status == "feasible" else 0.0,
                    "feasibility_check": "passed" if status in ["optimal", "feasible"] else "failed"
                },
                metadata={
                    "model_id": model_spec.model_id,
                    "solve_timestamp": datetime.utcnow().isoformat()
                },
                execution_time=execution_time,
                solver_name="SCIP"
            )
            
        except Exception as e:
            logger.error(f"Error standardizing SCIP result: {e}")
            return SolverResult(
                solve_status=SolverStatus.ERROR.value,
                objective_value=None,
                solution={},
                solver_info={"solver_name": "SCIP", "error": str(e)},
                solution_quality={},
                metadata={"model_id": model_spec.model_id},
                execution_time=execution_time,
                solver_name="SCIP"
            )
    
    @staticmethod
    def from_cp_sat(solver, variables, model_spec: ModelSpecification, execution_time: float) -> SolverResult:
        """Convert CP-SAT result to standard format"""
        try:
            from ortools.sat.python import cp_model
            
            status_map = {
                cp_model.OPTIMAL: SolverStatus.OPTIMAL.value,
                cp_model.FEASIBLE: SolverStatus.FEASIBLE.value,
                cp_model.INFEASIBLE: SolverStatus.INFEASIBLE.value,
                cp_model.MODEL_INVALID: SolverStatus.ERROR.value,
                cp_model.UNKNOWN: SolverStatus.NOT_SOLVED.value
            }
            
            status = solver.StatusName()
            
            return SolverResult(
                solve_status=status_map.get(solver.StatusName(), SolverStatus.ERROR.value),
                objective_value=solver.ObjectiveValue() if status in ["OPTIMAL", "FEASIBLE"] else None,
                solution={name: solver.Value(var) for name, var in variables.items()} if status in ["OPTIMAL", "FEASIBLE"] else {},
                solver_info={
                    "solver_name": "CP-SAT",
                    "solve_time": solver.WallTime(),
                    "branches": solver.NumBranches(),
                    "conflicts": solver.NumConflicts()
                },
                solution_quality={
                    "optimality_gap": 0.0 if status == "OPTIMAL" else None,
                    "feasibility_check": "passed" if status in ["OPTIMAL", "FEASIBLE"] else "failed"
                },
                metadata={
                    "model_id": model_spec.model_id,
                    "solve_timestamp": datetime.utcnow().isoformat()
                },
                execution_time=execution_time,
                solver_name="CP-SAT"
            )
            
        except Exception as e:
            logger.error(f"Error standardizing CP-SAT result: {e}")
            return SolverResult(
                solve_status=SolverStatus.ERROR.value,
                objective_value=None,
                solution={},
                solver_info={"solver_name": "CP-SAT", "error": str(e)},
                solution_quality={},
                metadata={"model_id": model_spec.model_id},
                execution_time=execution_time,
                solver_name="CP-SAT"
            )


# Competitive Solver Agents

class BaseSolverAgent:
    """Base class for competitive solver agents"""
    
    def __init__(self, name: str, specialization: str, solvers: List[str]):
        self.name = name
        self.specialization = specialization
        self.solvers = solvers
        self.performance_history = []
        self.success_rate = 0.8  # Initial success rate
        self.avg_execution_time = 0.0
        self.solution_quality_score = 0.8
        self.strands_agent = None
        self.strands_tools = {}
    
    async def initialize(self) -> bool:
        """Initialize the solver agent with Strands tools integration"""
        try:
            # Initialize Strands tools for agent memory and learning
            try:
                from strands_tools import memory, retrieve
                from strands import Agent
                
                self.strands_agent = Agent(tools=[memory, retrieve])
                self.strands_tools = {
                    'memory': self.strands_agent.tool.memory,
                    'retrieve': self.strands_agent.tool.retrieve
                }
                logger.info(f"Strands tools initialized for {self.name}")
                
            except ImportError as e:
                logger.warning(f"Strands tools not available for {self.name}: {e}")
                self.strands_tools = {}
            
            # Check availability of assigned solvers
            available_solvers = []
            for solver_name in self.solvers:
                # This would be checked via SolverRegistry
                available_solvers.append(solver_name)
            
            self.available_solvers = available_solvers
            return len(available_solvers) > 0
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {e}")
            return False
    
    def select_solver(self, model_spec: ModelSpecification) -> Optional[str]:
        """Select best solver for the given model"""
        # Default implementation - override in subclasses
        return self.available_solvers[0] if self.available_solvers else None
    
    async def solve_model(self, model_spec: ModelSpecification, solver_registry: SolverRegistry) -> SolverResult:
        """Solve model using selected solver"""
        solver_name = self.select_solver(model_spec)
        if not solver_name:
            raise ToolExecutionError(f"No available solver for {self.name}", "solver_tool")
        
        start_time = time.time()
        
        try:
            # Convert model to solver-specific format
            if solver_name in ["GLOP", "CLP", "HiGHS"]:
                solver_model, variables = ModelConverter.to_ortools_lp(model_spec, solver_name)
                result = ResultStandardizer.from_ortools(solver_model, variables, model_spec, 
                                                       time.time() - start_time, solver_name)
            elif solver_name == "SCIP":
                solver_model, variables = ModelConverter.to_scip_mip(model_spec)
                solver_model.optimize()
                result = ResultStandardizer.from_scip(solver_model, variables, model_spec, 
                                                    time.time() - start_time)
            elif solver_name == "CP-SAT":
                solver_model, variables = ModelConverter.to_cp_sat(model_spec)
                from ortools.sat.python import cp_model
                solver = cp_model.CpSolver()
                solver.Solve(solver_model)
                result = ResultStandardizer.from_cp_sat(solver, variables, model_spec, 
                                                      time.time() - start_time)
            else:
                # Only real solver implementations - no fallbacks
                result = await self._solve_with_real_solver(model_spec, solver_name, start_time)
            
            # Record performance
            execution_time = time.time() - start_time
            self._record_performance(result, execution_time, model_spec)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Solver {solver_name} failed: {e}")
            
            return SolverResult(
                solve_status=SolverStatus.ERROR.value,
                objective_value=None,
                solution={},
                solver_info={"solver_name": solver_name, "error": str(e)},
                solution_quality={},
                metadata={"model_id": model_spec.model_id},
                execution_time=execution_time,
                solver_name=solver_name
            )
    
    async def _solve_with_real_solver(self, model_spec: ModelSpecification, solver_name: str, start_time: float) -> SolverResult:
        """Solve using real solver implementation - NO MOCKS"""
        execution_time = time.time() - start_time
        
        # Only use real solvers - no fallback simulations
        if solver_name == "DEAP":
            return await self._solve_with_real_deap(model_spec, execution_time)
        elif solver_name == "PySwarms":
            return await self._solve_with_real_pyswarms(model_spec, execution_time)
        elif solver_name == "Optuna":
            return await self._solve_with_real_optuna(model_spec, execution_time)
        else:
            # If solver not implemented, raise error instead of mock
            raise ToolExecutionError(f"Solver {solver_name} not implemented with real integration", self.name)
    
    def _record_performance(self, result: SolverResult, execution_time: float, model_spec: ModelSpecification):
        """Record performance metrics for learning using Strands memory"""
        performance_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "execution_time": execution_time,
            "solve_status": result.solve_status,
            "solution_quality": result.solution_quality.get("optimality_gap", 1.0),
            "problem_type": model_spec.problem_type,
            "problem_size": model_spec.metadata.get("problem_size", "medium")
        }
        
        self.performance_history.append(performance_record)
        
        # Store performance in Strands memory for learning
        if self.strands_tools.get("memory"):
            try:
                content = f"Agent {self.name} solved {model_spec.problem_type} problem in {execution_time:.3f}s with status {result.solve_status}"
                
                self.strands_tools["memory"](
                    action="store",
                    content=content,
                    metadata={
                        "type": "agent_performance",
                        "agent_name": self.name,
                        "solver_used": result.solver_name,
                        "execution_time": execution_time,
                        "solve_status": result.solve_status,
                        "problem_type": model_spec.problem_type,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to store agent performance in memory: {e}")
        
        # Update running statistics
        if len(self.performance_history) > 10:
            recent_history = self.performance_history[-10:]
            self.success_rate = len([r for r in recent_history if r["solve_status"] in ["optimal", "feasible"]]) / len(recent_history)
            self.avg_execution_time = statistics.mean([r["execution_time"] for r in recent_history])
            self.solution_quality_score = 1.0 - statistics.mean([r["solution_quality"] for r in recent_history])


class ExactSolverExpert(BaseSolverAgent):
    """Expert in exact optimization methods for optimal solutions"""
    
    def __init__(self):
        super().__init__(
            name="ExactSolverExpert",
            specialization="Optimal solutions with mathematical guarantees",
            solvers=["SCIP", "CBC", "HiGHS"]
        )
    
    def select_solver(self, model_spec: ModelSpecification) -> Optional[str]:
        """Select best exact solver based on problem characteristics"""
        problem_type = model_spec.problem_type
        problem_size = model_spec.metadata.get("problem_size", "medium")
        
        if problem_type == "mixed_integer_programming":
            # Check for logical constraints
            has_logical = any(c.get("type") == "logical" for c in model_spec.constraints)
            has_integer_only = all(v.get("type") in ["integer", "binary"] for v in model_spec.variables)
            
            if has_logical and "SCIP" in self.available_solvers:
                return "SCIP"  # Best for complex MIP with logic
            elif has_integer_only and "CBC" in self.available_solvers:
                return "CBC"   # Optimized for pure integer problems
            elif "HiGHS" in self.available_solvers:
                return "HiGHS" # Modern, fast MIP solver
            elif "SCIP" in self.available_solvers:
                return "SCIP"  # Fallback for complex problems
        
        elif problem_type == "linear_programming":
            if "HiGHS" in self.available_solvers:
                return "HiGHS"  # Excellent LP performance
            elif "SCIP" in self.available_solvers:
                return "SCIP"   # Can handle LP as well
        
        # Default fallback
        return self.available_solvers[0] if self.available_solvers else None
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for competitive evaluation"""
        return {
            "optimality_focus": 0.9,  # High focus on optimal solutions
            "speed_factor": 0.7,      # Moderate speed
            "robustness": 0.8,        # High robustness
            "success_rate": self.success_rate,
            "avg_execution_time": self.avg_execution_time,
            "solution_quality": self.solution_quality_score
        }


class FastSolverExpert(BaseSolverAgent):
    """Expert in fast solving for time-critical applications"""
    
    def __init__(self):
        super().__init__(
            name="FastSolverExpert",
            specialization="Quick solutions for time-sensitive applications",
            solvers=["GLOP", "CLP", "HiGHS"]
        )
    
    def select_solver(self, model_spec: ModelSpecification) -> Optional[str]:
        """Select fastest solver based on problem characteristics"""
        problem_size = model_spec.metadata.get("problem_size", "medium")
        special_structure = model_spec.metadata.get("special_structure", [])
        
        if problem_size == "large" and "sparse" in special_structure:
            if "CLP" in self.available_solvers:
                return "CLP"    # Best for large sparse problems
        elif problem_size == "small":
            if "GLOP" in self.available_solvers:
                return "GLOP"   # Fast for small problems
        
        # Default to HiGHS for balanced performance
        if "HiGHS" in self.available_solvers:
            return "HiGHS"
        elif "GLOP" in self.available_solvers:
            return "GLOP"
        
        return self.available_solvers[0] if self.available_solvers else None
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for competitive evaluation"""
        return {
            "speed_focus": 0.95,      # Very high focus on speed
            "optimality_factor": 0.7, # Moderate optimality concern
            "memory_efficiency": 0.8, # Good memory usage
            "success_rate": self.success_rate,
            "avg_execution_time": self.avg_execution_time,
            "solution_quality": self.solution_quality_score
        }


class SpecializedSolverExpert(BaseSolverAgent):
    """Expert in domain-specific optimization paradigms"""
    
    def __init__(self):
        super().__init__(
            name="SpecializedSolverExpert",
            specialization="Domain-specific optimization paradigms",
            solvers=["CP-SAT", "Ipopt", "SLSQP"]
        )
    
    def select_solver(self, model_spec: ModelSpecification) -> Optional[str]:
        """Select specialized solver based on problem type"""
        problem_type = model_spec.problem_type
        special_structure = model_spec.metadata.get("special_structure", [])
        problem_size = model_spec.metadata.get("problem_size", "medium")
        
        if problem_type == "constraint_programming" or "scheduling" in special_structure:
            if "CP-SAT" in self.available_solvers:
                return "CP-SAT"  # Best CP solver available
        
        elif problem_type == "nonlinear_programming":
            if problem_size == "small" and "SLSQP" in self.available_solvers:
                return "SLSQP"  # Fast for small NLP
            elif "Ipopt" in self.available_solvers:
                return "Ipopt"  # Robust for large NLP
        
        # Check for special problem structures
        if "scheduling" in special_structure and "CP-SAT" in self.available_solvers:
            return "CP-SAT"
        
        return None  # Not applicable for this problem type
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for competitive evaluation"""
        return {
            "specialization_fit": 0.9,  # High specialization match
            "constraint_handling": 0.9, # Excellent constraint handling
            "domain_expertise": 0.85,   # Strong domain knowledge
            "success_rate": self.success_rate,
            "avg_execution_time": self.avg_execution_time,
            "solution_quality": self.solution_quality_score
        }


class HeuristicSolverExpert(BaseSolverAgent):
    """Expert in heuristic methods for large-scale complex problems"""
    
    def __init__(self):
        super().__init__(
            name="HeuristicSolverExpert",
            specialization="Large-scale and complex optimization problems",
            solvers=["DEAP", "PySwarms", "Optuna"]
        )
    
    def select_solver(self, model_spec: ModelSpecification) -> Optional[str]:
        """Select heuristic solver based on problem characteristics"""
        complexity = model_spec.metadata.get("complexity_estimate", 0.5)
        problem_size = model_spec.metadata.get("problem_size", "medium")
        special_structure = model_spec.metadata.get("special_structure", [])
        
        # Use heuristics for complex or large problems
        if complexity > 0.8 or problem_size == "large":
            # Check variable types
            has_discrete = any(v.get("type") in ["integer", "binary"] for v in model_spec.variables)
            
            if has_discrete and "DEAP" in self.available_solvers:
                return "DEAP"      # GA good for discrete optimization
            elif not has_discrete and "PySwarms" in self.available_solvers:
                return "PySwarms"  # PSO good for continuous optimization
        
        elif "multi_objective" in special_structure and "DEAP" in self.available_solvers:
            return "DEAP"          # Excellent multi-objective support
        
        elif "Optuna" in self.available_solvers:
            return "Optuna"        # Bayesian optimization for general problems
        
        return self.available_solvers[0] if self.available_solvers else None
    
    async def _solve_with_heuristic(self, model_spec: ModelSpecification, solver_name: str, start_time: float) -> SolverResult:
        """Solve using heuristic methods"""
        execution_time = time.time() - start_time
        
        try:
            if solver_name == "DEAP":
                return await self._solve_with_deap(model_spec, execution_time)
            elif solver_name == "PySwarms":
                return await self._solve_with_pyswarms(model_spec, execution_time)
            elif solver_name == "Optuna":
                return await self._solve_with_optuna(model_spec, execution_time)
            else:
                return await self._solve_with_real_solver(model_spec, solver_name, start_time)
                
        except Exception as e:
            logger.error(f"Heuristic solver {solver_name} failed: {e}")
            return SolverResult(
                solve_status=SolverStatus.ERROR.value,
                objective_value=None,
                solution={},
                solver_info={"solver_name": solver_name, "error": str(e)},
                solution_quality={},
                metadata={"model_id": model_spec.model_id},
                execution_time=execution_time,
                solver_name=solver_name
            )
    
    async def _solve_with_real_deap(self, model_spec: ModelSpecification, execution_time: float) -> SolverResult:
        """Solve using real DEAP genetic algorithm implementation"""
        try:
            import random
            from deap import base, creator, tools, algorithms
            import numpy as np
            
            # Extract problem information
            variables = model_spec.variables
            objective = model_spec.objective
            constraints = model_spec.constraints
            
            # Convert enhanced format to solver-compatible format
            variables, objective, constraints = self._convert_enhanced_format(variables, objective, constraints)
            
            # Create fitness and individual classes
            creator.create("FitnessMax", base.Fitness, weights=(1.0,) if objective['type'] == 'maximize' else (-1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMax)
            
            toolbox = base.Toolbox()
            
            # Register variable generators based on variable types and bounds
            def create_individual():
                individual = []
                for var in variables:
                    bounds = ModelConverter.parse_bounds(var['bounds'])
                    if var['type'] == 'continuous':
                        individual.append(random.uniform(bounds[0], bounds[1]))
                    elif var['type'] == 'integer':
                        individual.append(random.randint(int(bounds[0]), int(bounds[1])))
                    elif var['type'] == 'binary':
                        individual.append(random.choice([0, 1]))
                return individual
            
            toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
            toolbox.register("population", tools.initRepeat, list, toolbox.individual)
            
            # Define evaluation function based on objective
            def evaluate(individual):
                try:
                    # Calculate objective value
                    obj_value = 0.0
                    obj_coefficients = objective.get('coefficients', {})
                    
                    for i, var in enumerate(variables):
                        var_name = var['name']
                        if var_name in obj_coefficients:
                            obj_value += obj_coefficients[var_name] * individual[i]
                    
                    # Apply constraint penalties
                    penalty = 0.0
                    for constraint in constraints:
                        if constraint['type'] == 'linear':
                            constraint_value = 0.0
                            coefficients = constraint.get('coefficients', {})
                            
                            for i, var in enumerate(variables):
                                var_name = var['name']
                                if var_name in coefficients:
                                    constraint_value += coefficients[var_name] * individual[i]
                            
                            rhs = constraint.get('rhs', 0)
                            sense = constraint.get('sense', '<=')
                            
                            # Apply penalty for constraint violations
                            if sense == '<=' and constraint_value > rhs:
                                penalty += 1000 * (constraint_value - rhs)
                            elif sense == '>=' and constraint_value < rhs:
                                penalty += 1000 * (rhs - constraint_value)
                            elif sense == '=' and abs(constraint_value - rhs) > 1e-6:
                                penalty += 1000 * abs(constraint_value - rhs)
                    
                    # Return fitness (subtract penalty for maximization, add for minimization)
                    if objective['type'] == 'maximize':
                        return (obj_value - penalty,)
                    else:
                        return (obj_value + penalty,)
                        
                except Exception as e:
                    # Return very poor fitness for invalid individuals
                    return (-1e6,) if objective['type'] == 'maximize' else (1e6,)
            
            toolbox.register("evaluate", evaluate)
            toolbox.register("mate", tools.cxTwoPoint)
            toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2)
            toolbox.register("select", tools.selTournament, tournsize=3)
            
            # Run genetic algorithm
            population_size = model_spec.solver_hints.get('population_size', 50)
            generations = model_spec.solver_hints.get('generations', 100)
            
            population = toolbox.population(n=population_size)
            
            # Run algorithm
            result_pop, logbook = algorithms.eaSimple(
                population, toolbox, 
                cxpb=0.7, mutpb=0.2, 
                ngen=generations, 
                verbose=False
            )
            
            # Get best individual
            best_individual = tools.selBest(result_pop, 1)[0]
            best_fitness = best_individual.fitness.values[0]
            
            # Create solution dictionary
            solution = {}
            for i, var in enumerate(variables):
                solution[var['name']] = best_individual[i]
            
            return SolverResult(
                solve_status=SolverStatus.FEASIBLE.value,
                objective_value=best_fitness,
                solution=solution,
                solver_info={
                    "solver_name": "DEAP",
                    "solve_time": execution_time,
                    "generations": generations,
                    "population_size": population_size,
                    "best_fitness": best_fitness,
                    "algorithm": "genetic_algorithm"
                },
                solution_quality={
                    "optimality_gap": None,  # Heuristic - no gap guarantee
                    "feasibility_check": "heuristic",
                    "convergence": "completed"
                },
                metadata={"model_id": model_spec.model_id},
                execution_time=execution_time,
                solver_name="DEAP"
            )
            
        except Exception as e:
            logger.error(f"DEAP solver failed: {e}")
            raise ToolExecutionError(f"DEAP genetic algorithm failed: {str(e)}", self.name)
    
    async def _solve_with_real_pyswarms(self, model_spec: ModelSpecification, execution_time: float) -> SolverResult:
        """Solve using real PySwarms particle swarm optimization"""
        try:
            import pyswarms as ps
            import numpy as np
            
            # Extract problem information
            variables = model_spec.variables
            objective = model_spec.objective
            constraints = model_spec.constraints
            
            # Convert enhanced format to solver-compatible format
            variables, objective, constraints = self._convert_enhanced_format(variables, objective, constraints)
            
            # Prepare bounds for continuous variables only
            continuous_vars = [var for var in variables if var['type'] == 'continuous']
            if not continuous_vars:
                raise ToolExecutionError("PySwarms requires continuous variables", self.name)
            
            # Set up bounds
            lower_bounds = []
            upper_bounds = []
            var_names = []
            
            for var in continuous_vars:
                bounds = ModelConverter.parse_bounds(var['bounds'])
                lower_bounds.append(bounds[0] if bounds[0] != float('-inf') else -1000)
                upper_bounds.append(bounds[1] if bounds[1] != float('inf') else 1000)
                var_names.append(var['name'])
            
            bounds = (np.array(lower_bounds), np.array(upper_bounds))
            
            # Define objective function
            def objective_function(x):
                """Objective function for PySwarms (expects array of particles)"""
                costs = []
                obj_coefficients = objective.get('coefficients', {})
                
                for particle in x:
                    # Calculate objective value for this particle
                    obj_value = 0.0
                    for i, var_name in enumerate(var_names):
                        if var_name in obj_coefficients:
                            obj_value += obj_coefficients[var_name] * particle[i]
                    
                    # Apply constraint penalties
                    penalty = 0.0
                    for constraint in constraints:
                        if constraint['type'] == 'linear':
                            constraint_value = 0.0
                            coefficients = constraint.get('coefficients', {})
                            
                            for i, var_name in enumerate(var_names):
                                if var_name in coefficients:
                                    constraint_value += coefficients[var_name] * particle[i]
                            
                            rhs = constraint.get('rhs', 0)
                            sense = constraint.get('sense', '<=')
                            
                            # Apply penalty for constraint violations
                            if sense == '<=' and constraint_value > rhs:
                                penalty += 1000 * (constraint_value - rhs)
                            elif sense == '>=' and constraint_value < rhs:
                                penalty += 1000 * (rhs - constraint_value)
                            elif sense == '=' and abs(constraint_value - rhs) > 1e-6:
                                penalty += 1000 * abs(constraint_value - rhs)
                    
                    # PySwarms minimizes, so negate for maximization problems
                    if objective['type'] == 'maximize':
                        costs.append(-(obj_value - penalty))
                    else:
                        costs.append(obj_value + penalty)
                
                return np.array(costs)
            
            # Set up PSO parameters
            n_particles = model_spec.solver_hints.get('particles', 30)
            iters = model_spec.solver_hints.get('iterations', 100)
            
            options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}
            
            # Initialize optimizer
            optimizer = ps.single.GlobalBestPSO(
                n_particles=n_particles, 
                dimensions=len(continuous_vars),
                options=options, 
                bounds=bounds
            )
            
            # Perform optimization
            best_cost, best_pos = optimizer.optimize(objective_function, iters=iters)
            
            # Create solution dictionary
            solution = {}
            for i, var_name in enumerate(var_names):
                solution[var_name] = best_pos[i]
            
            # Add non-continuous variables with default values
            for var in variables:
                if var['type'] != 'continuous' and var['name'] not in solution:
                    bounds = ModelConverter.parse_bounds(var['bounds'])
                    if var['type'] == 'binary':
                        solution[var['name']] = 0.0
                    else:
                        solution[var['name']] = bounds[0]
            
            # Convert cost back to objective value
            if objective['type'] == 'maximize':
                objective_value = -best_cost
            else:
                objective_value = best_cost
            
            return SolverResult(
                solve_status=SolverStatus.FEASIBLE.value,
                objective_value=objective_value,
                solution=solution,
                solver_info={
                    "solver_name": "PySwarms",
                    "solve_time": execution_time,
                    "iterations": iters,
                    "particles": n_particles,
                    "best_cost": best_cost,
                    "algorithm": "particle_swarm_optimization"
                },
                solution_quality={
                    "optimality_gap": None,  # Heuristic - no gap guarantee
                    "feasibility_check": "heuristic",
                    "swarm_convergence": "completed"
                },
                metadata={"model_id": model_spec.model_id},
                execution_time=execution_time,
                solver_name="PySwarms"
            )
            
        except Exception as e:
            logger.error(f"PySwarms solver failed: {e}")
            raise ToolExecutionError(f"PySwarms PSO failed: {str(e)}", self.name)
    
    def _convert_enhanced_format(self, variables, objective, constraints):
        """Convert enhanced model builder format to solver-compatible format"""
        # Enhanced format has:
        # - variables: list of dicts with 'name', 'mathematical_name', 'variables' list
        # - constraints: list of dicts with 'variables' list and 'coefficients' list
        # - objective: dict with 'coefficients' that might be dict or list
        
        converted_variables = []
        converted_objective = objective.copy()
        converted_constraints = []
        
        # Convert variables if they have enhanced format
        for var in variables:
            if 'mathematical_name' in var:
                # Enhanced format - use the name field
                converted_var = var.copy()
                converted_variables.append(converted_var)
            else:
                # Standard format - keep as is
                converted_variables.append(var)
        
        # Convert objective coefficients if needed
        if 'coefficients' in objective:
            obj_coeffs = objective['coefficients']
            if isinstance(obj_coeffs, list):
                # Enhanced format: coefficients list needs to be converted to dict
                # For now, use simple mapping - this might need enhancement
                converted_objective['coefficients'] = {f"var_{i}": coeff for i, coeff in enumerate(obj_coeffs)}
            else:
                # Already dict format
                converted_objective['coefficients'] = obj_coeffs
        
        # Convert constraints
        for constraint in constraints:
            converted_constraint = constraint.copy()
            
            if 'coefficients' in constraint and 'variables' in constraint:
                coeffs = constraint['coefficients']
                vars_list = constraint['variables']
                
                if isinstance(coeffs, list) and isinstance(vars_list, list):
                    # Enhanced format: convert list of coefficients to dict mapping variable names
                    coeff_dict = {}
                    for i, (var_name, coeff) in enumerate(zip(vars_list, coeffs)):
                        coeff_dict[var_name] = coeff
                    converted_constraint['coefficients'] = coeff_dict
                else:
                    # Already dict format
                    converted_constraint['coefficients'] = coeffs
            
            converted_constraints.append(converted_constraint)
        
        return converted_variables, converted_objective, converted_constraints
    
    async def _solve_with_real_optuna(self, model_spec: ModelSpecification, execution_time: float) -> SolverResult:
        """Solve using real Optuna Bayesian optimization"""
        try:
            import optuna
            
            # Extract problem information
            variables = model_spec.variables
            objective = model_spec.objective
            constraints = model_spec.constraints
            
            # Convert enhanced format to solver-compatible format
            variables, objective, constraints = self._convert_enhanced_format(variables, objective, constraints)
            
            # Define objective function for Optuna
            def objective_function(trial):
                # Suggest values for each variable
                solution_values = {}
                
                for var in variables:
                    bounds = ModelConverter.parse_bounds(var['bounds'])
                    var_name = var['name']
                    
                    if var['type'] == 'continuous':
                        solution_values[var_name] = trial.suggest_float(
                            var_name, 
                            bounds[0] if bounds[0] != float('-inf') else -1000,
                            bounds[1] if bounds[1] != float('inf') else 1000
                        )
                    elif var['type'] == 'integer':
                        solution_values[var_name] = trial.suggest_int(
                            var_name,
                            int(bounds[0]) if bounds[0] != float('-inf') else -1000,
                            int(bounds[1]) if bounds[1] != float('inf') else 1000
                        )
                    elif var['type'] == 'binary':
                        solution_values[var_name] = trial.suggest_categorical(var_name, [0, 1])
                
                # Calculate objective value
                obj_value = 0.0
                obj_coefficients = objective.get('coefficients', {})
                
                for var_name, coeff in obj_coefficients.items():
                    if var_name in solution_values:
                        obj_value += coeff * solution_values[var_name]
                
                # Apply constraint penalties
                penalty = 0.0
                for constraint in constraints:
                    if constraint['type'] == 'linear':
                        constraint_value = 0.0
                        coefficients = constraint.get('coefficients', {})
                        
                        for var_name, coeff in coefficients.items():
                            if var_name in solution_values:
                                constraint_value += coeff * solution_values[var_name]
                        
                        rhs = constraint.get('rhs', 0)
                        sense = constraint.get('sense', '<=')
                        
                        # Apply penalty for constraint violations
                        if sense == '<=' and constraint_value > rhs:
                            penalty += 1000 * (constraint_value - rhs)
                        elif sense == '>=' and constraint_value < rhs:
                            penalty += 1000 * (rhs - constraint_value)
                        elif sense == '=' and abs(constraint_value - rhs) > 1e-6:
                            penalty += 1000 * abs(constraint_value - rhs)
                
                # Return objective (Optuna minimizes, so negate for maximization)
                if objective['type'] == 'maximize':
                    return -(obj_value - penalty)
                else:
                    return obj_value + penalty
            
            # Create study
            direction = 'minimize'  # Optuna always minimizes
            study = optuna.create_study(direction=direction)
            
            # Optimize
            n_trials = model_spec.solver_hints.get('trials', 100)
            study.optimize(objective_function, n_trials=n_trials)
            
            # Get best result
            best_params = study.best_params
            best_value = study.best_value
            
            # Convert back to original objective value
            if objective['type'] == 'maximize':
                objective_value = -best_value
            else:
                objective_value = best_value
            
            return SolverResult(
                solve_status=SolverStatus.FEASIBLE.value,
                objective_value=objective_value,
                solution=best_params,
                solver_info={
                    "solver_name": "Optuna",
                    "solve_time": execution_time,
                    "trials": n_trials,
                    "best_value": best_value,
                    "sampler": "TPE",
                    "algorithm": "bayesian_optimization"
                },
                solution_quality={
                    "optimality_gap": None,  # Heuristic - no gap guarantee
                    "feasibility_check": "heuristic",
                    "bayesian_confidence": study.best_trial.value if study.best_trial else 0.0
                },
                metadata={"model_id": model_spec.model_id},
                execution_time=execution_time,
                solver_name="Optuna"
            )
            
        except Exception as e:
            logger.error(f"Optuna solver failed: {e}")
            raise ToolExecutionError(f"Optuna Bayesian optimization failed: {str(e)}", self.name)
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for competitive evaluation"""
        return {
            "scalability": 0.9,        # Excellent scalability
            "exploration": 0.85,       # Good solution space exploration
            "complex_handling": 0.9,   # Handles complex problems well
            "success_rate": self.success_rate,
            "avg_execution_time": self.avg_execution_time,
            "solution_quality": self.solution_quality_score
        }


# Main Solver Tool Implementation

class SolverTool(BaseTool):
    """Enhanced Solver Tool with Multi-Solver Swarm Integration and Backward Compatibility"""
    
    def __init__(self):
        super().__init__(
            name="solver_tool",
            description="Enhanced solver tool with multi-solver swarm integration and backward compatibility",
            version="2.1.0"
        )
        
        # Enhanced integration (lazy initialization for backward compatibility)
        self._enhanced_integration = None
        self._enhanced_integration_available = False
        
        # Legacy components (maintained for backward compatibility)
        self.solver_registry = SolverRegistry()
        self.competitive_agents = {}
        self.swarm_tool = None
        
        # Session memory integration
        self.strands_tools = {}
        
        # Performance tracking
        self.execution_history = deque(maxlen=1000)
        self.competitive_results_history = deque(maxlen=500)
        
        # AgentCore integration for production deployment
        self.agentcore_app = None
        self.agentcore_context = None
        
        # Configuration
        self.max_concurrent_solvers = 4
        self.default_timeout = 300  # 5 minutes
        self.quality_threshold = 0.7
        
        # Enhanced integration configuration
        self.enable_enhanced_features = True
        self.fallback_to_legacy = True
    
    async def initialize(self) -> bool:
        """Initialize Solver Tool with enhanced integration and legacy components"""
        try:
            # Initialize enhanced integration first
            if self.enable_enhanced_features:
                await self._initialize_enhanced_integration()
            
            # Initialize legacy components for backward compatibility
            await self._initialize_legacy_components()
            
            # Initialize AgentCore integration for production deployment
            if AGENTCORE_AVAILABLE:
                try:
                    # Initialize AgentCore App
                    self.agentcore_app = BedrockAgentCoreApp()
                    
                    # Initialize AgentCore Context for solver state management
                    self.agentcore_context = BedrockAgentCoreContext()
                    
                    self.logger.info("AgentCore integration initialized successfully")
                    
                except Exception as e:
                    self.logger.warning(f"AgentCore initialization failed: {e}")
                    self.agentcore_app = None
                    self.agentcore_context = None
            else:
                self.logger.info("AgentCore SDK not available - using Strands-only mode")
            
            self._initialized = True
            self.logger.info("Enhanced Solver Tool initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Enhanced Solver Tool: {e}")
            return False
    
    async def _initialize_enhanced_integration(self):
        """Initialize enhanced multi-solver integration"""
        try:
            from .enhanced_solver_integration import EnhancedSolverIntegration
        except ImportError:
            try:
                from tools.enhanced_solver_integration import EnhancedSolverIntegration
            except ImportError:
                from enhanced_solver_integration import EnhancedSolverIntegration
            
            self._enhanced_integration = EnhancedSolverIntegration()
            success = await self._enhanced_integration.initialize()
            
            if success:
                self._enhanced_integration_available = True
                self.logger.info("Enhanced solver integration initialized successfully")
            else:
                self.logger.warning("Enhanced solver integration initialization failed, using legacy mode")
                self._enhanced_integration_available = False
                
        except ImportError as e:
            self.logger.warning(f"Enhanced integration not available: {e}")
            self._enhanced_integration_available = False
        except Exception as e:
            self.logger.error(f"Error initializing enhanced integration: {e}")
            self._enhanced_integration_available = False
    
    async def _initialize_legacy_components(self):
        """Initialize legacy components for backward compatibility"""
        try:
            # Initialize Strands tools integration
            await self._initialize_strands_tools()
            
            # Initialize competitive agents
            await self._initialize_competitive_agents()
            
            # Initialize swarm intelligence
            await self._initialize_swarm_intelligence()
            
            # Check solver availability
            await self._check_solver_availability()
            
            self.logger.info("Legacy components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize legacy components: {e}")
            if not self._enhanced_integration_available:
                raise  # Re-raise if no enhanced integration available
    
    async def _initialize_strands_tools(self):
        """Initialize Strands tools integration - Production implementation required"""
        from strands_tools import memory, retrieve, use_aws
        from strands import Agent
        
        # Create Strands agent with required tools
        self.strands_agent = Agent(tools=[memory, retrieve, use_aws])
        self.strands_tools = {
            'memory': self.strands_agent.tool.memory,
            'retrieve': self.strands_agent.tool.retrieve,
            'use_aws': self.strands_agent.tool.use_aws
        }
        self.logger.info("Strands tools initialized for solver tool")
    
    async def _initialize_competitive_agents(self):
        """Initialize competitive solver agents"""
        try:
            self.competitive_agents = {
                "exact_solver_expert": ExactSolverExpert(),
                "fast_solver_expert": FastSolverExpert(),
                "specialized_solver_expert": SpecializedSolverExpert(),
                "heuristic_solver_expert": HeuristicSolverExpert()
            }
            
            # Initialize all agents
            for agent_name, agent in self.competitive_agents.items():
                success = await agent.initialize()
                if success:
                    self.logger.info(f"Initialized competitive agent: {agent_name}")
                else:
                    self.logger.warning(f"Failed to initialize agent: {agent_name}")
            
            self.logger.info("Competitive solver agents initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize competitive agents: {e}")
            self.competitive_agents = {}
    
    async def _initialize_swarm_intelligence(self):
        """Initialize competitive swarm intelligence coordination - Production implementation required"""
        try:
            # Initialize adaptive swarm tool for coordination
            self.swarm_tool = AdaptiveManufacturingSwarms.create_competitive_model_swarm()
            await self.swarm_tool.initialize()
            
            # Initialize the core swarm tool for competitive coordination
            from tools.swarm_tool import SwarmTool
            self.core_swarm_tool = AdaptiveManufacturingSwarms.create_competitive_model_swarm()
            await self.core_swarm_tool.initialize()
            self.logger.info("Core swarm tool initialized for competitive coordination")
            
            self.logger.info("Competitive swarm intelligence coordination initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize swarm intelligence: {e}")
            # Set fallback values to prevent attribute errors
            self.swarm_tool = None
            self.core_swarm_tool = None
    
    async def _check_solver_availability(self):
        """Check availability of all registered solvers"""
        try:
            available_count = 0
            total_count = len(self.solver_registry.solvers)
            
            for solver_name in self.solver_registry.solvers.keys():
                if self.solver_registry.check_solver_availability(solver_name):
                    available_count += 1
            
            self.logger.info(f"Solver availability: {available_count}/{total_count} solvers available")
            
            if available_count == 0:
                self.logger.warning("No solvers available - tool may not function properly")
            
        except Exception as e:
            self.logger.error(f"Error checking solver availability: {e}")
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute solver operation with enhanced integration when available"""
        
        # Use enhanced integration if available and enabled
        if (self._enhanced_integration_available and 
            self._enhanced_integration and 
            self.enable_enhanced_features):
            try:
                result = await self._enhanced_integration.execute(**kwargs)
                # Add backward compatibility metadata
                result["enhanced_features_used"] = True
                result["backward_compatible"] = True
                return result
            except Exception as e:
                self.logger.warning(f"Enhanced integration failed, falling back to legacy: {e}")
                if not self.fallback_to_legacy:
                    raise ToolExecutionError(f"Enhanced integration failed: {str(e)}", self.name)
        
        # Fallback to legacy implementation
        return await self._execute_legacy(**kwargs)
    
    async def _execute_legacy(self, **kwargs) -> Dict[str, Any]:
        """Execute using legacy solver implementation"""
        operation = kwargs.get("operation", "solve")
        
        if operation == "solve":
            return await self._solve_optimization_problem(**kwargs)
        elif operation == "competitive_solve":
            return await self._competitive_solve(**kwargs)
        elif operation == "get_solver_info":
            return await self._get_solver_info(**kwargs)
        elif operation == "benchmark_solvers":
            return await self._benchmark_solvers(**kwargs)
        elif operation == "get_performance_insights":
            return await self._get_performance_insights(**kwargs)
        else:
            raise ToolExecutionError(f"Unknown operation: {operation}", self.name)
    
    async def _solve_optimization_problem(self, 
                                        model_spec: Dict[str, Any],
                                        solver_preferences: Optional[List[str]] = None,
                                        use_competitive_swarm: bool = True,
                                        timeout: Optional[int] = None,
                                        **kwargs) -> Dict[str, Any]:
        """Solve optimization problem with competitive swarm intelligence"""
        start_time = datetime.utcnow()
        
        try:
            # Convert input to ModelSpecification if needed
            if isinstance(model_spec, dict):
                # Check if it's a ModelSpecification object
                if hasattr(model_spec, 'problem_type'):
                    # It's already a ModelSpecification object
                    pass
                elif 'best_model' in model_spec:
                    # Extract the best_model from the result
                    model_spec = model_spec['best_model']
                else:
                    # Skip dict conversion for now - let the solver handle it
                    pass
            
            # Store problem context in session memory
            await self._store_problem_context(model_spec)
            
            if use_competitive_swarm and self.competitive_agents:
                # Use competitive swarm approach
                result = await self._competitive_solve(
                    model_spec=model_spec,
                    solver_preferences=solver_preferences,
                    timeout=timeout or self.default_timeout
                )
            else:
                # Use single best solver approach
                result = await self._single_solver_solve(model_spec, solver_preferences, timeout)
            
            # Store results in session memory
            await self._store_solver_results(result)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution("solve_optimization_problem", kwargs, True, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Optimization solving failed: {str(e)}"
            self._log_execution("solve_optimization_problem", kwargs, False, execution_time, error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _competitive_solve(self, 
                               model_spec: ModelSpecification,
                               solver_preferences: Optional[List[str]] = None,
                               timeout: int = 300) -> Dict[str, Any]:
        """Execute competitive solving with swarm intelligence framework"""
        try:
            # Select applicable competitive agents
            applicable_agents = self._select_applicable_agents(model_spec)
            
            if not applicable_agents:
                raise ToolExecutionError("No applicable competitive agents for problem", self.name)
            
            self.logger.info(f"Starting competitive swarm solving with {len(applicable_agents)} agents")
            
            # Use swarm intelligence framework if available
            if self.core_swarm_tool:
                return await self._execute_swarm_competitive_solving(applicable_agents, model_spec, timeout)
            else:
                return await self._execute_basic_competitive_solving(applicable_agents, model_spec, timeout)
            
        except Exception as e:
            self.logger.error(f"Competitive solving failed: {e}")
            raise ToolExecutionError(f"Competitive solving failed: {str(e)}", self.name)
    
    async def _execute_swarm_competitive_solving(self, agents: Dict[str, Any], 
                                               model_spec: ModelSpecification, 
                                               timeout: int) -> Dict[str, Any]:
        """Execute competitive solving using swarm intelligence framework"""
        try:
            # Prepare swarm task for competitive coordination
            swarm_task = {
                "task_type": "competitive_optimization_solving",
                "problem_description": f"Solve {model_spec.problem_type} optimization problem with {len(model_spec.variables)} variables",
                "coordination_pattern": "competitive",
                "agents": list(agents.keys()),
                "problem_context": {
                    "problem_type": model_spec.problem_type,
                    "complexity": model_spec.metadata.get("complexity_estimate", 0.5),
                    "domain": model_spec.metadata.get("domain", "general"),
                    "problem_size": model_spec.metadata.get("problem_size", "medium")
                },
                "timeout": timeout
            }
            
            # Execute competitive swarm coordination
            swarm_result = await self.core_swarm_tool.execute(
                operation="coordinate_agents",
                **swarm_task
            )
            
            # Execute individual agents in competitive mode
            agent_results = []
            for agent_name, agent in agents.items():
                try:
                    result = await self._execute_agent_with_timeout(agent, model_spec, timeout // len(agents))
                    if result:
                        agent_results.append((agent_name, result))
                except Exception as e:
                    self.logger.error(f"Competitive agent {agent_name} failed: {e}")
            
            if not agent_results:
                raise ToolExecutionError("All competitive agents failed in swarm execution", self.name)
            
            # Select best result using swarm intelligence
            best_agent, best_result = self._select_best_competitive_result(agent_results, model_spec)
            
            # Check if any solver actually succeeded
            successful_solvers = [result for name, result in agent_results if result.solve_status in ["optimal", "feasible"]]
            
            # Validate solver results before creating final result
            validated_results = []
            for name, result in agent_results:
                if result is not None:
                    validated_result = self._validate_solver_result({
                        "success": result.solve_status in ["optimal", "feasible"],
                        "best_solution": {
                            "solve_status": result.solve_status,
                            "objective_value": result.objective_value,
                            "solution": result.solution if hasattr(result, 'solution') else {},
                            "solver_info": {
                                "solver_name": result.solver_name,
                                "solve_time": result.execution_time
                            }
                        }
                    })
                    validated_results.append((name, validated_result))
            
            # Create comprehensive swarm result
            competitive_result = {
            "success": len([r for _, r in validated_results if r.get("success", False)]) > 0,
                "best_solution": asdict(best_result),
                "winning_agent": best_agent,
                "competitive_analysis": {
                    "total_agents": len(agents),
                    "successful_agents": len(agent_results),
                    "coordination_pattern": "competitive",
                    "swarm_coordination": True,
                    "agent_results": [
                        {
                            "agent_name": name,
                            "success": result.solve_status in ["optimal", "feasible"],
                            "solver_used": result.solver_name,
                            "execution_time": result.execution_time,
                            "objective_value": result.objective_value,
                            "solve_status": result.solve_status
                        }
                        for name, result in agent_results
                    ]
                },
                "swarm_intelligence": {
                    "framework_used": "SwarmTool",
                    "coordination_pattern": "competitive",
                    "quality_improvement": self._calculate_competitive_improvement(agent_results),
                    "swarm_efficiency": len(agent_results) / len(agents),
                    "best_agent_selection": "multi_criteria_optimization"
                },
                "performance_comparison": self._compare_agent_performance(agent_results)
            }
            
            # Record swarm performance for learning
            await self._record_swarm_performance(competitive_result, model_spec)
            
            return competitive_result
            
        except Exception as e:
            self.logger.error(f"Swarm competitive solving failed: {e}")
            # Fallback to basic competitive solving
            return await self._execute_basic_competitive_solving(agents, model_spec, timeout)
    
    async def _execute_basic_competitive_solving(self, agents: Dict[str, Any], 
                                               model_spec: ModelSpecification, 
                                               timeout: int) -> Dict[str, Any]:
        """Execute basic competitive solving without swarm framework"""
        # Execute agents in parallel with timeout
        solver_tasks = []
        for agent_name, agent in agents.items():
            task = asyncio.create_task(
                self._execute_agent_with_timeout(agent, model_spec, timeout // len(agents))
            )
            solver_tasks.append((agent_name, task))
        
        # Wait for all tasks to complete or timeout
        results = []
        for agent_name, task in solver_tasks:
            try:
                result = await task
                results.append((agent_name, result))
            except Exception as e:
                self.logger.error(f"Agent {agent_name} failed: {e}")
                results.append((agent_name, None))
        
        # Filter successful results (only those that actually solved the problem)
        successful_results = [(name, result) for name, result in results if result is not None and result.solve_status in ["optimal", "feasible"]]
        
        if not successful_results:
            # If no solvers succeeded, still return a result but mark as failed
            best_agent, best_result = self._select_best_competitive_result([(name, result) for name, result in results if result is not None], model_spec)
        else:
            # Select best result from successful solvers
            best_agent, best_result = self._select_best_competitive_result(successful_results, model_spec)
        
        # Create basic competitive result
        competitive_result = {
            "success": len(successful_results) > 0,
            "best_solution": asdict(best_result),
            "winning_agent": best_agent,
            "competitive_analysis": {
                "total_agents": len(agents),
                "successful_agents": len(successful_results),
                "coordination_pattern": "competitive",
                "swarm_coordination": False,
                "agent_results": [
                    {
                        "agent_name": name,
                        "success": result is not None,
                        "solver_used": result.solver_name if result else None,
                        "execution_time": result.execution_time if result else None,
                        "objective_value": result.objective_value if result else None
                    }
                    for name, result in results
                ]
            },
            "performance_comparison": self._compare_agent_performance(successful_results),
            "swarm_metadata": {
                "coordination_pattern": "competitive",
                "selection_criteria": "multi_objective_optimization",
                "quality_improvement": self._calculate_competitive_improvement(successful_results)
            }
        }
        
        # Record competitive performance
        await self._record_competitive_performance(competitive_result, model_spec)
        
        return competitive_result
    
    def _select_applicable_agents(self, model_spec: ModelSpecification) -> Dict[str, BaseSolverAgent]:
        """Select agents applicable to the problem type"""
        applicable = {}
        
        for agent_name, agent in self.competitive_agents.items():
            # Check if agent can handle this problem type
            selected_solver = agent.select_solver(model_spec)
            if selected_solver:
                applicable[agent_name] = agent
        
        return applicable
    
    async def _execute_agent_with_timeout(self, agent: BaseSolverAgent, 
                                        model_spec: ModelSpecification, 
                                        timeout: int) -> Optional[SolverResult]:
        """Execute agent with timeout protection"""
        try:
            return await asyncio.wait_for(
                agent.solve_model(model_spec, self.solver_registry),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            self.logger.warning(f"Agent {agent.name} timed out after {timeout}s")
            return None
        except Exception as e:
            self.logger.error(f"Agent {agent.name} execution failed: {e}")
            return None
    
    def _select_best_competitive_result(self, results: List[Tuple[str, SolverResult]], 
                                      model_spec: ModelSpecification) -> Tuple[str, SolverResult]:
        """Select best result from competitive agents"""
        if not results:
            raise ToolExecutionError("No results to select from", self.name)
        
        # Score each result
        scored_results = []
        for agent_name, result in results:
            score = self._calculate_result_score(result, model_spec)
            scored_results.append((score, agent_name, result))
        
        # Sort by score (higher is better)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        best_score, best_agent, best_result = scored_results[0]
        
        self.logger.info(f"Selected best result from {best_agent} with score {best_score:.3f}")
        
        return best_agent, best_result
    
    def _calculate_result_score(self, result: SolverResult, model_spec: ModelSpecification) -> float:
        """Calculate composite score for result quality"""
        weights = {
            "optimality": 0.4,
            "feasibility": 0.3,
            "solve_time": 0.2,
            "robustness": 0.1
        }
        
        # Optimality score
        if result.solve_status == SolverStatus.OPTIMAL.value:
            optimality_score = 1.0
        elif result.solve_status == SolverStatus.FEASIBLE.value:
            gap = result.solution_quality.get("optimality_gap")
            if gap is not None:
                optimality_score = max(0, 1.0 - gap)
            else:
                optimality_score = 0.8  # Default for feasible without gap info
        else:
            optimality_score = 0.0
        
        # Feasibility score
        feasibility_score = 1.0 if result.solve_status in [SolverStatus.OPTIMAL.value, SolverStatus.FEASIBLE.value] else 0.0
        
        # Solve time score (normalized, faster is better)
        max_time = model_spec.solver_hints.get("time_limit", self.default_timeout)
        solve_time = result.execution_time
        time_score = max(0, 1.0 - (solve_time / max_time))
        
        # Robustness score (based on solver reliability)
        solver_name = result.solver_name
        robustness_score = self._get_solver_robustness_score(solver_name)
        
        # Calculate weighted score
        composite_score = (
            optimality_score * weights["optimality"] +
            feasibility_score * weights["feasibility"] +
            time_score * weights["solve_time"] +
            robustness_score * weights["robustness"]
        )
        
        return composite_score
    
    def _get_solver_robustness_score(self, solver_name: str) -> float:
        """Get robustness score for solver"""
        robustness_map = {
            "SCIP": 0.9,
            "HiGHS": 0.85,
            "GLOP": 0.8,
            "CLP": 0.85,
            "CBC": 0.75,
            "CP-SAT": 0.9,
            "Ipopt": 0.8,
            "SLSQP": 0.7,
            "DEAP": 0.7,
            "PySwarms": 0.65,
            "Optuna": 0.75
        }
        
        return robustness_map.get(solver_name, 0.6)
    
    def _compare_agent_performance(self, results: List[Tuple[str, SolverResult]]) -> Dict[str, Any]:
        """Compare performance across competitive agents"""
        if not results:
            return {}
        
        comparison = {
            "execution_times": {},
            "solution_qualities": {},
            "solver_preferences": {},
            "success_rates": {}
        }
        
        for agent_name, result in results:
            comparison["execution_times"][agent_name] = result.execution_time
            comparison["solution_qualities"][agent_name] = result.objective_value
            comparison["solver_preferences"][agent_name] = result.solver_name
            comparison["success_rates"][agent_name] = 1.0 if result.solve_status in [SolverStatus.OPTIMAL.value, SolverStatus.FEASIBLE.value] else 0.0
        
        # Calculate statistics
        execution_times = list(comparison["execution_times"].values())
        if execution_times:
            comparison["avg_execution_time"] = statistics.mean(execution_times)
            comparison["fastest_agent"] = min(comparison["execution_times"], key=comparison["execution_times"].get)
        
        objective_values = [v for v in comparison["solution_qualities"].values() if v is not None]
        if objective_values:
            comparison["best_objective"] = max(objective_values)  # Assuming maximization
            comparison["best_solution_agent"] = max(comparison["solution_qualities"], key=lambda k: comparison["solution_qualities"][k] or 0)
        
        return comparison
    
    def _calculate_competitive_improvement(self, results: List[Tuple[str, SolverResult]]) -> float:
        """Calculate improvement from competitive approach"""
        if len(results) <= 1:
            return 0.0
        
        objective_values = [result.objective_value for _, result in results if result.objective_value is not None]
        
        if len(objective_values) <= 1:
            return 0.0
        
        best_value = max(objective_values)
        avg_value = statistics.mean(objective_values)
        
        improvement = (best_value - avg_value) / avg_value if avg_value > 0 else 0.0
        return min(1.0, max(0.0, improvement))
    
    async def _single_solver_solve(self, model_spec: ModelSpecification, 
                                 solver_preferences: Optional[List[str]] = None,
                                 timeout: Optional[int] = None) -> Dict[str, Any]:
        """Solve using single best solver (fallback approach)"""
        try:
            # Select best solver
            compatible_solvers = self.solver_registry.get_compatible_solvers(
                model_spec.problem_type,
                model_spec.metadata.get("problem_size", "medium")
            )
            
            if solver_preferences:
                # Filter by preferences
                preferred_available = [s for s in solver_preferences if s in compatible_solvers]
                if preferred_available:
                    compatible_solvers = preferred_available
            
            if not compatible_solvers:
                raise ToolExecutionError("No compatible solvers available", self.name)
            
            solver_name = compatible_solvers[0]
            
            # Create appropriate agent for solver
            if solver_name in ["SCIP", "CBC", "HiGHS"]:
                agent = self.competitive_agents.get("exact_solver_expert")
            elif solver_name in ["GLOP", "CLP"]:
                agent = self.competitive_agents.get("fast_solver_expert")
            elif solver_name in ["CP-SAT", "Ipopt", "SLSQP"]:
                agent = self.competitive_agents.get("specialized_solver_expert")
            else:
                agent = self.competitive_agents.get("heuristic_solver_expert")
            
            if not agent:
                raise ToolExecutionError("No suitable agent available", self.name)
            
            # Solve with selected agent
            result = await agent.solve_model(model_spec, self.solver_registry)
            
            return {
                "success": True,
                "solution": asdict(result),
                "solver_used": solver_name,
                "approach": "single_solver",
                "agent_used": agent.name
            }
            
        except Exception as e:
            self.logger.error(f"Single solver approach failed: {e}")
            raise ToolExecutionError(f"Single solver approach failed: {str(e)}", self.name)
    
    async def _store_problem_context(self, model_spec: ModelSpecification):
        """Store problem context in session memory using Strands memory tool"""
        if self.strands_tools.get("memory"):
            try:
                context_content = f"Solver optimization problem started: {model_spec.problem_type} with {len(model_spec.variables)} variables and {len(model_spec.constraints)} constraints"
                
                self.strands_tools["memory"](
                    action="store",
                    content=context_content,
                    metadata={
                        "type": "solver_context",
                        "model_id": model_spec.model_id,
                        "problem_type": model_spec.problem_type,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
            except Exception as e:
                self.logger.warning(f"Failed to store problem context: {e}")
    
    async def _store_solver_results(self, result: Dict[str, Any]):
        """Store solver results in session memory using Strands memory tool"""
        if self.strands_tools.get("memory"):
            try:
                # Create human-readable content for memory storage
                if result.get("success"):
                    best_solution = result.get("best_solution", {})
                    content = f"Solver optimization completed successfully. Winning agent: {result.get('winning_agent', 'unknown')}, Objective value: {best_solution.get('objective_value', 'N/A')}, Status: {best_solution.get('solve_status', 'unknown')}"
                else:
                    content = f"Solver optimization failed: {result.get('error', 'Unknown error')}"
                
                self.strands_tools["memory"](
                    action="store",
                    content=content,
                    metadata={
                        "type": "solver_results",
                        "success": result.get("success", False),
                        "winning_agent": result.get("winning_agent"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
            except Exception as e:
                self.logger.warning(f"Failed to store solver results: {e}")
    
    async def _record_competitive_performance(self, result: Dict[str, Any], model_spec: ModelSpecification):
        """Record competitive performance for learning"""
        try:
            performance_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "model_id": model_spec.model_id,
                "problem_type": model_spec.problem_type,
                "winning_agent": result.get("winning_agent"),
                "total_agents": result["competitive_analysis"]["total_agents"],
                "successful_agents": result["competitive_analysis"]["successful_agents"],
                "quality_improvement": result.get("swarm_metadata", {}).get("quality_improvement", 0),
                "best_objective": result["best_solution"]["objective_value"]
            }
            
            self.competitive_results_history.append(performance_record)
            
            # Record in solver registry
            if result.get("best_solution"):
                best_solution = result["best_solution"]
                self.solver_registry.record_solver_performance(
                    best_solution["solver_name"],
                    best_solution["execution_time"],
                    best_solution.get("objective_value", 0),
                    model_spec.metadata
                )
            
        except Exception as e:
            self.logger.error(f"Failed to record competitive performance: {e}")
    
    async def _record_swarm_performance(self, result: Dict[str, Any], model_spec: ModelSpecification):
        """Record swarm intelligence performance for adaptive learning"""
        try:
            # Record in adaptive swarm tool for learning
            if self.swarm_tool:
                swarm_metrics = {
                    "swarm_id": str(uuid.uuid4()),
                    "execution_time": result["best_solution"]["execution_time"],
                    "success_rate": result["competitive_analysis"]["successful_agents"] / result["competitive_analysis"]["total_agents"],
                    "confidence_score": result.get("swarm_intelligence", {}).get("swarm_efficiency", 0.8),
                    "solution_quality": 1.0 - result.get("swarm_intelligence", {}).get("quality_improvement", 0),
                    "problem_type": model_spec.problem_type,
                    "problem_complexity": model_spec.metadata.get("complexity_estimate", 0.5),
                    "coordination_pattern": "competitive",
                    "swarm_size": result["competitive_analysis"]["total_agents"],
                    "specializations": list(self.competitive_agents.keys())
                }
                
                await self.swarm_tool.execute(
                    operation="record_feedback",
                    swarm_id=swarm_metrics["swarm_id"],
                    satisfaction_score=swarm_metrics["success_rate"],
                    feedback_text=f"Competitive solver swarm completed with {result['winning_agent']} winning"
                )
            
            # Store in Strands memory for cross-tool learning
            if self.strands_tools.get("memory"):
                content = f"Competitive swarm solving completed: {result['winning_agent']} won with {result['competitive_analysis']['successful_agents']}/{result['competitive_analysis']['total_agents']} agents successful"
                
                self.strands_tools["memory"](
                    action="store",
                    content=content,
                    metadata={
                        "type": "swarm_performance",
                        "coordination_pattern": "competitive",
                        "winning_agent": result.get("winning_agent"),
                        "success_rate": result["competitive_analysis"]["successful_agents"] / result["competitive_analysis"]["total_agents"],
                        "problem_type": model_spec.problem_type,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
        except Exception as e:
            self.logger.error(f"Failed to record swarm performance: {e}")
    
    async def _get_solver_info(self, **kwargs) -> Dict[str, Any]:
        """Get information about available solvers"""
        try:
            solver_info = {}
            
            for solver_name, capability in self.solver_registry.solvers.items():
                solver_info[solver_name] = {
                    "category": capability.category.value,
                    "problem_types": capability.problem_types,
                    "performance_profile": capability.performance_profile,
                    "available": self.solver_registry.check_solver_availability(solver_name),
                    "version": capability.version
                }
            
            return {
                "success": True,
                "solvers": solver_info,
                "total_solvers": len(solver_info),
                "available_solvers": len([s for s in solver_info.values() if s["available"]]),
                "categories": list(set(s["category"] for s in solver_info.values()))
            }
            
        except Exception as e:
            error_msg = f"Failed to get solver info: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _benchmark_solvers(self, problem_types: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Benchmark solver performance on test problems"""
        try:
            if not problem_types:
                problem_types = ["linear_programming", "mixed_integer_programming"]
            
            benchmark_results = {}
            
            for problem_type in problem_types:
                # Create simple test problem
                test_model = self._create_test_model(problem_type)
                
                # Test with competitive solving
                result = await self._competitive_solve(test_model, timeout=30)
                
                benchmark_results[problem_type] = {
                    "test_completed": True,
                    "winning_agent": result.get("winning_agent"),
                    "execution_time": result["best_solution"]["execution_time"],
                    "solution_quality": result["best_solution"]["objective_value"],
                    "agents_tested": result["competitive_analysis"]["total_agents"],
                    "success_rate": result["competitive_analysis"]["successful_agents"] / result["competitive_analysis"]["total_agents"]
                }
            
            return {
                "success": True,
                "benchmark_results": benchmark_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Solver benchmarking failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _create_test_model(self, problem_type: str) -> ModelSpecification:
        """Create simple test model for benchmarking"""
        if problem_type == "linear_programming":
            return ModelSpecification(
                problem_type="linear_programming",
                variables=[
                    {"name": "x", "type": "continuous", "bounds": "[0, 10]"},
                    {"name": "y", "type": "continuous", "bounds": "[0, 10]"}
                ],
                constraints=[
                    {
                        "name": "constraint1",
                        "type": "linear",
                        "coefficients": {"x": 1, "y": 2},
                        "rhs": 10,
                        "sense": "<="
                    }
                ],
                objective={
                    "type": "maximize",
                    "coefficients": {"x": 3, "y": 2}
                },
                solver_hints={"time_limit": 30},
                metadata={"problem_size": "small", "test_problem": True}
            )
        
        elif problem_type == "mixed_integer_programming":
            return ModelSpecification(
                problem_type="mixed_integer_programming",
                variables=[
                    {"name": "x", "type": "continuous", "bounds": "[0, 10]"},
                    {"name": "y", "type": "integer", "bounds": "[0, 10]"},
                    {"name": "z", "type": "binary", "bounds": "[0, 1]"}
                ],
                constraints=[
                    {
                        "name": "constraint1",
                        "type": "linear",
                        "coefficients": {"x": 1, "y": 2, "z": 1},
                        "rhs": 10,
                        "sense": "<="
                    }
                ],
                objective={
                    "type": "maximize",
                    "coefficients": {"x": 3, "y": 2, "z": 5}
                },
                solver_hints={"time_limit": 30},
                metadata={"problem_size": "small", "test_problem": True}
            )
        
        else:
            # Default simple LP
            return self._create_test_model("linear_programming")
    
    async def _get_performance_insights(self, **kwargs) -> Dict[str, Any]:
        """Get performance insights and analytics"""
        try:
            insights = {
                "execution_statistics": self._get_execution_statistics(),
                "competitive_analysis": self._get_competitive_analysis(),
                "solver_performance": self._get_solver_performance_analysis(),
                "agent_effectiveness": self._get_agent_effectiveness_analysis(),
                "recommendations": self._get_performance_recommendations()
            }
            
            return {
                "success": True,
                "insights": insights,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to generate performance insights: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {"message": "No execution history available"}
        
        recent_executions = list(self.execution_history)[-50:]  # Last 50 executions
        
        return {
            "total_executions": len(self.execution_history),
            "recent_executions": len(recent_executions),
            "success_rate": len([e for e in recent_executions if e.get("success", False)]) / len(recent_executions),
            "average_execution_time": statistics.mean([e.get("execution_time", 0) for e in recent_executions])
        }
    
    def _get_competitive_analysis(self) -> Dict[str, Any]:
        """Analyze competitive solving performance"""
        if not self.competitive_results_history:
            return {"message": "No competitive results available"}
        
        recent_results = list(self.competitive_results_history)[-20:]
        
        winning_agents = [r["winning_agent"] for r in recent_results]
        agent_wins = {agent: winning_agents.count(agent) for agent in set(winning_agents)}
        
        return {
            "total_competitive_solves": len(self.competitive_results_history),
            "recent_competitive_solves": len(recent_results),
            "agent_win_rates": agent_wins,
            "average_quality_improvement": statistics.mean([r["quality_improvement"] for r in recent_results]),
            "average_agents_per_solve": statistics.mean([r["total_agents"] for r in recent_results]),
            "average_success_rate": statistics.mean([r["successful_agents"] / r["total_agents"] for r in recent_results])
        }
    
    def _get_solver_performance_analysis(self) -> Dict[str, Any]:
        """Analyze individual solver performance"""
        solver_stats = {}
        
        for solver_name, history in self.solver_registry.performance_history.items():
            if history:
                recent_history = history[-10:]  # Last 10 executions
                solver_stats[solver_name] = {
                    "total_executions": len(history),
                    "recent_executions": len(recent_history),
                    "average_execution_time": statistics.mean([h["execution_time"] for h in recent_history]),
                    "average_solution_quality": statistics.mean([h["solution_quality"] for h in recent_history]),
                    "success_rate": len([h for h in recent_history if h.get("success", False)]) / len(recent_history)
                }
        
        return solver_stats
    
    def _get_agent_effectiveness_analysis(self) -> Dict[str, Any]:
        """Analyze competitive agent effectiveness"""
        agent_stats = {}
        
        for agent_name, agent in self.competitive_agents.items():
            metrics = agent.get_performance_metrics()
            agent_stats[agent_name] = {
                "specialization": agent.specialization,
                "available_solvers": len(agent.available_solvers) if hasattr(agent, 'available_solvers') else 0,
                "performance_metrics": metrics,
                "recent_performance": {
                    "success_rate": agent.success_rate,
                    "avg_execution_time": agent.avg_execution_time,
                    "solution_quality_score": agent.solution_quality_score
                }
            }
        
        return agent_stats
    
    def _get_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Analyze competitive results
        if self.competitive_results_history:
            recent_results = list(self.competitive_results_history)[-10:]
            avg_improvement = statistics.mean([r["quality_improvement"] for r in recent_results])
            
            if avg_improvement < 0.1:
                recommendations.append("Consider tuning solver parameters to improve competitive advantage")
            
            success_rates = [r["successful_agents"] / r["total_agents"] for r in recent_results]
            avg_success_rate = statistics.mean(success_rates)
            
            if avg_success_rate < 0.8:
                recommendations.append("Some solvers may need configuration updates - check solver availability")
        
        # Analyze agent performance
        for agent_name, agent in self.competitive_agents.items():
            if agent.success_rate < 0.7:
                recommendations.append(f"Agent {agent_name} showing low success rate - consider solver updates")
        
        if not recommendations:
            recommendations.append("Performance is optimal - continue current competitive strategy")
        
        return recommendations
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters for solver execution"""
        required_params = ["model_spec"]
        
        for param in required_params:
            if param not in kwargs:
                return False
        
        # Validate model specification
        model_spec = kwargs["model_spec"]
        if isinstance(model_spec, dict):
            required_fields = ["problem_type", "variables", "constraints", "objective"]
            for field in required_fields:
                if field not in model_spec:
                    return False
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup solver tool resources"""
        try:
            # Cleanup enhanced integration
            if self._enhanced_integration:
                await self._enhanced_integration.cleanup()
            
            # Cleanup competitive agents
            for agent in self.competitive_agents.values():
                if hasattr(agent, 'cleanup'):
                    await agent.cleanup()
            
            # Cleanup swarm tool
            if self.swarm_tool:
                await self.swarm_tool.cleanup()
            
            self.logger.info("Enhanced Solver Tool cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    # Enhanced Integration Management Methods
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status including enhanced features"""
        try:
            status = {
                "solver_tool_version": "2.1.0",
                "enhanced_integration_available": self._enhanced_integration_available,
                "enhanced_features_enabled": self.enable_enhanced_features,
                "fallback_to_legacy_enabled": self.fallback_to_legacy,
                "backward_compatibility": True
            }
            
            # Get enhanced integration status if available
            if self._enhanced_integration_available and self._enhanced_integration:
                enhanced_status = await self._enhanced_integration.get_integration_status()
                status["enhanced_integration_status"] = enhanced_status
            
            # Get legacy component status
            status["legacy_components"] = {
                "solver_registry_initialized": bool(self.solver_registry),
                "competitive_agents_count": len(self.competitive_agents),
                "swarm_tool_available": self.swarm_tool is not None,
                "strands_tools_available": bool(self.strands_tools)
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            return {
                "error": str(e),
                "solver_tool_version": "2.1.0",
                "status": "error"
            }
    
    def enable_enhanced_features(self, enable: bool = True):
        """Enable or disable enhanced multi-solver features"""
        self.enable_enhanced_features = enable
        self.logger.info(f"Enhanced features {'enabled' if enable else 'disabled'}")
    
    def set_production_mode(self, enable_production: bool = True):
        """Enable production-only mode (no fallbacks allowed)"""
        self.production_mode = enable_production
        self.logger.info(f"Production mode {'enabled' if enable_production else 'disabled'}")
    
    async def get_solver_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive solver capabilities from both enhanced and legacy systems"""
        try:
            capabilities = {
                "integration_type": "enhanced_with_legacy_fallback",
                "total_capabilities": {}
            }
            
            # Get enhanced capabilities if available
            if self._enhanced_integration_available and self._enhanced_integration:
                enhanced_caps = await self._enhanced_integration.get_integration_status()
                capabilities["enhanced_capabilities"] = enhanced_caps.get("available_solvers", [])
                capabilities["enhanced_solver_count"] = enhanced_caps.get("solver_count", 0)
            
            # Get legacy capabilities
            legacy_solvers = []
            for solver_name, solver_capability in self.solver_registry.solvers.items():
                if self.solver_registry.check_solver_availability(solver_name):
                    legacy_solvers.append(solver_name)
            
            capabilities["legacy_capabilities"] = legacy_solvers
            capabilities["legacy_solver_count"] = len(legacy_solvers)
            
            # Combine capabilities
            all_solvers = set()
            if "enhanced_capabilities" in capabilities:
                all_solvers.update(capabilities["enhanced_capabilities"])
            all_solvers.update(capabilities["legacy_capabilities"])
            
            capabilities["total_capabilities"] = {
                "all_available_solvers": list(all_solvers),
                "total_solver_count": len(all_solvers),
                "enhanced_features": [
                    "intelligent_solver_selection",
                    "multi_solver_swarm_orchestration", 
                    "real_time_progress_monitoring",
                    "advanced_solution_comparison",
                    "performance_analytics_and_learning",
                    "agentcore_memory_integration",
                    "comprehensive_observability"
                ] if self._enhanced_integration_available else [],
                "legacy_features": [
                    "competitive_agent_coordination",
                    "basic_solver_registry",
                    "performance_tracking",
                    "strands_tools_integration"
                ]
            }
            
            return capabilities
            
        except Exception as e:
            self.logger.error(f"Error getting solver capabilities: {e}")
            return {
                "error": str(e),
                "integration_type": "error"
            }
    
    def _validate_solver_result(self, solver_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced solver result validation to prevent false success reports"""
        
        # Extract key information
        success = solver_result.get("success", False)
        best_solution = solver_result.get("best_solution", {})
        objective_value = best_solution.get("objective_value", 0)
        solve_status = best_solution.get("solve_status", "unknown")
        solution = best_solution.get("solution", {})
        solver_info = best_solution.get("solver_info", {})
        
        # CRITICAL FIX: Enhanced validation checks
        validation_issues = []
        
        # Check for zero objective value with optimal status
        if objective_value == 0 and solve_status == "optimal":
            validation_issues.append("ZERO_OBJECTIVE_VALUE")
            self.logger.warning(f"Solver reported optimal status with zero objective value - likely invalid")
        
        # Check for empty or invalid solution
        if not solution or all(v == 0 for v in solution.values()):
            validation_issues.append("EMPTY_SOLUTION")
            self.logger.warning(f"Solver returned empty solution - likely invalid")
        
        # Check for unrealistic solve times
        solve_time = solver_info.get("solve_time", 0)
        if solve_time == 0 and solve_status == "optimal":
            validation_issues.append("ZERO_SOLVE_TIME")
            self.logger.warning(f"Solver reported optimal status with zero solve time - likely invalid")
        
        # Check for missing critical solver information
        if not solver_info.get("solver_name"):
            validation_issues.append("MISSING_SOLVER_INFO")
            self.logger.warning(f"Solver result missing solver name information")
        
        # CRITICAL FIX: Override false success reports
        if validation_issues:
            solver_result["success"] = False
            solver_result["validation_issues"] = validation_issues
            solver_result["corrected_status"] = "VALIDATION_FAILED"
            solver_result["validation_timestamp"] = datetime.now().isoformat()
            
            self.logger.error(f"Solver validation failed with issues: {validation_issues}")
            self.logger.error(f"Original success status: {success}, Corrected status: VALIDATION_FAILED")
        
        return solver_result