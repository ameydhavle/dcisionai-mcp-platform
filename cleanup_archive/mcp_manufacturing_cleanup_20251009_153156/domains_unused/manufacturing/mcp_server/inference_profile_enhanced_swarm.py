#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Inference Profile Enhanced Swarm
====================================================================

Base class for peer-to-peer agent swarms with inference profile optimization.
Provides swarm orchestration, peer-to-peer communication, and consensus mechanisms.

NO MOCK RESPONSES POLICY: All implementations use real AWS Bedrock calls only.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from swarm_inference_profile import SwarmInferenceProfile, InferenceProfileManager, AgentRole
from consensus_mechanism import ConsensusMechanism, ConsensusAlgorithm, AgentResult, ConsensusResult

logger = logging.getLogger(__name__)

@dataclass
class SwarmAgent:
    """Individual agent in the swarm."""
    agent_id: str
    specialization: str
    agent_role: AgentRole
    region: str
    inference_profile: SwarmInferenceProfile
    status: str = "active"
    peer_connections: List[str] = field(default_factory=list)
    task_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SwarmTask:
    """Task for swarm execution."""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: datetime
    priority: int = 1

@dataclass
class SwarmResult:
    """Result from swarm execution."""
    task_id: str
    consensus_result: ConsensusResult
    individual_results: Dict[str, AgentResult]
    execution_time: float
    swarm_metadata: Dict[str, Any]

class InferenceProfileEnhancedSwarm:
    """
    Base class for peer-to-peer agent swarms with inference profile optimization.
    
    NO MOCK RESPONSES: All swarm operations use real AWS Bedrock calls only.
    """
    
    def __init__(self, swarm_id: str, agent_count: int):
        self.swarm_id = swarm_id
        self.agent_count = agent_count
        self.agents: Dict[str, SwarmAgent] = {}
        self.peer_connections: Dict[str, List[str]] = {}
        self.consensus_mechanism = ConsensusMechanism()
        self.inference_profile_manager = InferenceProfileManager()
        self.executor = ThreadPoolExecutor(max_workers=agent_count)
        
        logger.info(f"🤖 InferenceProfileEnhancedSwarm initialized: {swarm_id} with {agent_count} agents")
    
    def add_agent(self, agent_id: str, specialization: str, agent_role: AgentRole, region: str):
        """
        Add agent with specialized inference profile to the peer-to-peer network.
        
        NO MOCK RESPONSES: Creates real inference profiles with AWS Bedrock integration.
        """
        try:
            # Create specialized inference profile for this agent
            inference_profile = self.inference_profile_manager.create_swarm_inference_profile(
                specialization=specialization,
                agent_role=agent_role,
                latency_requirement=100
            )
            
            # Create swarm agent
            agent = SwarmAgent(
                agent_id=agent_id,
                specialization=specialization,
                agent_role=agent_role,
                region=region,
                inference_profile=inference_profile
            )
            
            self.agents[agent_id] = agent
            self._establish_peer_connections(agent_id)
            
            logger.info(f"✅ Agent {agent_id} added to swarm {self.swarm_id} in {region}")
            
        except Exception as e:
            logger.error(f"❌ Failed to add agent {agent_id}: {str(e)}")
            raise
    
    def _establish_peer_connections(self, agent_id: str):
        """Establish peer-to-peer connections for collaborative decision making."""
        try:
            peer_connections = []
            for other_agent_id in self.agents:
                if other_agent_id != agent_id:
                    # Create bidirectional peer connection
                    peer_connections.append(other_agent_id)
                    if other_agent_id not in self.peer_connections:
                        self.peer_connections[other_agent_id] = []
                    self.peer_connections[other_agent_id].append(agent_id)
            
            self.peer_connections[agent_id] = peer_connections
            self.agents[agent_id].peer_connections = peer_connections
            
            logger.info(f"🔗 Established {len(peer_connections)} peer connections for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to establish peer connections for {agent_id}: {str(e)}")
            raise
    
    def execute_swarm_task(self, task: SwarmTask, 
                          consensus_algorithm: ConsensusAlgorithm = ConsensusAlgorithm.CONFIDENCE_AGGREGATION) -> SwarmResult:
        """
        Execute task using peer-to-peer swarm collaboration.
        
        NO MOCK RESPONSES: All agents use real AWS Bedrock calls.
        """
        start_time = datetime.now()
        
        try:
            # Handle both task objects and dictionaries
            task_id = getattr(task, 'task_id', task.get('task_id', 'unknown'))
            logger.info(f"🚀 Executing swarm task {task_id} with {len(self.agents)} agents")
            
            # Distribute task to all agents in parallel
            agent_results = self._execute_agents_parallel(task)
            
            # Execute peer-to-peer consensus mechanism
            consensus_result = self.consensus_mechanism.aggregate_results(
                agent_results, 
                consensus_algorithm
            )
            
            # Update agent performance metrics
            self._update_performance_metrics(agent_results, consensus_result)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create swarm result
            swarm_result = SwarmResult(
                task_id=getattr(task, 'task_id', task.get('task_id', 'unknown')),
                consensus_result=consensus_result,
                individual_results=agent_results,
                execution_time=execution_time,
                swarm_metadata={
                    "swarm_id": self.swarm_id,
                    "agent_count": len(self.agents),
                    "consensus_algorithm": consensus_algorithm.value,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            task_id = getattr(task, 'task_id', task.get('task_id', 'unknown'))
            logger.info(f"✅ Swarm task {task_id} completed in {execution_time:.2f}s")
            return swarm_result
            
        except Exception as e:
            task_id = getattr(task, 'task_id', task.get('task_id', 'unknown'))
            logger.error(f"❌ Swarm task {task_id} failed: {str(e)}")
            # NO MOCK RESPONSES - Return error gracefully
            execution_time = (datetime.now() - start_time).total_seconds()
            return SwarmResult(
                task_id=task_id,
                consensus_result=ConsensusResult(
                    consensus_value=None,
                    confidence=0.0,
                    agreement_score=0.0,
                    participating_agents=list(self.agents.keys()),
                    algorithm_used=consensus_algorithm.value,
                    metadata={"error": str(e), "error_type": type(e).__name__},
                    timestamp=datetime.now()
                ),
                individual_results={},
                execution_time=execution_time,
                swarm_metadata={
                    "swarm_id": self.swarm_id,
                    "agent_count": len(self.agents),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _execute_agents_parallel(self, task: SwarmTask) -> Dict[str, AgentResult]:
        """
        Execute task on all agents with intelligent parallel execution using cross-region inference profiles.
        
        AWS Bedrock Claude 3.5 Sonnet V2 Limits:
        - 1 request per minute (on-demand) per region
        - Cross-region inference profiles distribute across multiple regions
        
        Strategy: Use cross-region inference profiles to leverage multiple regions for parallel execution.
        """
        from parallel_execution_strategy import IntelligentParallelExecutor
        
        # Use intelligent parallel executor with cross-region strategy
        executor = IntelligentParallelExecutor(strategy_name="cross_region_parallel")
        
        # Execute agents using the intelligent strategy
        raw_results = executor.execute_agents_parallel(self.agents, task)
        
        # Convert raw results to AgentResult objects
        agent_results = {}
        for agent_id, result in raw_results.items():
            if isinstance(result, AgentResult):
                agent_results[agent_id] = result
            else:
                # Convert dict result to AgentResult
                agent_results[agent_id] = AgentResult(
                    agent_id=agent_id,
                    specialization=result.get("specialization", "unknown"),
                    region=result.get("region", "unknown"),
                    result=result.get("result", {}),
                    confidence=result.get("confidence", 0.0),
                    timestamp=result.get("timestamp", datetime.now()),
                    performance_metrics=result.get("performance_metrics", {})
                )
        
        logger.info(f"📊 Collected results from {len(agent_results)} agents")
        return agent_results
    
    def _execute_agent_task(self, agent: SwarmAgent, task: SwarmTask) -> AgentResult:
        """
        Execute task on individual agent using real AWS Bedrock calls.
        
        NO MOCK RESPONSES: Always uses real inference profile execution.
        """
        start_time = datetime.now()
        
        try:
            # Create specialized prompt for this agent
            prompt = self._create_agent_prompt(agent, task)
            
            # Execute inference using real AWS Bedrock
            inference_result = agent.inference_profile.execute_inference(prompt, task.context)
            
            # Extract confidence from result
            confidence = inference_result.get("confidence", 0.5)
            if "agent_metadata" in inference_result:
                confidence = inference_result["agent_metadata"].get("confidence", confidence)
            
            # Calculate performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            performance_metrics = {
                "execution_time": execution_time,
                "region": agent.region,
                "specialization": agent.specialization,
                "agent_role": agent.agent_role.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # Create agent result
            agent_result = AgentResult(
                agent_id=agent.agent_id,
                specialization=agent.specialization,
                region=agent.region,
                result=inference_result,
                confidence=confidence,
                timestamp=datetime.now(),
                performance_metrics=performance_metrics
            )
            
            # Update agent task history
            agent.task_history.append({
                "task_id": task.task_id,
                "execution_time": execution_time,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ Agent {agent.agent_id} completed task in {execution_time:.2f}s")
            return agent_result
            
        except Exception as e:
            logger.error(f"❌ Agent {agent.agent_id} task execution failed: {str(e)}")
            # NO MOCK RESPONSES - Return error result
            execution_time = (datetime.now() - start_time).total_seconds()
            return AgentResult(
                agent_id=agent.agent_id,
                specialization=agent.specialization,
                region=agent.region,
                result={"error": str(e), "error_type": type(e).__name__},
                confidence=0.0,
                timestamp=datetime.now(),
                performance_metrics={"error": str(e), "execution_time": execution_time}
            )
    
    def _create_agent_prompt(self, agent: SwarmAgent, task: SwarmTask) -> str:
        """Create specialized prompt for agent based on role and task."""
        # This method should be overridden by specific swarm implementations
        # to provide domain-specific prompting
        return f"Task: {task.task_type}\nPayload: {json.dumps(task.payload, indent=2)}"
    
    def _update_performance_metrics(self, agent_results: Dict[str, AgentResult], consensus_result: ConsensusResult):
        """Update performance metrics for all agents."""
        try:
            for agent_id, agent_result in agent_results.items():
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    
                    # Update performance metrics
                    if "performance_metrics" not in agent.performance_metrics:
                        agent.performance_metrics = {}
                    
                    agent.performance_metrics.update({
                        "last_confidence": agent_result.confidence,
                        "last_execution_time": agent_result.performance_metrics.get("execution_time", 0),
                        "total_tasks": len(agent.task_history),
                        "average_confidence": self._calculate_average_confidence(agent),
                        "last_updated": datetime.now().isoformat()
                    })
            
            logger.info(f"📊 Updated performance metrics for {len(agent_results)} agents")
            
        except Exception as e:
            logger.error(f"❌ Failed to update performance metrics: {str(e)}")
    
    def _calculate_average_confidence(self, agent: SwarmAgent) -> float:
        """Calculate average confidence for agent based on task history."""
        if not agent.task_history:
            return 0.5
        
        confidences = [task.get("confidence", 0.5) for task in agent.task_history]
        return sum(confidences) / len(confidences)
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status and performance metrics."""
        try:
            active_agents = sum(1 for agent in self.agents.values() if agent.status == "active")
            total_tasks = sum(len(agent.task_history) for agent in self.agents.values())
            
            # Calculate average performance metrics
            avg_confidence = 0.0
            avg_execution_time = 0.0
            
            if self.agents:
                confidences = [agent.performance_metrics.get("average_confidence", 0.5) 
                             for agent in self.agents.values()]
                execution_times = [agent.performance_metrics.get("last_execution_time", 0) 
                                 for agent in self.agents.values()]
                
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
                avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
            
            return {
                "swarm_id": self.swarm_id,
                "agent_count": len(self.agents),
                "active_agents": active_agents,
                "total_tasks": total_tasks,
                "average_confidence": avg_confidence,
                "average_execution_time": avg_execution_time,
                "regions": list(set(agent.region for agent in self.agents.values())),
                "specializations": list(set(agent.specialization for agent in self.agents.values())),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get swarm status: {str(e)}")
            return {
                "swarm_id": self.swarm_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def shutdown(self):
        """Shutdown swarm and cleanup resources."""
        try:
            self.executor.shutdown(wait=True)
            logger.info(f"🛑 Swarm {self.swarm_id} shutdown completed")
        except Exception as e:
            logger.error(f"❌ Failed to shutdown swarm {self.swarm_id}: {str(e)}")
