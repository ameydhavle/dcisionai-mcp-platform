"""
Intelligent Solver Selection Engine
==================================

Implements intelligent solver selection based on problem analysis, solver scoring,
and decision trees for manufacturing optimization problems.

Features:
- Problem analysis system that extracts characteristics (size, type, complexity)
- Solver scoring algorithm that ranks solvers based on problem fit
- Decision tree for different manufacturing problem types
- Fallback solver selection logic for unavailable solvers
- Performance-based learning and adaptation

Requirements: 2.1, 2.2, 2.3, 2.4
"""

import logging
import math
import time
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json
import threading
from collections import defaultdict

from .enhanced_solver_registry import EnhancedSolverRegistry, SolverCapability, SolverCategory, SolverStatus
from .solver_detection_system import SolverDetectionSystem

logger = logging.getLogger(__name__)


class ProblemType(Enum):
    """Types of optimization problems"""
    LINEAR_PROGRAMMING = "linear_programming"
    MIXED_INTEGER_PROGRAMMING = "mixed_integer_programming"
    CONSTRAINT_PROGRAMMING = "constraint_programming"
    NONLINEAR_PROGRAMMING = "nonlinear_programming"
    MULTI_OBJECTIVE = "multi_objective"
    ROUTING = "routing"
    SCHEDULING = "scheduling"
    RESOURCE_ALLOCATION = "resource_allocation"
    CAPACITY_PLANNING = "capacity_planning"
    PRODUCTION_PLANNING = "production_planning"


class ProblemSize(Enum):
    """Problem size categories"""
    SMALL = "small"      # < 100 variables
    MEDIUM = "medium"    # 100-10,000 variables
    LARGE = "large"      # 10,000-1,000,000 variables
    VERY_LARGE = "very_large"  # > 1,000,000 variables


class ProblemComplexity(Enum):
    """Problem complexity levels"""
    LOW = "low"          # Simple linear constraints
    MEDIUM = "medium"    # Mixed constraints, some nonlinearity
    HIGH = "high"        # Complex constraints, high nonlinearity
    VERY_HIGH = "very_high"  # Highly nonlinear, combinatorial


@dataclass
class ProblemCharacteristics:
    """Comprehensive problem characteristics analysis"""
    problem_type: ProblemType
    size: ProblemSize
    complexity: ProblemComplexity
    
    # Problem dimensions
    num_variables: int
    num_constraints: int
    num_objectives: int = 1
    
    # Variable types
    continuous_vars: int = 0
    integer_vars: int = 0
    binary_vars: int = 0
    
    # Constraint types
    linear_constraints: int = 0
    quadratic_constraints: int = 0
    nonlinear_constraints: int = 0
    logical_constraints: int = 0
    
    # Objective characteristics
    linear_objective: bool = True
    quadratic_objective: bool = False
    nonlinear_objective: bool = False
    
    # Manufacturing-specific characteristics
    manufacturing_domain: Optional[str] = None  # production, scheduling, routing, etc.
    time_horizon: Optional[str] = None  # short, medium, long
    resource_types: List[str] = None
    
    # Performance requirements
    max_solve_time: Optional[float] = None
    solution_quality_priority: str = "balanced"  # speed, quality, balanced
    
    # Problem metadata
    problem_id: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical
    
    def __post_init__(self):
        if self.resource_types is None:
            self.resource_types = []


@dataclass
class SolverScore:
    """Solver scoring result"""
    solver_name: str
    total_score: float
    component_scores: Dict[str, float]
    ranking: int = 0
    selection_rationale: str = ""
    confidence: float = 0.0
    estimated_solve_time: Optional[float] = None
    expected_solution_quality: Optional[float] = None


@dataclass
class SolverSelection:
    """Complete solver selection result"""
    primary_solver: str
    backup_solvers: List[str]
    solver_scores: List[SolverScore]
    selection_rationale: str
    problem_characteristics: ProblemCharacteristics
    selection_timestamp: datetime
    fallback_chain: List[str]
    confidence_score: float


class IntelligentSolverSelector:
    """
    Intelligent solver selection engine with comprehensive problem analysis,
    scoring algorithms, and decision trees for manufacturing optimization.
    """
    
    def __init__(self, solver_registry: Optional[EnhancedSolverRegistry] = None):
        self.solver_registry = solver_registry or EnhancedSolverRegistry()
        self.detection_system = SolverDetectionSystem()
        
        # Selection history for learning
        self.selection_history: List[SolverSelection] = []
        self.performance_feedback: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Scoring weights for different criteria
        self.scoring_weights = {
            "problem_fit": 0.30,
            "performance": 0.25,
            "reliability": 0.20,
            "availability": 0.15,
            "scalability": 0.10
        }
        
        # Manufacturing-specific decision trees
        self.manufacturing_decision_trees = self._initialize_manufacturing_decision_trees()
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("Intelligent solver selector initialized")
    
    def _initialize_manufacturing_decision_trees(self) -> Dict[str, Dict[str, Any]]:
        """Initialize decision trees for manufacturing problem types"""
        
        return {
            "production_scheduling": {
                "small_problems": {
                    "preferred_solvers": ["CP_SAT", "SCIP", "CBC"],
                    "criteria": {
                        "max_variables": 1000,
                        "max_constraints": 500,
                        "solver_types": ["constraint_programming", "mixed_integer_programming"]
                    }
                },
                "medium_problems": {
                    "preferred_solvers": ["CP_SAT", "SCIP", "HiGHS_MIP"],
                    "criteria": {
                        "max_variables": 50000,
                        "max_constraints": 25000,
                        "parallel_capable": True
                    }
                },
                "large_problems": {
                    "preferred_solvers": ["SCIP", "HiGHS_MIP", "CBC"],
                    "criteria": {
                        "max_variables": 1000000,
                        "memory_efficient": True,
                        "parallel_capable": True
                    }
                }
            },
            
            "capacity_planning": {
                "small_problems": {
                    "preferred_solvers": ["HiGHS_LP", "GLOP", "CLP"],
                    "criteria": {
                        "max_variables": 10000,
                        "solver_types": ["linear_programming"]
                    }
                },
                "medium_problems": {
                    "preferred_solvers": ["HiGHS_LP", "CLP", "GLOP"],
                    "criteria": {
                        "max_variables": 100000,
                        "performance_tier": ["fast", "very_fast"]
                    }
                },
                "large_problems": {
                    "preferred_solvers": ["CLP", "HiGHS_LP"],
                    "criteria": {
                        "max_variables": 10000000,
                        "memory_efficient": True,
                        "parallel_capable": True
                    }
                }
            },
            
            "resource_allocation": {
                "small_problems": {
                    "preferred_solvers": ["HiGHS_LP", "GLOP", "SCIPY_LINPROG"],
                    "criteria": {
                        "max_variables": 5000,
                        "solver_types": ["linear_programming"]
                    }
                },
                "medium_problems": {
                    "preferred_solvers": ["HiGHS_LP", "CLP", "GLOP"],
                    "criteria": {
                        "max_variables": 50000,
                        "speed_priority": True
                    }
                },
                "large_problems": {
                    "preferred_solvers": ["CLP", "HiGHS_LP"],
                    "criteria": {
                        "max_variables": 1000000,
                        "memory_efficient": True
                    }
                }
            },
            
            "routing_optimization": {
                "small_problems": {
                    "preferred_solvers": ["OR_TOOLS_ROUTING", "CP_SAT"],
                    "criteria": {
                        "max_variables": 1000,
                        "solver_types": ["constraint_programming"]
                    }
                },
                "medium_problems": {
                    "preferred_solvers": ["OR_TOOLS_ROUTING", "CP_SAT", "SCIP"],
                    "criteria": {
                        "max_variables": 10000,
                        "routing_specialized": True
                    }
                },
                "large_problems": {
                    "preferred_solvers": ["CP_SAT", "SCIP"],
                    "criteria": {
                        "max_variables": 100000,
                        "parallel_capable": True
                    }
                }
            },
            
            "mixed_integer_optimization": {
                "small_problems": {
                    "preferred_solvers": ["HiGHS_MIP", "SCIP", "CBC"],
                    "criteria": {
                        "max_variables": 5000,
                        "solver_types": ["mixed_integer_programming"]
                    }
                },
                "medium_problems": {
                    "preferred_solvers": ["HiGHS_MIP", "SCIP", "CBC"],
                    "criteria": {
                        "max_variables": 100000,
                        "performance_tier": ["fast", "very_fast"]
                    }
                },
                "large_problems": {
                    "preferred_solvers": ["SCIP", "HiGHS_MIP"],
                    "criteria": {
                        "max_variables": 1000000,
                        "memory_efficient": True,
                        "parallel_capable": True
                    }
                }
            }
        }
    
    def analyze_problem_characteristics(self, problem_data: Dict[str, Any]) -> ProblemCharacteristics:
        """
        Comprehensive problem analysis to extract characteristics
        
        Args:
            problem_data: Problem specification dictionary
            
        Returns:
            Detailed problem characteristics
        """
        logger.debug("Analyzing problem characteristics...")
        
        try:
            # Extract basic dimensions
            num_variables = problem_data.get("num_variables", 0)
            num_constraints = problem_data.get("num_constraints", 0)
            num_objectives = problem_data.get("num_objectives", 1)
            
            # Determine problem size
            size = self._determine_problem_size(num_variables)
            
            # Analyze variable types
            variables = problem_data.get("variables", {})
            continuous_vars = len([v for v in variables.values() if v.get("type") == "continuous"])
            integer_vars = len([v for v in variables.values() if v.get("type") == "integer"])
            binary_vars = len([v for v in variables.values() if v.get("type") == "binary"])
            
            # Analyze constraint types
            constraints = problem_data.get("constraints", [])
            linear_constraints = len([c for c in constraints if c.get("type") == "linear"])
            quadratic_constraints = len([c for c in constraints if c.get("type") == "quadratic"])
            nonlinear_constraints = len([c for c in constraints if c.get("type") == "nonlinear"])
            logical_constraints = len([c for c in constraints if c.get("type") == "logical"])
            
            # Determine problem type
            problem_type = self._determine_problem_type(
                continuous_vars, integer_vars, binary_vars,
                linear_constraints, quadratic_constraints, nonlinear_constraints, logical_constraints,
                problem_data
            )
            
            # Determine complexity
            complexity = self._determine_problem_complexity(
                problem_type, num_variables, num_constraints,
                nonlinear_constraints, logical_constraints, problem_data
            )
            
            # Analyze objective
            objective = problem_data.get("objective", {})
            linear_objective = objective.get("type", "linear") == "linear"
            quadratic_objective = objective.get("type") == "quadratic"
            nonlinear_objective = objective.get("type") == "nonlinear"
            
            # Extract manufacturing-specific information
            manufacturing_domain = problem_data.get("domain", "general")
            time_horizon = problem_data.get("time_horizon", "medium")
            resource_types = problem_data.get("resource_types", [])
            
            # Performance requirements
            max_solve_time = problem_data.get("max_solve_time")
            solution_quality_priority = problem_data.get("solution_quality_priority", "balanced")
            priority = problem_data.get("priority", "medium")
            
            characteristics = ProblemCharacteristics(
                problem_type=problem_type,
                size=size,
                complexity=complexity,
                num_variables=num_variables,
                num_constraints=num_constraints,
                num_objectives=num_objectives,
                continuous_vars=continuous_vars,
                integer_vars=integer_vars,
                binary_vars=binary_vars,
                linear_constraints=linear_constraints,
                quadratic_constraints=quadratic_constraints,
                nonlinear_constraints=nonlinear_constraints,
                logical_constraints=logical_constraints,
                linear_objective=linear_objective,
                quadratic_objective=quadratic_objective,
                nonlinear_objective=nonlinear_objective,
                manufacturing_domain=manufacturing_domain,
                time_horizon=time_horizon,
                resource_types=resource_types,
                max_solve_time=max_solve_time,
                solution_quality_priority=solution_quality_priority,
                problem_id=problem_data.get("problem_id"),
                priority=priority
            )
            
            logger.info(f"Problem analysis complete: {problem_type.value}, {size.value}, {complexity.value}")
            return characteristics
            
        except Exception as e:
            logger.error(f"Error analyzing problem characteristics: {e}")
            # Return default characteristics
            return ProblemCharacteristics(
                problem_type=ProblemType.LINEAR_PROGRAMMING,
                size=ProblemSize.SMALL,
                complexity=ProblemComplexity.LOW,
                num_variables=problem_data.get("num_variables", 10),
                num_constraints=problem_data.get("num_constraints", 5)
            )
    
    def _determine_problem_size(self, num_variables: int) -> ProblemSize:
        """Determine problem size category based on number of variables"""
        
        if num_variables < 100:
            return ProblemSize.SMALL
        elif num_variables < 10000:
            return ProblemSize.MEDIUM
        elif num_variables < 1000000:
            return ProblemSize.LARGE
        else:
            return ProblemSize.VERY_LARGE
    
    def _determine_problem_type(self, continuous_vars: int, integer_vars: int, binary_vars: int,
                               linear_constraints: int, quadratic_constraints: int, 
                               nonlinear_constraints: int, logical_constraints: int,
                               problem_data: Dict[str, Any]) -> ProblemType:
        """Determine problem type based on variable and constraint analysis"""
        
        # Check for explicit problem type first
        explicit_type = problem_data.get("problem_type")
        if explicit_type:
            try:
                return ProblemType(explicit_type)
            except ValueError:
                pass
        
        # Determine based on variable and constraint types (primary logic)
        total_vars = continuous_vars + integer_vars + binary_vars
        
        if logical_constraints > 0 or (integer_vars + binary_vars) > total_vars * 0.5:
            if logical_constraints > linear_constraints:
                return ProblemType.CONSTRAINT_PROGRAMMING
            else:
                return ProblemType.MIXED_INTEGER_PROGRAMMING
        
        elif nonlinear_constraints > 0 or quadratic_constraints > 0:
            return ProblemType.NONLINEAR_PROGRAMMING
        
        elif integer_vars > 0 or binary_vars > 0:
            return ProblemType.MIXED_INTEGER_PROGRAMMING
        
        elif continuous_vars > 0:
            return ProblemType.LINEAR_PROGRAMMING
        
        # Fallback to manufacturing domain hints only if no clear mathematical type
        domain = problem_data.get("domain", "").lower()
        if "scheduling" in domain or "schedule" in domain:
            return ProblemType.SCHEDULING
        elif "routing" in domain or "vehicle" in domain:
            return ProblemType.ROUTING
        elif "capacity" in domain:
            return ProblemType.CAPACITY_PLANNING
        elif "production" in domain:
            return ProblemType.PRODUCTION_PLANNING
        elif "resource" in domain:
            return ProblemType.RESOURCE_ALLOCATION
        
        # Default fallback
        return ProblemType.LINEAR_PROGRAMMING
    
    def _determine_problem_complexity(self, problem_type: ProblemType, num_variables: int,
                                    num_constraints: int, nonlinear_constraints: int,
                                    logical_constraints: int, problem_data: Dict[str, Any]) -> ProblemComplexity:
        """Determine problem complexity level"""
        
        # Base complexity on problem type
        base_complexity = {
            ProblemType.LINEAR_PROGRAMMING: ProblemComplexity.LOW,
            ProblemType.MIXED_INTEGER_PROGRAMMING: ProblemComplexity.MEDIUM,
            ProblemType.CONSTRAINT_PROGRAMMING: ProblemComplexity.HIGH,
            ProblemType.NONLINEAR_PROGRAMMING: ProblemComplexity.HIGH,
            ProblemType.ROUTING: ProblemComplexity.HIGH,
            ProblemType.SCHEDULING: ProblemComplexity.MEDIUM
        }.get(problem_type, ProblemComplexity.MEDIUM)
        
        # Adjust based on problem characteristics
        complexity_score = 0
        
        # Size factor
        if num_variables > 100000:
            complexity_score += 2
        elif num_variables > 10000:
            complexity_score += 1
        
        # Constraint complexity
        if nonlinear_constraints > num_constraints * 0.5:
            complexity_score += 3
        elif nonlinear_constraints > 0:
            complexity_score += 2
        
        if logical_constraints > num_constraints * 0.3:
            complexity_score += 1
        
        # Special problem characteristics
        if problem_data.get("multi_objective", False):
            complexity_score += 1
        
        if problem_data.get("time_dependent", False):
            complexity_score += 1
        
        if problem_data.get("stochastic", False):
            complexity_score += 2
        
        # Determine final complexity
        if complexity_score >= 4:
            return ProblemComplexity.VERY_HIGH
        elif complexity_score >= 2:
            return ProblemComplexity.HIGH
        elif complexity_score >= 1:
            return ProblemComplexity.MEDIUM
        else:
            return base_complexity
    
    def select_optimal_solver(self, problem_data: Dict[str, Any]) -> SolverSelection:
        """
        Select the optimal solver for a given problem using comprehensive analysis
        
        Args:
            problem_data: Problem specification dictionary
            
        Returns:
            Complete solver selection with rationale and fallback options
        """
        logger.info("Starting intelligent solver selection...")
        start_time = time.time()
        
        try:
            # Analyze problem characteristics
            characteristics = self.analyze_problem_characteristics(problem_data)
            
            # Get available solvers
            available_solvers = self._get_available_solvers()
            
            if not available_solvers:
                raise ValueError("No solvers available for selection")
            
            # Score all available solvers
            solver_scores = self._score_solvers(characteristics, available_solvers)
            
            # Rank solvers by score
            solver_scores.sort(key=lambda x: x.total_score, reverse=True)
            for i, score in enumerate(solver_scores):
                score.ranking = i + 1
            
            # Select primary solver and backups
            primary_solver = solver_scores[0].solver_name
            backup_solvers = [score.solver_name for score in solver_scores[1:4]]  # Top 3 backups
            
            # Generate fallback chain
            fallback_chain = self._generate_fallback_chain(characteristics, available_solvers)
            
            # Calculate confidence score
            confidence_score = self._calculate_selection_confidence(solver_scores, characteristics)
            
            # Generate selection rationale
            selection_rationale = self._generate_selection_rationale(
                characteristics, solver_scores[0], solver_scores
            )
            
            selection = SolverSelection(
                primary_solver=primary_solver,
                backup_solvers=backup_solvers,
                solver_scores=solver_scores,
                selection_rationale=selection_rationale,
                problem_characteristics=characteristics,
                selection_timestamp=datetime.now(),
                fallback_chain=fallback_chain,
                confidence_score=confidence_score
            )
            
            # Store selection for learning
            with self._lock:
                self.selection_history.append(selection)
            
            selection_time = time.time() - start_time
            logger.info(f"Solver selection complete: {primary_solver} selected in {selection_time:.3f}s "
                       f"(confidence: {confidence_score:.2f})")
            
            return selection
            
        except Exception as e:
            logger.error(f"Error in solver selection: {e}")
            # Return fallback selection
            return self._create_fallback_selection(problem_data, str(e))
    
    def _get_available_solvers(self) -> List[str]:
        """Get list of currently available solvers"""
        
        available_solvers = []
        
        for solver_name, solver_capability in self.solver_registry.solvers.items():
            if self.solver_registry.check_solver_availability(solver_name):
                available_solvers.append(solver_name)
        
        logger.debug(f"Found {len(available_solvers)} available solvers")
        return available_solvers
    
    def _score_solvers(self, characteristics: ProblemCharacteristics, 
                      available_solvers: List[str]) -> List[SolverScore]:
        """Score all available solvers for the given problem characteristics"""
        
        solver_scores = []
        
        for solver_name in available_solvers:
            try:
                score = self._score_individual_solver(solver_name, characteristics)
                solver_scores.append(score)
            except Exception as e:
                logger.warning(f"Error scoring solver {solver_name}: {e}")
        
        return solver_scores
    
    def _score_individual_solver(self, solver_name: str, 
                                characteristics: ProblemCharacteristics) -> SolverScore:
        """Score an individual solver for the given problem characteristics"""
        
        solver_capability = self.solver_registry.solvers[solver_name]
        
        # Component scores
        component_scores = {}
        
        # 1. Problem fit score (30%)
        component_scores["problem_fit"] = self._calculate_problem_fit_score(
            solver_capability, characteristics
        )
        
        # 2. Performance score (25%)
        component_scores["performance"] = self._calculate_performance_score(
            solver_name, solver_capability, characteristics
        )
        
        # 3. Reliability score (20%)
        component_scores["reliability"] = self._calculate_reliability_score(
            solver_name, solver_capability
        )
        
        # 4. Availability score (15%)
        component_scores["availability"] = self._calculate_availability_score(
            solver_name, solver_capability
        )
        
        # 5. Scalability score (10%)
        component_scores["scalability"] = self._calculate_scalability_score(
            solver_capability, characteristics
        )
        
        # Calculate weighted total score
        total_score = sum(
            component_scores[component] * self.scoring_weights[component]
            for component in component_scores
        )
        
        # Generate rationale
        rationale = self._generate_solver_rationale(solver_name, component_scores, characteristics)
        
        # Estimate solve time and solution quality
        estimated_solve_time = self._estimate_solve_time(solver_name, characteristics)
        expected_solution_quality = self._estimate_solution_quality(solver_name, characteristics)
        
        return SolverScore(
            solver_name=solver_name,
            total_score=total_score,
            component_scores=component_scores,
            selection_rationale=rationale,
            confidence=min(total_score, 1.0),
            estimated_solve_time=estimated_solve_time,
            expected_solution_quality=expected_solution_quality
        )
    
    def _calculate_problem_fit_score(self, solver_capability: SolverCapability,
                                   characteristics: ProblemCharacteristics) -> float:
        """Calculate how well a solver fits the problem characteristics"""
        
        score = 0.0
        
        # Problem type compatibility
        problem_type_match = False
        if characteristics.problem_type.value in solver_capability.problem_types:
            score += 0.4
            problem_type_match = True
        elif characteristics.manufacturing_domain in solver_capability.problem_types:
            score += 0.3
            problem_type_match = True
        
        # Variable type compatibility
        variable_compatibility = 0.0
        if characteristics.continuous_vars > 0 and "continuous" in solver_capability.variable_types:
            variable_compatibility += 0.4
        if characteristics.integer_vars > 0 and "integer" in solver_capability.variable_types:
            variable_compatibility += 0.3
        if characteristics.binary_vars > 0 and "binary" in solver_capability.variable_types:
            variable_compatibility += 0.3
        
        score += min(variable_compatibility, 0.3)
        
        # Constraint type compatibility
        constraint_compatibility = 0.0
        if characteristics.linear_constraints > 0 and "linear" in solver_capability.constraint_types:
            constraint_compatibility += 0.2
        if characteristics.quadratic_constraints > 0 and "quadratic" in solver_capability.constraint_types:
            constraint_compatibility += 0.1
        if characteristics.nonlinear_constraints > 0 and "nonlinear" in solver_capability.constraint_types:
            constraint_compatibility += 0.1
        if characteristics.logical_constraints > 0 and "logical" in solver_capability.constraint_types:
            constraint_compatibility += 0.1
        
        score += min(constraint_compatibility, 0.2)
        
        # Size compatibility
        if (characteristics.num_variables <= solver_capability.max_variables and
            characteristics.num_constraints <= solver_capability.max_constraints):
            score += 0.1
        else:
            # Penalize if problem is too large
            size_penalty = min(
                characteristics.num_variables / solver_capability.max_variables,
                characteristics.num_constraints / solver_capability.max_constraints
            )
            score -= min(size_penalty - 1.0, 0.2)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_performance_score(self, solver_name: str, solver_capability: SolverCapability,
                                   characteristics: ProblemCharacteristics) -> float:
        """Calculate performance score based on solver characteristics and problem size"""
        
        # Get performance profile
        performance_profile = solver_capability.performance_profile
        
        # Base performance score based on problem size
        size_key = f"{characteristics.size.value}_problems"
        base_score = performance_profile.get(size_key, 3) / 5.0  # Normalize to 0-1
        
        # Adjust for specific performance characteristics
        speed_score = performance_profile.get("speed", 3) / 5.0
        memory_score = performance_profile.get("memory_efficiency", 3) / 5.0
        robustness_score = performance_profile.get("robustness", 3) / 5.0
        
        # Weight based on solution quality priority
        if characteristics.solution_quality_priority == "speed":
            performance_score = 0.6 * speed_score + 0.2 * base_score + 0.2 * robustness_score
        elif characteristics.solution_quality_priority == "quality":
            performance_score = 0.6 * robustness_score + 0.2 * base_score + 0.2 * speed_score
        else:  # balanced
            performance_score = 0.4 * base_score + 0.3 * speed_score + 0.3 * robustness_score
        
        # Memory efficiency bonus for large problems
        if characteristics.size in [ProblemSize.LARGE, ProblemSize.VERY_LARGE]:
            if solver_capability.memory_efficient:
                performance_score += 0.1
        
        # Parallel processing bonus for large problems
        if characteristics.size in [ProblemSize.LARGE, ProblemSize.VERY_LARGE]:
            if solver_capability.parallel_capable:
                performance_score += 0.1
        
        return max(0.0, min(1.0, performance_score))
    
    def _calculate_reliability_score(self, solver_name: str, solver_capability: SolverCapability) -> float:
        """Calculate reliability score based on solver stability and track record"""
        
        # Base reliability from performance profile
        base_reliability = solver_capability.performance_profile.get("robustness", 3) / 5.0
        numerical_stability = solver_capability.performance_profile.get("numerical_stability", 3) / 5.0
        
        # Historical performance feedback
        historical_reliability = 0.8  # Default
        if solver_name in self.performance_feedback:
            feedback_data = self.performance_feedback[solver_name]
            if feedback_data:
                success_rate = sum(1 for f in feedback_data if f.get("success", False)) / len(feedback_data)
                historical_reliability = success_rate
        
        # License and support reliability
        license_bonus = 0.0
        if solver_capability.license_type == "open_source":
            license_bonus = 0.05  # Slight bonus for open source
        
        reliability_score = (
            0.4 * base_reliability +
            0.3 * numerical_stability +
            0.3 * historical_reliability +
            license_bonus
        )
        
        return max(0.0, min(1.0, reliability_score))
    
    def _calculate_availability_score(self, solver_name: str, solver_capability: SolverCapability) -> float:
        """Calculate availability score based on installation and current status"""
        
        # Current availability
        if solver_capability.status == SolverStatus.AVAILABLE:
            availability_score = 1.0
        elif solver_capability.status == SolverStatus.UNAVAILABLE:
            availability_score = 0.0
        else:
            availability_score = 0.5
        
        # Installation ease bonus
        installation_bonus = {
            "pip": 0.1,
            "conda": 0.05,
            "system": 0.0,
            "manual": -0.1
        }.get(solver_capability.installation_method, 0.0)
        
        # Dependency complexity penalty
        dependency_penalty = min(len(solver_capability.dependencies) * 0.02, 0.1)
        
        final_score = availability_score + installation_bonus - dependency_penalty
        
        return max(0.0, min(1.0, final_score))
    
    def _calculate_scalability_score(self, solver_capability: SolverCapability,
                                   characteristics: ProblemCharacteristics) -> float:
        """Calculate scalability score based on solver limits and problem size"""
        
        # Variable scalability
        var_ratio = characteristics.num_variables / solver_capability.max_variables
        var_score = max(0.0, 1.0 - var_ratio) if var_ratio <= 1.0 else 0.0
        
        # Constraint scalability
        const_ratio = characteristics.num_constraints / solver_capability.max_constraints
        const_score = max(0.0, 1.0 - const_ratio) if const_ratio <= 1.0 else 0.0
        
        # Parallel processing bonus for large problems
        parallel_bonus = 0.0
        if characteristics.size in [ProblemSize.LARGE, ProblemSize.VERY_LARGE]:
            if solver_capability.parallel_capable:
                parallel_bonus = 0.2
        
        # Memory efficiency bonus
        memory_bonus = 0.1 if solver_capability.memory_efficient else 0.0
        
        scalability_score = (
            0.4 * var_score +
            0.4 * const_score +
            parallel_bonus +
            memory_bonus
        )
        
        return max(0.0, min(1.0, scalability_score))
    
    def _generate_fallback_chain(self, characteristics: ProblemCharacteristics,
                               available_solvers: List[str]) -> List[str]:
        """Generate fallback chain based on problem characteristics and solver availability"""
        
        # Start with manufacturing-specific decision tree
        fallback_chain = []
        
        # Get decision tree for problem domain
        domain_key = characteristics.manufacturing_domain
        if domain_key in self.manufacturing_decision_trees:
            decision_tree = self.manufacturing_decision_trees[domain_key]
            size_key = f"{characteristics.size.value}_problems"
            
            if size_key in decision_tree:
                preferred_solvers = decision_tree[size_key]["preferred_solvers"]
                fallback_chain.extend([s for s in preferred_solvers if s in available_solvers])
        
        # Add general fallback chains from registry
        problem_type_key = characteristics.problem_type.value
        if problem_type_key in self.solver_registry.fallback_chains:
            registry_fallbacks = self.solver_registry.fallback_chains[problem_type_key]
            for solver in registry_fallbacks:
                if solver in available_solvers and solver not in fallback_chain:
                    fallback_chain.append(solver)
        
        # Add any remaining available solvers
        for solver in available_solvers:
            if solver not in fallback_chain:
                fallback_chain.append(solver)
        
        return fallback_chain[:5]  # Limit to top 5 fallbacks
    
    def _calculate_selection_confidence(self, solver_scores: List[SolverScore],
                                      characteristics: ProblemCharacteristics) -> float:
        """Calculate confidence in the solver selection"""
        
        if not solver_scores:
            return 0.0
        
        # Score gap between top solvers
        if len(solver_scores) > 1:
            score_gap = solver_scores[0].total_score - solver_scores[1].total_score
            gap_confidence = min(score_gap * 2, 0.4)  # Max 0.4 from gap
        else:
            gap_confidence = 0.2
        
        # Top solver absolute score
        top_score_confidence = solver_scores[0].total_score * 0.4
        
        # Problem complexity factor (lower confidence for complex problems)
        complexity_factor = {
            ProblemComplexity.LOW: 0.2,
            ProblemComplexity.MEDIUM: 0.15,
            ProblemComplexity.HIGH: 0.1,
            ProblemComplexity.VERY_HIGH: 0.05
        }.get(characteristics.complexity, 0.1)
        
        confidence = gap_confidence + top_score_confidence + complexity_factor
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_selection_rationale(self, characteristics: ProblemCharacteristics,
                                    top_score: SolverScore, all_scores: List[SolverScore]) -> str:
        """Generate human-readable rationale for solver selection"""
        
        rationale_parts = []
        
        # Problem summary
        rationale_parts.append(
            f"Selected {top_score.solver_name} for {characteristics.problem_type.value} problem "
            f"with {characteristics.num_variables} variables and {characteristics.num_constraints} constraints "
            f"({characteristics.size.value} size, {characteristics.complexity.value} complexity)."
        )
        
        # Key selection factors
        top_components = sorted(top_score.component_scores.items(), key=lambda x: x[1], reverse=True)
        key_factors = [f"{comp}: {score:.2f}" for comp, score in top_components[:3]]
        rationale_parts.append(f"Key factors: {', '.join(key_factors)}.")
        
        # Performance expectations
        if top_score.estimated_solve_time:
            rationale_parts.append(f"Estimated solve time: {top_score.estimated_solve_time:.2f}s.")
        
        # Alternative options
        if len(all_scores) > 1:
            alternatives = [score.solver_name for score in all_scores[1:3]]
            rationale_parts.append(f"Alternative solvers: {', '.join(alternatives)}.")
        
        return " ".join(rationale_parts)
    
    def _generate_solver_rationale(self, solver_name: str, component_scores: Dict[str, float],
                                 characteristics: ProblemCharacteristics) -> str:
        """Generate rationale for individual solver score"""
        
        top_component = max(component_scores.items(), key=lambda x: x[1])
        return f"Strong {top_component[0]} ({top_component[1]:.2f}) for {characteristics.problem_type.value}"
    
    def _estimate_solve_time(self, solver_name: str, characteristics: ProblemCharacteristics) -> Optional[float]:
        """Estimate solve time based on solver performance and problem characteristics"""
        
        try:
            # Get baseline performance data
            if solver_name in self.detection_system.performance_baselines:
                baseline = self.detection_system.performance_baselines[solver_name]
                
                # Scale based on problem size
                size_multipliers = {
                    ProblemSize.SMALL: 1.0,
                    ProblemSize.MEDIUM: 5.0,
                    ProblemSize.LARGE: 25.0,
                    ProblemSize.VERY_LARGE: 100.0
                }
                
                base_time = baseline.get(f"{characteristics.size.value}_problem_time", 1.0)
                multiplier = size_multipliers.get(characteristics.size, 10.0)
                
                # Adjust for complexity
                complexity_multipliers = {
                    ProblemComplexity.LOW: 1.0,
                    ProblemComplexity.MEDIUM: 2.0,
                    ProblemComplexity.HIGH: 5.0,
                    ProblemComplexity.VERY_HIGH: 10.0
                }
                
                complexity_mult = complexity_multipliers.get(characteristics.complexity, 3.0)
                
                estimated_time = base_time * multiplier * complexity_mult
                
                # Apply solver-specific factors
                solver_capability = self.solver_registry.solvers[solver_name]
                speed_factor = solver_capability.performance_profile.get("speed", 3) / 3.0
                
                return estimated_time / speed_factor
                
        except Exception as e:
            logger.debug(f"Error estimating solve time for {solver_name}: {e}")
        
        return None
    
    def _estimate_solution_quality(self, solver_name: str, characteristics: ProblemCharacteristics) -> Optional[float]:
        """Estimate expected solution quality"""
        
        try:
            solver_capability = self.solver_registry.solvers[solver_name]
            
            # Base quality from solver robustness
            base_quality = solver_capability.performance_profile.get("robustness", 3) / 5.0
            
            # Adjust for problem fit
            problem_fit = self._calculate_problem_fit_score(solver_capability, characteristics)
            
            # Numerical stability factor
            stability = solver_capability.performance_profile.get("numerical_stability", 3) / 5.0
            
            quality_estimate = 0.5 * base_quality + 0.3 * problem_fit + 0.2 * stability
            
            return max(0.0, min(1.0, quality_estimate))
            
        except Exception as e:
            logger.debug(f"Error estimating solution quality for {solver_name}: {e}")
        
        return None
    
    def _create_fallback_selection(self, problem_data: Dict[str, Any], error_message: str) -> SolverSelection:
        """Create fallback selection when main selection fails"""
        
        # Use simple heuristics for fallback
        num_variables = problem_data.get("num_variables", 10)
        
        # Default solver selection based on problem size
        if num_variables < 1000:
            primary_solver = "GLOP"  # Simple linear solver
            backup_solvers = ["SCIPY_LINPROG", "CLP"]
        elif num_variables < 10000:
            primary_solver = "HiGHS_LP"
            backup_solvers = ["GLOP", "CLP"]
        else:
            primary_solver = "CLP"
            backup_solvers = ["HiGHS_LP", "GLOP"]
        
        # Create minimal characteristics
        characteristics = ProblemCharacteristics(
            problem_type=ProblemType.LINEAR_PROGRAMMING,
            size=ProblemSize.SMALL if num_variables < 100 else ProblemSize.MEDIUM,
            complexity=ProblemComplexity.LOW,
            num_variables=num_variables,
            num_constraints=problem_data.get("num_constraints", 5)
        )
        
        return SolverSelection(
            primary_solver=primary_solver,
            backup_solvers=backup_solvers,
            solver_scores=[],
            selection_rationale=f"Fallback selection due to error: {error_message}",
            problem_characteristics=characteristics,
            selection_timestamp=datetime.now(),
            fallback_chain=[primary_solver] + backup_solvers,
            confidence_score=0.3
        )
    
    def get_selection_history(self) -> List[SolverSelection]:
        """Get history of solver selections for analysis"""
        with self._lock:
            return self.selection_history.copy()
    
    def record_performance_feedback(self, solver_name: str, problem_characteristics: ProblemCharacteristics,
                                  actual_solve_time: float, solution_quality: float, success: bool):
        """Record performance feedback for learning and improvement"""
        
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "problem_type": problem_characteristics.problem_type.value,
            "problem_size": problem_characteristics.size.value,
            "problem_complexity": problem_characteristics.complexity.value,
            "actual_solve_time": actual_solve_time,
            "solution_quality": solution_quality,
            "success": success,
            "num_variables": problem_characteristics.num_variables,
            "num_constraints": problem_characteristics.num_constraints
        }
        
        with self._lock:
            self.performance_feedback[solver_name].append(feedback)
            
            # Keep only recent feedback (last 100 entries per solver)
            if len(self.performance_feedback[solver_name]) > 100:
                self.performance_feedback[solver_name] = self.performance_feedback[solver_name][-100:]
        
        logger.info(f"Recorded performance feedback for {solver_name}: "
                   f"time={actual_solve_time:.3f}s, quality={solution_quality:.2f}, success={success}")


# Global instance for easy access
intelligent_solver_selector = IntelligentSolverSelector()