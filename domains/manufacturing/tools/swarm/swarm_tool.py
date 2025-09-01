"""
Swarm Intelligence Tool for DcisionAI Platform
Coordinates multiple AI agents for collective problem solving
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import json

try:
    from strands import Agent, ToolExecutionError, ToolInitializationError
except ImportError:
    from tools.base import BaseTool, ToolExecutionError, ToolInitializationError

logger = logging.getLogger(__name__)


class CoordinationPattern(Enum):
    """Available coordination patterns for swarm intelligence"""
    COLLABORATIVE = "collaborative"  # Agents share information and build together
    COMPETITIVE = "competitive"      # Agents compete for best solutions
    HIERARCHICAL = "hierarchical"    # Leader-follower structure
    CONSENSUS = "consensus"          # Agents reach agreement through voting


class SwarmAgent:
    """Individual agent in the swarm"""
    
    def __init__(self, agent_id: str, specialization: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.specialization = specialization
        self.capabilities = capabilities
        self.performance_history = []
        self.current_task = None
        self.shared_context = {}
        
    async def execute_task(self, task: Dict[str, Any], shared_memory: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute assigned task with specialization"""
        try:
            start_time = datetime.utcnow()
            
            # Apply specialization to task
            specialized_task = await self._apply_specialization(task)
            
            # Use shared context if available
            if shared_memory:
                specialized_task["shared_context"] = shared_memory
            
            # Execute based on specialization
            result = await self._execute_specialized_task(specialized_task)
            
            # Record performance
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.performance_history.append({
                "task_id": task.get("task_id"),
                "execution_time": execution_time,
                "success": True,
                "timestamp": start_time.isoformat()
            })
            
            return {
                "agent_id": self.agent_id,
                "specialization": self.specialization,
                "result": result,
                "confidence": result.get("confidence", 0.8),
                "execution_time": execution_time,
                "insights": result.get("insights", []),
                "recommendations": result.get("recommendations", [])
            }
            
        except Exception as e:
            logger.error(f"SwarmAgent {self.agent_id} task execution failed: {e}")
            return {
                "agent_id": self.agent_id,
                "specialization": self.specialization,
                "error": str(e),
                "success": False
            }
    
    async def _apply_specialization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Apply agent specialization to the task"""
        specialized_task = task.copy()
        specialized_task["specialization"] = self.specialization
        specialized_task["focus_areas"] = self._get_focus_areas()
        return specialized_task
    
    def _get_focus_areas(self) -> List[str]:
        """Get focus areas based on specialization"""
        focus_map = {
            "capacity_analysis": ["throughput", "bottlenecks", "utilization", "constraints"],
            "quality_optimization": ["defect_rates", "standards", "compliance", "improvement"],
            "cost_minimization": ["expenses", "efficiency", "waste_reduction", "roi"],
            "scheduling_optimization": ["timeline", "resources", "dependencies", "priorities"],
            "risk_assessment": ["uncertainties", "mitigation", "scenarios", "contingency"],
            "data_analysis": ["patterns", "trends", "correlations", "insights"],
            "model_building": ["formulation", "variables", "constraints", "objectives"],
            "solution_validation": ["feasibility", "optimality", "robustness", "sensitivity"]
        }
        return focus_map.get(self.specialization, ["general_analysis"])
    
    async def _execute_specialized_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task based on specialization"""
        specialization = task["specialization"]
        focus_areas = task["focus_areas"]
        
        # Simulate specialized analysis based on focus areas
        if specialization == "capacity_analysis":
            return await self._analyze_capacity(task)
        elif specialization == "quality_optimization":
            return await self._optimize_quality(task)
        elif specialization == "cost_minimization":
            return await self._minimize_costs(task)
        elif specialization == "scheduling_optimization":
            return await self._optimize_schedule(task)
        elif specialization == "risk_assessment":
            return await self._assess_risks(task)
        else:
            return await self._general_analysis(task)
    
    async def _analyze_capacity(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized capacity analysis"""
        # Simulate capacity analysis
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "analysis_type": "capacity_analysis",
            "findings": {
                "current_utilization": 0.78,
                "bottlenecks": ["assembly_line_2", "quality_control"],
                "max_capacity": 1200,
                "recommended_capacity": 1350
            },
            "insights": [
                "Assembly line 2 is operating at 95% capacity",
                "Quality control station creates 15-minute delays",
                "Adding one more quality inspector could increase throughput by 12%"
            ],
            "recommendations": [
                "Add parallel assembly line",
                "Implement automated quality checks",
                "Cross-train workers for flexibility"
            ],
            "confidence": 0.85
        }
    
    async def _optimize_quality(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized quality optimization"""
        await asyncio.sleep(0.1)
        
        return {
            "analysis_type": "quality_optimization",
            "findings": {
                "current_defect_rate": 0.023,
                "target_defect_rate": 0.015,
                "quality_stations": 3,
                "inspection_coverage": 0.85
            },
            "insights": [
                "Defect rate is 53% above target",
                "Station 2 has highest defect rate (4.2%)",
                "Preventive measures could reduce defects by 40%"
            ],
            "recommendations": [
                "Implement statistical process control",
                "Add real-time quality monitoring",
                "Increase inspection frequency at Station 2"
            ],
            "confidence": 0.82
        }
    
    async def _minimize_costs(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized cost minimization"""
        await asyncio.sleep(0.1)
        
        return {
            "analysis_type": "cost_minimization",
            "findings": {
                "current_cost_per_unit": 45.30,
                "target_cost_per_unit": 42.00,
                "major_cost_drivers": ["materials", "labor", "overhead"],
                "potential_savings": 0.15
            },
            "insights": [
                "Material costs account for 60% of total cost",
                "Overtime labor adds 8% premium",
                "Energy costs could be reduced by 20%"
            ],
            "recommendations": [
                "Negotiate bulk material discounts",
                "Optimize shift scheduling to reduce overtime",
                "Implement energy-efficient equipment"
            ],
            "confidence": 0.88
        }
    
    async def _optimize_schedule(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized scheduling optimization"""
        await asyncio.sleep(0.1)
        
        return {
            "analysis_type": "scheduling_optimization",
            "findings": {
                "current_makespan": 480,  # minutes
                "optimal_makespan": 420,
                "resource_conflicts": 3,
                "critical_path_length": 380
            },
            "insights": [
                "Current schedule has 12.5% slack time",
                "Resource conflicts cause 60-minute delays",
                "Parallel processing could reduce makespan by 15%"
            ],
            "recommendations": [
                "Implement parallel task execution",
                "Resolve resource conflicts through better allocation",
                "Use just-in-time scheduling for materials"
            ],
            "confidence": 0.79
        }
    
    async def _assess_risks(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized risk assessment"""
        await asyncio.sleep(0.1)
        
        return {
            "analysis_type": "risk_assessment",
            "findings": {
                "high_risk_factors": 2,
                "medium_risk_factors": 5,
                "overall_risk_score": 0.35,
                "mitigation_coverage": 0.70
            },
            "insights": [
                "Supply chain disruption is highest risk (0.8 probability)",
                "Equipment failure could cause 2-day delays",
                "Quality issues have moderate financial impact"
            ],
            "recommendations": [
                "Diversify supplier base",
                "Implement predictive maintenance",
                "Create quality contingency plans"
            ],
            "confidence": 0.75
        }
    
    async def _general_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """General analysis for unknown specializations"""
        await asyncio.sleep(0.1)
        
        return {
            "analysis_type": "general_analysis",
            "findings": {
                "complexity_score": 0.6,
                "data_quality": 0.8,
                "analysis_depth": "moderate"
            },
            "insights": [
                "Problem requires multi-faceted approach",
                "Data quality is sufficient for analysis",
                "Multiple optimization objectives identified"
            ],
            "recommendations": [
                "Break down into sub-problems",
                "Apply specialized analysis techniques",
                "Validate results with domain experts"
            ],
            "confidence": 0.70
        }


class IntentSwarmAgentWrapper(SwarmAgent):
    """Wrapper to adapt IntentSwarmAgent to SwarmAgent interface"""
    
    def __init__(self, intent_agent):
        self.intent_agent = intent_agent
        super().__init__(
            agent_id=intent_agent.agent_id,
            specialization=intent_agent.specialization,
            capabilities=intent_agent._get_focus_areas()
        )
    
    async def execute_task(self, task: Dict[str, Any], shared_memory: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute task using the specialized intent agent"""
        try:
            # Add Strands tools to shared memory if available
            if shared_memory is None:
                shared_memory = {}
            
            # Execute using the specialized intent agent
            result = await self.intent_agent.execute_task(task, shared_memory)
            
            # Ensure result has the expected SwarmAgent format
            if "success" not in result:
                result["success"] = not result.get("error")
            
            return result
            
        except Exception as e:
            logger.error(f"IntentSwarmAgentWrapper execution failed: {e}")
            return {
                "agent_id": self.agent_id,
                "specialization": self.specialization,
                "error": str(e),
                "success": False
            }


class SwarmCoordinator:
    """Coordinates swarm agents using different patterns"""
    
    def __init__(self, coordination_pattern: CoordinationPattern):
        self.pattern = coordination_pattern
        self.shared_memory = {}
        self.coordination_history = []
        
    async def coordinate(self, agents: List[SwarmAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate agents based on pattern"""
        coordination_start = datetime.utcnow()
        
        if self.pattern == CoordinationPattern.COLLABORATIVE:
            result = await self._collaborative_coordination(agents, task)
        elif self.pattern == CoordinationPattern.COMPETITIVE:
            result = await self._competitive_coordination(agents, task)
        elif self.pattern == CoordinationPattern.HIERARCHICAL:
            result = await self._hierarchical_coordination(agents, task)
        elif self.pattern == CoordinationPattern.CONSENSUS:
            result = await self._consensus_coordination(agents, task)
        else:
            raise ValueError(f"Unknown coordination pattern: {self.pattern}")
        
        coordination_time = (datetime.utcnow() - coordination_start).total_seconds()
        
        # Record coordination history
        self.coordination_history.append({
            "pattern": self.pattern.value,
            "agents": len(agents),
            "coordination_time": coordination_time,
            "success": result.get("success", True),
            "timestamp": coordination_start.isoformat()
        })
        
        result["coordination_time"] = coordination_time
        result["coordination_pattern"] = self.pattern.value
        
        return result
    
    async def _collaborative_coordination(self, agents: List[SwarmAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborative pattern: agents share information and build together"""
        rounds = 2  # Number of collaboration rounds
        all_results = []
        
        for round_num in range(rounds):
            logger.info(f"Collaborative round {round_num + 1}/{rounds}")
            
            # Each agent works with shared context
            round_tasks = []
            for agent in agents:
                agent_task = task.copy()
                agent_task["round"] = round_num
                agent_task["shared_memory"] = self.shared_memory.copy()
                round_tasks.append(agent.execute_task(agent_task, self.shared_memory))
            
            # Execute in parallel
            round_results = await asyncio.gather(*round_tasks, return_exceptions=True)
            
            # Filter successful results
            successful_results = [r for r in round_results if isinstance(r, dict) and r.get("success", True)]
            all_results.extend(successful_results)
            
            # Update shared memory with insights
            for result in successful_results:
                if "insights" in result:
                    for insight in result["insights"]:
                        if insight not in self.shared_memory.get("insights", []):
                            self.shared_memory.setdefault("insights", []).append(insight)
                
                if "recommendations" in result:
                    for rec in result["recommendations"]:
                        if rec not in self.shared_memory.get("recommendations", []):
                            self.shared_memory.setdefault("recommendations", []).append(rec)
        
        # Synthesize collaborative result
        return await self._synthesize_collaborative_results(all_results)
    
    async def _competitive_coordination(self, agents: List[SwarmAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Competitive pattern: agents compete for best solutions"""
        logger.info(f"Competitive coordination with {len(agents)} agents")
        
        # All agents work on the same task independently
        tasks = [agent.execute_task(task) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success", True)]
        
        if not successful_results:
            return {"success": False, "error": "No agents produced successful results"}
        
        # Rank solutions by confidence and quality
        ranked_results = sorted(successful_results, key=lambda x: x.get("confidence", 0), reverse=True)
        
        # Select top solutions
        top_solutions = ranked_results[:min(3, len(ranked_results))]
        
        return await self._synthesize_competitive_results(top_solutions, ranked_results)
    
    async def _hierarchical_coordination(self, agents: List[SwarmAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Hierarchical pattern: leader-follower structure"""
        if not agents:
            return {"success": False, "error": "No agents available"}
        
        # Select leader (highest performing agent or first one)
        leader = max(agents, key=lambda a: len(a.performance_history)) if agents[0].performance_history else agents[0]
        followers = [a for a in agents if a != leader]
        
        logger.info(f"Hierarchical coordination: leader={leader.specialization}, followers={len(followers)}")
        
        # Leader analyzes and decomposes task
        leader_task = task.copy()
        leader_task["role"] = "leader"
        leader_result = await leader.execute_task(leader_task)
        
        if not leader_result.get("success", True):
            return {"success": False, "error": "Leader failed to analyze task"}
        
        # Followers work on sub-tasks based on leader's analysis
        follower_tasks = []
        for i, follower in enumerate(followers):
            follower_task = task.copy()
            follower_task["role"] = "follower"
            follower_task["leader_guidance"] = leader_result
            follower_task["subtask_id"] = i
            follower_tasks.append(follower.execute_task(follower_task))
        
        follower_results = await asyncio.gather(*follower_tasks, return_exceptions=True)
        successful_follower_results = [r for r in follower_results if isinstance(r, dict) and r.get("success", True)]
        
        return await self._synthesize_hierarchical_results(leader_result, successful_follower_results)
    
    async def _consensus_coordination(self, agents: List[SwarmAgent], task: Dict[str, Any]) -> Dict[str, Any]:
        """Consensus pattern: agents reach agreement through voting"""
        max_iterations = 3
        current_solution = None
        
        for iteration in range(max_iterations):
            logger.info(f"Consensus iteration {iteration + 1}/{max_iterations}")
            
            # Each agent proposes a solution or improvement
            proposal_tasks = []
            for agent in agents:
                agent_task = task.copy()
                agent_task["iteration"] = iteration
                agent_task["current_solution"] = current_solution
                proposal_tasks.append(agent.execute_task(agent_task))
            
            proposals = await asyncio.gather(*proposal_tasks, return_exceptions=True)
            successful_proposals = [p for p in proposals if isinstance(p, dict) and p.get("success", True)]
            
            if not successful_proposals:
                break
            
            # Vote on best proposal
            current_solution = await self._consensus_vote(agents, successful_proposals)
            
            # Check if consensus reached (simplified: if confidence > threshold)
            if current_solution.get("confidence", 0) > 0.8:
                break
        
        return current_solution or {"success": False, "error": "Failed to reach consensus"}
    
    async def _consensus_vote(self, agents: List[SwarmAgent], proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple voting mechanism for consensus"""
        if not proposals:
            return {"success": False, "error": "No proposals to vote on"}
        
        # Simple voting: select proposal with highest average confidence
        best_proposal = max(proposals, key=lambda p: p.get("confidence", 0))
        
        # Combine insights from all proposals
        all_insights = []
        all_recommendations = []
        
        for proposal in proposals:
            all_insights.extend(proposal.get("insights", []))
            all_recommendations.extend(proposal.get("recommendations", []))
        
        # Remove duplicates
        unique_insights = list(set(all_insights))
        unique_recommendations = list(set(all_recommendations))
        
        best_proposal["insights"] = unique_insights
        best_proposal["recommendations"] = unique_recommendations
        best_proposal["consensus_votes"] = len(proposals)
        
        return best_proposal
    
    async def _synthesize_collaborative_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize results from collaborative coordination"""
        if not results:
            return {"success": False, "error": "No results to synthesize"}
        
        # Combine all insights and recommendations
        all_insights = []
        all_recommendations = []
        total_confidence = 0
        specializations = []
        
        for result in results:
            all_insights.extend(result.get("insights", []))
            all_recommendations.extend(result.get("recommendations", []))
            total_confidence += result.get("confidence", 0)
            specializations.append(result.get("specialization", "unknown"))
        
        # Remove duplicates and calculate averages
        unique_insights = list(set(all_insights))
        unique_recommendations = list(set(all_recommendations))
        avg_confidence = total_confidence / len(results) if results else 0
        
        return {
            "success": True,
            "coordination_type": "collaborative",
            "agents_participated": len(results),
            "specializations": list(set(specializations)),
            "insights": unique_insights,
            "recommendations": unique_recommendations,
            "confidence": avg_confidence,
            "synthesis_method": "collaborative_aggregation"
        }
    
    async def _synthesize_competitive_results(self, top_solutions: List[Dict[str, Any]], all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize results from competitive coordination"""
        if not top_solutions:
            return {"success": False, "error": "No solutions to synthesize"}
        
        best_solution = top_solutions[0]
        
        return {
            "success": True,
            "coordination_type": "competitive",
            "agents_participated": len(all_results),
            "winning_solution": best_solution,
            "runner_up_solutions": top_solutions[1:],
            "confidence": best_solution.get("confidence", 0),
            "insights": best_solution.get("insights", []),
            "recommendations": best_solution.get("recommendations", []),
            "synthesis_method": "competitive_selection"
        }
    
    async def _synthesize_hierarchical_results(self, leader_result: Dict[str, Any], follower_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize results from hierarchical coordination"""
        # Combine leader's analysis with followers' work
        combined_insights = leader_result.get("insights", [])
        combined_recommendations = leader_result.get("recommendations", [])
        
        for result in follower_results:
            combined_insights.extend(result.get("insights", []))
            combined_recommendations.extend(result.get("recommendations", []))
        
        return {
            "success": True,
            "coordination_type": "hierarchical",
            "leader_specialization": leader_result.get("specialization"),
            "followers_count": len(follower_results),
            "insights": list(set(combined_insights)),
            "recommendations": list(set(combined_recommendations)),
            "confidence": leader_result.get("confidence", 0),
            "synthesis_method": "hierarchical_integration"
        }


class SwarmTool(BaseTool):
    """Swarm Intelligence Tool for collective problem solving"""
    
    def __init__(self):
        super().__init__(
            name="swarm_tool",
            description="Coordinate multiple AI agents for collective intelligence and problem solving",
            version="1.0.0"
        )
        self.agent_pool = {}
        self.active_swarms = {}
        self.coordination_patterns = {
            pattern.value: pattern for pattern in CoordinationPattern
        }
        self.strands_agent = None
        self.strands_tools = {}
    
    async def initialize(self) -> bool:
        """Initialize Swarm Tool"""
        try:
            # Initialize Strands tools integration (graceful degradation)
            await self._initialize_strands_tools()
            
            # Initialize agent pool
            await self._initialize_agent_pool()
            
            self._initialized = True
            self.logger.info("Swarm Tool initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Swarm Tool: {e}")
            return False
    
    async def _initialize_strands_tools(self):
        """Initialize Strands tools integration"""
        try:
            from strands_tools import memory, retrieve, use_aws, think, use_llm
            from strands import Agent
            
            self.strands_agent = Agent(tools=[memory, retrieve, use_aws, think, use_llm])
            self.strands_tools = {
                'memory': self.strands_agent.tool.memory,
                'retrieve': self.strands_agent.tool.retrieve,
                'use_aws': self.strands_agent.tool.use_aws,
                'think': self.strands_agent.tool.think,
                'use_llm': self.strands_agent.tool.use_llm
            }
            self.logger.info("Strands tools initialized for swarm coordination")
            
        except ImportError as e:
            self.logger.warning(f"Strands tools not available: {e}")
            self.strands_agent = None
            self.strands_tools = {}
    
    async def _initialize_agent_pool(self):
        """Initialize pool of available agent specializations"""
        self.agent_pool = {
            # Manufacturing specializations
            "capacity_analysis": ["throughput", "bottlenecks", "utilization"],
            "quality_optimization": ["defect_rates", "standards", "compliance"],
            "cost_minimization": ["expenses", "efficiency", "waste_reduction"],
            "scheduling_optimization": ["timeline", "resources", "dependencies"],
            "risk_assessment": ["uncertainties", "mitigation", "scenarios"],
            "data_analysis": ["patterns", "trends", "correlations"],
            "model_building": ["formulation", "variables", "constraints"],
            "solution_validation": ["feasibility", "optimality", "robustness"],
            
            # Intent-specific specializations
            "intent_classification": ["request_type", "optimization_type", "domain_analysis"],
            "domain_detection": ["manufacturing", "finance", "logistics", "healthcare"],
            "entity_extraction": ["constraints", "objectives", "parameters"],
            "context_enrichment": ["knowledge_base", "domain_expertise", "recommendations"]
        }
        
        self.logger.info(f"Agent pool initialized with {len(self.agent_pool)} specializations")
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute swarm intelligence task"""
        operation = kwargs.get("operation", "swarm")
        
        if operation == "swarm":
            return await self._execute_swarm(**kwargs)
        elif operation == "list_patterns":
            return await self._list_coordination_patterns()
        elif operation == "list_specializations":
            return await self._list_specializations()
        else:
            raise ToolExecutionError(f"Unknown operation: {operation}", self.name)
    
    async def _execute_swarm(self, 
                           task: str,
                           swarm_size: int = 3,
                           coordination_pattern: str = "collaborative",
                           specializations: Optional[List[str]] = None,
                           **kwargs) -> Dict[str, Any]:
        """Execute swarm intelligence task"""
        start_time = datetime.utcnow()
        swarm_id = str(uuid.uuid4())
        
        try:
            # Validate parameters
            if not await self.validate_parameters(
                task=task, 
                swarm_size=swarm_size, 
                coordination_pattern=coordination_pattern,
                specializations=specializations
            ):
                raise ToolExecutionError("Invalid swarm parameters", self.name)
            
            # Store swarm context in Strands memory if available
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Swarm task started: {task}",
                    metadata={
                        "type": "swarm_start",
                        "swarm_id": swarm_id,
                        "swarm_size": swarm_size,
                        "pattern": coordination_pattern
                    }
                )
            
            # Create swarm agents
            agents = await self._create_swarm_agents(swarm_size, specializations, task)
            
            # Create coordinator
            pattern = self.coordination_patterns[coordination_pattern]
            coordinator = SwarmCoordinator(pattern)
            
            # Prepare task for agents
            agent_task = {
                "task_id": swarm_id,
                "description": task,
                "context": kwargs.get("context", {}),
                "requirements": kwargs.get("requirements", []),
                "constraints": kwargs.get("constraints", [])
            }
            
            # Execute swarm coordination
            self.active_swarms[swarm_id] = {
                "agents": agents,
                "coordinator": coordinator,
                "start_time": start_time,
                "status": "running"
            }
            
            result = await coordinator.coordinate(agents, agent_task)
            
            # Update swarm status
            self.active_swarms[swarm_id]["status"] = "completed"
            self.active_swarms[swarm_id]["result"] = result
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Store results in Strands memory if available
            if self.strands_tools.get('memory'):
                self.strands_tools['memory'](
                    action="store",
                    content=f"Swarm task completed: {len(result.get('insights', []))} insights generated",
                    metadata={
                        "type": "swarm_complete",
                        "swarm_id": swarm_id,
                        "execution_time": execution_time,
                        "success": result.get("success", True)
                    }
                )
            
            # Add execution metadata
            result.update({
                "swarm_id": swarm_id,
                "task": task,
                "swarm_size": len(agents),
                "execution_time": execution_time,
                "timestamp": start_time.isoformat()
            })
            
            self._log_execution("swarm", kwargs, True, execution_time)
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution("swarm", kwargs, False, execution_time, str(e))
            
            # Update swarm status
            if swarm_id in self.active_swarms:
                self.active_swarms[swarm_id]["status"] = "failed"
                self.active_swarms[swarm_id]["error"] = str(e)
            
            raise ToolExecutionError(f"Swarm execution failed: {e}", self.name)
    
    async def _create_swarm_agents(self, swarm_size: int, specializations: Optional[List[str]], task: str) -> List[SwarmAgent]:
        """Create swarm agents with appropriate specializations"""
        agents = []
        
        # Check if this is an intent classification task
        if self._is_intent_classification_task(task, specializations):
            return await self._create_intent_swarm_agents(specializations or [])
        
        # Determine specializations
        if specializations:
            # Use provided specializations
            selected_specializations = specializations[:swarm_size]
        else:
            # Auto-select based on task content
            selected_specializations = await self._auto_select_specializations(task, swarm_size)
        
        # Pad with general agents if needed
        while len(selected_specializations) < swarm_size:
            selected_specializations.append("data_analysis")
        
        # Create agents
        for i, specialization in enumerate(selected_specializations):
            agent_id = f"agent_{i}_{specialization}"
            capabilities = self.agent_pool.get(specialization, ["general_analysis"])
            
            agent = SwarmAgent(agent_id, specialization, capabilities)
            agents.append(agent)
        
        self.logger.info(f"Created swarm with {len(agents)} agents: {[a.specialization for a in agents]}")
        return agents
    
    def _is_intent_classification_task(self, task: str, specializations: Optional[List[str]]) -> bool:
        """Check if this is an intent classification task"""
        if specializations:
            intent_specializations = {"intent_classification", "domain_detection", "entity_extraction", "context_enrichment"}
            return bool(set(specializations) & intent_specializations)
        
        task_lower = task.lower()
        return "intent" in task_lower and "classification" in task_lower
    
    async def _create_intent_swarm_agents(self, specializations: List[str]) -> List[SwarmAgent]:
        """Create specialized intent swarm agents"""
        try:
            from tools.swarm.agents.intent_swarm_agents import create_intent_swarm_agents, initialize_intent_swarm_agents
            
            # Create intent-specific agents
            intent_agents = create_intent_swarm_agents()
            initialized_agents = await initialize_intent_swarm_agents(intent_agents)
            
            # Convert to SwarmAgent format
            swarm_agents = []
            for agent in initialized_agents:
                # Create a wrapper SwarmAgent that delegates to the specialized intent agent
                swarm_agent = IntentSwarmAgentWrapper(agent)
                swarm_agents.append(swarm_agent)
            
            self.logger.info(f"Created {len(swarm_agents)} specialized intent swarm agents")
            return swarm_agents
            
        except ImportError as e:
            self.logger.warning(f"Intent swarm agents not available: {e}, falling back to regular agents")
            return await self._create_regular_swarm_agents(4, specializations)
        except Exception as e:
            self.logger.error(f"Failed to create intent swarm agents: {e}, falling back to regular agents")
            return await self._create_regular_swarm_agents(4, specializations)
    
    async def _create_regular_swarm_agents(self, swarm_size: int, specializations: List[str]) -> List[SwarmAgent]:
        """Create regular swarm agents as fallback"""
        agents = []
        
        for i in range(swarm_size):
            specialization = specializations[i] if i < len(specializations) else "data_analysis"
            capabilities = self.agent_pool.get(specialization, ["general_analysis"])
            
            agent = SwarmAgent(
                agent_id=f"agent_{i}_{specialization}",
                specialization=specialization,
                capabilities=capabilities
            )
            agents.append(agent)
        
        return agents
    
    async def _auto_select_specializations(self, task: str, swarm_size: int) -> List[str]:
        """Auto-select specializations based on task content"""
        task_lower = task.lower()
        
        # Keyword-based specialization selection
        specialization_keywords = {
            "capacity_analysis": ["capacity", "throughput", "bottleneck", "utilization"],
            "quality_optimization": ["quality", "defect", "standard", "compliance"],
            "cost_minimization": ["cost", "expense", "budget", "efficiency"],
            "scheduling_optimization": ["schedule", "timeline", "resource", "priority"],
            "risk_assessment": ["risk", "uncertainty", "scenario", "contingency"],
            "data_analysis": ["data", "analysis", "pattern", "trend"],
            "model_building": ["model", "optimization", "constraint", "objective"],
            "solution_validation": ["validate", "verify", "feasible", "optimal"]
        }
        
        # Score specializations based on keyword matches
        scores = {}
        for specialization, keywords in specialization_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            if score > 0:
                scores[specialization] = score
        
        # Select top specializations
        if scores:
            sorted_specializations = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
            return sorted_specializations[:swarm_size]
        else:
            # Default specializations for manufacturing optimization
            return ["capacity_analysis", "quality_optimization", "cost_minimization"][:swarm_size]
    
    async def _list_coordination_patterns(self) -> Dict[str, Any]:
        """List available coordination patterns"""
        return {
            "coordination_patterns": [
                {
                    "name": pattern.value,
                    "description": self._get_pattern_description(pattern)
                }
                for pattern in CoordinationPattern
            ]
        }
    
    def _get_pattern_description(self, pattern: CoordinationPattern) -> str:
        """Get description for coordination pattern"""
        descriptions = {
            CoordinationPattern.COLLABORATIVE: "Agents share information and build solutions together",
            CoordinationPattern.COMPETITIVE: "Agents compete to find the best solutions",
            CoordinationPattern.HIERARCHICAL: "Leader-follower structure with task decomposition",
            CoordinationPattern.CONSENSUS: "Agents reach agreement through iterative voting"
        }
        return descriptions.get(pattern, "Unknown pattern")
    
    async def _list_specializations(self) -> Dict[str, Any]:
        """List available agent specializations"""
        return {
            "specializations": [
                {
                    "name": specialization,
                    "capabilities": capabilities
                }
                for specialization, capabilities in self.agent_pool.items()
            ]
        }
    
    async def validate_parameters(self, **kwargs) -> bool:
        """Validate swarm tool parameters"""
        try:
            task = kwargs.get("task")
            swarm_size = kwargs.get("swarm_size", 3)
            coordination_pattern = kwargs.get("coordination_pattern", "collaborative")
            specializations = kwargs.get("specializations")
            
            # Validate required parameters
            if not task or not isinstance(task, str):
                self.logger.error(f"Invalid task parameter: {task}")
                return False
            
            if not isinstance(swarm_size, int) or swarm_size < 1 or swarm_size > 10:
                self.logger.error(f"Invalid swarm_size parameter: {swarm_size}")
                return False
            
            if coordination_pattern not in self.coordination_patterns:
                self.logger.error(f"Invalid coordination_pattern: {coordination_pattern}. Available: {list(self.coordination_patterns.keys())}")
                return False
            
            if specializations and not isinstance(specializations, list):
                self.logger.error(f"Invalid specializations parameter: {specializations}")
                return False
            
            if specializations:
                for spec in specializations:
                    if spec not in self.agent_pool:
                        self.logger.warning(f"Unknown specialization: {spec}. Available: {list(self.agent_pool.keys())}")
                        # Don't fail validation, just log warning - we can auto-select alternatives
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup swarm tool resources"""
        try:
            # Clear active swarms
            self.active_swarms.clear()
            
            # Clear agent pool
            self.agent_pool.clear()
            
            self.logger.info("Swarm Tool cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during Swarm Tool cleanup: {e}")