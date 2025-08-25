"""
Solver Agent Integration for Multi-Solver Swarm Optimization
===========================================================

Integrates individual solver agents with the existing swarm orchestrator and
enhanced solver registry. Provides seamless integration between Strands agents
and the multi-solver swarm optimization system.

Requirements: 1.1, 6.1, 8.1, 8.2, 8.3, 8.4
"""

import logging
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from ..utils.base import BaseTool, ToolExecutionError, ToolInitializationError
from .enhanced_solver_registry import EnhancedSolverRegistry
from .solver_swarm_orchestrator import SolverSwarmOrchestrator
from .intelligent_solver_selector import IntelligentSolverSelector
try:
    from agents.solver_agents import SolverAgentFactory, SolverAgentExecutor, SolverAgentResult
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from agents.solver_agents import SolverAgentFactory, SolverAgentExecutor, SolverAgentResult

logger = logging.getLogger(__name__)


@dataclass
class IntegratedSolverResult:
    """Integrated result combining traditional solver and agent capabilities"""
    solver_agent_result: SolverAgentResult
    swarm_context: Dict[str, Any]
    integration_metadata: Dict[str, Any]
    enhanced_insights: Dict[str, Any]


class SolverAgentIntegration(BaseTool):
    """
    Integration layer between solver agents and existing swarm infrastructure.
    Provides enhanced solver capabilities while maintaining compatibility with
    existing multi-solver swarm optimization system.
    """
    
    def __init__(self):
        super().__init__(
            name="solver_agent_integration",
            description="Integration layer for solver agents with swarm orchestration",
            version="1.0.0"
        )
        
        # Core components
        self.solver_registry = EnhancedSolverRegistry()
        self.swarm_orchestrator = SolverSwarmOrchestrator()
        self.solver_selector = IntelligentSolverSelector(self.solver_registry)
        
        # Solver agent components
        self.agent_factory = SolverAgentFactory()
        self.agent_executor = SolverAgentExecutor()
        
        # Integration state
        self.integrated_agents = {}
        self.agent_performance_history = {}
        
        # Strands integration
        self.strands_agent = None
        self.strands_tools = {}
    
    async def initialize(self) -> bool:
        """Initialize the solver agent integration system"""
        try:
            # Initialize core components
            swarm_init = await self.swarm_orchestrator.initialize()
            if not swarm_init:
                self.logger.error("Failed to initialize swarm orchestrator")
                return False
            
            # Initialize solver agents
            agent_init = await self.agent_executor.initialize()
            if not agent_init:
                self.logger.error("Failed to initialize solver agents")
                return False
            
            # Initialize Strands integration
            await self._initialize_strands_integration()
            
            # Create integrated agent mappings
            await self._create_integrated_mappings()
            
            self._initialized = True
            self.logger.info("Solver agent integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize solver agent integration: {e}")
            return False
    
    async def _initialize_strands_integration(self):
        """Initialize Strands tools integration for coordination"""
        try:
            from strands import Agent
            from strands_tools import memory, retrieve, use_aws, think, use_agent
            
            self.strands_agent = Agent(
                name="solver_agent_coordinator",
                system_prompt="""You are a solver agent coordination expert managing the integration
                between individual solver agents and swarm orchestration.
                
                Your role:
                1. Coordinate between traditional solvers and Strands solver agents
                2. Enhance solver results with agent-specific insights
                3. Manage solver agent performance and selection
                4. Provide integrated optimization recommendations
                5. Facilitate knowledge sharing between solver agents
                
                AVAILABLE TOOLS:
                - memory: Store integrated solver results and coordination data
                - retrieve: Access solver and optimization knowledge bases
                - use_aws: Coordinate cloud resources for solver agents
                - think: Advanced reasoning about solver coordination strategies
                - use_agent: Generate integrated optimization explanations
                
                Focus on maximizing the benefits of both traditional solver performance
                and agent-based insights for comprehensive optimization solutions.""",
                tools=[memory, retrieve, use_aws, think, use_agent]
            )
            
            self.strands_tools = {
                'memory': self.strands_agent.tool.memory,
                'retrieve': self.strands_agent.tool.retrieve,
                'use_aws': self.strands_agent.tool.use_aws,
                'think': self.strands_agent.tool.think,
                'use_agent': self.strands_agent.tool.use_agent
            }
            
            self.logger.info("Strands integration for solver agent coordination initialized")
            
        except ImportError:
            self.logger.warning("Strands tools not available for solver agent coordination")
            self.strands_agent = None
            self.strands_tools = {}
    
    async def _create_integrated_mappings(self):
        """Create mappings between traditional solvers and solver agents"""
        available_agents = self.agent_executor.get_available_agents()
        
        for agent_name in available_agents:
            # Map agent to corresponding solver in registry
            solver_mapping = self._map_agent_to_solver(agent_name)
            if solver_mapping:
                self.integrated_agents[agent_name] = solver_mapping
        
        self.logger.info(f"Created {len(self.integrated_agents)} integrated solver agent mappings")
    
    def _map_agent_to_solver(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Map solver agent to corresponding solver in registry"""
        # Extract solver name from agent name
        if "glop" in agent_name.lower():
            return {"solver_name": "GLOP", "category": "linear_programming"}
        elif "clp" in agent_name.lower():
            return {"solver_name": "CLP", "category": "linear_programming"}
        elif "scip" in agent_name.lower():
            return {"solver_name": "SCIP", "category": "mixed_integer_programming"}
        elif "cbc" in agent_name.lower():
            return {"solver_name": "CBC", "category": "mixed_integer_programming"}
        elif "cpsat" in agent_name.lower():
            return {"solver_name": "CP_SAT", "category": "constraint_programming"}
        elif "highs_lp" in agent_name.lower():
            return {"solver_name": "HiGHS_LP", "category": "linear_programming"}
        elif "highs_mip" in agent_name.lower():
            return {"solver_name": "HiGHS_MIP", "category": "mixed_integer_programming"}
        elif "ipopt" in agent_name.lower():
            return {"solver_name": "IPOPT", "category": "nonlinear_programming"}
        elif "bonmin" in agent_name.lower():
            return {"solver_name": "BONMIN", "category": "nonlinear_programming"}
        elif "cvxpy" in agent_name.lower():
            return {"solver_name": "CVXPY_ECOS", "category": "convex_optimization"}
        elif "pyomo" in agent_name.lower():
            return {"solver_name": "PYOMO_CBC", "category": "algebraic_modeling"}
        
        return None
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute solver agent integration operations"""
        operation = kwargs.get("operation", "integrated_solve")
        
        if operation == "integrated_solve":
            return await self._execute_integrated_solve(**kwargs)
        elif operation == "agent_enhanced_swarm":
            return await self._execute_agent_enhanced_swarm(**kwargs)
        elif operation == "compare_traditional_vs_agent":
            return await self._compare_traditional_vs_agent(**kwargs)
        elif operation == "get_agent_recommendations":
            return await self._get_agent_recommendations(**kwargs)
        elif operation == "analyze_agent_performance":
            return await self._analyze_agent_performance(**kwargs)
        else:
            raise ToolExecutionError(f"Unknown operation: {operation}", self.name)
    
    async def _execute_integrated_solve(self, 
                                      problem_data: Dict[str, Any],
                                      solver_name: str,
                                      model_spec: Dict[str, Any],
                                      use_agent_enhancement: bool = True,
                                      **kwargs) -> Dict[str, Any]:
        """Execute integrated solve combining traditional solver with agent enhancement"""
        start_time = time.time()
        
        try:
            # Validate solver availability
            if not self.solver_registry.check_solver_availability(solver_name):
                raise ToolExecutionError(f"Solver {solver_name} not available", self.name)
            
            # Find corresponding agent
            agent_name = None
            for agent, mapping in self.integrated_agents.items():
                if mapping["solver_name"] == solver_name:
                    agent_name = agent
                    break
            
            if not agent_name and use_agent_enhancement:
                self.logger.warning(f"No agent available for solver {solver_name}, using traditional solving")
                use_agent_enhancement = False
            
            # Execute traditional solver through swarm orchestrator
            traditional_result = await self.swarm_orchestrator.execute(
                operation="orchestrate_swarm",
                problem_data=problem_data,
                pattern="competitive",
                solver_count=1,
                selected_solvers=[solver_name]
            )
            
            # Execute agent enhancement if available
            agent_result = None
            if use_agent_enhancement and agent_name:
                try:
                    from tools.solver_tool import ModelSpecification
                    
                    # Convert model spec to proper format
                    model_specification = ModelSpecification(
                        problem_type=model_spec.get("problem_type", "linear_programming"),
                        variables=model_spec.get("variables", []),
                        constraints=model_spec.get("constraints", []),
                        objective=model_spec.get("objective", {}),
                        solver_hints=model_spec.get("solver_hints", {}),
                        metadata=model_spec.get("metadata", {})
                    )
                    
                    agent_result = await self.agent_executor.execute_solver_agent(
                        solver_name=agent_name,
                        problem_data=problem_data,
                        model_spec=model_specification
                    )
                    
                except Exception as e:
                    self.logger.warning(f"Agent enhancement failed: {e}")
                    agent_result = None
            
            # Integrate results
            integrated_result = await self._integrate_results(
                traditional_result, agent_result, solver_name, problem_data
            )
            
            execution_time = time.time() - start_time
            
            # Store results in memory if available
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Integrated solve completed for {solver_name}",
                    metadata={
                        "type": "integrated_solve",
                        "solver_name": solver_name,
                        "execution_time": execution_time,
                        "agent_enhanced": agent_result is not None,
                        "success": integrated_result.get("success", False)
                    }
                )
            
            return {
                "success": True,
                "solver_name": solver_name,
                "execution_time": execution_time,
                "traditional_result": traditional_result,
                "agent_result": asdict(agent_result) if agent_result else None,
                "integrated_result": integrated_result,
                "enhancement_used": agent_result is not None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Integrated solve failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _execute_agent_enhanced_swarm(self, 
                                          problem_data: Dict[str, Any],
                                          pattern: str = "competitive",
                                          solver_count: int = 3,
                                          **kwargs) -> Dict[str, Any]:
        """Execute swarm solving with agent enhancement for all participating solvers"""
        start_time = time.time()
        
        try:
            # Select optimal solvers
            solver_selection = self.solver_selector.select_optimal_solver(problem_data)
            selected_solvers = [solver_selection.primary_solver] + solver_selection.backup_solvers[:solver_count-1]
            
            # Execute traditional swarm
            swarm_result = await self.swarm_orchestrator.execute(
                operation="orchestrate_swarm",
                problem_data=problem_data,
                pattern=pattern,
                solver_count=solver_count,
                selected_solvers=selected_solvers
            )
            
            # Enhance results with agent insights
            enhanced_results = []
            for solver_name in selected_solvers:
                agent_name = None
                for agent, mapping in self.integrated_agents.items():
                    if mapping["solver_name"] == solver_name:
                        agent_name = agent
                        break
                
                if agent_name:
                    try:
                        # Get agent insights for this solver
                        agent_insights = await self._get_solver_agent_insights(
                            agent_name, solver_name, problem_data
                        )
                        enhanced_results.append({
                            "solver_name": solver_name,
                            "agent_insights": agent_insights
                        })
                    except Exception as e:
                        self.logger.warning(f"Failed to get agent insights for {solver_name}: {e}")
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "pattern": pattern,
                "execution_time": execution_time,
                "swarm_result": swarm_result,
                "agent_enhancements": enhanced_results,
                "solvers_used": selected_solvers
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Agent enhanced swarm failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _compare_traditional_vs_agent(self, 
                                          problem_data: Dict[str, Any],
                                          solver_name: str,
                                          model_spec: Dict[str, Any],
                                          **kwargs) -> Dict[str, Any]:
        """Compare traditional solver execution with agent-enhanced execution"""
        start_time = time.time()
        
        try:
            # Execute traditional solving
            traditional_start = time.time()
            traditional_result = await self.swarm_orchestrator.execute(
                operation="competitive_solving",
                problem_data=problem_data,
                selected_solvers=[solver_name]
            )
            traditional_time = time.time() - traditional_start
            
            # Execute agent-enhanced solving
            agent_result = None
            agent_time = 0.0
            
            agent_name = None
            for agent, mapping in self.integrated_agents.items():
                if mapping["solver_name"] == solver_name:
                    agent_name = agent
                    break
            
            if agent_name:
                agent_start = time.time()
                try:
                    from tools.solver_tool import ModelSpecification
                    
                    model_specification = ModelSpecification(
                        problem_type=model_spec.get("problem_type", "linear_programming"),
                        variables=model_spec.get("variables", []),
                        constraints=model_spec.get("constraints", []),
                        objective=model_spec.get("objective", {}),
                        solver_hints=model_spec.get("solver_hints", {}),
                        metadata=model_spec.get("metadata", {})
                    )
                    
                    agent_result = await self.agent_executor.execute_solver_agent(
                        solver_name=agent_name,
                        problem_data=problem_data,
                        model_spec=model_specification
                    )
                    agent_time = time.time() - agent_start
                    
                except Exception as e:
                    self.logger.error(f"Agent execution failed: {e}")
                    agent_result = None
            
            # Generate comparison analysis
            comparison_analysis = await self._generate_comparison_analysis(
                traditional_result, agent_result, traditional_time, agent_time, solver_name
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "solver_name": solver_name,
                "execution_time": execution_time,
                "traditional_result": traditional_result,
                "traditional_execution_time": traditional_time,
                "agent_result": asdict(agent_result) if agent_result else None,
                "agent_execution_time": agent_time,
                "comparison_analysis": comparison_analysis
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Traditional vs agent comparison failed: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _get_agent_recommendations(self, 
                                       problem_data: Dict[str, Any],
                                       **kwargs) -> Dict[str, Any]:
        """Get solver recommendations from all available agents"""
        try:
            recommendations = {}
            
            for agent_name in self.agent_executor.get_available_agents():
                try:
                    # Get agent capabilities
                    capabilities = self.agent_executor.get_agent_capabilities(agent_name)
                    
                    # Generate recommendation based on problem characteristics
                    recommendation = await self._generate_agent_recommendation(
                        agent_name, capabilities, problem_data
                    )
                    
                    recommendations[agent_name] = recommendation
                    
                except Exception as e:
                    self.logger.warning(f"Failed to get recommendation from {agent_name}: {e}")
            
            # Rank recommendations
            ranked_recommendations = await self._rank_agent_recommendations(
                recommendations, problem_data
            )
            
            return {
                "success": True,
                "recommendations": recommendations,
                "ranked_recommendations": ranked_recommendations,
                "total_agents": len(recommendations)
            }
            
        except Exception as e:
            error_msg = f"Failed to get agent recommendations: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _analyze_agent_performance(self, **kwargs) -> Dict[str, Any]:
        """Analyze performance of solver agents"""
        try:
            # Get execution statistics from agent executor
            agent_stats = self.agent_executor.get_execution_statistics()
            
            # Get performance history from swarm orchestrator
            swarm_stats = getattr(self.swarm_orchestrator, 'performance_metrics', {})
            
            # Combine and analyze performance data
            performance_analysis = {
                "agent_statistics": agent_stats,
                "swarm_statistics": dict(swarm_stats) if swarm_stats else {},
                "integration_performance": self._analyze_integration_performance(),
                "recommendations": self._generate_performance_recommendations(agent_stats)
            }
            
            return {
                "success": True,
                "performance_analysis": performance_analysis
            }
            
        except Exception as e:
            error_msg = f"Failed to analyze agent performance: {str(e)}"
            self.logger.error(error_msg)
            raise ToolExecutionError(error_msg, self.name)
    
    async def _integrate_results(self, 
                               traditional_result: Dict[str, Any],
                               agent_result: Optional[SolverAgentResult],
                               solver_name: str,
                               problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate traditional solver results with agent insights"""
        
        integrated_insights = {
            "solver_performance": traditional_result.get("performance_comparison", {}),
            "solution_quality": traditional_result.get("best_solution", {}),
            "execution_metrics": {
                "traditional_time": traditional_result.get("execution_time", 0),
                "agent_time": agent_result.solver_result.execution_time if agent_result else 0
            }
        }
        
        if agent_result:
            integrated_insights.update({
                "agent_insights": agent_result.agent_insights,
                "performance_analysis": agent_result.performance_analysis,
                "recommendations": agent_result.recommendations,
                "confidence_score": agent_result.confidence_score
            })
        
        # Generate enhanced recommendations using Strands if available
        if self.strands_tools.get('use_agent'):
            try:
                enhanced_explanation = self.strands_tools['use_agent'](
                    prompt=f"""Analyze and explain the integrated optimization results:
                    
                    Solver: {solver_name}
                    Traditional Result: {json.dumps(traditional_result, indent=2)}
                    Agent Insights: {json.dumps(agent_result.agent_insights if agent_result else {}, indent=2)}
                    
                    Provide comprehensive analysis including:
                    1. Solution quality assessment
                    2. Performance comparison
                    3. Implementation recommendations
                    4. Manufacturing-specific insights
                    """,
                    max_tokens=1000
                )
                
                integrated_insights["enhanced_explanation"] = enhanced_explanation
                
            except Exception as e:
                self.logger.warning(f"Failed to generate enhanced explanation: {e}")
        
        return integrated_insights
    
    async def _get_solver_agent_insights(self, 
                                       agent_name: str,
                                       solver_name: str,
                                       problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights from a specific solver agent"""
        
        # Get agent capabilities
        capabilities = self.agent_executor.get_agent_capabilities(agent_name)
        
        # Generate insights based on problem characteristics
        insights = {
            "solver_suitability": self._assess_solver_suitability(capabilities, problem_data),
            "expected_performance": self._predict_performance(capabilities, problem_data),
            "optimization_strategy": self._recommend_strategy(capabilities, problem_data),
            "implementation_considerations": self._get_implementation_considerations(capabilities)
        }
        
        return insights
    
    def _assess_solver_suitability(self, capabilities: Dict[str, Any], problem_data: Dict[str, Any]) -> str:
        """Assess how suitable a solver is for the given problem"""
        problem_type = problem_data.get("problem_type", "unknown")
        problem_size = problem_data.get("problem_size", "medium")
        
        if not capabilities:
            return "unknown"
        
        # Check if problem type matches solver capabilities
        problem_types = capabilities.get("problem_types", [])
        if problem_type in problem_types:
            # Check performance profile for problem size
            performance_profile = capabilities.get("performance_profile", {})
            size_score = performance_profile.get(f"{problem_size}_problems", 3)
            
            if size_score >= 4:
                return "excellent"
            elif size_score >= 3:
                return "good"
            else:
                return "moderate"
        
        return "poor"
    
    def _predict_performance(self, capabilities: Dict[str, Any], problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict solver performance based on capabilities and problem characteristics"""
        if not capabilities:
            return {"prediction": "unknown"}
        
        performance_profile = capabilities.get("performance_profile", {})
        problem_size = problem_data.get("problem_size", "medium")
        
        return {
            "speed_prediction": performance_profile.get("speed", 3),
            "memory_efficiency": performance_profile.get("memory_efficiency", 3),
            "robustness": performance_profile.get("robustness", 3),
            "size_suitability": performance_profile.get(f"{problem_size}_problems", 3)
        }
    
    def _recommend_strategy(self, capabilities: Dict[str, Any], problem_data: Dict[str, Any]) -> str:
        """Recommend optimization strategy based on solver capabilities"""
        if not capabilities:
            return "standard approach"
        
        category = capabilities.get("category", "unknown")
        
        if category == "linear_programming":
            return "Use dual simplex method with preprocessing for optimal performance"
        elif category == "mixed_integer_programming":
            return "Enable cutting planes and heuristics for faster convergence"
        elif category == "constraint_programming":
            return "Use parallel search workers and solution hints for complex scheduling"
        elif category == "nonlinear_programming":
            return "Apply interior point methods with careful initialization"
        else:
            return "Apply solver-specific best practices"
    
    def _get_implementation_considerations(self, capabilities: Dict[str, Any]) -> List[str]:
        """Get implementation considerations for the solver"""
        if not capabilities:
            return ["Standard implementation considerations apply"]
        
        considerations = []
        
        if capabilities.get("parallel_capable", False):
            considerations.append("Consider enabling parallel processing for better performance")
        
        performance_profile = capabilities.get("performance_profile", {})
        if performance_profile.get("memory_efficiency", 3) < 3:
            considerations.append("Monitor memory usage for large problems")
        
        if performance_profile.get("speed", 3) >= 4:
            considerations.append("Excellent for time-critical applications")
        
        if performance_profile.get("robustness", 3) >= 4:
            considerations.append("Reliable choice for production environments")
        
        return considerations if considerations else ["Standard implementation considerations apply"]
    
    async def _generate_comparison_analysis(self, 
                                          traditional_result: Dict[str, Any],
                                          agent_result: Optional[SolverAgentResult],
                                          traditional_time: float,
                                          agent_time: float,
                                          solver_name: str) -> Dict[str, Any]:
        """Generate comprehensive comparison analysis"""
        
        analysis = {
            "performance_comparison": {
                "traditional_time": traditional_time,
                "agent_time": agent_time,
                "time_difference": agent_time - traditional_time,
                "relative_performance": agent_time / traditional_time if traditional_time > 0 else 1.0
            },
            "capability_comparison": {
                "traditional_capabilities": ["Standard solver execution", "Basic result reporting"],
                "agent_capabilities": [
                    "Enhanced problem analysis",
                    "Detailed performance insights",
                    "Manufacturing-specific recommendations",
                    "Confidence scoring"
                ] if agent_result else []
            },
            "value_proposition": self._assess_agent_value_proposition(agent_result, traditional_time, agent_time)
        }
        
        return analysis
    
    def _assess_agent_value_proposition(self, 
                                      agent_result: Optional[SolverAgentResult],
                                      traditional_time: float,
                                      agent_time: float) -> Dict[str, Any]:
        """Assess the value proposition of using solver agents"""
        
        if not agent_result:
            return {
                "overall_value": "low",
                "reasoning": "Agent enhancement not available",
                "recommendation": "Use traditional solver"
            }
        
        # Calculate value based on insights quality and time overhead
        time_overhead = (agent_time - traditional_time) / traditional_time if traditional_time > 0 else 0
        confidence_score = agent_result.confidence_score
        insights_count = len(agent_result.recommendations)
        
        if confidence_score >= 0.9 and time_overhead < 0.5 and insights_count >= 3:
            return {
                "overall_value": "high",
                "reasoning": "High confidence insights with acceptable time overhead",
                "recommendation": "Use agent enhancement for critical problems"
            }
        elif confidence_score >= 0.7 and time_overhead < 1.0:
            return {
                "overall_value": "medium",
                "reasoning": "Good insights with moderate time overhead",
                "recommendation": "Consider agent enhancement for complex problems"
            }
        else:
            return {
                "overall_value": "low",
                "reasoning": "Limited insights or high time overhead",
                "recommendation": "Use traditional solver for routine problems"
            }
    
    async def _generate_agent_recommendation(self, 
                                           agent_name: str,
                                           capabilities: Dict[str, Any],
                                           problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendation from a specific agent"""
        
        suitability = self._assess_solver_suitability(capabilities, problem_data)
        performance_prediction = self._predict_performance(capabilities, problem_data)
        
        return {
            "agent_name": agent_name,
            "suitability": suitability,
            "performance_prediction": performance_prediction,
            "recommendation_score": self._calculate_recommendation_score(suitability, performance_prediction),
            "reasoning": f"Based on {capabilities.get('category', 'unknown')} capabilities and problem characteristics"
        }
    
    def _calculate_recommendation_score(self, suitability: str, performance_prediction: Dict[str, Any]) -> float:
        """Calculate numerical recommendation score"""
        suitability_scores = {"excellent": 1.0, "good": 0.8, "moderate": 0.6, "poor": 0.3, "unknown": 0.5}
        base_score = suitability_scores.get(suitability, 0.5)
        
        # Adjust based on performance prediction
        avg_performance = sum(performance_prediction.values()) / len(performance_prediction) if performance_prediction else 3
        performance_factor = avg_performance / 5.0  # Normalize to 0-1
        
        return min(1.0, base_score * performance_factor)
    
    async def _rank_agent_recommendations(self, 
                                        recommendations: Dict[str, Dict[str, Any]],
                                        problem_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank agent recommendations by score"""
        
        ranked = []
        for agent_name, recommendation in recommendations.items():
            ranked.append({
                "agent_name": agent_name,
                "score": recommendation.get("recommendation_score", 0.0),
                "suitability": recommendation.get("suitability", "unknown"),
                "reasoning": recommendation.get("reasoning", "")
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        return ranked
    
    def _analyze_integration_performance(self) -> Dict[str, Any]:
        """Analyze integration performance metrics"""
        return {
            "integrated_agents": len(self.integrated_agents),
            "available_agents": len(self.agent_executor.get_available_agents()),
            "integration_success_rate": 1.0,  # Placeholder
            "average_enhancement_overhead": 0.2  # Placeholder
        }
    
    def _generate_performance_recommendations(self, agent_stats: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        total_executions = agent_stats.get("total_executions", 0)
        success_rate = agent_stats.get("success_rate", 0.0)
        
        if total_executions == 0:
            recommendations.append("No agent executions recorded - consider testing agent capabilities")
        elif success_rate < 0.8:
            recommendations.append("Agent success rate is low - investigate common failure modes")
        elif success_rate >= 0.95:
            recommendations.append("Excellent agent performance - consider expanding agent usage")
        
        return recommendations
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate integration parameters"""
        operation = kwargs.get("operation")
        if not operation:
            return False
        
        if operation in ["integrated_solve", "compare_traditional_vs_agent"]:
            return all(key in kwargs for key in ["problem_data", "solver_name", "model_spec"])
        elif operation == "agent_enhanced_swarm":
            return "problem_data" in kwargs
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup integration resources"""
        if hasattr(self.swarm_orchestrator, 'cleanup'):
            await self.swarm_orchestrator.cleanup()
        
        if hasattr(self.agent_executor, 'cleanup'):
            await self.agent_executor.cleanup()