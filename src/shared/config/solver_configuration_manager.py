"""
Advanced Solver Configuration Management System
==============================================

Implements comprehensive solver-specific configuration and parameter management
for the multi-solver swarm optimization system with advanced features.

Features:
- Solver-specific parameter validation and optimization
- Configuration profiles for different manufacturing problem types
- Dynamic parameter tuning based on problem characteristics and historical performance
- Machine learning-based configuration optimization
- Advanced manufacturing domain-specific optimizations
- Performance prediction and configuration recommendation

Requirements: 6.1, 6.2, 6.3, 6.4
"""

import logging
import json
import copy
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
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from pathlib import Path
import pickle
import hashlib
from collections import defaultdict, deque
import statistics

from .enhanced_solver_registry import enhanced_solver_registry, SolverCategory

logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """Types of solver parameters"""
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    STRING = "string"
    ENUM = "enum"
    LIST = "list"


@dataclass
class ParameterSpec:
    """Advanced specification for a solver parameter"""
    name: str
    parameter_type: ParameterType
    default_value: Any
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    valid_values: Optional[List[Any]] = None
    description: str = ""
    category: str = "general"  # general, performance, numerical, output
    impact_level: str = "medium"  # low, medium, high
    requires_restart: bool = False
    optimization_hint: str = "none"  # none, minimize, maximize, balance
    correlation_params: List[str] = field(default_factory=list)  # Parameters that correlate with this one
    manufacturing_relevance: float = 1.0  # Relevance to manufacturing problems (0-1)
    
    def validate_value(self, value: Any) -> Tuple[bool, str]:
        """Validate a parameter value with enhanced checks"""
        try:
            if self.parameter_type == ParameterType.INTEGER:
                if not isinstance(value, int):
                    return False, f"Expected integer, got {type(value).__name__}"
                if self.min_value is not None and value < self.min_value:
                    return False, f"Value {value} below minimum {self.min_value}"
                if self.max_value is not None and value > self.max_value:
                    return False, f"Value {value} above maximum {self.max_value}"
            
            elif self.parameter_type == ParameterType.FLOAT:
                if not isinstance(value, (int, float)):
                    return False, f"Expected float, got {type(value).__name__}"
                value = float(value)
                if self.min_value is not None and value < self.min_value:
                    return False, f"Value {value} below minimum {self.min_value}"
                if self.max_value is not None and value > self.max_value:
                    return False, f"Value {value} above maximum {self.max_value}"
            
            elif self.parameter_type == ParameterType.BOOLEAN:
                if not isinstance(value, bool):
                    return False, f"Expected boolean, got {type(value).__name__}"
            
            elif self.parameter_type == ParameterType.STRING:
                if not isinstance(value, str):
                    return False, f"Expected string, got {type(value).__name__}"
            
            elif self.parameter_type == ParameterType.ENUM:
                if self.valid_values and value not in self.valid_values:
                    return False, f"Value {value} not in valid values {self.valid_values}"
            
            elif self.parameter_type == ParameterType.LIST:
                if not isinstance(value, list):
                    return False, f"Expected list, got {type(value).__name__}"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def suggest_optimization_value(self, current_value: Any, performance_trend: str) -> Any:
        """Suggest optimized value based on performance trend"""
        if self.optimization_hint == "none":
            return current_value
        
        try:
            if self.parameter_type == ParameterType.INTEGER:
                if performance_trend == "slow" and self.optimization_hint == "maximize":
                    return min(int(current_value * 1.2), self.max_value or current_value * 2)
                elif performance_trend == "fast" and self.optimization_hint == "minimize":
                    return max(int(current_value * 0.8), self.min_value or 1)
            
            elif self.parameter_type == ParameterType.FLOAT:
                if performance_trend == "slow" and self.optimization_hint == "maximize":
                    return min(current_value * 1.2, self.max_value or current_value * 2)
                elif performance_trend == "fast" and self.optimization_hint == "minimize":
                    return max(current_value * 0.8, self.min_value or 0.1)
            
            elif self.parameter_type == ParameterType.BOOLEAN:
                if performance_trend == "slow":
                    return not current_value  # Try opposite
            
        except Exception:
            pass
        
        return current_value


@dataclass
class AdvancedConfigurationProfile:
    """Advanced configuration profile with machine learning capabilities"""
    profile_name: str
    solver_name: str
    problem_type: str
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    creation_date: datetime
    last_updated: datetime
    usage_count: int = 0
    success_rate: float = 0.0
    average_solve_time: float = 0.0
    
    # Advanced metrics
    performance_variance: float = 0.0
    parameter_sensitivity: Dict[str, float] = field(default_factory=dict)
    problem_size_scaling: Dict[str, float] = field(default_factory=dict)
    manufacturing_domain_score: float = 0.0
    
    # Machine learning features
    feature_importance: Dict[str, float] = field(default_factory=dict)
    performance_prediction_model: Optional[Any] = None
    optimization_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Manufacturing-specific metrics
    production_efficiency_score: float = 0.0
    resource_utilization_score: float = 0.0
    schedule_feasibility_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['creation_date'] = self.creation_date.isoformat()
        result['last_updated'] = self.last_updated.isoformat()
        # Exclude non-serializable ML model
        result.pop('performance_prediction_model', None)
        return result
    
    def calculate_manufacturing_score(self) -> float:
        """Calculate overall manufacturing optimization score"""
        weights = {
            'production_efficiency': 0.4,
            'resource_utilization': 0.3,
            'schedule_feasibility': 0.3
        }
        
        return (
            weights['production_efficiency'] * self.production_efficiency_score +
            weights['resource_utilization'] * self.resource_utilization_score +
            weights['schedule_feasibility'] * self.schedule_feasibility_score
        )
    
    def update_sensitivity_analysis(self, parameter_impacts: Dict[str, float]):
        """Update parameter sensitivity based on performance impacts"""
        for param, impact in parameter_impacts.items():
            if param in self.parameter_sensitivity:
                # Exponential moving average
                self.parameter_sensitivity[param] = (
                    0.7 * self.parameter_sensitivity[param] + 0.3 * impact
                )
            else:
                self.parameter_sensitivity[param] = impact


@dataclass
class ManufacturingProblemCharacteristics:
    """Characteristics specific to manufacturing optimization problems"""
    problem_size: str  # small, medium, large, very_large
    time_horizon: str  # short_term, medium_term, long_term
    resource_constraints: List[str]  # labor, material, equipment, energy
    optimization_objectives: List[str]  # cost, time, quality, efficiency
    production_type: str  # batch, continuous, job_shop, flow_shop
    complexity_factors: Dict[str, float]  # setup_times, changeovers, etc.
    real_time_requirements: bool = False
    uncertainty_level: str = "low"  # low, medium, high
    
    def calculate_complexity_score(self) -> float:
        """Calculate overall problem complexity score"""
        base_score = {
            "small": 1.0, "medium": 2.0, "large": 3.0, "very_large": 4.0
        }.get(self.problem_size, 2.0)
        
        # Adjust for time horizon
        time_multiplier = {
            "short_term": 1.0, "medium_term": 1.5, "long_term": 2.0
        }.get(self.time_horizon, 1.0)
        
        # Adjust for constraints and objectives
        constraint_factor = 1.0 + 0.2 * len(self.resource_constraints)
        objective_factor = 1.0 + 0.1 * len(self.optimization_objectives)
        
        # Adjust for production type complexity
        production_complexity = {
            "continuous": 1.0, "batch": 1.2, "flow_shop": 1.5, "job_shop": 2.0
        }.get(self.production_type, 1.0)
        
        # Adjust for uncertainty
        uncertainty_factor = {
            "low": 1.0, "medium": 1.3, "high": 1.6
        }.get(self.uncertainty_level, 1.0)
        
        return (base_score * time_multiplier * constraint_factor * 
                objective_factor * production_complexity * uncertainty_factor)


# Legacy alias for backward compatibility
ConfigurationProfile = AdvancedConfigurationProfile


class AdvancedSolverConfigurationManager:
    """
    Advanced solver configuration management system with machine learning capabilities
    
    Manages solver-specific parameters, configuration profiles, and
    dynamic parameter tuning for optimal performance with manufacturing-specific optimizations.
    """
    
    def __init__(self):
        self.registry = enhanced_solver_registry
        
        # Parameter specifications for each solver
        self.parameter_specs: Dict[str, Dict[str, ParameterSpec]] = {}
        
        # Configuration profiles
        self.configuration_profiles: Dict[str, AdvancedConfigurationProfile] = {}
        
        # Performance history for configuration optimization
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Manufacturing-specific configuration templates
        self.manufacturing_templates: Dict[str, Dict[str, Any]] = {}
        
        # Parameter optimization models
        self.optimization_models: Dict[str, Any] = {}
        
        # Performance prediction models
        self.prediction_models: Dict[str, Any] = {}
        
        # Configuration cache for fast lookup
        self.config_cache: Dict[str, Tuple[Dict[str, Any], datetime]] = {}
        self.cache_ttl = timedelta(hours=1)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Advanced analytics
        self.parameter_correlations: Dict[str, Dict[str, float]] = {}
        self.performance_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Initialize parameter specifications
        self._initialize_advanced_parameter_specs()
        
        # Initialize manufacturing-specific templates
        self._initialize_manufacturing_templates()
        
        # Initialize default configuration profiles
        self._initialize_advanced_profiles()
        
        logger.info("Advanced solver configuration manager initialized")
    
    def _initialize_advanced_parameter_specs(self):
        """Initialize advanced parameter specifications for all solvers with manufacturing focus"""
        
        # OR-Tools GLOP parameters with manufacturing optimizations
        self.parameter_specs["GLOP"] = {
            "max_time_in_seconds": ParameterSpec(
                name="max_time_in_seconds",
                parameter_type=ParameterType.FLOAT,
                default_value=60.0,
                min_value=0.1,
                max_value=3600.0,
                description="Maximum solve time in seconds",
                category="performance",
                impact_level="high",
                optimization_hint="balance",
                manufacturing_relevance=1.0
            ),
            "use_preprocessing": ParameterSpec(
                name="use_preprocessing",
                parameter_type=ParameterType.BOOLEAN,
                default_value=True,
                description="Enable preprocessing for manufacturing problems",
                category="performance",
                impact_level="medium",
                manufacturing_relevance=0.9
            ),
            "use_dual_simplex": ParameterSpec(
                name="use_dual_simplex",
                parameter_type=ParameterType.BOOLEAN,
                default_value=True,
                description="Use dual simplex algorithm (better for capacity planning)",
                category="performance",
                impact_level="medium",
                manufacturing_relevance=0.8
            ),
            "primal_feasibility_tolerance": ParameterSpec(
                name="primal_feasibility_tolerance",
                parameter_type=ParameterType.FLOAT,
                default_value=1e-7,
                min_value=1e-12,
                max_value=1e-3,
                description="Primal feasibility tolerance (critical for production constraints)",
                category="numerical",
                impact_level="low",
                manufacturing_relevance=0.7
            ),
            "scaling": ParameterSpec(
                name="scaling",
                parameter_type=ParameterType.BOOLEAN,
                default_value=True,
                description="Enable scaling for better numerical stability in manufacturing models",
                category="numerical",
                impact_level="medium",
                manufacturing_relevance=0.8
            )
        }
        
        # OR-Tools SCIP parameters with manufacturing optimizations
        self.parameter_specs["SCIP"] = {
            "limits/time": ParameterSpec(
                name="limits/time",
                parameter_type=ParameterType.FLOAT,
                default_value=300.0,
                min_value=1.0,
                max_value=7200.0,
                description="Time limit in seconds for production scheduling",
                category="performance",
                impact_level="high",
                optimization_hint="balance",
                manufacturing_relevance=1.0
            ),
            "parallel/maxnthreads": ParameterSpec(
                name="parallel/maxnthreads",
                parameter_type=ParameterType.INTEGER,
                default_value=4,
                min_value=1,
                max_value=32,
                description="Maximum number of threads (optimize for manufacturing workloads)",
                category="performance",
                impact_level="high",
                optimization_hint="maximize",
                correlation_params=["limits/time"],
                manufacturing_relevance=0.9
            ),
            "display/verblevel": ParameterSpec(
                name="display/verblevel",
                parameter_type=ParameterType.INTEGER,
                default_value=2,
                min_value=0,
                max_value=5,
                description="Verbosity level for manufacturing problem debugging",
                category="output",
                impact_level="low",
                manufacturing_relevance=0.3
            ),
            "heuristics/emphasis": ParameterSpec(
                name="heuristics/emphasis",
                parameter_type=ParameterType.ENUM,
                default_value="aggressive",
                valid_values=["aggressive", "default", "fast", "off"],
                description="Heuristics emphasis (aggressive for complex scheduling)",
                category="performance",
                impact_level="medium",
                manufacturing_relevance=0.8
            ),
            "separating/emphasis": ParameterSpec(
                name="separating/emphasis",
                parameter_type=ParameterType.ENUM,
                default_value="default",
                valid_values=["aggressive", "default", "fast", "off"],
                description="Separating emphasis for manufacturing constraints",
                category="performance",
                impact_level="medium",
                manufacturing_relevance=0.7
            ),
            "presolving/maxrounds": ParameterSpec(
                name="presolving/maxrounds",
                parameter_type=ParameterType.INTEGER,
                default_value=10,
                min_value=0,
                max_value=100,
                description="Maximum presolving rounds for manufacturing models",
                category="performance",
                impact_level="medium",
                manufacturing_relevance=0.8
            )
        }
        
        # COIN-OR CBC parameters
        self.parameter_specs["CBC"] = {
            "seconds": ParameterSpec(
                name="seconds",
                parameter_type=ParameterType.FLOAT,
                default_value=60.0,
                min_value=1.0,
                max_value=3600.0,
                description="Time limit in seconds",
                category="performance",
                impact_level="high"
            ),
            "threads": ParameterSpec(
                name="threads",
                parameter_type=ParameterType.INTEGER,
                default_value=4,
                min_value=1,
                max_value=16,
                description="Number of threads",
                category="performance",
                impact_level="high"
            ),
            "ratioGap": ParameterSpec(
                name="ratioGap",
                parameter_type=ParameterType.FLOAT,
                default_value=0.01,
                min_value=0.0,
                max_value=1.0,
                description="Relative gap tolerance",
                category="numerical",
                impact_level="medium"
            ),
            "allowableGap": ParameterSpec(
                name="allowableGap",
                parameter_type=ParameterType.FLOAT,
                default_value=1e-6,
                min_value=0.0,
                max_value=1e6,
                description="Absolute gap tolerance",
                category="numerical",
                impact_level="medium"
            )
        }
        
        # HiGHS parameters
        self.parameter_specs["HiGHS_LP"] = self.parameter_specs["HiGHS_MIP"] = {
            "time_limit": ParameterSpec(
                name="time_limit",
                parameter_type=ParameterType.FLOAT,
                default_value=60.0,
                min_value=0.1,
                max_value=3600.0,
                description="Time limit in seconds",
                category="performance",
                impact_level="high"
            ),
            "presolve": ParameterSpec(
                name="presolve",
                parameter_type=ParameterType.ENUM,
                default_value="on",
                valid_values=["on", "off"],
                description="Presolve setting",
                category="performance",
                impact_level="medium"
            ),
            "parallel": ParameterSpec(
                name="parallel",
                parameter_type=ParameterType.ENUM,
                default_value="on",
                valid_values=["on", "off"],
                description="Parallel processing",
                category="performance",
                impact_level="high"
            ),
            "mip_rel_gap": ParameterSpec(
                name="mip_rel_gap",
                parameter_type=ParameterType.FLOAT,
                default_value=0.01,
                min_value=0.0,
                max_value=1.0,
                description="MIP relative gap tolerance",
                category="numerical",
                impact_level="medium"
            )
        }
        
        # OR-Tools CP-SAT parameters
        self.parameter_specs["CP_SAT"] = {
            "max_time_in_seconds": ParameterSpec(
                name="max_time_in_seconds",
                parameter_type=ParameterType.FLOAT,
                default_value=300.0,
                min_value=1.0,
                max_value=7200.0,
                description="Maximum solve time in seconds",
                category="performance",
                impact_level="high"
            ),
            "num_search_workers": ParameterSpec(
                name="num_search_workers",
                parameter_type=ParameterType.INTEGER,
                default_value=4,
                min_value=1,
                max_value=16,
                description="Number of search workers",
                category="performance",
                impact_level="high"
            ),
            "log_search_progress": ParameterSpec(
                name="log_search_progress",
                parameter_type=ParameterType.BOOLEAN,
                default_value=True,
                description="Log search progress",
                category="output",
                impact_level="low"
            ),
            "use_fixed_search": ParameterSpec(
                name="use_fixed_search",
                parameter_type=ParameterType.BOOLEAN,
                default_value=False,
                description="Use fixed search strategy",
                category="performance",
                impact_level="medium"
            ),
            "linearization_level": ParameterSpec(
                name="linearization_level",
                parameter_type=ParameterType.INTEGER,
                default_value=1,
                min_value=0,
                max_value=2,
                description="Linearization level",
                category="performance",
                impact_level="medium"
            )
        }
        
        # Metaheuristic solver parameters
        self.parameter_specs["DEAP"] = {
            "population_size": ParameterSpec(
                name="population_size",
                parameter_type=ParameterType.INTEGER,
                default_value=100,
                min_value=10,
                max_value=1000,
                description="Population size",
                category="performance",
                impact_level="high"
            ),
            "generations": ParameterSpec(
                name="generations",
                parameter_type=ParameterType.INTEGER,
                default_value=100,
                min_value=10,
                max_value=1000,
                description="Number of generations",
                category="performance",
                impact_level="high"
            ),
            "crossover_prob": ParameterSpec(
                name="crossover_prob",
                parameter_type=ParameterType.FLOAT,
                default_value=0.8,
                min_value=0.0,
                max_value=1.0,
                description="Crossover probability",
                category="performance",
                impact_level="medium"
            ),
            "mutation_prob": ParameterSpec(
                name="mutation_prob",
                parameter_type=ParameterType.FLOAT,
                default_value=0.1,
                min_value=0.0,
                max_value=1.0,
                description="Mutation probability",
                category="performance",
                impact_level="medium"
            )
        }
        
        self.parameter_specs["PYSWARMS"] = {
            "n_particles": ParameterSpec(
                name="n_particles",
                parameter_type=ParameterType.INTEGER,
                default_value=50,
                min_value=10,
                max_value=500,
                description="Number of particles",
                category="performance",
                impact_level="high"
            ),
            "iters": ParameterSpec(
                name="iters",
                parameter_type=ParameterType.INTEGER,
                default_value=100,
                min_value=10,
                max_value=1000,
                description="Number of iterations",
                category="performance",
                impact_level="high"
            ),
            "c1": ParameterSpec(
                name="c1",
                parameter_type=ParameterType.FLOAT,
                default_value=0.5,
                min_value=0.0,
                max_value=2.0,
                description="Cognitive parameter",
                category="performance",
                impact_level="medium"
            ),
            "c2": ParameterSpec(
                name="c2",
                parameter_type=ParameterType.FLOAT,
                default_value=0.3,
                min_value=0.0,
                max_value=2.0,
                description="Social parameter",
                category="performance",
                impact_level="medium"
            ),
            "w": ParameterSpec(
                name="w",
                parameter_type=ParameterType.FLOAT,
                default_value=0.9,
                min_value=0.0,
                max_value=1.0,
                description="Inertia weight",
                category="performance",
                impact_level="medium"
            )
        }
        
        self.parameter_specs["OPTUNA"] = {
            "n_trials": ParameterSpec(
                name="n_trials",
                parameter_type=ParameterType.INTEGER,
                default_value=100,
                min_value=10,
                max_value=1000,
                description="Number of trials",
                category="performance",
                impact_level="high"
            ),
            "timeout": ParameterSpec(
                name="timeout",
                parameter_type=ParameterType.FLOAT,
                default_value=300.0,
                min_value=10.0,
                max_value=3600.0,
                description="Timeout in seconds",
                category="performance",
                impact_level="high"
            ),
            "sampler": ParameterSpec(
                name="sampler",
                parameter_type=ParameterType.ENUM,
                default_value="TPE",
                valid_values=["TPE", "Random", "CmaEs", "Grid"],
                description="Sampling algorithm",
                category="performance",
                impact_level="medium"
            )
        }
    
    def _initialize_manufacturing_templates(self):
        """Initialize manufacturing-specific configuration templates"""
        
        # Production Scheduling Templates
        self.manufacturing_templates["production_scheduling"] = {
            "small_batch": {
                "description": "Small batch production scheduling (< 100 jobs)",
                "recommended_solvers": ["CP_SAT", "SCIP"],
                "time_limits": {"CP_SAT": 60, "SCIP": 120},
                "parallel_settings": {"threads": 2},
                "heuristic_emphasis": "fast"
            },
            "large_batch": {
                "description": "Large batch production scheduling (> 1000 jobs)",
                "recommended_solvers": ["SCIP", "CBC"],
                "time_limits": {"SCIP": 600, "CBC": 900},
                "parallel_settings": {"threads": 8},
                "heuristic_emphasis": "aggressive"
            },
            "job_shop": {
                "description": "Job shop scheduling with complex routing",
                "recommended_solvers": ["CP_SAT", "SCIP"],
                "time_limits": {"CP_SAT": 300, "SCIP": 600},
                "parallel_settings": {"threads": 4},
                "constraint_emphasis": "aggressive"
            }
        }
        
        # Capacity Planning Templates
        self.manufacturing_templates["capacity_planning"] = {
            "short_term": {
                "description": "Short-term capacity planning (1-4 weeks)",
                "recommended_solvers": ["GLOP", "HiGHS_LP"],
                "time_limits": {"GLOP": 30, "HiGHS_LP": 45},
                "numerical_precision": "high",
                "preprocessing": True
            },
            "medium_term": {
                "description": "Medium-term capacity planning (1-6 months)",
                "recommended_solvers": ["HiGHS_MIP", "SCIP"],
                "time_limits": {"HiGHS_MIP": 120, "SCIP": 180},
                "gap_tolerance": 0.02,
                "parallel_settings": {"threads": 4}
            },
            "long_term": {
                "description": "Long-term capacity planning (6+ months)",
                "recommended_solvers": ["SCIP", "CBC"],
                "time_limits": {"SCIP": 600, "CBC": 900},
                "gap_tolerance": 0.05,
                "heuristic_emphasis": "aggressive"
            }
        }
        
        # Resource Allocation Templates
        self.manufacturing_templates["resource_allocation"] = {
            "workforce": {
                "description": "Workforce allocation and shift planning",
                "recommended_solvers": ["CBC", "SCIP"],
                "time_limits": {"CBC": 180, "SCIP": 240},
                "integer_focus": True,
                "constraint_emphasis": "default"
            },
            "equipment": {
                "description": "Equipment allocation and maintenance scheduling",
                "recommended_solvers": ["CP_SAT", "SCIP"],
                "time_limits": {"CP_SAT": 300, "SCIP": 450},
                "parallel_settings": {"threads": 6},
                "maintenance_constraints": True
            },
            "material": {
                "description": "Material allocation and inventory optimization",
                "recommended_solvers": ["HiGHS_MIP", "CBC"],
                "time_limits": {"HiGHS_MIP": 90, "CBC": 150},
                "inventory_constraints": True,
                "demand_uncertainty": True
            }
        }
        
        # Supply Chain Templates
        self.manufacturing_templates["supply_chain"] = {
            "distribution": {
                "description": "Distribution network optimization",
                "recommended_solvers": ["SCIP", "CBC"],
                "time_limits": {"SCIP": 300, "CBC": 450},
                "network_flow": True,
                "transportation_costs": True
            },
            "procurement": {
                "description": "Procurement and supplier selection",
                "recommended_solvers": ["HiGHS_MIP", "SCIP"],
                "time_limits": {"HiGHS_MIP": 120, "SCIP": 180},
                "multi_objective": True,
                "risk_constraints": True
            }
        }
    
    def _initialize_advanced_profiles(self):
        """Initialize advanced configuration profiles for manufacturing problems"""
        
        now = datetime.now()
        
        # Production Scheduling profiles
        self.configuration_profiles["production_scheduling_cp_sat"] = AdvancedConfigurationProfile(
            profile_name="production_scheduling_cp_sat",
            solver_name="CP_SAT",
            problem_type="production_scheduling",
            parameters={
                "max_time_in_seconds": 300,
                "num_search_workers": 4,
                "log_search_progress": True,
                "use_fixed_search": False,
                "linearization_level": 1
            },
            performance_metrics={
                "expected_solve_time": 120.0,
                "success_rate": 0.95,
                "solution_quality": 0.9
            },
            creation_date=now,
            last_updated=now,
            manufacturing_domain_score=0.95,
            production_efficiency_score=0.9,
            resource_utilization_score=0.85,
            schedule_feasibility_score=0.92
        )
        
        self.configuration_profiles["production_scheduling_scip"] = AdvancedConfigurationProfile(
            profile_name="production_scheduling_scip",
            solver_name="SCIP",
            problem_type="production_scheduling",
            parameters={
                "limits/time": 300,
                "parallel/maxnthreads": 4,
                "display/verblevel": 2,
                "heuristics/emphasis": "aggressive",
                "separating/emphasis": "default"
            },
            performance_metrics={
                "expected_solve_time": 180.0,
                "success_rate": 0.85,
                "solution_quality": 0.85
            },
            creation_date=now,
            last_updated=now,
            manufacturing_domain_score=0.88,
            production_efficiency_score=0.82,
            resource_utilization_score=0.80,
            schedule_feasibility_score=0.85
        )
        
        # Capacity Planning profiles
        self.configuration_profiles["capacity_planning_highs"] = ConfigurationProfile(
            profile_name="capacity_planning_highs",
            solver_name="HiGHS_LP",
            problem_type="capacity_planning",
            parameters={
                "time_limit": 60,
                "presolve": "on",
                "parallel": "on"
            },
            performance_metrics={
                "expected_solve_time": 30.0,
                "success_rate": 0.98,
                "solution_quality": 0.95
            },
            creation_date=now,
            last_updated=now
        )
        
        self.configuration_profiles["capacity_planning_glop"] = ConfigurationProfile(
            profile_name="capacity_planning_glop",
            solver_name="GLOP",
            problem_type="capacity_planning",
            parameters={
                "max_time_in_seconds": 60,
                "use_preprocessing": True,
                "use_dual_simplex": True,
                "primal_feasibility_tolerance": 1e-7
            },
            performance_metrics={
                "expected_solve_time": 25.0,
                "success_rate": 0.96,
                "solution_quality": 0.92
            },
            creation_date=now,
            last_updated=now
        )
        
        # Resource Allocation profiles
        self.configuration_profiles["resource_allocation_cbc"] = ConfigurationProfile(
            profile_name="resource_allocation_cbc",
            solver_name="CBC",
            problem_type="resource_allocation",
            parameters={
                "seconds": 120,
                "threads": 4,
                "ratioGap": 0.01,
                "allowableGap": 1e-6
            },
            performance_metrics={
                "expected_solve_time": 60.0,
                "success_rate": 0.88,
                "solution_quality": 0.87
            },
            creation_date=now,
            last_updated=now
        )
    
    def get_solver_parameters(self, solver_name: str) -> Dict[str, ParameterSpec]:
        """Get parameter specifications for a solver"""
        return self.parameter_specs.get(solver_name, {})
    
    def validate_configuration(self, solver_name: str, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a configuration for a solver
        
        Args:
            solver_name: Name of the solver
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if solver_name not in self.parameter_specs:
            errors.append(f"No parameter specifications found for solver {solver_name}")
            return False, errors
        
        param_specs = self.parameter_specs[solver_name]
        
        # Check each parameter in the configuration
        for param_name, param_value in config.items():
            if param_name not in param_specs:
                errors.append(f"Unknown parameter: {param_name}")
                continue
            
            param_spec = param_specs[param_name]
            is_valid, error_msg = param_spec.validate_value(param_value)
            
            if not is_valid:
                errors.append(f"Parameter {param_name}: {error_msg}")
        
        return len(errors) == 0, errors
    
    def get_configuration_profile(self, solver_name: str, problem_type: str) -> Optional[ConfigurationProfile]:
        """
        Get configuration profile for a solver and problem type
        
        Args:
            solver_name: Name of the solver
            problem_type: Type of optimization problem
            
        Returns:
            Configuration profile if found, None otherwise
        """
        profile_key = f"{problem_type}_{solver_name.lower()}"
        
        return self.configuration_profiles.get(profile_key)
    
    def create_configuration_profile(self, profile_name: str, solver_name: str, 
                                   problem_type: str, parameters: Dict[str, Any]) -> ConfigurationProfile:
        """
        Create a new configuration profile
        
        Args:
            profile_name: Name of the profile
            solver_name: Name of the solver
            problem_type: Type of optimization problem
            parameters: Configuration parameters
            
        Returns:
            Created configuration profile
        """
        # Validate configuration
        is_valid, errors = self.validate_configuration(solver_name, parameters)
        if not is_valid:
            raise ValueError(f"Invalid configuration: {'; '.join(errors)}")
        
        now = datetime.now()
        
        profile = ConfigurationProfile(
            profile_name=profile_name,
            solver_name=solver_name,
            problem_type=problem_type,
            parameters=copy.deepcopy(parameters),
            performance_metrics={},
            creation_date=now,
            last_updated=now
        )
        
        with self._lock:
            self.configuration_profiles[profile_name] = profile
        
        logger.info(f"Created configuration profile: {profile_name}")
        return profile
    
    def update_configuration_profile(self, profile_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Update an existing configuration profile
        
        Args:
            profile_name: Name of the profile to update
            parameters: New configuration parameters
            
        Returns:
            True if updated successfully, False otherwise
        """
        with self._lock:
            if profile_name not in self.configuration_profiles:
                logger.warning(f"Configuration profile not found: {profile_name}")
                return False
            
            profile = self.configuration_profiles[profile_name]
            
            # Validate new configuration
            is_valid, errors = self.validate_configuration(profile.solver_name, parameters)
            if not is_valid:
                logger.error(f"Invalid configuration update for {profile_name}: {'; '.join(errors)}")
                return False
            
            # Update profile
            profile.parameters = copy.deepcopy(parameters)
            profile.last_updated = datetime.now()
            
            logger.info(f"Updated configuration profile: {profile_name}")
            return True
    
    def optimize_configuration(self, solver_name: str, problem_type: str, 
                             problem_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize configuration based on problem characteristics and historical performance
        
        Args:
            solver_name: Name of the solver
            problem_type: Type of optimization problem
            problem_characteristics: Characteristics of the specific problem
            
        Returns:
            Optimized configuration dictionary
        """
        # Start with default configuration
        base_config = self._get_default_configuration(solver_name)
        
        # Get problem-specific profile if available
        profile = self.get_configuration_profile(solver_name, problem_type)
        if profile:
            base_config.update(profile.parameters)
        
        # Apply problem-specific optimizations
        optimized_config = self._apply_problem_specific_optimizations(
            solver_name, problem_type, problem_characteristics, base_config
        )
        
        # Apply performance-based optimizations
        optimized_config = self._apply_performance_optimizations(
            solver_name, problem_type, optimized_config
        )
        
        return optimized_config
    
    def _get_default_configuration(self, solver_name: str) -> Dict[str, Any]:
        """Get default configuration for a solver"""
        
        if solver_name not in self.parameter_specs:
            return {}
        
        param_specs = self.parameter_specs[solver_name]
        default_config = {}
        
        for param_name, param_spec in param_specs.items():
            default_config[param_name] = param_spec.default_value
        
        return default_config
    
    def _apply_problem_specific_optimizations(self, solver_name: str, problem_type: str,
                                            problem_characteristics: Dict[str, Any],
                                            base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations based on problem characteristics"""
        
        config = copy.deepcopy(base_config)
        
        # Get problem size
        num_variables = problem_characteristics.get("num_variables", 0)
        num_constraints = problem_characteristics.get("num_constraints", 0)
        problem_complexity = problem_characteristics.get("complexity", "medium")
        
        # Adjust time limits based on problem size
        if solver_name in ["GLOP", "HiGHS_LP", "HiGHS_MIP"]:
            if num_variables > 10000:
                if "max_time_in_seconds" in config:
                    config["max_time_in_seconds"] = min(config["max_time_in_seconds"] * 2, 300)
                elif "time_limit" in config:
                    config["time_limit"] = min(config["time_limit"] * 2, 300)
        
        elif solver_name in ["SCIP", "CBC"]:
            if num_variables > 1000:
                if "limits/time" in config:
                    config["limits/time"] = min(config["limits/time"] * 1.5, 600)
                elif "seconds" in config:
                    config["seconds"] = min(config["seconds"] * 1.5, 600)
        
        elif solver_name == "CP_SAT":
            if problem_complexity == "high":
                config["max_time_in_seconds"] = min(config.get("max_time_in_seconds", 300) * 2, 900)
                config["num_search_workers"] = min(config.get("num_search_workers", 4) * 2, 8)
        
        # Adjust metaheuristic parameters
        elif solver_name == "DEAP":
            if num_variables > 100:
                config["population_size"] = min(config.get("population_size", 100) * 2, 500)
                config["generations"] = min(config.get("generations", 100) * 1.5, 300)
        
        elif solver_name == "PYSWARMS":
            if num_variables > 50:
                config["n_particles"] = min(config.get("n_particles", 50) * 2, 200)
                config["iters"] = min(config.get("iters", 100) * 1.5, 300)
        
        return config
    
    def _apply_performance_optimizations(self, solver_name: str, problem_type: str,
                                       base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations based on historical performance"""
        
        config = copy.deepcopy(base_config)
        
        # Get performance history for this solver and problem type
        history_key = f"{solver_name}_{problem_type}"
        
        if history_key in self.performance_history:
            history = self.performance_history[history_key]
            
            if len(history) >= 5:  # Need sufficient data
                # Analyze performance trends
                recent_history = history[-10:]  # Last 10 runs
                
                avg_solve_time = sum(run.get("solve_time", 0) for run in recent_history) / len(recent_history)
                success_rate = sum(1 for run in recent_history if run.get("success", False)) / len(recent_history)
                
                # Adjust based on performance
                if success_rate < 0.8:  # Low success rate
                    # Increase time limits
                    if "max_time_in_seconds" in config:
                        config["max_time_in_seconds"] *= 1.5
                    elif "time_limit" in config:
                        config["time_limit"] *= 1.5
                    elif "limits/time" in config:
                        config["limits/time"] *= 1.5
                
                elif avg_solve_time < 10.0 and success_rate > 0.95:  # Very fast and reliable
                    # Can reduce time limits to speed up
                    if "max_time_in_seconds" in config:
                        config["max_time_in_seconds"] *= 0.8
                    elif "time_limit" in config:
                        config["time_limit"] *= 0.8
        
        return config
    
    def record_performance(self, solver_name: str, problem_type: str, 
                          configuration: Dict[str, Any], performance_data: Dict[str, Any]):
        """
        Record performance data for configuration optimization
        
        Args:
            solver_name: Name of the solver
            problem_type: Type of optimization problem
            configuration: Configuration used
            performance_data: Performance metrics
        """
        history_key = f"{solver_name}_{problem_type}"
        
        performance_record = {
            "timestamp": datetime.now().isoformat(),
            "solver_name": solver_name,
            "problem_type": problem_type,
            "configuration": copy.deepcopy(configuration),
            "solve_time": performance_data.get("solve_time", 0.0),
            "success": performance_data.get("success", False),
            "objective_value": performance_data.get("objective_value"),
            "solution_quality": performance_data.get("solution_quality", 0.0),
            "memory_usage": performance_data.get("memory_usage", 0.0)
        }
        
        with self._lock:
            if history_key not in self.performance_history:
                self.performance_history[history_key] = []
            
            self.performance_history[history_key].append(performance_record)
            
            # Keep only recent history (last 100 records)
            if len(self.performance_history[history_key]) > 100:
                self.performance_history[history_key] = self.performance_history[history_key][-100:]
        
        # Update configuration profile if it exists
        profile = self.get_configuration_profile(solver_name, problem_type)
        if profile:
            with self._lock:
                profile.usage_count += 1
                
                # Update running averages
                if performance_data.get("success", False):
                    old_success_rate = profile.success_rate
                    old_avg_time = profile.average_solve_time
                    
                    profile.success_rate = (old_success_rate * (profile.usage_count - 1) + 1.0) / profile.usage_count
                    profile.average_solve_time = (old_avg_time * (profile.usage_count - 1) + 
                                                performance_data.get("solve_time", 0.0)) / profile.usage_count
                else:
                    profile.success_rate = (profile.success_rate * (profile.usage_count - 1)) / profile.usage_count
    
    def get_configuration_recommendations(self, solver_name: str, problem_type: str) -> List[Dict[str, Any]]:
        """
        Get configuration recommendations based on performance analysis
        
        Args:
            solver_name: Name of the solver
            problem_type: Type of optimization problem
            
        Returns:
            List of configuration recommendations
        """
        recommendations = []
        
        # Get current profile
        profile = self.get_configuration_profile(solver_name, problem_type)
        
        if profile and profile.usage_count > 10:
            # Analyze performance
            if profile.success_rate < 0.8:
                recommendations.append({
                    "type": "performance",
                    "priority": "high",
                    "description": f"Low success rate ({profile.success_rate:.2f}). Consider increasing time limits or using alternative solver.",
                    "suggested_changes": {
                        "increase_time_limit": True,
                        "alternative_solvers": self._get_alternative_solvers(solver_name, problem_type)
                    }
                })
            
            if profile.average_solve_time > 300:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "description": f"High average solve time ({profile.average_solve_time:.1f}s). Consider parameter tuning.",
                    "suggested_changes": {
                        "enable_parallel": True,
                        "adjust_tolerances": True
                    }
                })
        
        # Check for parameter-specific recommendations
        if solver_name in self.parameter_specs:
            param_specs = self.parameter_specs[solver_name]
            current_config = profile.parameters if profile else self._get_default_configuration(solver_name)
            
            for param_name, param_spec in param_specs.items():
                if param_spec.impact_level == "high" and param_name not in current_config:
                    recommendations.append({
                        "type": "configuration",
                        "priority": "medium",
                        "description": f"Consider setting high-impact parameter: {param_name}",
                        "suggested_changes": {
                            param_name: param_spec.default_value
                        }
                    })
        
        return recommendations
    
    def _get_alternative_solvers(self, solver_name: str, problem_type: str) -> List[str]:
        """Get alternative solvers for the same problem type"""
        
        alternatives = []
        
        if solver_name in self.registry.solvers:
            current_category = self.registry.solvers[solver_name].category
            
            for alt_solver_name, alt_capability in self.registry.solvers.items():
                if (alt_solver_name != solver_name and 
                    alt_capability.category == current_category and
                    problem_type in alt_capability.problem_types):
                    alternatives.append(alt_solver_name)
        
        return alternatives
    
    def optimize_configuration_ml(self, solver_name: str, problem_type: str,
                                 problem_characteristics: ManufacturingProblemCharacteristics) -> Dict[str, Any]:
        """
        Use machine learning to optimize configuration based on problem characteristics
        
        Args:
            solver_name: Name of the solver
            problem_type: Type of optimization problem
            problem_characteristics: Manufacturing-specific problem characteristics
            
        Returns:
            ML-optimized configuration dictionary
        """
        # Start with template-based configuration
        base_config = self._get_manufacturing_template_config(solver_name, problem_type, problem_characteristics)
        
        # Apply ML-based optimizations if model exists
        model_key = f"{solver_name}_{problem_type}"
        if model_key in self.optimization_models:
            try:
                # Prepare features for ML model
                features = self._extract_problem_features(problem_characteristics)
                
                # Predict optimal parameters
                model = self.optimization_models[model_key]
                predicted_params = model.predict([features])[0]
                
                # Apply predicted parameters
                base_config = self._apply_ml_predictions(base_config, predicted_params, solver_name)
                
                logger.info(f"Applied ML optimization for {solver_name} on {problem_type}")
                
            except Exception as e:
                logger.warning(f"ML optimization failed for {model_key}: {e}")
        
        # Apply manufacturing-specific heuristics
        optimized_config = self._apply_manufacturing_heuristics(
            base_config, solver_name, problem_type, problem_characteristics
        )
        
        return optimized_config
    
    def _get_manufacturing_template_config(self, solver_name: str, problem_type: str,
                                         characteristics: ManufacturingProblemCharacteristics) -> Dict[str, Any]:
        """Get configuration from manufacturing templates"""
        
        base_config = self._get_default_configuration(solver_name)
        
        # Apply template if available
        if problem_type in self.manufacturing_templates:
            templates = self.manufacturing_templates[problem_type]
            
            # Select appropriate template based on characteristics
            template_key = self._select_template(characteristics, templates)
            
            if template_key and template_key in templates:
                template = templates[template_key]
                
                # Apply template settings
                if solver_name in template.get("recommended_solvers", []):
                    if "time_limits" in template and solver_name in template["time_limits"]:
                        time_param = self._get_time_parameter_name(solver_name)
                        if time_param:
                            base_config[time_param] = template["time_limits"][solver_name]
                    
                    if "parallel_settings" in template:
                        parallel_param = self._get_parallel_parameter_name(solver_name)
                        if parallel_param and "threads" in template["parallel_settings"]:
                            base_config[parallel_param] = template["parallel_settings"]["threads"]
        
        return base_config
    
    def _select_template(self, characteristics: ManufacturingProblemCharacteristics,
                        templates: Dict[str, Any]) -> Optional[str]:
        """Select appropriate template based on problem characteristics"""
        
        complexity_score = characteristics.calculate_complexity_score()
        
        # Simple heuristic for template selection
        if complexity_score < 2.0:
            return next((k for k in templates.keys() if "small" in k), None)
        elif complexity_score > 4.0:
            return next((k for k in templates.keys() if "large" in k), None)
        else:
            return next((k for k in templates.keys() if "medium" in k or "default" in k), None)
    
    def _extract_problem_features(self, characteristics: ManufacturingProblemCharacteristics) -> List[float]:
        """Extract numerical features for ML models"""
        
        features = []
        
        # Size features
        size_mapping = {"small": 1, "medium": 2, "large": 3, "very_large": 4}
        features.append(size_mapping.get(characteristics.problem_size, 2))
        
        # Time horizon features
        horizon_mapping = {"short_term": 1, "medium_term": 2, "long_term": 3}
        features.append(horizon_mapping.get(characteristics.time_horizon, 2))
        
        # Constraint and objective counts
        features.append(len(characteristics.resource_constraints))
        features.append(len(characteristics.optimization_objectives))
        
        # Production type features
        production_mapping = {"continuous": 1, "batch": 2, "flow_shop": 3, "job_shop": 4}
        features.append(production_mapping.get(characteristics.production_type, 2))
        
        # Complexity factors
        features.extend(list(characteristics.complexity_factors.values())[:5])  # Take first 5
        
        # Boolean features
        features.append(1.0 if characteristics.real_time_requirements else 0.0)
        
        # Uncertainty level
        uncertainty_mapping = {"low": 1, "medium": 2, "high": 3}
        features.append(uncertainty_mapping.get(characteristics.uncertainty_level, 1))
        
        # Pad or truncate to fixed size
        target_size = 15
        if len(features) < target_size:
            features.extend([0.0] * (target_size - len(features)))
        else:
            features = features[:target_size]
        
        return features
    
    def _apply_ml_predictions(self, base_config: Dict[str, Any], predictions: List[float],
                            solver_name: str) -> Dict[str, Any]:
        """Apply ML model predictions to configuration"""
        
        config = copy.deepcopy(base_config)
        
        # Map predictions to parameters (simplified example)
        if solver_name in self.parameter_specs:
            param_names = list(self.parameter_specs[solver_name].keys())
            
            for i, pred_value in enumerate(predictions[:len(param_names)]):
                param_name = param_names[i]
                param_spec = self.parameter_specs[solver_name][param_name]
                
                # Convert prediction to valid parameter value
                if param_spec.parameter_type == ParameterType.FLOAT:
                    if param_spec.min_value is not None and param_spec.max_value is not None:
                        # Scale prediction to parameter range
                        scaled_value = (param_spec.min_value + 
                                      (param_spec.max_value - param_spec.min_value) * 
                                      max(0, min(1, pred_value)))
                        config[param_name] = scaled_value
                
                elif param_spec.parameter_type == ParameterType.INTEGER:
                    if param_spec.min_value is not None and param_spec.max_value is not None:
                        scaled_value = int(param_spec.min_value + 
                                         (param_spec.max_value - param_spec.min_value) * 
                                         max(0, min(1, pred_value)))
                        config[param_name] = scaled_value
        
        return config
    
    def _apply_manufacturing_heuristics(self, base_config: Dict[str, Any], solver_name: str,
                                       problem_type: str, 
                                       characteristics: ManufacturingProblemCharacteristics) -> Dict[str, Any]:
        """Apply manufacturing-specific optimization heuristics"""
        
        config = copy.deepcopy(base_config)
        
        # Real-time requirements adjustments
        if characteristics.real_time_requirements:
            time_param = self._get_time_parameter_name(solver_name)
            if time_param and time_param in config:
                config[time_param] = min(config[time_param], 30.0)  # Max 30 seconds for real-time
        
        # High uncertainty adjustments
        if characteristics.uncertainty_level == "high":
            # Use more robust settings
            if solver_name == "SCIP":
                config["heuristics/emphasis"] = "aggressive"
                config["separating/emphasis"] = "aggressive"
            elif solver_name == "CBC":
                config["ratioGap"] = max(config.get("ratioGap", 0.01), 0.02)
        
        # Production type specific adjustments
        if characteristics.production_type == "job_shop":
            # Job shop problems benefit from constraint programming
            if solver_name == "CP_SAT":
                config["linearization_level"] = 2
                config["use_fixed_search"] = True
        
        elif characteristics.production_type == "continuous":
            # Continuous production benefits from linear programming
            if solver_name in ["GLOP", "HiGHS_LP"]:
                config["use_preprocessing"] = True
                if "scaling" in config:
                    config["scaling"] = True
        
        return config
    
    def _get_time_parameter_name(self, solver_name: str) -> Optional[str]:
        """Get the time limit parameter name for a solver"""
        time_params = {
            "GLOP": "max_time_in_seconds",
            "SCIP": "limits/time",
            "CBC": "seconds",
            "HiGHS_LP": "time_limit",
            "HiGHS_MIP": "time_limit",
            "CP_SAT": "max_time_in_seconds"
        }
        return time_params.get(solver_name)
    
    def _get_parallel_parameter_name(self, solver_name: str) -> Optional[str]:
        """Get the parallel processing parameter name for a solver"""
        parallel_params = {
            "SCIP": "parallel/maxnthreads",
            "CBC": "threads",
            "CP_SAT": "num_search_workers"
        }
        return parallel_params.get(solver_name)
    
    def train_optimization_model(self, solver_name: str, problem_type: str):
        """Train ML model for parameter optimization"""
        
        history_key = f"{solver_name}_{problem_type}"
        
        if history_key not in self.performance_history or len(self.performance_history[history_key]) < 50:
            logger.warning(f"Insufficient data to train model for {history_key}")
            return
        
        try:
            # Prepare training data
            X, y = self._prepare_training_data(history_key)
            
            if len(X) < 10:
                logger.warning(f"Insufficient training samples for {history_key}")
                return
            
            # Simple linear regression model (can be replaced with more sophisticated models)
            from sklearn.linear_model import LinearRegression
            from sklearn.preprocessing import StandardScaler
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model = LinearRegression()
            model.fit(X_scaled, y)
            
            # Store model and scaler
            self.optimization_models[history_key] = {
                'model': model,
                'scaler': scaler,
                'trained_at': datetime.now()
            }
            
            logger.info(f"Trained optimization model for {history_key}")
            
        except Exception as e:
            logger.error(f"Failed to train model for {history_key}: {e}")
    
    def _prepare_training_data(self, history_key: str) -> Tuple[List[List[float]], List[float]]:
        """Prepare training data from performance history"""
        
        X = []  # Features (problem characteristics + configuration)
        y = []  # Target (performance score)
        
        for record in self.performance_history[history_key]:
            try:
                # Extract features (simplified)
                features = []
                
                # Configuration features
                config = record.get('configuration', {})
                for param_name in ['max_time_in_seconds', 'limits/time', 'seconds', 'time_limit']:
                    features.append(config.get(param_name, 0.0))
                
                # Performance target (inverse of solve time, higher is better)
                solve_time = record.get('solve_time', float('inf'))
                success = record.get('success', False)
                
                if success and solve_time > 0:
                    performance_score = 1.0 / solve_time  # Simple performance metric
                    
                    X.append(features)
                    y.append(performance_score)
                    
            except Exception as e:
                logger.debug(f"Skipping record due to error: {e}")
                continue
        
        return X, y
    
    def get_manufacturing_recommendations(self, solver_name: str, problem_type: str,
                                        characteristics: ManufacturingProblemCharacteristics) -> Dict[str, Any]:
        """Get manufacturing-specific configuration recommendations"""
        
        recommendations = {
            "solver_recommendations": [],
            "parameter_recommendations": [],
            "template_suggestions": [],
            "performance_predictions": {}
        }
        
        # Solver recommendations
        if problem_type in self.manufacturing_templates:
            templates = self.manufacturing_templates[problem_type]
            template_key = self._select_template(characteristics, templates)
            
            if template_key and template_key in templates:
                template = templates[template_key]
                recommendations["solver_recommendations"] = template.get("recommended_solvers", [])
                recommendations["template_suggestions"].append({
                    "template": template_key,
                    "description": template.get("description", ""),
                    "rationale": f"Selected based on problem complexity score: {characteristics.calculate_complexity_score():.2f}"
                })
        
        # Parameter recommendations
        if solver_name in self.parameter_specs:
            for param_name, param_spec in self.parameter_specs[solver_name].items():
                if param_spec.manufacturing_relevance > 0.8:
                    recommendations["parameter_recommendations"].append({
                        "parameter": param_name,
                        "importance": param_spec.manufacturing_relevance,
                        "description": param_spec.description,
                        "category": param_spec.category
                    })
        
        # Performance predictions
        try:
            optimized_config = self.optimize_configuration_ml(solver_name, problem_type, characteristics)
            estimated_time = self._predict_solve_time(solver_name, problem_type, optimized_config, characteristics)
            
            recommendations["performance_predictions"] = {
                "estimated_solve_time": estimated_time,
                "confidence": "medium",  # Could be improved with actual confidence intervals
                "configuration_used": optimized_config
            }
            
        except Exception as e:
            logger.warning(f"Performance prediction failed: {e}")
        
        return recommendations
    
    def _predict_solve_time(self, solver_name: str, problem_type: str, 
                          config: Dict[str, Any], 
                          characteristics: ManufacturingProblemCharacteristics) -> float:
        """Predict solve time based on configuration and problem characteristics"""
        
        # Simple heuristic-based prediction (can be improved with ML)
        base_time = 60.0  # Base time in seconds
        
        # Adjust for problem complexity
        complexity_score = characteristics.calculate_complexity_score()
        time_multiplier = complexity_score / 2.0
        
        # Adjust for solver-specific factors
        solver_factors = {
            "GLOP": 0.5,      # Fast for LP
            "HiGHS_LP": 0.6,  # Fast for LP
            "HiGHS_MIP": 1.2, # Slower for MIP
            "SCIP": 1.5,      # Slower but more capable
            "CBC": 1.3,       # Medium speed
            "CP_SAT": 1.0     # Balanced
        }
        
        solver_factor = solver_factors.get(solver_name, 1.0)
        
        # Adjust for time limit in configuration
        time_param = self._get_time_parameter_name(solver_name)
        if time_param and time_param in config:
            config_time_limit = config[time_param]
            # Predicted time is usually less than time limit
            predicted_time = min(base_time * time_multiplier * solver_factor, config_time_limit * 0.7)
        else:
            predicted_time = base_time * time_multiplier * solver_factor
        
        return max(1.0, predicted_time)  # At least 1 second
    
    def export_configurations(self) -> Dict[str, Any]:
        """Export all configuration profiles and performance data"""
        
        with self._lock:
            return {
                "configuration_profiles": {
                    name: profile.to_dict() 
                    for name, profile in self.configuration_profiles.items()
                },
                "performance_history": {
                    key: list(history) for key, history in self.performance_history.items()
                },
                "parameter_specifications": {
                    solver_name: {
                        param_name: asdict(param_spec)
                        for param_name, param_spec in params.items()
                    }
                    for solver_name, params in self.parameter_specs.items()
                },
                "manufacturing_templates": self.manufacturing_templates,
                "parameter_correlations": self.parameter_correlations,
                "export_timestamp": datetime.now().isoformat()
            }
    
    def import_configurations(self, data: Dict[str, Any]) -> bool:
        """Import configuration profiles and performance data"""
        
        try:
            with self._lock:
                # Import configuration profiles
                if "configuration_profiles" in data:
                    for name, profile_data in data["configuration_profiles"].items():
                        # Convert datetime strings back to datetime objects
                        profile_data["creation_date"] = datetime.fromisoformat(profile_data["creation_date"])
                        profile_data["last_updated"] = datetime.fromisoformat(profile_data["last_updated"])
                        
                        # Create profile object
                        profile = AdvancedConfigurationProfile(**profile_data)
                        self.configuration_profiles[name] = profile
                
                # Import performance history
                if "performance_history" in data:
                    for key, history in data["performance_history"].items():
                        self.performance_history[key] = deque(history, maxlen=1000)
                
                # Import parameter correlations
                if "parameter_correlations" in data:
                    self.parameter_correlations.update(data["parameter_correlations"])
                
                logger.info("Successfully imported configuration data")
                return True
                
        except Exception as e:
            logger.error(f"Failed to import configuration data: {e}")
            return False
    
    def get_configuration_cache_key(self, solver_name: str, problem_type: str,
                                   characteristics_hash: str) -> str:
        """Generate cache key for configuration lookup"""
        return f"{solver_name}_{problem_type}_{characteristics_hash}"
    
    def get_cached_configuration(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached configuration if still valid"""
        
        if cache_key in self.config_cache:
            config, timestamp = self.config_cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return config
            else:
                # Remove expired cache entry
                del self.config_cache[cache_key]
        
        return None
    
    def cache_configuration(self, cache_key: str, config: Dict[str, Any]):
        """Cache configuration for future use"""
        
        self.config_cache[cache_key] = (copy.deepcopy(config), datetime.now())
        
        # Limit cache size
        if len(self.config_cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(self.config_cache.keys(), 
                               key=lambda k: self.config_cache[k][1])[:100]
            for key in oldest_keys:
                del self.config_cache[key]


# Legacy class alias for backward compatibility
SolverConfigurationManager = AdvancedSolverConfigurationManager

# Global configuration manager instance
solver_configuration_manager = AdvancedSolverConfigurationManager()


def get_solver_configuration_manager() -> AdvancedSolverConfigurationManager:
    """Get the global advanced solver configuration manager instance"""
    return solver_configuration_manager