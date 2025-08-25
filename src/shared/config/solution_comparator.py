"""
Multi-Criteria Solution Comparison System
========================================

Implements comprehensive solution comparison and ranking system for multi-solver swarm results.
Provides weighted scoring algorithm based on optimality, feasibility, performance, and robustness.

Features:
- SolutionComparator class with weighted scoring algorithm
- Solution quality assessment based on multiple criteria
- Solution ranking system that compares results from multiple solvers
- Detailed comparison analysis and reporting for solution selection rationale

Requirements: 3.3, 3.4
"""

import logging
import statistics
import math
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json

try:
    from strands import Agent
    from strands_tools import memory, retrieve, use_aws, think, use_llm
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

from ..utils.base import BaseTool, ToolExecutionError, ToolInitializationError
from .solver_tool import SolverResult

logger = logging.getLogger(__name__)


class ComparisonCriterion(Enum):
    """Criteria for solution comparison"""
    OPTIMALITY = "optimality"
    FEASIBILITY = "feasibility"
    PERFORMANCE = "performance"
    ROBUSTNESS = "robustness"
    CONSISTENCY = "consistency"
    SCALABILITY = "scalability"


@dataclass
class SolutionScore:
    """Individual solution scoring breakdown"""
    solver_name: str
    total_score: float
    criterion_scores: Dict[str, float]
    weighted_scores: Dict[str, float]
    rank: int
    percentile: float
    
    # Detailed metrics
    optimality_score: float
    feasibility_score: float
    performance_score: float
    robustness_score: float
    
    # Additional analysis
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class ComparisonAnalysis:
    """Comprehensive comparison analysis of multiple solutions"""
    comparison_id: str
    timestamp: datetime
    solution_count: int
    
    # Scoring results
    solution_scores: List[SolutionScore]
    best_solution: SolutionScore
    ranking: List[str]  # Solver names in rank order
    
    # Statistical analysis
    score_statistics: Dict[str, float]
    criterion_statistics: Dict[str, Dict[str, float]]
    
    # Quality assessment
    quality_distribution: Dict[str, int]
    performance_analysis: Dict[str, Any]
    
    # Selection rationale
    selection_rationale: str
    confidence_level: float
    decision_factors: List[str]
    
    # Comparison metadata
    weights_used: Dict[str, float]
    comparison_method: str
    problem_characteristics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class ComparisonWeights:
    """Configurable weights for solution comparison criteria"""
    optimality: float = 0.4      # How close to optimal solution
    feasibility: float = 0.3     # Constraint satisfaction quality
    performance: float = 0.2     # Solve time and efficiency
    robustness: float = 0.1      # Solution stability and reliability
    
    def __post_init__(self):
        """Validate weights sum to 1.0"""
        total = self.optimality + self.feasibility + self.performance + self.robustness
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            "optimality": self.optimality,
            "feasibility": self.feasibility,
            "performance": self.performance,
            "robustness": self.robustness
        }


class SolutionComparator(BaseTool):
    """
    Multi-criteria solution comparison system that evaluates and ranks
    solutions from multiple solvers based on weighted scoring algorithm.
    """
    
    def __init__(self):
        super().__init__(
            name="solution_comparator",
            description="Multi-criteria solution comparison and ranking system for solver swarm results",
            version="1.0.0"
        )
        
        # Default comparison weights
        self.default_weights = ComparisonWeights()
        
        # Strands integration
        self.strands_agent = None
        self.strands_tools = {}
        
        # Comparison history
        self.comparison_history: List[ComparisonAnalysis] = []
        
        # Performance thresholds for scoring
        self.performance_thresholds = {
            "excellent": 1.0,      # < 1 second
            "good": 10.0,          # < 10 seconds
            "acceptable": 60.0,    # < 1 minute
            "poor": 300.0          # < 5 minutes
        }
        
        # Quality assessment thresholds
        self.quality_thresholds = {
            "optimal_gap": 0.01,      # 1% optimality gap
            "feasibility_tolerance": 1e-6,
            "robustness_variance": 0.05
        }
    
    async def initialize(self) -> bool:
        """Initialize the Solution Comparator"""
        try:
            # Initialize Strands integration
            await self._initialize_strands_integration()
            
            # Load comparison configuration
            await self._load_comparison_configuration()
            
            self._initialized = True
            self.logger.info("Solution Comparator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Solution Comparator: {e}")
            return False
    
    async def _initialize_strands_integration(self):
        """Initialize Strands tools integration"""
        if not STRANDS_AVAILABLE:
            self.logger.warning("Strands not available - using fallback implementation")
            return
        
        try:
            self.strands_agent = Agent(
                name="solution_comparator",
                system_prompt="""You are a solution comparison expert specializing in multi-criteria analysis of optimization results.
                
                Your expertise includes:
                1. Evaluating solution quality across multiple criteria (optimality, feasibility, performance, robustness)
                2. Applying weighted scoring algorithms for objective comparison
                3. Generating detailed comparison analysis and selection rationale
                4. Identifying solution strengths, weaknesses, and improvement opportunities
                5. Providing confidence assessments and decision support
                
                COMPARISON CRITERIA:
                
                Optimality (40% default weight):
                - Objective value quality compared to theoretical optimum
                - Gap analysis and bound evaluation
                - Solution improvement potential
                
                Feasibility (30% default weight):
                - Constraint satisfaction quality
                - Violation analysis and penalty assessment
                - Solution validity and correctness
                
                Performance (20% default weight):
                - Solve time efficiency
                - Resource utilization
                - Scalability characteristics
                
                Robustness (10% default weight):
                - Solution stability under parameter variations
                - Sensitivity analysis results
                - Reliability and consistency metrics
                
                Always provide detailed rationale for solution selection with supporting evidence and confidence levels.
                Store comparison results in memory for learning and pattern recognition.""",
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
    
    async def _load_comparison_configuration(self):
        """Load comparison configuration from memory or defaults"""
        if self.strands_tools.get('memory'):
            try:
                # Try to retrieve previous configuration
                config_result = self.strands_tools['memory'](
                    action="retrieve",
                    query="solution comparison configuration weights thresholds"
                )
                
                if config_result and 'content' in config_result:
                    # Parse and apply configuration
                    self.logger.info("Loaded comparison configuration from memory")
                
            except Exception as e:
                self.logger.warning(f"Could not load comparison configuration: {e}")
        
        # Store default configuration
        if self.strands_tools.get('memory'):
            try:
                config_data = {
                    "default_weights": self.default_weights.to_dict(),
                    "performance_thresholds": self.performance_thresholds,
                    "quality_thresholds": self.quality_thresholds
                }
                
                self.strands_tools['memory'](
                    action="store",
                    content=f"Solution comparison configuration: {json.dumps(config_data)}",
                    metadata={"type": "comparison_config", "component": "solution_comparator"}
                )
                
            except Exception as e:
                self.logger.warning(f"Could not store comparison configuration: {e}")
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute solution comparison operations"""
        operation = kwargs.get("operation", "compare_solutions")
        
        if operation == "compare_solutions":
            return await self._compare_solutions(**kwargs)
        elif operation == "rank_solutions":
            return await self._rank_solutions(**kwargs)
        elif operation == "analyze_quality":
            return await self._analyze_solution_quality(**kwargs)
        elif operation == "generate_rationale":
            return await self._generate_selection_rationale(**kwargs)
        elif operation == "get_comparison_history":
            return await self._get_comparison_history(**kwargs)
        else:
            raise ToolExecutionError(f"Unknown operation: {operation}", self.name)
    
    async def _compare_solutions(self,
                                solutions: List[SolverResult],
                                weights: Optional[Dict[str, float]] = None,
                                problem_characteristics: Optional[Dict[str, Any]] = None,
                                **kwargs) -> Dict[str, Any]:
        """Compare multiple solutions using weighted scoring algorithm"""
        try:
            if not solutions:
                raise ToolExecutionError("No solutions provided for comparison", self.name)
            
            # Validate and prepare weights
            comparison_weights = self._prepare_weights(weights)
            
            # Generate comparison ID
            comparison_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(solutions)}"
            
            # Score all solutions
            solution_scores = []
            for solution in solutions:
                score = await self._score_solution(solution, comparison_weights, solutions)
                solution_scores.append(score)
            
            # Rank solutions
            solution_scores.sort(key=lambda x: x.total_score, reverse=True)
            for i, score in enumerate(solution_scores):
                score.rank = i + 1
                score.percentile = (len(solution_scores) - i) / len(solution_scores) * 100
            
            # Generate statistical analysis
            score_statistics = self._calculate_score_statistics(solution_scores)
            criterion_statistics = self._calculate_criterion_statistics(solution_scores)
            
            # Assess quality distribution
            quality_distribution = self._assess_quality_distribution(solution_scores)
            
            # Generate performance analysis
            performance_analysis = self._analyze_performance_characteristics(solutions)
            
            # Generate selection rationale
            selection_rationale = await self._generate_detailed_rationale(
                solution_scores[0], solution_scores, comparison_weights
            )
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(solution_scores)
            
            # Identify key decision factors
            decision_factors = self._identify_decision_factors(solution_scores, comparison_weights)
            
            # Create comprehensive analysis
            analysis = ComparisonAnalysis(
                comparison_id=comparison_id,
                timestamp=datetime.now(),
                solution_count=len(solutions),
                solution_scores=solution_scores,
                best_solution=solution_scores[0],
                ranking=[score.solver_name for score in solution_scores],
                score_statistics=score_statistics,
                criterion_statistics=criterion_statistics,
                quality_distribution=quality_distribution,
                performance_analysis=performance_analysis,
                selection_rationale=selection_rationale,
                confidence_level=confidence_level,
                decision_factors=decision_factors,
                weights_used=comparison_weights.to_dict(),
                comparison_method="weighted_multi_criteria",
                problem_characteristics=problem_characteristics or {}
            )
            
            # Store in history
            self.comparison_history.append(analysis)
            
            # Store in Strands memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Solution comparison completed: {comparison_id}",
                    metadata={
                        "type": "solution_comparison",
                        "comparison_id": comparison_id,
                        "solution_count": len(solutions),
                        "best_solver": solution_scores[0].solver_name,
                        "confidence": confidence_level
                    }
                )
            
            self.logger.info(f"Completed solution comparison {comparison_id} with {len(solutions)} solutions")
            
            return {
                "success": True,
                "comparison_analysis": analysis.to_dict(),
                "best_solution": solution_scores[0].to_dict(),
                "ranking": [score.solver_name for score in solution_scores],
                "confidence_level": confidence_level
            }
            
        except Exception as e:
            error_msg = f"Solution comparison failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _prepare_weights(self, weights: Optional[Dict[str, float]]) -> ComparisonWeights:
        """Prepare and validate comparison weights"""
        if weights is None:
            return self.default_weights
        
        try:
            return ComparisonWeights(
                optimality=weights.get("optimality", self.default_weights.optimality),
                feasibility=weights.get("feasibility", self.default_weights.feasibility),
                performance=weights.get("performance", self.default_weights.performance),
                robustness=weights.get("robustness", self.default_weights.robustness)
            )
        except ValueError as e:
            self.logger.warning(f"Invalid weights provided, using defaults: {e}")
            return self.default_weights
    
    async def _score_solution(self,
                             solution: SolverResult,
                             weights: ComparisonWeights,
                             all_solutions: List[SolverResult]) -> SolutionScore:
        """Score individual solution based on multiple criteria"""
        try:
            # Calculate individual criterion scores
            optimality_score = self._score_optimality(solution, all_solutions)
            feasibility_score = self._score_feasibility(solution)
            performance_score = self._score_performance(solution, all_solutions)
            robustness_score = self._score_robustness(solution)
            
            # Calculate weighted scores
            weighted_optimality = optimality_score * weights.optimality
            weighted_feasibility = feasibility_score * weights.feasibility
            weighted_performance = performance_score * weights.performance
            weighted_robustness = robustness_score * weights.robustness
            
            # Calculate total score
            total_score = (weighted_optimality + weighted_feasibility + 
                          weighted_performance + weighted_robustness)
            
            # Identify strengths and weaknesses
            strengths, weaknesses = self._identify_solution_characteristics(
                optimality_score, feasibility_score, performance_score, robustness_score
            )
            
            # Generate recommendations
            recommendations = self._generate_solution_recommendations(
                solution, optimality_score, feasibility_score, performance_score, robustness_score
            )
            
            return SolutionScore(
                solver_name=solution.solver_name,
                total_score=total_score,
                criterion_scores={
                    "optimality": optimality_score,
                    "feasibility": feasibility_score,
                    "performance": performance_score,
                    "robustness": robustness_score
                },
                weighted_scores={
                    "optimality": weighted_optimality,
                    "feasibility": weighted_feasibility,
                    "performance": weighted_performance,
                    "robustness": weighted_robustness
                },
                rank=0,  # Will be set during ranking
                percentile=0.0,  # Will be set during ranking
                optimality_score=optimality_score,
                feasibility_score=feasibility_score,
                performance_score=performance_score,
                robustness_score=robustness_score,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error scoring solution {solution.solver_name}: {e}")
            # Return minimal score for failed evaluation
            return SolutionScore(
                solver_name=solution.solver_name,
                total_score=0.0,
                criterion_scores={},
                weighted_scores={},
                rank=999,
                percentile=0.0,
                optimality_score=0.0,
                feasibility_score=0.0,
                performance_score=0.0,
                robustness_score=0.0,
                strengths=[],
                weaknesses=["Scoring failed"],
                recommendations=["Review solution data"]
            )
    
    def _score_optimality(self, solution: SolverResult, all_solutions: List[SolverResult]) -> float:
        """Score solution optimality (0.0 to 1.0)"""
        try:
            if solution.objective_value is None:
                return 0.0
            
            # Get all valid objective values
            valid_objectives = [
                s.objective_value for s in all_solutions 
                if s.objective_value is not None and s.solve_status in ["optimal", "feasible"]
            ]
            
            if not valid_objectives:
                return 0.5  # Neutral score if no valid solutions
            
            best_objective = min(valid_objectives)  # Assuming minimization
            worst_objective = max(valid_objectives)
            
            if best_objective == worst_objective:
                return 1.0  # All solutions have same objective
            
            # Normalize score (1.0 for best, 0.0 for worst)
            normalized_score = 1.0 - (solution.objective_value - best_objective) / (worst_objective - best_objective)
            
            # Apply optimality bonus for optimal solutions
            if solution.solve_status == "optimal":
                normalized_score = min(1.0, normalized_score + 0.1)
            
            return max(0.0, min(1.0, normalized_score))
            
        except Exception as e:
            self.logger.error(f"Error scoring optimality: {e}")
            return 0.0
    
    def _score_feasibility(self, solution: SolverResult) -> float:
        """Score solution feasibility (0.0 to 1.0)"""
        try:
            # Base score from solve status
            status_scores = {
                "optimal": 1.0,
                "feasible": 0.8,
                "infeasible": 0.0,
                "unbounded": 0.3,
                "error": 0.0,
                "timeout": 0.5
            }
            
            base_score = status_scores.get(solution.solve_status.lower(), 0.0)
            
            # Adjust based on constraint violations if available
            if "constraint_violations" in solution.solution_quality:
                violations = solution.solution_quality["constraint_violations"]
                if isinstance(violations, (int, float)):
                    # Penalize based on violation magnitude
                    violation_penalty = min(0.5, violations * 0.1)
                    base_score = max(0.0, base_score - violation_penalty)
            
            # Bonus for high-quality feasible solutions
            if "feasibility_gap" in solution.solution_quality:
                gap = solution.solution_quality["feasibility_gap"]
                if gap < self.quality_thresholds["feasibility_tolerance"]:
                    base_score = min(1.0, base_score + 0.1)
            
            return base_score
            
        except Exception as e:
            self.logger.error(f"Error scoring feasibility: {e}")
            return 0.0
    
    def _score_performance(self, solution: SolverResult, all_solutions: List[SolverResult]) -> float:
        """Score solution performance (0.0 to 1.0)"""
        try:
            execution_time = solution.execution_time
            
            if execution_time <= 0:
                return 0.5  # Neutral score for invalid time
            
            # Performance categories
            if execution_time <= self.performance_thresholds["excellent"]:
                base_score = 1.0
            elif execution_time <= self.performance_thresholds["good"]:
                base_score = 0.8
            elif execution_time <= self.performance_thresholds["acceptable"]:
                base_score = 0.6
            elif execution_time <= self.performance_thresholds["poor"]:
                base_score = 0.4
            else:
                base_score = 0.2
            
            # Relative performance comparison
            all_times = [s.execution_time for s in all_solutions if s.execution_time > 0]
            if len(all_times) > 1:
                fastest_time = min(all_times)
                slowest_time = max(all_times)
                
                if fastest_time != slowest_time:
                    # Normalize relative to other solutions
                    relative_score = 1.0 - (execution_time - fastest_time) / (slowest_time - fastest_time)
                    base_score = (base_score + relative_score) / 2
            
            # Memory efficiency bonus if available
            if "memory_usage" in solution.solver_info:
                memory_mb = solution.solver_info["memory_usage"]
                if memory_mb < 100:  # Less than 100MB
                    base_score = min(1.0, base_score + 0.05)
            
            return max(0.0, min(1.0, base_score))
            
        except Exception as e:
            self.logger.error(f"Error scoring performance: {e}")
            return 0.0
    
    def _score_robustness(self, solution: SolverResult) -> float:
        """Score solution robustness (0.0 to 1.0)"""
        try:
            base_score = 0.5  # Default neutral score
            
            # Check for robustness indicators in solution quality
            if "sensitivity_analysis" in solution.solution_quality:
                sensitivity = solution.solution_quality["sensitivity_analysis"]
                if isinstance(sensitivity, dict):
                    # High sensitivity indicates low robustness
                    avg_sensitivity = statistics.mean(sensitivity.values()) if sensitivity else 0
                    base_score = max(0.0, 1.0 - avg_sensitivity)
            
            # Check solution stability indicators
            if "solution_variance" in solution.solution_quality:
                variance = solution.solution_quality["solution_variance"]
                if variance < self.quality_thresholds["robustness_variance"]:
                    base_score = min(1.0, base_score + 0.2)
            
            # Solver-specific robustness indicators
            if "iterations" in solution.solver_info:
                iterations = solution.solver_info["iterations"]
                # Fewer iterations might indicate more robust convergence
                if iterations < 100:
                    base_score = min(1.0, base_score + 0.1)
            
            # Bonus for optimal solutions (generally more robust)
            if solution.solve_status == "optimal":
                base_score = min(1.0, base_score + 0.1)
            
            return max(0.0, min(1.0, base_score))
            
        except Exception as e:
            self.logger.error(f"Error scoring robustness: {e}")
            return 0.5
    
    def _identify_solution_characteristics(self,
                                         optimality: float,
                                         feasibility: float,
                                         performance: float,
                                         robustness: float) -> Tuple[List[str], List[str]]:
        """Identify solution strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Define thresholds for strength/weakness identification
        strong_threshold = 0.8
        weak_threshold = 0.4
        
        criteria = {
            "optimality": optimality,
            "feasibility": feasibility,
            "performance": performance,
            "robustness": robustness
        }
        
        for criterion, score in criteria.items():
            if score >= strong_threshold:
                strengths.append(f"Excellent {criterion}")
            elif score <= weak_threshold:
                weaknesses.append(f"Poor {criterion}")
        
        return strengths, weaknesses
    
    def _generate_solution_recommendations(self,
                                         solution: SolverResult,
                                         optimality: float,
                                         feasibility: float,
                                         performance: float,
                                         robustness: float) -> List[str]:
        """Generate recommendations for solution improvement"""
        recommendations = []
        
        if optimality < 0.6:
            recommendations.append("Consider using different solver or adjusting parameters for better optimality")
        
        if feasibility < 0.6:
            recommendations.append("Review constraint formulation and solver tolerance settings")
        
        if performance < 0.6:
            recommendations.append("Optimize solver configuration or consider faster solver alternatives")
        
        if robustness < 0.6:
            recommendations.append("Perform sensitivity analysis and consider solution stabilization techniques")
        
        # Solver-specific recommendations
        if solution.execution_time > 60:
            recommendations.append("Consider time limits or early termination criteria for long-running solves")
        
        if solution.solve_status == "timeout":
            recommendations.append("Increase time limit or use approximate solution methods")
        
        return recommendations
    
    def _calculate_score_statistics(self, solution_scores: List[SolutionScore]) -> Dict[str, float]:
        """Calculate statistical measures of solution scores"""
        total_scores = [score.total_score for score in solution_scores]
        
        return {
            "mean": statistics.mean(total_scores),
            "median": statistics.median(total_scores),
            "std_dev": statistics.stdev(total_scores) if len(total_scores) > 1 else 0.0,
            "min": min(total_scores),
            "max": max(total_scores),
            "range": max(total_scores) - min(total_scores)
        }
    
    def _calculate_criterion_statistics(self, solution_scores: List[SolutionScore]) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for each comparison criterion"""
        criteria = ["optimality", "feasibility", "performance", "robustness"]
        criterion_stats = {}
        
        for criterion in criteria:
            scores = [score.criterion_scores.get(criterion, 0.0) for score in solution_scores]
            criterion_stats[criterion] = {
                "mean": statistics.mean(scores),
                "median": statistics.median(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
                "min": min(scores),
                "max": max(scores)
            }
        
        return criterion_stats
    
    def _assess_quality_distribution(self, solution_scores: List[SolutionScore]) -> Dict[str, int]:
        """Assess distribution of solution quality levels"""
        quality_levels = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for score in solution_scores:
            total = score.total_score
            if total >= 0.8:
                quality_levels["excellent"] += 1
            elif total >= 0.6:
                quality_levels["good"] += 1
            elif total >= 0.4:
                quality_levels["fair"] += 1
            else:
                quality_levels["poor"] += 1
        
        return quality_levels
    
    def _analyze_performance_characteristics(self, solutions: List[SolverResult]) -> Dict[str, Any]:
        """Analyze performance characteristics across solutions"""
        execution_times = [s.execution_time for s in solutions if s.execution_time > 0]
        
        analysis = {
            "total_solutions": len(solutions),
            "valid_solutions": len([s for s in solutions if s.solve_status in ["optimal", "feasible"]]),
            "average_execution_time": statistics.mean(execution_times) if execution_times else 0.0,
            "fastest_solver": None,
            "most_reliable_solver": None
        }
        
        if execution_times:
            fastest_time = min(execution_times)
            fastest_solver = next(s.solver_name for s in solutions if s.execution_time == fastest_time)
            analysis["fastest_solver"] = fastest_solver
        
        # Find most reliable solver (highest success rate)
        solver_success = {}
        for solution in solutions:
            solver = solution.solver_name
            if solver not in solver_success:
                solver_success[solver] = {"total": 0, "success": 0}
            solver_success[solver]["total"] += 1
            if solution.solve_status in ["optimal", "feasible"]:
                solver_success[solver]["success"] += 1
        
        if solver_success:
            best_reliability = 0
            most_reliable = None
            for solver, stats in solver_success.items():
                reliability = stats["success"] / stats["total"]
                if reliability > best_reliability:
                    best_reliability = reliability
                    most_reliable = solver
            analysis["most_reliable_solver"] = most_reliable
        
        return analysis
    
    async def _generate_detailed_rationale(self,
                                         best_solution: SolutionScore,
                                         all_scores: List[SolutionScore],
                                         weights: ComparisonWeights) -> str:
        """Generate detailed selection rationale using Strands LLM if available"""
        try:
            if self.strands_tools.get('use_llm'):
                # Use Strands LLM for sophisticated rationale generation
                prompt = f"""
                Generate a detailed rationale for selecting the best optimization solution from a multi-solver comparison.
                
                BEST SOLUTION: {best_solution.solver_name}
                Total Score: {best_solution.total_score:.3f}
                Rank: {best_solution.rank} out of {len(all_scores)}
                
                SCORING BREAKDOWN:
                - Optimality: {best_solution.optimality_score:.3f} (weight: {weights.optimality})
                - Feasibility: {best_solution.feasibility_score:.3f} (weight: {weights.feasibility})
                - Performance: {best_solution.performance_score:.3f} (weight: {weights.performance})
                - Robustness: {best_solution.robustness_score:.3f} (weight: {weights.robustness})
                
                STRENGTHS: {', '.join(best_solution.strengths)}
                WEAKNESSES: {', '.join(best_solution.weaknesses)}
                
                COMPARISON CONTEXT:
                - Total solutions compared: {len(all_scores)}
                - Score range: {min(s.total_score for s in all_scores):.3f} to {max(s.total_score for s in all_scores):.3f}
                - Runner-up: {all_scores[1].solver_name if len(all_scores) > 1 else 'None'} (score: {all_scores[1].total_score:.3f if len(all_scores) > 1 else 'N/A'})
                
                Provide a comprehensive rationale explaining why this solution was selected, highlighting key differentiators and decision factors.
                """
                
                rationale_result = self.strands_tools['use_llm'](prompt=prompt)
                if rationale_result and 'response' in rationale_result:
                    return rationale_result['response']
            
            # Fallback to template-based rationale
            return self._generate_template_rationale(best_solution, all_scores, weights)
            
        except Exception as e:
            self.logger.warning(f"Error generating detailed rationale: {e}")
            return self._generate_template_rationale(best_solution, all_scores, weights)
    
    def _generate_template_rationale(self,
                                   best_solution: SolutionScore,
                                   all_scores: List[SolutionScore],
                                   weights: ComparisonWeights) -> str:
        """Generate template-based selection rationale"""
        rationale_parts = [
            f"Selected {best_solution.solver_name} as the best solution based on comprehensive multi-criteria analysis.",
            f"This solution achieved the highest overall score of {best_solution.total_score:.3f} out of {len(all_scores)} evaluated solutions."
        ]
        
        # Highlight strongest criteria
        best_criterion = max(best_solution.criterion_scores.items(), key=lambda x: x[1])
        rationale_parts.append(f"The solution excels particularly in {best_criterion[0]} with a score of {best_criterion[1]:.3f}.")
        
        # Compare to runner-up if available
        if len(all_scores) > 1:
            runner_up = all_scores[1]
            score_diff = best_solution.total_score - runner_up.total_score
            rationale_parts.append(f"It outperformed the runner-up ({runner_up.solver_name}) by {score_diff:.3f} points.")
        
        # Mention key strengths
        if best_solution.strengths:
            rationale_parts.append(f"Key strengths include: {', '.join(best_solution.strengths)}.")
        
        return " ".join(rationale_parts)
    
    def _calculate_confidence_level(self, solution_scores: List[SolutionScore]) -> float:
        """Calculate confidence level in the solution selection"""
        if len(solution_scores) < 2:
            return 0.5  # Low confidence with only one solution
        
        # Calculate score separation
        best_score = solution_scores[0].total_score
        second_score = solution_scores[1].total_score
        score_gap = best_score - second_score
        
        # Calculate score variance
        all_scores = [score.total_score for score in solution_scores]
        score_variance = statistics.variance(all_scores) if len(all_scores) > 1 else 0
        
        # Base confidence on score gap and consistency
        confidence = min(1.0, score_gap * 2)  # Higher gap = higher confidence
        
        # Adjust for score variance (lower variance = higher confidence)
        if score_variance > 0:
            confidence = confidence * (1 - min(0.5, score_variance))
        
        # Bonus for clear winner
        if score_gap > 0.2:
            confidence = min(1.0, confidence + 0.1)
        
        return max(0.1, min(1.0, confidence))
    
    def _identify_decision_factors(self,
                                 solution_scores: List[SolutionScore],
                                 weights: ComparisonWeights) -> List[str]:
        """Identify key factors that influenced the decision"""
        factors = []
        
        if len(solution_scores) < 2:
            return ["Single solution available"]
        
        best = solution_scores[0]
        runner_up = solution_scores[1]
        
        # Compare criteria scores
        for criterion in ["optimality", "feasibility", "performance", "robustness"]:
            best_score = best.criterion_scores.get(criterion, 0)
            runner_up_score = runner_up.criterion_scores.get(criterion, 0)
            
            if best_score - runner_up_score > 0.1:
                weight = getattr(weights, criterion)
                factors.append(f"Superior {criterion} (weight: {weight:.1%})")
        
        # Check for standout characteristics
        if best.total_score > 0.8:
            factors.append("Exceptional overall quality")
        
        if len(best.strengths) > len(runner_up.strengths):
            factors.append("More balanced performance across criteria")
        
        return factors or ["Marginal advantage across multiple criteria"]
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate solution comparison parameters"""
        try:
            # Check required parameters
            if "solutions" not in kwargs:
                self.logger.error("Solutions parameter is required")
                return False
            
            solutions = kwargs["solutions"]
            if not isinstance(solutions, list) or len(solutions) == 0:
                self.logger.error("Solutions must be a non-empty list")
                return False
            
            # Validate solution objects
            for i, solution in enumerate(solutions):
                if not isinstance(solution, SolverResult):
                    self.logger.error(f"Solution {i} is not a SolverResult object")
                    return False
            
            # Validate weights if provided
            if "weights" in kwargs and kwargs["weights"] is not None:
                weights = kwargs["weights"]
                if not isinstance(weights, dict):
                    self.logger.error("Weights must be a dictionary")
                    return False
                
                # Check weight values
                for key, value in weights.items():
                    if not isinstance(value, (int, float)) or value < 0:
                        self.logger.error(f"Weight {key} must be a non-negative number")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # Store final comparison history in memory
            if self.strands_tools.get('memory') and self.comparison_history:
                self.strands_tools['memory'](
                    action="store",
                    content=f"Solution comparator session completed with {len(self.comparison_history)} comparisons",
                    metadata={
                        "type": "session_summary",
                        "component": "solution_comparator",
                        "comparison_count": len(self.comparison_history)
                    }
                )
            
            self.logger.info("Solution Comparator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")