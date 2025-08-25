"""
Comprehensive Performance Analytics System
=========================================

Implements comprehensive performance tracking, analysis, and benchmarking system
for multi-solver swarm optimization with historical analysis and trend identification.

Features:
- PerformanceAnalyzer class for solver performance tracking and analysis
- Solver benchmarking system with standardized test problems
- Performance metrics collection (solve time, memory usage, solution quality)
- Historical performance analysis and trend identification
- Machine learning-based performance prediction and optimization

Requirements: 4.1, 4.2, 4.3
"""

import logging
import asyncio
import json
import time
import statistics
import threading
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
        def percentile(data, percentile):
            if not data:
                return 0
            sorted_data = sorted(data)
            index = int(len(sorted_data) * percentile / 100)
            return sorted_data[min(index, len(sorted_data) - 1)]

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid
import pickle
import os
from pathlib import Path

try:
    from strands import Agent
    from strands_tools import memory, retrieve, use_aws, think, use_llm
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False

from ..utils.base import BaseTool, ToolExecutionError, ToolInitializationError
from .solver_tool import SolverResult, ModelSpecification
from .enhanced_solver_registry import EnhancedSolverRegistry, SolverCapability
from .solution_comparator import SolutionComparator

logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    """Types of performance metrics"""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    SOLUTION_QUALITY = "solution_quality"
    SUCCESS_RATE = "success_rate"
    CONVERGENCE_RATE = "convergence_rate"
    SCALABILITY = "scalability"
    ROBUSTNESS = "robustness"


class BenchmarkCategory(Enum):
    """Categories of benchmark problems"""
    SMALL_LINEAR = "small_linear"
    MEDIUM_LINEAR = "medium_linear"
    LARGE_LINEAR = "large_linear"
    SMALL_MIP = "small_mip"
    MEDIUM_MIP = "medium_mip"
    LARGE_MIP = "large_mip"
    CONSTRAINT_PROGRAMMING = "constraint_programming"
    NONLINEAR = "nonlinear"
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    FINANCE = "finance"


@dataclass
class PerformanceMetric:
    """Individual performance metric data point"""
    metric_id: str
    solver_name: str
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    problem_characteristics: Dict[str, Any]
    execution_context: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['metric_type'] = self.metric_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class BenchmarkProblem:
    """Standardized benchmark problem definition"""
    problem_id: str
    name: str
    category: BenchmarkCategory
    description: str
    problem_size: Dict[str, int]  # variables, constraints, etc.
    expected_optimal_value: Optional[float]
    time_limit: float
    memory_limit: float
    difficulty_level: int  # 1-5 scale
    problem_data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['category'] = self.category.value
        return result


@dataclass
class BenchmarkResult:
    """Results from running a benchmark problem"""
    benchmark_id: str
    problem_id: str
    solver_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    solution_quality: float
    success: bool
    optimal_gap: Optional[float]
    iterations: Optional[int]
    solver_status: str
    timestamp: datetime
    detailed_metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class PerformanceAnalysis:
    """Comprehensive performance analysis results"""
    analysis_id: str
    solver_name: str
    time_period: Tuple[datetime, datetime]
    total_executions: int
    
    # Performance statistics
    avg_execution_time: float
    median_execution_time: float
    p95_execution_time: float
    execution_time_trend: str  # "improving", "degrading", "stable"
    
    avg_memory_usage: float
    peak_memory_usage: float
    memory_efficiency_score: float
    
    avg_solution_quality: float
    quality_consistency: float
    quality_trend: str
    
    success_rate: float
    reliability_score: float
    
    # Comparative analysis
    relative_performance: Dict[str, float]  # vs other solvers
    performance_rank: int
    
    # Trend analysis
    performance_trends: Dict[str, List[float]]
    trend_predictions: Dict[str, float]
    
    # Recommendations
    optimization_recommendations: List[str]
    configuration_suggestions: Dict[str, Any]
    
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['time_period'] = [self.time_period[0].isoformat(), self.time_period[1].isoformat()]
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    metric_type: PerformanceMetricType
    solver_name: str
    trend_direction: str  # "improving", "degrading", "stable"
    trend_strength: float  # 0-1 scale
    trend_confidence: float  # 0-1 scale
    slope: float
    r_squared: float
    prediction_accuracy: float
    future_predictions: List[Tuple[datetime, float]]
    anomalies_detected: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['metric_type'] = self.metric_type.value
        result['future_predictions'] = [(dt.isoformat(), val) for dt, val in self.future_predictions]
        return result


class PerformanceAnalyzer(BaseTool):
    """
    Comprehensive Performance Analytics System for multi-solver optimization
    
    Provides:
    - Real-time performance tracking and metrics collection
    - Comprehensive benchmarking with standardized test problems
    - Historical performance analysis and trend identification
    - Machine learning-based performance prediction
    - Comparative analysis across solvers
    - Performance optimization recommendations
    """
    
    def __init__(self):
        super().__init__(
            name="performance_analyzer",
            description="Comprehensive performance analytics system for multi-solver optimization",
            version="1.0.0"
        )
        
        # Core components
        self.solver_registry = None
        self.solution_comparator = None
        
        # Performance data storage
        self.performance_metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.benchmark_results: Dict[str, List[BenchmarkResult]] = defaultdict(list)
        self.analysis_history: List[PerformanceAnalysis] = []
        self.trend_analyses: Dict[str, List[TrendAnalysis]] = defaultdict(list)
        
        # Benchmark problems
        self.benchmark_problems: Dict[str, BenchmarkProblem] = {}
        
        # Strands integration
        self.strands_agent = None
        self.strands_tools = {}
        
        # Configuration
        self.data_retention_days = 90
        self.analysis_window_days = 30
        self.trend_analysis_min_points = 10
        
        # Performance thresholds
        self.performance_thresholds = {
            "execution_time": {"excellent": 1.0, "good": 10.0, "acceptable": 60.0},
            "memory_usage": {"excellent": 100.0, "good": 500.0, "acceptable": 2000.0},  # MB
            "solution_quality": {"excellent": 0.95, "good": 0.85, "acceptable": 0.70},
            "success_rate": {"excellent": 0.98, "good": 0.90, "acceptable": 0.80}
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Data persistence
        self.data_dir = Path("data/performance_analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> bool:
        """Initialize the Performance Analyzer"""
        try:
            # Initialize solver registry
            self.solver_registry = EnhancedSolverRegistry()
            
            # Initialize solution comparator
            self.solution_comparator = SolutionComparator()
            await self.solution_comparator.initialize()
            
            # Initialize Strands integration
            await self._initialize_strands_integration()
            
            # Initialize benchmark problems
            await self._initialize_benchmark_problems()
            
            # Load historical data
            await self._load_historical_data()
            
            # Start background analysis tasks
            await self._start_background_tasks()
            
            self._initialized = True
            self.logger.info("Performance Analyzer initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Performance Analyzer: {e}")
            return False
    
    async def _initialize_strands_integration(self):
        """Initialize Strands tools integration"""
        if not STRANDS_AVAILABLE:
            self.logger.warning("Strands not available - using fallback implementation")
            return
        
        try:
            self.strands_agent = Agent(
                name="performance_analyzer",
                system_prompt="""You are a performance analytics expert specializing in optimization solver analysis.
                
                Your expertise includes:
                1. Analyzing solver performance metrics across multiple dimensions
                2. Identifying performance trends and patterns in historical data
                3. Benchmarking solvers against standardized test problems
                4. Providing optimization recommendations based on performance analysis
                5. Predicting future performance based on historical trends
                
                PERFORMANCE ANALYSIS AREAS:
                
                Execution Performance:
                - Solve time analysis and optimization
                - Memory usage patterns and efficiency
                - CPU utilization and resource management
                - Scalability characteristics across problem sizes
                
                Solution Quality:
                - Optimality gap analysis and improvement
                - Solution consistency and reliability
                - Convergence behavior and stability
                - Robustness under different conditions
                
                Comparative Analysis:
                - Solver ranking and relative performance
                - Problem-specific solver recommendations
                - Performance trade-off analysis
                - Best-fit solver selection criteria
                
                Trend Analysis:
                - Historical performance trend identification
                - Performance degradation detection
                - Improvement opportunity identification
                - Future performance prediction
                
                Always provide data-driven insights with statistical confidence measures and actionable recommendations.
                Store all analysis results in memory for continuous learning and improvement.""",
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
    
    async def _initialize_benchmark_problems(self):
        """Initialize standardized benchmark problems"""
        try:
            # Small Linear Programming Problems
            self.benchmark_problems["small_lp_1"] = BenchmarkProblem(
                problem_id="small_lp_1",
                name="Small Linear Programming - Production Planning",
                category=BenchmarkCategory.SMALL_LINEAR,
                description="Simple production planning with 5 products and 3 resources",
                problem_size={"variables": 5, "constraints": 3, "nonzeros": 15},
                expected_optimal_value=1250.0,
                time_limit=10.0,
                memory_limit=100.0,
                difficulty_level=1,
                problem_data={
                    "variables": [
                        {"name": "x1", "type": "continuous", "lb": 0, "ub": 100, "obj_coeff": 40},
                        {"name": "x2", "type": "continuous", "lb": 0, "ub": 100, "obj_coeff": 30},
                        {"name": "x3", "type": "continuous", "lb": 0, "ub": 100, "obj_coeff": 50},
                        {"name": "x4", "type": "continuous", "lb": 0, "ub": 100, "obj_coeff": 25},
                        {"name": "x5", "type": "continuous", "lb": 0, "ub": 100, "obj_coeff": 35}
                    ],
                    "constraints": [
                        {"name": "resource_1", "type": "<=", "rhs": 200, "coeffs": {"x1": 2, "x2": 1, "x3": 3, "x4": 1, "x5": 2}},
                        {"name": "resource_2", "type": "<=", "rhs": 150, "coeffs": {"x1": 1, "x2": 2, "x3": 1, "x4": 3, "x5": 1}},
                        {"name": "resource_3", "type": "<=", "rhs": 180, "coeffs": {"x1": 3, "x2": 1, "x3": 2, "x4": 1, "x5": 3}}
                    ],
                    "objective": {"sense": "maximize", "type": "linear"}
                },
                metadata={"domain": "manufacturing", "complexity": "low"}
            )
            
            # Medium Linear Programming Problem
            self.benchmark_problems["medium_lp_1"] = BenchmarkProblem(
                problem_id="medium_lp_1",
                name="Medium Linear Programming - Multi-Product Planning",
                category=BenchmarkCategory.MEDIUM_LINEAR,
                description="Multi-product planning with 20 products and 15 constraints",
                problem_size={"variables": 20, "constraints": 15, "nonzeros": 200},
                expected_optimal_value=5420.0,
                time_limit=30.0,
                memory_limit=200.0,
                difficulty_level=3,
                problem_data=self._generate_medium_lp_problem(),
                metadata={"domain": "manufacturing", "complexity": "medium"}
            )
            
            # Small Mixed-Integer Problem
            self.benchmark_problems["small_mip_1"] = BenchmarkProblem(
                problem_id="small_mip_1",
                name="Small MIP - Facility Location",
                category=BenchmarkCategory.SMALL_MIP,
                description="Facility location problem with 5 facilities and 10 customers",
                problem_size={"variables": 15, "constraints": 20, "integer_vars": 5},
                expected_optimal_value=2850.0,
                time_limit=60.0,
                memory_limit=300.0,
                difficulty_level=2,
                problem_data=self._generate_facility_location_problem(),
                metadata={"domain": "logistics", "complexity": "medium"}
            )
            
            # Manufacturing Scheduling Problem
            self.benchmark_problems["manufacturing_scheduling"] = BenchmarkProblem(
                problem_id="manufacturing_scheduling",
                name="Manufacturing Job Shop Scheduling",
                category=BenchmarkCategory.MANUFACTURING,
                description="Job shop scheduling with 10 jobs and 5 machines",
                problem_size={"variables": 50, "constraints": 100, "integer_vars": 50},
                expected_optimal_value=None,  # No known optimal
                time_limit=120.0,
                memory_limit=500.0,
                difficulty_level=4,
                problem_data=self._generate_scheduling_problem(),
                metadata={"domain": "manufacturing", "complexity": "high"}
            )
            
            # Large Linear Programming Problem
            self.benchmark_problems["large_lp_1"] = BenchmarkProblem(
                problem_id="large_lp_1",
                name="Large Linear Programming - Supply Chain",
                category=BenchmarkCategory.LARGE_LINEAR,
                description="Large-scale supply chain optimization with 100 variables",
                problem_size={"variables": 100, "constraints": 50, "nonzeros": 1000},
                expected_optimal_value=None,  # To be determined
                time_limit=300.0,
                memory_limit=1000.0,
                difficulty_level=5,
                problem_data=self._generate_large_lp_problem(),
                metadata={"domain": "supply_chain", "complexity": "high"}
            )
            
            self.logger.info(f"Initialized {len(self.benchmark_problems)} benchmark problems")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize benchmark problems: {e}")
    
    def _generate_medium_lp_problem(self) -> Dict[str, Any]:
        """Generate medium-sized linear programming problem"""
        variables = []
        for i in range(20):
            variables.append({
                "name": f"x{i+1}",
                "type": "continuous",
                "lb": 0,
                "ub": 50,
                "obj_coeff": np.random.uniform(10, 100)
            })
        
        constraints = []
        for i in range(15):
            coeffs = {}
            for j in range(20):
                if np.random.random() < 0.3:  # 30% sparsity
                    coeffs[f"x{j+1}"] = np.random.uniform(0.1, 5.0)
            
            constraints.append({
                "name": f"constraint_{i+1}",
                "type": "<=",
                "rhs": np.random.uniform(50, 200),
                "coeffs": coeffs
            })
        
        return {
            "variables": variables,
            "constraints": constraints,
            "objective": {"sense": "maximize", "type": "linear"}
        }
    
    def _generate_facility_location_problem(self) -> Dict[str, Any]:
        """Generate facility location MIP problem"""
        # 5 binary facility variables + 10 continuous flow variables
        variables = []
        
        # Facility variables
        for i in range(5):
            variables.append({
                "name": f"facility_{i+1}",
                "type": "binary",
                "lb": 0,
                "ub": 1,
                "obj_coeff": -np.random.uniform(100, 500)  # Fixed costs
            })
        
        # Flow variables
        for i in range(5):
            for j in range(10):
                variables.append({
                    "name": f"flow_{i+1}_{j+1}",
                    "type": "continuous",
                    "lb": 0,
                    "ub": 100,
                    "obj_coeff": np.random.uniform(1, 10)  # Transport costs
                })
        
        constraints = []
        
        # Demand constraints
        for j in range(10):
            coeffs = {}
            for i in range(5):
                coeffs[f"flow_{i+1}_{j+1}"] = 1
            constraints.append({
                "name": f"demand_{j+1}",
                "type": ">=",
                "rhs": np.random.uniform(10, 30),
                "coeffs": coeffs
            })
        
        # Capacity constraints
        for i in range(5):
            coeffs = {f"facility_{i+1}": -1000}  # Big M
            for j in range(10):
                coeffs[f"flow_{i+1}_{j+1}"] = 1
            constraints.append({
                "name": f"capacity_{i+1}",
                "type": "<=",
                "rhs": 0,
                "coeffs": coeffs
            })
        
        return {
            "variables": variables,
            "constraints": constraints,
            "objective": {"sense": "minimize", "type": "linear"}
        }
    
    def _generate_scheduling_problem(self) -> Dict[str, Any]:
        """Generate job shop scheduling problem"""
        # Simplified representation for benchmarking
        jobs = 10
        machines = 5
        
        variables = []
        for j in range(jobs):
            for m in range(machines):
                variables.append({
                    "name": f"start_{j+1}_{m+1}",
                    "type": "continuous",
                    "lb": 0,
                    "ub": 1000,
                    "obj_coeff": 0
                })
        
        # Makespan variable
        variables.append({
            "name": "makespan",
            "type": "continuous",
            "lb": 0,
            "ub": 1000,
            "obj_coeff": 1
        })
        
        constraints = []
        # Simplified constraints for benchmarking
        for j in range(jobs):
            for m in range(machines-1):
                constraints.append({
                    "name": f"precedence_{j+1}_{m+1}",
                    "type": "<=",
                    "rhs": -np.random.uniform(5, 20),
                    "coeffs": {
                        f"start_{j+1}_{m+1}": 1,
                        f"start_{j+1}_{m+2}": -1
                    }
                })
        
        return {
            "variables": variables,
            "constraints": constraints,
            "objective": {"sense": "minimize", "type": "linear"}
        }
    
    def _generate_large_lp_problem(self) -> Dict[str, Any]:
        """Generate large-scale linear programming problem"""
        variables = []
        for i in range(100):
            variables.append({
                "name": f"x{i+1}",
                "type": "continuous",
                "lb": 0,
                "ub": 100,
                "obj_coeff": np.random.uniform(1, 50)
            })
        
        constraints = []
        for i in range(50):
            coeffs = {}
            for j in range(100):
                if np.random.random() < 0.2:  # 20% sparsity
                    coeffs[f"x{j+1}"] = np.random.uniform(0.1, 10.0)
            
            constraints.append({
                "name": f"constraint_{i+1}",
                "type": "<=",
                "rhs": np.random.uniform(100, 1000),
                "coeffs": coeffs
            })
        
        return {
            "variables": variables,
            "constraints": constraints,
            "objective": {"sense": "maximize", "type": "linear"}
        }
    
    async def _load_historical_data(self):
        """Load historical performance data from storage"""
        try:
            # Load performance metrics
            metrics_file = self.data_dir / "performance_metrics.pkl"
            if metrics_file.exists():
                with open(metrics_file, 'rb') as f:
                    self.performance_metrics = pickle.load(f)
                self.logger.info(f"Loaded {sum(len(metrics) for metrics in self.performance_metrics.values())} historical performance metrics")
            
            # Load benchmark results
            benchmarks_file = self.data_dir / "benchmark_results.pkl"
            if benchmarks_file.exists():
                with open(benchmarks_file, 'rb') as f:
                    self.benchmark_results = pickle.load(f)
                self.logger.info(f"Loaded {sum(len(results) for results in self.benchmark_results.values())} historical benchmark results")
            
            # Load analysis history
            analysis_file = self.data_dir / "analysis_history.pkl"
            if analysis_file.exists():
                with open(analysis_file, 'rb') as f:
                    self.analysis_history = pickle.load(f)
                self.logger.info(f"Loaded {len(self.analysis_history)} historical analyses")
            
        except Exception as e:
            self.logger.warning(f"Could not load historical data: {e}")
    
    async def _start_background_tasks(self):
        """Start background analysis tasks"""
        try:
            # Start periodic data cleanup
            asyncio.create_task(self._periodic_data_cleanup())
            
            # Start periodic trend analysis
            asyncio.create_task(self._periodic_trend_analysis())
            
            self.logger.info("Background analysis tasks started")
            
        except Exception as e:
            self.logger.warning(f"Could not start background tasks: {e}")
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute performance analysis operations"""
        operation = kwargs.get("operation", "analyze_performance")
        
        if operation == "analyze_performance":
            return await self._analyze_solver_performance(**kwargs)
        elif operation == "run_benchmarks":
            return await self._run_solver_benchmarks(**kwargs)
        elif operation == "collect_metrics":
            return await self._collect_performance_metrics(**kwargs)
        elif operation == "analyze_trends":
            return await self._analyze_performance_trends(**kwargs)
        elif operation == "compare_solvers":
            return await self._compare_solver_performance(**kwargs)
        elif operation == "generate_report":
            return await self._generate_performance_report(**kwargs)
        elif operation == "predict_performance":
            return await self._predict_future_performance(**kwargs)
        elif operation == "get_recommendations":
            return await self._get_optimization_recommendations(**kwargs)
        else:
            raise ToolExecutionError(f"Unknown operation: {operation}", self.name)
    
    async def _analyze_solver_performance(self,
                                        solver_name: str,
                                        time_period: Optional[str] = None,
                                        **kwargs) -> Dict[str, Any]:
        """Analyze comprehensive performance for a specific solver"""
        try:
            # Determine time period
            if time_period == "last_week":
                start_time = datetime.now() - timedelta(days=7)
            elif time_period == "last_month":
                start_time = datetime.now() - timedelta(days=30)
            elif time_period == "last_quarter":
                start_time = datetime.now() - timedelta(days=90)
            else:
                start_time = datetime.now() - timedelta(days=self.analysis_window_days)
            
            end_time = datetime.now()
            
            # Get performance metrics for the solver
            solver_metrics = self.performance_metrics.get(solver_name, [])
            period_metrics = [
                m for m in solver_metrics 
                if start_time <= m.timestamp <= end_time
            ]
            
            if not period_metrics:
                return {
                    "success": False,
                    "error": f"No performance data found for solver {solver_name} in specified period",
                    "solver_name": solver_name,
                    "time_period": [start_time.isoformat(), end_time.isoformat()]
                }
            
            # Calculate performance statistics
            execution_times = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.EXECUTION_TIME]
            memory_usages = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.MEMORY_USAGE]
            quality_scores = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.SOLUTION_QUALITY]
            success_rates = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.SUCCESS_RATE]
            
            # Execution time analysis
            avg_execution_time = statistics.mean(execution_times) if execution_times else 0
            median_execution_time = statistics.median(execution_times) if execution_times else 0
            p95_execution_time = np.percentile(execution_times, 95) if execution_times else 0
            
            # Memory analysis
            avg_memory_usage = statistics.mean(memory_usages) if memory_usages else 0
            peak_memory_usage = max(memory_usages) if memory_usages else 0
            
            # Quality analysis
            avg_solution_quality = statistics.mean(quality_scores) if quality_scores else 0
            quality_consistency = 1.0 - (statistics.stdev(quality_scores) / avg_solution_quality if quality_scores and avg_solution_quality > 0 else 0)
            
            # Success rate analysis
            overall_success_rate = statistics.mean(success_rates) if success_rates else 0
            
            # Trend analysis
            execution_time_trend = self._calculate_trend(execution_times, [m.timestamp for m in period_metrics if m.metric_type == PerformanceMetricType.EXECUTION_TIME])
            quality_trend = self._calculate_trend(quality_scores, [m.timestamp for m in period_metrics if m.metric_type == PerformanceMetricType.SOLUTION_QUALITY])
            
            # Comparative analysis
            relative_performance = await self._calculate_relative_performance(solver_name, start_time, end_time)
            performance_rank = await self._calculate_performance_rank(solver_name, start_time, end_time)
            
            # Generate recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(
                solver_name, avg_execution_time, avg_memory_usage, avg_solution_quality, overall_success_rate
            )
            
            # Create comprehensive analysis (without configuration suggestions first)
            analysis = PerformanceAnalysis(
                analysis_id=str(uuid.uuid4()),
                solver_name=solver_name,
                time_period=(start_time, end_time),
                total_executions=len(period_metrics),
                avg_execution_time=avg_execution_time,
                median_execution_time=median_execution_time,
                p95_execution_time=p95_execution_time,
                execution_time_trend=execution_time_trend,
                avg_memory_usage=avg_memory_usage,
                peak_memory_usage=peak_memory_usage,
                memory_efficiency_score=self._calculate_memory_efficiency_score(avg_memory_usage, peak_memory_usage),
                avg_solution_quality=avg_solution_quality,
                quality_consistency=quality_consistency,
                quality_trend=quality_trend,
                success_rate=overall_success_rate,
                reliability_score=self._calculate_reliability_score(overall_success_rate, quality_consistency),
                relative_performance=relative_performance,
                performance_rank=performance_rank,
                performance_trends={
                    "execution_time": execution_times[-10:] if len(execution_times) >= 10 else execution_times,
                    "memory_usage": memory_usages[-10:] if len(memory_usages) >= 10 else memory_usages,
                    "solution_quality": quality_scores[-10:] if len(quality_scores) >= 10 else quality_scores
                },
                trend_predictions=await self._predict_trends(solver_name, period_metrics),
                optimization_recommendations=optimization_recommendations,
                configuration_suggestions={},  # Will be filled below
                timestamp=datetime.now()
            )
            
            # Generate configuration suggestions now that analysis exists
            analysis.configuration_suggestions = await self._generate_configuration_suggestions(solver_name, analysis)
            
            # Store analysis
            self.analysis_history.append(analysis)
            
            # Store in Strands memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Performance analysis completed for {solver_name}",
                    metadata={
                        "type": "performance_analysis",
                        "solver_name": solver_name,
                        "analysis_id": analysis.analysis_id,
                        "avg_execution_time": avg_execution_time,
                        "success_rate": overall_success_rate,
                        "performance_rank": performance_rank
                    }
                )
            
            return {
                "success": True,
                "analysis": analysis.to_dict(),
                "summary": {
                    "solver_name": solver_name,
                    "time_period": f"{start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}",
                    "total_executions": len(period_metrics),
                    "avg_execution_time": round(avg_execution_time, 3),
                    "success_rate": round(overall_success_rate, 3),
                    "avg_quality": round(avg_solution_quality, 3),
                    "performance_rank": performance_rank,
                    "trend": execution_time_trend
                }
            }
            
        except Exception as e:
            error_msg = f"Performance analysis failed for solver {solver_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _run_solver_benchmarks(self,
                                   solver_names: Optional[List[str]] = None,
                                   benchmark_categories: Optional[List[str]] = None,
                                   **kwargs) -> Dict[str, Any]:
        """Run comprehensive benchmarks for specified solvers"""
        try:
            # Determine solvers to benchmark
            if solver_names is None:
                available_solvers = [
                    name for name, capability in self.solver_registry.solvers.items()
                    if self.solver_registry.check_solver_availability(name)
                ]
            else:
                available_solvers = [
                    name for name in solver_names
                    if self.solver_registry.check_solver_availability(name)
                ]
            
            if not available_solvers:
                return {
                    "success": False,
                    "error": "No available solvers found for benchmarking"
                }
            
            # Determine benchmark problems to run
            if benchmark_categories:
                benchmark_problems = {
                    pid: problem for pid, problem in self.benchmark_problems.items()
                    if problem.category.value in benchmark_categories
                }
            else:
                benchmark_problems = self.benchmark_problems
            
            self.logger.info(f"Running benchmarks for {len(available_solvers)} solvers on {len(benchmark_problems)} problems")
            
            # Run benchmarks
            all_results = []
            benchmark_start_time = datetime.now()
            
            for solver_name in available_solvers:
                solver_results = []
                
                for problem_id, problem in benchmark_problems.items():
                    self.logger.info(f"Benchmarking {solver_name} on {problem.name}")
                    
                    try:
                        # Run benchmark
                        result = await self._run_single_benchmark(solver_name, problem)
                        solver_results.append(result)
                        all_results.append(result)
                        
                        # Store result
                        self.benchmark_results[solver_name].append(result)
                        
                    except Exception as e:
                        self.logger.error(f"Benchmark failed for {solver_name} on {problem_id}: {e}")
                        # Create failed result
                        failed_result = BenchmarkResult(
                            benchmark_id=str(uuid.uuid4()),
                            problem_id=problem_id,
                            solver_name=solver_name,
                            execution_time=problem.time_limit,
                            memory_usage=0,
                            cpu_usage=0,
                            solution_quality=0,
                            success=False,
                            optimal_gap=None,
                            iterations=None,
                            solver_status="error",
                            timestamp=datetime.now(),
                            detailed_metrics={"error": str(e)}
                        )
                        solver_results.append(failed_result)
                        all_results.append(failed_result)
            
            total_benchmark_time = (datetime.now() - benchmark_start_time).total_seconds()
            
            # Analyze benchmark results
            benchmark_analysis = await self._analyze_benchmark_results(all_results)
            
            # Generate comparative report
            comparative_report = await self._generate_comparative_benchmark_report(all_results, available_solvers)
            
            # Store in Strands memory
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Benchmark suite completed for {len(available_solvers)} solvers",
                    metadata={
                        "type": "benchmark_suite",
                        "solvers_tested": available_solvers,
                        "problems_tested": len(benchmark_problems),
                        "total_time": total_benchmark_time,
                        "success_rate": benchmark_analysis.get("overall_success_rate", 0)
                    }
                )
            
            return {
                "success": True,
                "benchmark_summary": {
                    "solvers_tested": len(available_solvers),
                    "problems_tested": len(benchmark_problems),
                    "total_benchmarks": len(all_results),
                    "successful_benchmarks": len([r for r in all_results if r.success]),
                    "total_time": round(total_benchmark_time, 2)
                },
                "results": [result.to_dict() for result in all_results],
                "analysis": benchmark_analysis,
                "comparative_report": comparative_report,
                "solver_rankings": await self._calculate_solver_rankings(all_results)
            }
            
        except Exception as e:
            error_msg = f"Benchmark execution failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _run_single_benchmark(self, solver_name: str, problem: BenchmarkProblem) -> BenchmarkResult:
        """Run a single benchmark test"""
        benchmark_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Start resource monitoring
        if PSUTIL_AVAILABLE:
            initial_memory = psutil.virtual_memory().used / (1024**2)  # MB
            process = psutil.Process()
            initial_cpu_time = process.cpu_times().user + process.cpu_times().system
        else:
            initial_memory = 0
            process = None
            initial_cpu_time = 0
        
        try:
            # Create model specification from benchmark problem
            model_spec = ModelSpecification(
                problem_type=problem.category.value,
                variables=problem.problem_data.get("variables", []),
                constraints=problem.problem_data.get("constraints", []),
                objective=problem.problem_data.get("objective", {}),
                solver_hints={"time_limit": problem.time_limit, "memory_limit": problem.memory_limit},
                metadata=problem.metadata
            )
            
            # Execute solver using the actual solver registry
            from .solver_tool import SolverTool
            
            solver_tool = SolverTool()
            await solver_tool.initialize()
            
            # Execute the actual solver
            solver_result = await solver_tool.execute(
                operation="solve",
                solver_name=solver_name,
                model_specification=model_spec
            )
            
            if solver_result.get("success", False):
                result_data = solver_result["result"]
                success = result_data.solve_status in ["optimal", "feasible"]
                objective_value = result_data.objective_value
                solution_quality = result_data.solution_quality.get("quality_score", 0.0)
                solver_status = result_data.solve_status
                
                if problem.expected_optimal_value and objective_value:
                    optimal_gap = abs(objective_value - problem.expected_optimal_value) / problem.expected_optimal_value
                else:
                    optimal_gap = result_data.solution_quality.get("optimality_gap", 0.0)
                
                execution_time = result_data.execution_time
            else:
                success = False
                objective_value = None
                optimal_gap = None
                solution_quality = 0
                solver_status = "error"
                execution_time = problem.time_limit
            
            # Calculate resource usage
            if PSUTIL_AVAILABLE and process:
                final_memory = psutil.virtual_memory().used / (1024**2)
                memory_usage = max(0, final_memory - initial_memory)
                
                final_cpu_time = process.cpu_times().user + process.cpu_times().system
                cpu_usage = (final_cpu_time - initial_cpu_time) / execution_time * 100 if execution_time > 0 else 0
            else:
                memory_usage = execution_time * 10  # Estimate based on execution time
                cpu_usage = 50.0  # Default estimate
            
            # Create detailed metrics from actual solver result
            if success and solver_result.get("success", False):
                result_data = solver_result["result"]
                detailed_metrics = {
                    "objective_value": objective_value,
                    "iterations": result_data.solver_info.get("iterations", 0),
                    "nodes_processed": result_data.solver_info.get("nodes_processed", 0),
                    "problem_size": problem.problem_size,
                    "solver_version": result_data.solver_info.get("version", "unknown"),
                    "algorithm_used": result_data.solver_info.get("algorithm", "default")
                }
            else:
                detailed_metrics = {
                    "objective_value": None,
                    "iterations": 0,
                    "nodes_processed": 0,
                    "problem_size": problem.problem_size,
                    "solver_version": "unknown",
                    "algorithm_used": "none",
                    "error": solver_result.get("error", "Unknown error")
                }
            
            return BenchmarkResult(
                benchmark_id=benchmark_id,
                problem_id=problem.problem_id,
                solver_name=solver_name,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                solution_quality=solution_quality,
                success=success,
                optimal_gap=optimal_gap,
                iterations=detailed_metrics["iterations"],
                solver_status=solver_status,
                timestamp=datetime.now(),
                detailed_metrics=detailed_metrics
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return BenchmarkResult(
                benchmark_id=benchmark_id,
                problem_id=problem.problem_id,
                solver_name=solver_name,
                execution_time=execution_time,
                memory_usage=0,
                cpu_usage=0,
                solution_quality=0,
                success=False,
                optimal_gap=None,
                iterations=None,
                solver_status="error",
                timestamp=datetime.now(),
                detailed_metrics={"error": str(e)}
            )
    
    async def _collect_performance_metrics(self,
                                         solver_result: SolverResult,
                                         problem_characteristics: Dict[str, Any],
                                         execution_context: Dict[str, Any],
                                         **kwargs) -> Dict[str, Any]:
        """Collect and store performance metrics from solver execution"""
        try:
            timestamp = datetime.now()
            metrics = []
            
            # Execution time metric
            if solver_result.execution_time > 0:
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    solver_name=solver_result.solver_name,
                    metric_type=PerformanceMetricType.EXECUTION_TIME,
                    value=solver_result.execution_time,
                    timestamp=timestamp,
                    problem_characteristics=problem_characteristics,
                    execution_context=execution_context,
                    metadata={"status": solver_result.solve_status}
                ))
            
            # Memory usage metric
            if "memory_usage" in solver_result.solver_info:
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    solver_name=solver_result.solver_name,
                    metric_type=PerformanceMetricType.MEMORY_USAGE,
                    value=solver_result.solver_info["memory_usage"],
                    timestamp=timestamp,
                    problem_characteristics=problem_characteristics,
                    execution_context=execution_context,
                    metadata={"status": solver_result.solve_status}
                ))
            
            # Solution quality metric
            if "quality_score" in solver_result.solution_quality:
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    solver_name=solver_result.solver_name,
                    metric_type=PerformanceMetricType.SOLUTION_QUALITY,
                    value=solver_result.solution_quality["quality_score"],
                    timestamp=timestamp,
                    problem_characteristics=problem_characteristics,
                    execution_context=execution_context,
                    metadata={"status": solver_result.solve_status}
                ))
            
            # Success rate metric (binary: 1 for success, 0 for failure)
            success_value = 1.0 if solver_result.solve_status in ["optimal", "feasible"] else 0.0
            metrics.append(PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                solver_name=solver_result.solver_name,
                metric_type=PerformanceMetricType.SUCCESS_RATE,
                value=success_value,
                timestamp=timestamp,
                problem_characteristics=problem_characteristics,
                execution_context=execution_context,
                metadata={"status": solver_result.solve_status}
            ))
            
            # Store metrics
            with self._lock:
                self.performance_metrics[solver_result.solver_name].extend(metrics)
            
            # Persist to storage
            await self._persist_metrics(metrics)
            
            return {
                "success": True,
                "metrics_collected": len(metrics),
                "solver_name": solver_result.solver_name,
                "timestamp": timestamp.isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to collect performance metrics: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _calculate_trend(self, values: List[float], timestamps: List[datetime]) -> str:
        """Calculate trend direction from time series data"""
        if len(values) < 3:
            return "insufficient_data"
        
        try:
            # Convert timestamps to numeric values (days since first timestamp)
            if timestamps:
                base_time = timestamps[0]
                x = [(ts - base_time).total_seconds() / 86400 for ts in timestamps]  # Days
            else:
                x = list(range(len(values)))
            
            # Calculate linear regression slope
            n = len(values)
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Determine trend based on slope and significance
            if abs(slope) < 0.01:  # Very small slope
                return "stable"
            elif slope > 0:
                return "improving" if values[0] > values[-1] else "degrading"  # For execution time, lower is better
            else:
                return "degrading" if values[0] > values[-1] else "improving"
                
        except (ZeroDivisionError, ValueError):
            return "stable"
    
    def _calculate_memory_efficiency_score(self, avg_memory: float, peak_memory: float) -> float:
        """Calculate memory efficiency score (0-1 scale)"""
        if peak_memory == 0:
            return 1.0
        
        # Score based on memory usage thresholds
        if avg_memory <= self.performance_thresholds["memory_usage"]["excellent"]:
            base_score = 1.0
        elif avg_memory <= self.performance_thresholds["memory_usage"]["good"]:
            base_score = 0.8
        elif avg_memory <= self.performance_thresholds["memory_usage"]["acceptable"]:
            base_score = 0.6
        else:
            base_score = 0.4
        
        # Adjust for memory consistency (lower peak vs average is better)
        consistency_factor = avg_memory / peak_memory if peak_memory > 0 else 1.0
        
        return min(1.0, base_score * consistency_factor)
    
    def _calculate_reliability_score(self, success_rate: float, quality_consistency: float) -> float:
        """Calculate overall reliability score"""
        return (success_rate * 0.7 + quality_consistency * 0.3)
    
    async def _calculate_relative_performance(self, solver_name: str, start_time: datetime, end_time: datetime) -> Dict[str, float]:
        """Calculate performance relative to other solvers"""
        try:
            # Get metrics for all solvers in the same time period
            all_solver_metrics = {}
            
            for other_solver, metrics in self.performance_metrics.items():
                period_metrics = [
                    m for m in metrics 
                    if start_time <= m.timestamp <= end_time and m.metric_type == PerformanceMetricType.EXECUTION_TIME
                ]
                if period_metrics:
                    all_solver_metrics[other_solver] = statistics.mean([m.value for m in period_metrics])
            
            if len(all_solver_metrics) < 2:
                return {"relative_speed": 1.0}
            
            # Calculate relative performance
            solver_avg_time = all_solver_metrics.get(solver_name, 0)
            other_solvers_avg = statistics.mean([time for name, time in all_solver_metrics.items() if name != solver_name])
            
            relative_speed = other_solvers_avg / solver_avg_time if solver_avg_time > 0 else 1.0
            
            return {
                "relative_speed": relative_speed,
                "vs_average": relative_speed,
                "percentile": self._calculate_percentile(solver_avg_time, list(all_solver_metrics.values()))
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating relative performance: {e}")
            return {"relative_speed": 1.0}
    
    def _calculate_percentile(self, value: float, all_values: List[float]) -> float:
        """Calculate percentile rank of value in list"""
        if not all_values:
            return 50.0
        
        sorted_values = sorted(all_values)
        rank = sum(1 for v in sorted_values if v <= value)
        return (rank / len(sorted_values)) * 100
    
    async def _calculate_performance_rank(self, solver_name: str, start_time: datetime, end_time: datetime) -> int:
        """Calculate performance rank among all solvers"""
        try:
            # Get average execution times for all solvers
            solver_avg_times = {}
            
            for other_solver, metrics in self.performance_metrics.items():
                period_metrics = [
                    m for m in metrics 
                    if start_time <= m.timestamp <= end_time and m.metric_type == PerformanceMetricType.EXECUTION_TIME
                ]
                if period_metrics:
                    solver_avg_times[other_solver] = statistics.mean([m.value for m in period_metrics])
            
            if solver_name not in solver_avg_times:
                return len(solver_avg_times) + 1
            
            # Sort by execution time (lower is better)
            sorted_solvers = sorted(solver_avg_times.items(), key=lambda x: x[1])
            
            # Find rank
            for rank, (name, _) in enumerate(sorted_solvers, 1):
                if name == solver_name:
                    return rank
            
            return len(sorted_solvers) + 1
            
        except Exception as e:
            self.logger.error(f"Error calculating performance rank: {e}")
            return 1
    
    async def _generate_optimization_recommendations(self, solver_name: str, avg_time: float, 
                                                   avg_memory: float, avg_quality: float, 
                                                   success_rate: float) -> List[str]:
        """Generate optimization recommendations based on performance analysis"""
        recommendations = []
        
        # Execution time recommendations
        if avg_time > self.performance_thresholds["execution_time"]["acceptable"]:
            recommendations.append("Consider using faster solver alternatives or optimizing solver parameters")
            recommendations.append("Implement time limits to prevent long-running optimizations")
        elif avg_time > self.performance_thresholds["execution_time"]["good"]:
            recommendations.append("Fine-tune solver parameters for better performance")
        
        # Memory usage recommendations
        if avg_memory > self.performance_thresholds["memory_usage"]["acceptable"]:
            recommendations.append("Optimize memory usage through problem preprocessing or solver configuration")
            recommendations.append("Consider memory-efficient solver alternatives")
        
        # Solution quality recommendations
        if avg_quality < self.performance_thresholds["solution_quality"]["acceptable"]:
            recommendations.append("Review problem formulation and solver selection for better solution quality")
            recommendations.append("Consider using multiple solvers in competitive mode")
        elif avg_quality < self.performance_thresholds["solution_quality"]["good"]:
            recommendations.append("Experiment with different solver algorithms or parameters")
        
        # Success rate recommendations
        if success_rate < self.performance_thresholds["success_rate"]["acceptable"]:
            recommendations.append("Investigate frequent solver failures and improve error handling")
            recommendations.append("Consider fallback solvers for improved reliability")
        elif success_rate < self.performance_thresholds["success_rate"]["good"]:
            recommendations.append("Implement retry mechanisms for failed optimizations")
        
        # Solver-specific recommendations
        if solver_name in self.solver_registry.solvers:
            solver_capability = self.solver_registry.solvers[solver_name]
            if solver_capability.parallel_capable and avg_time > 10.0:
                recommendations.append("Enable parallel processing to improve solve times")
        
        return recommendations
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate performance analyzer parameters"""
        operation = kwargs.get("operation")
        
        if operation == "analyze_performance":
            solver_name = kwargs.get("solver_name")
            if not solver_name:
                return False
            if solver_name not in self.solver_registry.solvers:
                return False
        
        elif operation == "run_benchmarks":
            solver_names = kwargs.get("solver_names")
            if solver_names:
                for name in solver_names:
                    if name not in self.solver_registry.solvers:
                        return False
        
        elif operation == "collect_metrics":
            solver_result = kwargs.get("solver_result")
            if not isinstance(solver_result, SolverResult):
                return False
        
        return True
    
    async def _persist_metrics(self, metrics: List[PerformanceMetric]):
        """Persist performance metrics to storage"""
        try:
            # Save to file
            metrics_file = self.data_dir / "performance_metrics.pkl"
            with open(metrics_file, 'wb') as f:
                pickle.dump(dict(self.performance_metrics), f)
            
        except Exception as e:
            self.logger.warning(f"Could not persist metrics: {e}")
    
    async def _periodic_data_cleanup(self):
        """Periodic cleanup of old performance data"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                
                cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
                
                # Clean up old metrics
                with self._lock:
                    for solver_name in self.performance_metrics:
                        self.performance_metrics[solver_name] = [
                            m for m in self.performance_metrics[solver_name]
                            if m.timestamp > cutoff_date
                        ]
                
                # Clean up old benchmark results
                for solver_name in self.benchmark_results:
                    self.benchmark_results[solver_name] = [
                        r for r in self.benchmark_results[solver_name]
                        if r.timestamp > cutoff_date
                    ]
                
                # Clean up old analyses
                self.analysis_history = [
                    a for a in self.analysis_history
                    if a.timestamp > cutoff_date
                ]
                
                self.logger.info("Completed periodic data cleanup")
                
            except Exception as e:
                self.logger.error(f"Error in periodic data cleanup: {e}")
    
    async def _periodic_trend_analysis(self):
        """Periodic trend analysis for all solvers"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run hourly
                
                # Analyze trends for all solvers with sufficient data
                for solver_name, metrics in self.performance_metrics.items():
                    if len(metrics) >= self.trend_analysis_min_points:
                        await self._analyze_solver_trends(solver_name)
                
                self.logger.info("Completed periodic trend analysis")
                
            except Exception as e:
                self.logger.error(f"Error in periodic trend analysis: {e}")
    
    async def _analyze_solver_trends(self, solver_name: str):
        """Analyze trends for a specific solver"""
        try:
            metrics = self.performance_metrics[solver_name]
            
            # Analyze execution time trends
            execution_time_metrics = [m for m in metrics if m.metric_type == PerformanceMetricType.EXECUTION_TIME]
            if len(execution_time_metrics) >= self.trend_analysis_min_points:
                trend_analysis = self._perform_trend_analysis(execution_time_metrics, PerformanceMetricType.EXECUTION_TIME, solver_name)
                self.trend_analyses[solver_name].append(trend_analysis)
            
            # Analyze quality trends
            quality_metrics = [m for m in metrics if m.metric_type == PerformanceMetricType.SOLUTION_QUALITY]
            if len(quality_metrics) >= self.trend_analysis_min_points:
                trend_analysis = self._perform_trend_analysis(quality_metrics, PerformanceMetricType.SOLUTION_QUALITY, solver_name)
                self.trend_analyses[solver_name].append(trend_analysis)
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends for {solver_name}: {e}")
    
    def _perform_trend_analysis(self, metrics: List[PerformanceMetric], 
                               metric_type: PerformanceMetricType, 
                               solver_name: str) -> TrendAnalysis:
        """Perform detailed trend analysis on metrics"""
        values = [m.value for m in metrics]
        timestamps = [m.timestamp for m in metrics]
        
        # Calculate trend
        trend_direction = self._calculate_trend(values, timestamps)
        
        # Calculate trend strength and confidence
        if len(values) >= 3:
            # Simple linear regression
            x = list(range(len(values)))
            n = len(values)
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            
            try:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                # Calculate R-squared
                y_mean = sum_y / n
                ss_tot = sum((y - y_mean) ** 2 for y in values)
                ss_res = sum((values[i] - (slope * x[i] + (sum_y - slope * sum_x) / n)) ** 2 for i in range(n))
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                
                trend_strength = min(1.0, abs(slope) / (max(values) - min(values)) if max(values) != min(values) else 0)
                trend_confidence = r_squared
                
            except (ZeroDivisionError, ValueError):
                slope = 0
                r_squared = 0
                trend_strength = 0
                trend_confidence = 0
        else:
            slope = 0
            r_squared = 0
            trend_strength = 0
            trend_confidence = 0
        
        # Generate future predictions (simple linear extrapolation)
        future_predictions = []
        if trend_confidence > 0.5 and len(values) >= 5:
            last_timestamp = timestamps[-1]
            for days_ahead in [1, 7, 30]:
                future_timestamp = last_timestamp + timedelta(days=days_ahead)
                future_value = values[-1] + slope * days_ahead
                future_predictions.append((future_timestamp, max(0, future_value)))
        
        # Detect anomalies (values more than 2 standard deviations from mean)
        anomalies = []
        if len(values) >= 5:
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values)
            for i, (value, timestamp) in enumerate(zip(values, timestamps)):
                if abs(value - mean_val) > 2 * std_val:
                    anomalies.append({
                        "timestamp": timestamp.isoformat(),
                        "value": value,
                        "deviation": abs(value - mean_val) / std_val,
                        "index": i
                    })
        
        return TrendAnalysis(
            metric_type=metric_type,
            solver_name=solver_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            trend_confidence=trend_confidence,
            slope=slope,
            r_squared=r_squared,
            prediction_accuracy=trend_confidence,  # Simplified
            future_predictions=future_predictions,
            anomalies_detected=anomalies
        )
    
    async def _analyze_benchmark_results(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze comprehensive benchmark results"""
        try:
            if not results:
                return {"error": "No benchmark results to analyze"}
            
            # Overall statistics
            total_benchmarks = len(results)
            successful_benchmarks = len([r for r in results if r.success])
            overall_success_rate = successful_benchmarks / total_benchmarks
            
            # Performance statistics
            successful_results = [r for r in results if r.success]
            if successful_results:
                avg_execution_time = statistics.mean([r.execution_time for r in successful_results])
                median_execution_time = statistics.median([r.execution_time for r in successful_results])
                avg_memory_usage = statistics.mean([r.memory_usage for r in successful_results])
                avg_solution_quality = statistics.mean([r.solution_quality for r in successful_results])
            else:
                avg_execution_time = 0
                median_execution_time = 0
                avg_memory_usage = 0
                avg_solution_quality = 0
            
            # Category analysis
            category_analysis = {}
            for result in results:
                problem = self.benchmark_problems.get(result.problem_id)
                if problem:
                    category = problem.category.value
                    if category not in category_analysis:
                        category_analysis[category] = {
                            "total": 0,
                            "successful": 0,
                            "avg_time": 0,
                            "avg_quality": 0
                        }
                    
                    category_analysis[category]["total"] += 1
                    if result.success:
                        category_analysis[category]["successful"] += 1
                        category_analysis[category]["avg_time"] += result.execution_time
                        category_analysis[category]["avg_quality"] += result.solution_quality
            
            # Calculate averages for categories
            for category, data in category_analysis.items():
                if data["successful"] > 0:
                    data["success_rate"] = data["successful"] / data["total"]
                    data["avg_time"] = data["avg_time"] / data["successful"]
                    data["avg_quality"] = data["avg_quality"] / data["successful"]
                else:
                    data["success_rate"] = 0
                    data["avg_time"] = 0
                    data["avg_quality"] = 0
            
            return {
                "overall_statistics": {
                    "total_benchmarks": total_benchmarks,
                    "successful_benchmarks": successful_benchmarks,
                    "overall_success_rate": overall_success_rate,
                    "avg_execution_time": avg_execution_time,
                    "median_execution_time": median_execution_time,
                    "avg_memory_usage": avg_memory_usage,
                    "avg_solution_quality": avg_solution_quality
                },
                "category_analysis": category_analysis,
                "performance_grade": self._calculate_benchmark_grade(overall_success_rate, avg_execution_time, avg_solution_quality)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing benchmark results: {e}")
            return {"error": str(e)}
    
    def _calculate_benchmark_grade(self, success_rate: float, avg_time: float, avg_quality: float) -> str:
        """Calculate overall benchmark performance grade"""
        score = 0
        
        # Success rate component (40%)
        if success_rate >= 0.95:
            score += 40
        elif success_rate >= 0.90:
            score += 35
        elif success_rate >= 0.80:
            score += 30
        else:
            score += 20
        
        # Execution time component (30%)
        if avg_time <= 10.0:
            score += 30
        elif avg_time <= 30.0:
            score += 25
        elif avg_time <= 60.0:
            score += 20
        else:
            score += 10
        
        # Solution quality component (30%)
        if avg_quality >= 0.90:
            score += 30
        elif avg_quality >= 0.80:
            score += 25
        elif avg_quality >= 0.70:
            score += 20
        else:
            score += 10
        
        # Convert to letter grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    async def _generate_comparative_benchmark_report(self, results: List[BenchmarkResult], 
                                                   solvers: List[str]) -> Dict[str, Any]:
        """Generate comparative benchmark report across solvers"""
        try:
            solver_performance = {}
            
            # Aggregate results by solver
            for solver_name in solvers:
                solver_results = [r for r in results if r.solver_name == solver_name]
                
                if solver_results:
                    successful_results = [r for r in solver_results if r.success]
                    
                    solver_performance[solver_name] = {
                        "total_benchmarks": len(solver_results),
                        "successful_benchmarks": len(successful_results),
                        "success_rate": len(successful_results) / len(solver_results),
                        "avg_execution_time": statistics.mean([r.execution_time for r in successful_results]) if successful_results else 0,
                        "avg_memory_usage": statistics.mean([r.memory_usage for r in successful_results]) if successful_results else 0,
                        "avg_solution_quality": statistics.mean([r.solution_quality for r in successful_results]) if successful_results else 0,
                        "total_execution_time": sum([r.execution_time for r in solver_results]),
                        "best_performance": min([r.execution_time for r in successful_results]) if successful_results else float('inf'),
                        "worst_performance": max([r.execution_time for r in successful_results]) if successful_results else 0
                    }
            
            # Calculate rankings
            rankings = {
                "by_success_rate": sorted(solver_performance.items(), key=lambda x: x[1]["success_rate"], reverse=True),
                "by_speed": sorted(solver_performance.items(), key=lambda x: x[1]["avg_execution_time"]),
                "by_quality": sorted(solver_performance.items(), key=lambda x: x[1]["avg_solution_quality"], reverse=True),
                "by_memory_efficiency": sorted(solver_performance.items(), key=lambda x: x[1]["avg_memory_usage"])
            }
            
            # Generate insights
            insights = []
            
            # Best overall performer
            best_overall = min(solver_performance.items(), 
                             key=lambda x: (1 - x[1]["success_rate"]) * 100 + x[1]["avg_execution_time"])
            insights.append(f"Best overall performer: {best_overall[0]} with {best_overall[1]['success_rate']:.1%} success rate and {best_overall[1]['avg_execution_time']:.2f}s average time")
            
            # Fastest solver
            fastest_solver = min(solver_performance.items(), key=lambda x: x[1]["avg_execution_time"])
            insights.append(f"Fastest solver: {fastest_solver[0]} with {fastest_solver[1]['avg_execution_time']:.2f}s average execution time")
            
            # Most reliable solver
            most_reliable = max(solver_performance.items(), key=lambda x: x[1]["success_rate"])
            insights.append(f"Most reliable solver: {most_reliable[0]} with {most_reliable[1]['success_rate']:.1%} success rate")
            
            # Best quality solver
            best_quality = max(solver_performance.items(), key=lambda x: x[1]["avg_solution_quality"])
            insights.append(f"Best solution quality: {best_quality[0]} with {best_quality[1]['avg_solution_quality']:.3f} average quality score")
            
            return {
                "solver_performance": solver_performance,
                "rankings": rankings,
                "insights": insights,
                "recommendation": self._generate_solver_recommendation(solver_performance)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating comparative report: {e}")
            return {"error": str(e)}
    
    def _generate_solver_recommendation(self, solver_performance: Dict[str, Dict[str, Any]]) -> str:
        """Generate solver recommendation based on benchmark results"""
        if not solver_performance:
            return "No solver performance data available for recommendation"
        
        # Find best balanced performer
        best_solver = None
        best_score = -1
        
        for solver_name, perf in solver_performance.items():
            # Composite score: success rate (40%) + speed (30%) + quality (30%)
            speed_score = 1.0 / (1.0 + perf["avg_execution_time"] / 10.0)  # Normalize speed
            composite_score = (perf["success_rate"] * 0.4 + 
                             speed_score * 0.3 + 
                             perf["avg_solution_quality"] * 0.3)
            
            if composite_score > best_score:
                best_score = composite_score
                best_solver = solver_name
        
        if best_solver:
            perf = solver_performance[best_solver]
            return (f"Recommended solver: {best_solver} - "
                   f"Excellent balance of reliability ({perf['success_rate']:.1%}), "
                   f"speed ({perf['avg_execution_time']:.2f}s), and "
                   f"quality ({perf['avg_solution_quality']:.3f})")
        
        return "Unable to determine best solver from available data"
    
    async def _calculate_solver_rankings(self, results: List[BenchmarkResult]) -> Dict[str, List[str]]:
        """Calculate solver rankings across different criteria"""
        try:
            solver_stats = defaultdict(lambda: {
                "total_time": 0,
                "total_quality": 0,
                "success_count": 0,
                "total_count": 0,
                "total_memory": 0
            })
            
            # Aggregate statistics
            for result in results:
                stats = solver_stats[result.solver_name]
                stats["total_count"] += 1
                stats["total_time"] += result.execution_time
                stats["total_memory"] += result.memory_usage
                
                if result.success:
                    stats["success_count"] += 1
                    stats["total_quality"] += result.solution_quality
            
            # Calculate averages
            solver_averages = {}
            for solver_name, stats in solver_stats.items():
                solver_averages[solver_name] = {
                    "avg_time": stats["total_time"] / stats["total_count"],
                    "avg_quality": stats["total_quality"] / stats["success_count"] if stats["success_count"] > 0 else 0,
                    "success_rate": stats["success_count"] / stats["total_count"],
                    "avg_memory": stats["total_memory"] / stats["total_count"]
                }
            
            # Create rankings
            rankings = {
                "speed": [name for name, _ in sorted(solver_averages.items(), key=lambda x: x[1]["avg_time"])],
                "quality": [name for name, _ in sorted(solver_averages.items(), key=lambda x: x[1]["avg_quality"], reverse=True)],
                "reliability": [name for name, _ in sorted(solver_averages.items(), key=lambda x: x[1]["success_rate"], reverse=True)],
                "memory_efficiency": [name for name, _ in sorted(solver_averages.items(), key=lambda x: x[1]["avg_memory"])]
            }
            
            return rankings
            
        except Exception as e:
            self.logger.error(f"Error calculating solver rankings: {e}")
            return {}
    
    async def _analyze_performance_trends(self, solver_name: str, **kwargs) -> Dict[str, Any]:
        """Analyze performance trends for a specific solver"""
        try:
            if solver_name not in self.performance_metrics:
                return {
                    "success": False,
                    "error": f"No performance data found for solver {solver_name}"
                }
            
            metrics = self.performance_metrics[solver_name]
            
            # Analyze different metric types
            trend_results = {}
            
            for metric_type in PerformanceMetricType:
                type_metrics = [m for m in metrics if m.metric_type == metric_type]
                
                if len(type_metrics) >= self.trend_analysis_min_points:
                    trend_analysis = self._perform_trend_analysis(type_metrics, metric_type, solver_name)
                    trend_results[metric_type.value] = trend_analysis.to_dict()
            
            # Generate trend summary
            trend_summary = self._generate_trend_summary(trend_results)
            
            return {
                "success": True,
                "solver_name": solver_name,
                "trend_analysis": trend_results,
                "trend_summary": trend_summary,
                "recommendations": self._generate_trend_recommendations(trend_results)
            }
            
        except Exception as e:
            error_msg = f"Trend analysis failed for solver {solver_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _generate_trend_summary(self, trend_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of trend analysis results"""
        summary = {
            "overall_trend": "stable",
            "key_insights": [],
            "concerns": [],
            "improvements": []
        }
        
        improving_trends = 0
        degrading_trends = 0
        
        for metric_type, trend_data in trend_results.items():
            direction = trend_data.get("trend_direction", "stable")
            confidence = trend_data.get("trend_confidence", 0)
            
            if confidence > 0.7:  # High confidence trends
                if direction == "improving":
                    improving_trends += 1
                    summary["improvements"].append(f"{metric_type} is improving with high confidence")
                elif direction == "degrading":
                    degrading_trends += 1
                    summary["concerns"].append(f"{metric_type} is degrading with high confidence")
            
            # Check for anomalies
            anomalies = trend_data.get("anomalies_detected", [])
            if len(anomalies) > 0:
                summary["concerns"].append(f"{len(anomalies)} anomalies detected in {metric_type}")
        
        # Determine overall trend
        if improving_trends > degrading_trends:
            summary["overall_trend"] = "improving"
        elif degrading_trends > improving_trends:
            summary["overall_trend"] = "degrading"
        
        return summary
    
    def _generate_trend_recommendations(self, trend_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on trend analysis"""
        recommendations = []
        
        for metric_type, trend_data in trend_results.items():
            direction = trend_data.get("trend_direction", "stable")
            confidence = trend_data.get("trend_confidence", 0)
            
            if confidence > 0.7 and direction == "degrading":
                if metric_type == "execution_time":
                    recommendations.append("Performance is degrading - consider solver parameter optimization or alternative solvers")
                elif metric_type == "solution_quality":
                    recommendations.append("Solution quality is declining - review problem formulation and solver selection")
                elif metric_type == "memory_usage":
                    recommendations.append("Memory usage is increasing - implement memory optimization strategies")
            
            # Check for anomalies
            anomalies = trend_data.get("anomalies_detected", [])
            if len(anomalies) > 2:
                recommendations.append(f"Multiple anomalies detected in {metric_type} - investigate system stability")
        
        return recommendations
    
    async def _compare_solver_performance(self, solvers: List[str], **kwargs) -> Dict[str, Any]:
        """Compare performance across multiple solvers"""
        try:
            time_period = kwargs.get("time_period", "last_month")
            
            # Determine time range
            if time_period == "last_week":
                start_time = datetime.now() - timedelta(days=7)
            elif time_period == "last_month":
                start_time = datetime.now() - timedelta(days=30)
            else:
                start_time = datetime.now() - timedelta(days=30)
            
            end_time = datetime.now()
            
            # Collect performance data for each solver
            solver_comparisons = {}
            
            for solver_name in solvers:
                if solver_name in self.performance_metrics:
                    metrics = self.performance_metrics[solver_name]
                    period_metrics = [m for m in metrics if start_time <= m.timestamp <= end_time]
                    
                    if period_metrics:
                        # Calculate statistics
                        execution_times = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.EXECUTION_TIME]
                        quality_scores = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.SOLUTION_QUALITY]
                        success_rates = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.SUCCESS_RATE]
                        
                        solver_comparisons[solver_name] = {
                            "avg_execution_time": statistics.mean(execution_times) if execution_times else 0,
                            "avg_quality": statistics.mean(quality_scores) if quality_scores else 0,
                            "success_rate": statistics.mean(success_rates) if success_rates else 0,
                            "total_executions": len(period_metrics),
                            "consistency": {
                                "time_std": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                                "quality_std": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
                            }
                        }
            
            # Generate comparative analysis
            comparative_analysis = self._generate_comparative_analysis(solver_comparisons)
            
            return {
                "success": True,
                "time_period": f"{start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}",
                "solver_comparisons": solver_comparisons,
                "comparative_analysis": comparative_analysis,
                "recommendations": self._generate_comparative_recommendations(solver_comparisons)
            }
            
        except Exception as e:
            error_msg = f"Solver comparison failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _generate_comparative_analysis(self, solver_comparisons: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparative analysis across solvers"""
        if not solver_comparisons:
            return {"error": "No solver data available for comparison"}
        
        # Find best performers in each category
        best_speed = min(solver_comparisons.items(), key=lambda x: x[1]["avg_execution_time"])
        best_quality = max(solver_comparisons.items(), key=lambda x: x[1]["avg_quality"])
        best_reliability = max(solver_comparisons.items(), key=lambda x: x[1]["success_rate"])
        
        # Calculate relative performance
        avg_execution_time = statistics.mean([data["avg_execution_time"] for data in solver_comparisons.values()])
        avg_quality = statistics.mean([data["avg_quality"] for data in solver_comparisons.values()])
        avg_success_rate = statistics.mean([data["success_rate"] for data in solver_comparisons.values()])
        
        return {
            "best_performers": {
                "speed": {"solver": best_speed[0], "time": best_speed[1]["avg_execution_time"]},
                "quality": {"solver": best_quality[0], "score": best_quality[1]["avg_quality"]},
                "reliability": {"solver": best_reliability[0], "rate": best_reliability[1]["success_rate"]}
            },
            "averages": {
                "execution_time": avg_execution_time,
                "quality": avg_quality,
                "success_rate": avg_success_rate
            },
            "performance_spread": {
                "time_range": [
                    min(data["avg_execution_time"] for data in solver_comparisons.values()),
                    max(data["avg_execution_time"] for data in solver_comparisons.values())
                ],
                "quality_range": [
                    min(data["avg_quality"] for data in solver_comparisons.values()),
                    max(data["avg_quality"] for data in solver_comparisons.values())
                ]
            }
        }
    
    def _generate_comparative_recommendations(self, solver_comparisons: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on solver comparison"""
        recommendations = []
        
        if not solver_comparisons:
            return ["No solver data available for recommendations"]
        
        # Find best overall solver
        best_solver = None
        best_score = -1
        
        for solver_name, data in solver_comparisons.items():
            # Composite score
            score = (data["success_rate"] * 0.4 + 
                    (1.0 / (1.0 + data["avg_execution_time"] / 10.0)) * 0.3 + 
                    data["avg_quality"] * 0.3)
            
            if score > best_score:
                best_score = score
                best_solver = solver_name
        
        if best_solver:
            recommendations.append(f"Use {best_solver} for best overall performance balance")
        
        # Specific use case recommendations
        fastest_solver = min(solver_comparisons.items(), key=lambda x: x[1]["avg_execution_time"])
        recommendations.append(f"Use {fastest_solver[0]} for time-critical applications")
        
        best_quality_solver = max(solver_comparisons.items(), key=lambda x: x[1]["avg_quality"])
        recommendations.append(f"Use {best_quality_solver[0]} for highest solution quality")
        
        return recommendations
    
    async def _generate_performance_report(self, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            report_type = kwargs.get("report_type", "comprehensive")
            time_period = kwargs.get("time_period", "last_month")
            
            # Determine time range
            if time_period == "last_week":
                start_time = datetime.now() - timedelta(days=7)
            elif time_period == "last_month":
                start_time = datetime.now() - timedelta(days=30)
            elif time_period == "last_quarter":
                start_time = datetime.now() - timedelta(days=90)
            else:
                start_time = datetime.now() - timedelta(days=30)
            
            end_time = datetime.now()
            
            # Collect data for all solvers
            report_data = {
                "report_metadata": {
                    "report_type": report_type,
                    "time_period": f"{start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}",
                    "generated_at": datetime.now().isoformat(),
                    "total_solvers": len(self.performance_metrics)
                },
                "solver_summaries": {},
                "overall_statistics": {},
                "trends": {},
                "benchmarks": {},
                "recommendations": []
            }
            
            # Generate solver summaries
            for solver_name, metrics in self.performance_metrics.items():
                period_metrics = [m for m in metrics if start_time <= m.timestamp <= end_time]
                
                if period_metrics:
                    execution_times = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.EXECUTION_TIME]
                    quality_scores = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.SOLUTION_QUALITY]
                    success_rates = [m.value for m in period_metrics if m.metric_type == PerformanceMetricType.SUCCESS_RATE]
                    
                    report_data["solver_summaries"][solver_name] = {
                        "total_executions": len(period_metrics),
                        "avg_execution_time": statistics.mean(execution_times) if execution_times else 0,
                        "avg_quality": statistics.mean(quality_scores) if quality_scores else 0,
                        "success_rate": statistics.mean(success_rates) if success_rates else 0,
                        "performance_grade": self._calculate_solver_grade(
                            statistics.mean(execution_times) if execution_times else 0,
                            statistics.mean(quality_scores) if quality_scores else 0,
                            statistics.mean(success_rates) if success_rates else 0
                        )
                    }
            
            # Generate overall statistics
            all_execution_times = []
            all_quality_scores = []
            all_success_rates = []
            
            for solver_data in report_data["solver_summaries"].values():
                if solver_data["avg_execution_time"] > 0:
                    all_execution_times.append(solver_data["avg_execution_time"])
                if solver_data["avg_quality"] > 0:
                    all_quality_scores.append(solver_data["avg_quality"])
                if solver_data["success_rate"] > 0:
                    all_success_rates.append(solver_data["success_rate"])
            
            report_data["overall_statistics"] = {
                "avg_execution_time": statistics.mean(all_execution_times) if all_execution_times else 0,
                "avg_quality": statistics.mean(all_quality_scores) if all_quality_scores else 0,
                "avg_success_rate": statistics.mean(all_success_rates) if all_success_rates else 0,
                "total_executions": sum(data["total_executions"] for data in report_data["solver_summaries"].values())
            }
            
            # Add benchmark data if available
            recent_benchmarks = []
            for solver_results in self.benchmark_results.values():
                recent_benchmarks.extend([
                    r for r in solver_results 
                    if start_time <= r.timestamp <= end_time
                ])
            
            if recent_benchmarks:
                report_data["benchmarks"] = {
                    "total_benchmarks": len(recent_benchmarks),
                    "successful_benchmarks": len([r for r in recent_benchmarks if r.success]),
                    "avg_benchmark_time": statistics.mean([r.execution_time for r in recent_benchmarks if r.success]),
                    "avg_benchmark_quality": statistics.mean([r.solution_quality for r in recent_benchmarks if r.success])
                }
            
            # Generate recommendations
            report_data["recommendations"] = self._generate_report_recommendations(report_data)
            
            return {
                "success": True,
                "performance_report": report_data
            }
            
        except Exception as e:
            error_msg = f"Performance report generation failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _calculate_solver_grade(self, avg_time: float, avg_quality: float, success_rate: float) -> str:
        """Calculate letter grade for solver performance"""
        score = 0
        
        # Time component (30%)
        if avg_time <= 1.0:
            score += 30
        elif avg_time <= 10.0:
            score += 25
        elif avg_time <= 30.0:
            score += 20
        else:
            score += 10
        
        # Quality component (35%)
        if avg_quality >= 0.95:
            score += 35
        elif avg_quality >= 0.85:
            score += 30
        elif avg_quality >= 0.75:
            score += 25
        else:
            score += 15
        
        # Success rate component (35%)
        if success_rate >= 0.98:
            score += 35
        elif success_rate >= 0.90:
            score += 30
        elif success_rate >= 0.80:
            score += 25
        else:
            score += 15
        
        # Convert to letter grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_report_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on performance report"""
        recommendations = []
        
        overall_stats = report_data.get("overall_statistics", {})
        solver_summaries = report_data.get("solver_summaries", {})
        
        # Overall performance recommendations
        avg_time = overall_stats.get("avg_execution_time", 0)
        avg_quality = overall_stats.get("avg_quality", 0)
        avg_success_rate = overall_stats.get("avg_success_rate", 0)
        
        if avg_time > 30.0:
            recommendations.append("Overall execution times are high - consider solver optimization or hardware upgrades")
        
        if avg_quality < 0.8:
            recommendations.append("Solution quality is below target - review problem formulations and solver selection")
        
        if avg_success_rate < 0.9:
            recommendations.append("Success rate is below target - implement better error handling and fallback mechanisms")
        
        # Solver-specific recommendations
        best_solver = None
        best_grade = "F"
        worst_solver = None
        worst_grade = "A"
        
        for solver_name, data in solver_summaries.items():
            grade = data.get("performance_grade", "F")
            if grade < best_grade:
                best_grade = grade
                best_solver = solver_name
            if grade > worst_grade:
                worst_grade = grade
                worst_solver = solver_name
        
        if best_solver:
            recommendations.append(f"Consider using {best_solver} more frequently - it has the best performance grade ({best_grade})")
        
        if worst_solver and worst_grade in ["D", "F"]:
            recommendations.append(f"Review configuration for {worst_solver} - it has poor performance grade ({worst_grade})")
        
        return recommendations
    
    async def _predict_future_performance(self, solver_name: str, **kwargs) -> Dict[str, Any]:
        """Predict future performance based on historical trends"""
        try:
            if solver_name not in self.performance_metrics:
                return {
                    "success": False,
                    "error": f"No performance data found for solver {solver_name}"
                }
            
            metrics = self.performance_metrics[solver_name]
            
            # Get recent trend analyses
            recent_trends = self.trend_analyses.get(solver_name, [])
            
            predictions = {}
            
            for metric_type in PerformanceMetricType:
                type_metrics = [m for m in metrics if m.metric_type == metric_type]
                
                if len(type_metrics) >= 5:  # Need minimum data for prediction
                    # Find most recent trend analysis
                    recent_trend = None
                    for trend in reversed(recent_trends):
                        if trend.metric_type == metric_type:
                            recent_trend = trend
                            break
                    
                    if recent_trend and recent_trend.trend_confidence > 0.5:
                        predictions[metric_type.value] = {
                            "current_trend": recent_trend.trend_direction,
                            "confidence": recent_trend.trend_confidence,
                            "future_predictions": recent_trend.future_predictions,
                            "prediction_accuracy": recent_trend.prediction_accuracy
                        }
            
            # Generate prediction summary
            prediction_summary = self._generate_prediction_summary(predictions)
            
            return {
                "success": True,
                "solver_name": solver_name,
                "predictions": predictions,
                "prediction_summary": prediction_summary,
                "recommendations": self._generate_prediction_recommendations(predictions)
            }
            
        except Exception as e:
            error_msg = f"Performance prediction failed for solver {solver_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _generate_prediction_summary(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of performance predictions"""
        summary = {
            "overall_outlook": "stable",
            "key_predictions": [],
            "confidence_level": 0.0,
            "time_horizon": "30 days"
        }
        
        if not predictions:
            return summary
        
        # Calculate average confidence
        confidences = [pred["confidence"] for pred in predictions.values()]
        summary["confidence_level"] = statistics.mean(confidences)
        
        # Analyze trends
        improving_count = 0
        degrading_count = 0
        
        for metric_type, pred_data in predictions.items():
            trend = pred_data["current_trend"]
            confidence = pred_data["confidence"]
            
            if confidence > 0.7:
                if trend == "improving":
                    improving_count += 1
                    summary["key_predictions"].append(f"{metric_type} expected to improve")
                elif trend == "degrading":
                    degrading_count += 1
                    summary["key_predictions"].append(f"{metric_type} expected to degrade")
        
        # Determine overall outlook
        if improving_count > degrading_count:
            summary["overall_outlook"] = "improving"
        elif degrading_count > improving_count:
            summary["overall_outlook"] = "degrading"
        
        return summary
    
    def _generate_prediction_recommendations(self, predictions: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on performance predictions"""
        recommendations = []
        
        for metric_type, pred_data in predictions.items():
            trend = pred_data["current_trend"]
            confidence = pred_data["confidence"]
            
            if confidence > 0.7 and trend == "degrading":
                if metric_type == "execution_time":
                    recommendations.append("Execution time is predicted to increase - consider proactive optimization")
                elif metric_type == "solution_quality":
                    recommendations.append("Solution quality is predicted to decline - review solver configuration")
                elif metric_type == "success_rate":
                    recommendations.append("Success rate is predicted to decrease - implement preventive measures")
        
        if not recommendations:
            recommendations.append("Performance predictions are stable - continue current practices")
        
        return recommendations
    
    async def _get_optimization_recommendations(self, solver_name: str, **kwargs) -> Dict[str, Any]:
        """Get optimization recommendations for a specific solver"""
        try:
            # Get recent performance analysis
            recent_analysis = None
            for analysis in reversed(self.analysis_history):
                if analysis.solver_name == solver_name:
                    recent_analysis = analysis
                    break
            
            if not recent_analysis:
                return {
                    "success": False,
                    "error": f"No recent performance analysis found for solver {solver_name}"
                }
            
            # Generate comprehensive recommendations
            recommendations = {
                "performance_optimization": recent_analysis.optimization_recommendations,
                "configuration_suggestions": recent_analysis.configuration_suggestions,
                "usage_recommendations": self._generate_usage_recommendations(recent_analysis),
                "monitoring_suggestions": self._generate_monitoring_suggestions(recent_analysis)
            }
            
            return {
                "success": True,
                "solver_name": solver_name,
                "recommendations": recommendations,
                "based_on_analysis": recent_analysis.analysis_id,
                "analysis_date": recent_analysis.timestamp.isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to get optimization recommendations for {solver_name}: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    def _generate_usage_recommendations(self, analysis: PerformanceAnalysis) -> List[str]:
        """Generate usage recommendations based on performance analysis"""
        recommendations = []
        
        # Based on performance characteristics
        if analysis.avg_execution_time < 5.0 and analysis.success_rate > 0.95:
            recommendations.append("Excellent for real-time applications and interactive optimization")
        elif analysis.avg_execution_time < 30.0 and analysis.avg_solution_quality > 0.9:
            recommendations.append("Well-suited for batch optimization with high quality requirements")
        elif analysis.success_rate > 0.98:
            recommendations.append("Highly reliable - good choice for critical production workflows")
        
        # Based on relative performance
        if analysis.performance_rank <= 3:
            recommendations.append("Top-performing solver - prioritize for important optimization tasks")
        elif analysis.performance_rank > 10:
            recommendations.append("Consider as backup solver or for specific problem types only")
        
        return recommendations
    
    def _generate_monitoring_suggestions(self, analysis: PerformanceAnalysis) -> List[str]:
        """Generate monitoring suggestions based on performance analysis"""
        suggestions = []
        
        # Based on trends
        if analysis.execution_time_trend == "degrading":
            suggestions.append("Monitor execution time closely - implement alerts for performance degradation")
        
        if analysis.quality_trend == "degrading":
            suggestions.append("Set up quality monitoring - track solution optimality gaps")
        
        if analysis.success_rate < 0.95:
            suggestions.append("Implement failure rate monitoring with automated notifications")
        
        # Based on consistency
        if analysis.reliability_score < 0.8:
            suggestions.append("Monitor solution consistency - track variance in results")
        
        return suggestions
    
    async def _predict_trends(self, solver_name: str, metrics: List[PerformanceMetric]) -> Dict[str, float]:
        """Predict future trends for solver performance"""
        predictions = {}
        
        try:
            # Group metrics by type
            metric_groups = defaultdict(list)
            for metric in metrics:
                metric_groups[metric.metric_type].append(metric)
            
            # Generate predictions for each metric type
            for metric_type, type_metrics in metric_groups.items():
                if len(type_metrics) >= 5:
                    values = [m.value for m in type_metrics[-10:]]  # Use last 10 points
                    
                    # Simple linear extrapolation
                    if len(values) >= 3:
                        x = list(range(len(values)))
                        n = len(values)
                        sum_x = sum(x)
                        sum_y = sum(values)
                        sum_xy = sum(x[i] * values[i] for i in range(n))
                        sum_x2 = sum(xi * xi for xi in x)
                        
                        try:
                            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                            intercept = (sum_y - slope * sum_x) / n
                            
                            # Predict next value
                            next_value = slope * n + intercept
                            predictions[metric_type.value] = max(0, next_value)
                            
                        except ZeroDivisionError:
                            predictions[metric_type.value] = values[-1] if values else 0
            
        except Exception as e:
            self.logger.error(f"Error predicting trends: {e}")
        
        return predictions
    
    async def _generate_configuration_suggestions(self, solver_name: str, analysis: PerformanceAnalysis) -> Dict[str, Any]:
        """Generate configuration suggestions based on performance analysis"""
        suggestions = {}
        
        try:
            # Get solver capability information
            if solver_name in self.solver_registry.solvers:
                solver_capability = self.solver_registry.solvers[solver_name]
                
                # Time-based suggestions
                if analysis.avg_execution_time > 30.0:
                    suggestions["time_limit"] = min(60.0, analysis.avg_execution_time * 1.5)
                    if solver_capability.parallel_capable:
                        suggestions["enable_parallel"] = True
                        suggestions["num_threads"] = 4
                
                # Memory-based suggestions
                if analysis.avg_memory_usage > 1000.0:  # > 1GB
                    suggestions["memory_limit"] = analysis.avg_memory_usage * 1.2
                    suggestions["enable_memory_optimization"] = True
                
                # Quality-based suggestions
                if analysis.avg_solution_quality < 0.8:
                    suggestions["increase_precision"] = True
                    suggestions["enable_advanced_algorithms"] = True
                
                # Reliability-based suggestions
                if analysis.success_rate < 0.9:
                    suggestions["enable_fallback_methods"] = True
                    suggestions["increase_tolerance"] = True
        
        except Exception as e:
            self.logger.error(f"Error generating configuration suggestions: {e}")
        
        return suggestions