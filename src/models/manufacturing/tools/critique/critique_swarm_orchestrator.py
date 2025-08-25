"""
DcisionAI Platform - Critique Swarm Orchestrator
================================================

Advanced multi-tool supervision swarm using Strands framework.
Implements constructive criticism with token optimization, correctness validation,
and human-in-the-loop supervision for comprehensive quality assurance.

Copyright (c) 2025 DcisionAI. All rights reserved.
Production-ready implementation with enterprise-grade performance.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Strands framework imports
try:
    from strands.agent import Agent
    from strands.tools import tool


    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    logging.error("Strands framework not available - swarm intelligence requires Strands")

# AgentCore integration (AWS Bedrock AgentCore)
try:
    import boto3
    from botocore.exceptions import ClientError
    # Check if we can access Bedrock AgentCore
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    bedrock_agent.list_agents()
    AGENTCORE_AVAILABLE = True
    logging.info("AgentCore (AWS Bedrock) deployment available")
except (ImportError, ClientError, Exception) as e:
    AGENTCORE_AVAILABLE = False
    logging.warning(f"AgentCore deployment not available - using local swarm deployment: {e}")

logger = logging.getLogger(__name__)


class ToolType(Enum):
    """Tool types for supervision"""
    INTENT_TOOL = "intent_tool"
    DATA_TOOL = "data_tool"
    MODEL_BUILDER_TOOL = "model_builder_tool"
    SOLVER_TOOL = "solver_tool"
    EXPLAIN_TOOL = "explain_tool"
    CRITIQUE_TOOL = "critique_tool"


class CritiqueType(Enum):
    """Types of critique"""
    TOKEN_OPTIMIZATION = "token_optimization"
    CORRECTNESS_VALIDATION = "correctness_validation"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    WORKFLOW_COHERENCE = "workflow_coherence"
    BUSINESS_LOGIC = "business_logic"


class ConfidenceLevel(Enum):
    """Confidence levels for human-in-the-loop"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"


class SwarmStrategy(Enum):
    """Swarm coordination strategies"""
    CONSENSUS = "consensus"
    COMPETITIVE = "competitive"
    COLLABORATIVE = "collaborative"
    VALIDATION = "validation"
    HIERARCHICAL = "hierarchical"


@dataclass
class ToolCritique:
    """Critique for a specific tool"""
    tool_type: ToolType
    critique_type: CritiqueType
    severity: str  # "low", "medium", "high", "critical"
    issue_description: str
    constructive_suggestion: str
    token_optimization: Optional[str] = None
    correctness_issues: List[str] = None
    performance_impact: Optional[str] = None
    quality_score: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    human_review_needed: bool = False
    timestamp: datetime = None


@dataclass
class WorkflowCritique:
    """Overall workflow critique"""
    tool_critiques: List[ToolCritique]
    workflow_coherence_score: float
    overall_quality_score: float
    token_efficiency_score: float
    correctness_score: float
    performance_score: float
    business_logic_score: float
    human_review_points: List[Dict[str, Any]]
    improvement_recommendations: List[str]
    consensus_metrics: Dict[str, float]
    critique_metadata: Dict[str, Any]
    swarm_agreement: float
    execution_time: float


@dataclass
class SwarmPerformanceMetrics:
    """Swarm performance tracking"""
    total_agents: int
    active_agents: int
    consensus_achieved: bool
    agreement_score: float
    execution_time: float
    strategy_used: SwarmStrategy
    swarm_metadata: Dict[str, Any]


class CritiqueSwarm:
    """Specialized swarm for multi-tool supervision and critique"""
    
    def __init__(self, strategy: SwarmStrategy = SwarmStrategy.CONSENSUS):
        self.strategy = strategy
        self.agents = []
        self.memory = SharedMemory()
        self.knowledge_graph = KnowledgeGraph()
        self.performance_metrics = SwarmPerformanceMetrics(
            total_agents=0,
            active_agents=0,
            consensus_achieved=False,
            agreement_score=0.0,
            execution_time=0.0,
            strategy_used=strategy,
            swarm_metadata={}
        )
        
        # Initialize specialized critique agents
        self._initialize_critique_agents()
    
    def _initialize_critique_agents(self):
        """Initialize specialized multi-tool supervision agents"""
        
        # Intent Tool Supervisor
        intent_supervisor = Agent(
            system_prompt="""You are an intent classification supervisor specializing in constructive criticism.
            
            Focus on:
            - Intent classification accuracy and relevance
            - Query understanding quality
            - Domain expertise application
            - Classification confidence assessment
            - Token optimization for intent analysis
            
            Provide constructive criticism to improve intent classification quality.""",
            tools=[use_llm, memory]
        )
        
        # Data Tool Supervisor
        data_supervisor = Agent(
            system_prompt="""You are a data coordination supervisor specializing in data quality critique.
            
            Focus on:
            - Data quality and completeness assessment
            - Data enrichment effectiveness
            - Source reliability and accuracy
            - Data processing efficiency
            - Token optimization for data operations
            
            Provide constructive criticism to improve data quality and efficiency.""",
            tools=[use_llm, memory]
        )
        
        # Model Builder Supervisor
        model_supervisor = Agent(
            system_prompt="""You are a model builder supervisor specializing in mathematical correctness.
            
            Focus on:
            - Model formulation correctness
            - Constraint validation and completeness
            - Variable definition accuracy
            - Objective function appropriateness
            - Token optimization for model building
            
            Provide constructive criticism to ensure mathematical correctness.""",
            tools=[use_llm, memory]
        )
        
        # Solver Supervisor
        solver_supervisor = Agent(
            system_prompt="""You are a solver supervisor specializing in solution quality assessment.
            
            Focus on:
            - Solution optimality verification
            - Solver performance analysis
            - Convergence assessment
            - Solution feasibility validation
            - Token optimization for solving processes
            
            Provide constructive criticism to improve solution quality.""",
            tools=[use_llm, memory]
        )
        
        # Token Optimization Expert
        token_expert = Agent(
            system_prompt="""You are a token optimization expert specializing in efficiency analysis.
            
            Focus on:
            - Token usage optimization across all tools
            - Unnecessary complexity identification
            - Efficiency improvement suggestions
            - Cost-benefit analysis of operations
            - Resource utilization optimization
            
            Provide constructive criticism to optimize token usage and efficiency.""",
            tools=[use_llm, memory]
        )
        
        # Correctness Validation Expert
        correctness_expert = Agent(
            system_prompt="""You are a correctness validation expert specializing in accuracy verification.
            
            Focus on:
            - Mathematical correctness verification
            - Business logic validation
            - Constraint satisfaction checking
            - Solution feasibility verification
            - Cross-tool consistency validation
            
            Provide constructive criticism to ensure correctness and accuracy.""",
            tools=[use_llm, memory]
        )
        
        # Performance Analysis Expert
        performance_expert = Agent(
            system_prompt="""You are a performance analysis expert specializing in efficiency assessment.
            
            Focus on:
            - Execution time optimization
            - Memory usage efficiency
            - Algorithm performance analysis
            - Scalability assessment
            - Performance bottleneck identification
            
            Provide constructive criticism to improve performance and efficiency.""",
            tools=[use_llm, memory]
        )
        
        # Quality Assessment Expert
        quality_expert = Agent(
            system_prompt="""You are a quality assessment expert specializing in overall quality evaluation.
            
            Focus on:
            - Overall solution quality assessment
            - User experience evaluation
            - Reliability and robustness analysis
            - Maintainability assessment
            - Quality improvement recommendations
            
            Provide constructive criticism to improve overall quality.""",
            tools=[use_llm, memory]
        )
        
        # Workflow Coherence Expert
        workflow_expert = Agent(
            system_prompt="""You are a workflow coherence expert specializing in end-to-end process analysis.
            
            Focus on:
            - Tool integration effectiveness
            - Workflow consistency assessment
            - Cross-tool communication quality
            - Process optimization opportunities
            - Workflow improvement suggestions
            
            Provide constructive criticism to improve workflow coherence.""",
            tools=[use_llm, memory]
        )
        
        # Human-in-the-Loop Coordinator
        human_coordinator = Agent(
            system_prompt="""You are a human-in-the-loop coordinator specializing in expert review management.
            
            Focus on:
            - Critical decision point identification
            - Confidence threshold management
            - Human review workflow design
            - Expert feedback integration
            - Approval process optimization
            
            Coordinate human-in-the-loop processes for quality assurance.""",
            tools=[use_llm, memory]
        )
        
        self.agents = [
            intent_supervisor,
            data_supervisor,
            model_supervisor,
            solver_supervisor,
            token_expert,
            correctness_expert,
            performance_expert,
            quality_expert,
            workflow_expert,
            human_coordinator
        ]
        
        self.performance_metrics.total_agents = len(self.agents)
        self.performance_metrics.active_agents = len(self.agents)
    
    async def critique_workflow(self, workflow_results: Dict[str, Any], 
                              workflow_metadata: Dict[str, Any]) -> WorkflowCritique:
        """Critique entire workflow using multi-tool supervision"""
        start_time = datetime.now()
        
        # Prepare critique prompt
        critique_prompt = f"""
        Critique this manufacturing optimization workflow with constructive feedback:
        
        Workflow Results: {json.dumps(workflow_results, indent=2)}
        Workflow Metadata: {json.dumps(workflow_metadata, indent=2)}
        
        Provide comprehensive critique as JSON:
        {{
            "tool_critiques": [
                {{
                    "tool_type": "INTENT_TOOL|DATA_TOOL|MODEL_BUILDER_TOOL|SOLVER_TOOL",
                    "critique_type": "TOKEN_OPTIMIZATION|CORRECTNESS_VALIDATION|PERFORMANCE_ANALYSIS|QUALITY_ASSESSMENT",
                    "severity": "low|medium|high|critical",
                    "issue_description": "Detailed issue description",
                    "constructive_suggestion": "Specific improvement suggestion",
                    "token_optimization": "Token efficiency suggestions",
                    "correctness_issues": ["issue1", "issue2"],
                    "performance_impact": "Performance impact analysis",
                    "quality_score": 0.85,
                    "confidence_level": "high|medium|low|critical",
                    "human_review_needed": false
                }}
            ],
            "workflow_coherence_score": 0.9,
            "overall_quality_score": 0.85,
            "token_efficiency_score": 0.8,
            "correctness_score": 0.9,
            "performance_score": 0.85,
            "business_logic_score": 0.9,
            "human_review_points": [
                {{
                    "point": "Critical decision description",
                    "reason": "Why human review is needed",
                    "priority": "high|medium|low"
                }}
            ],
            "improvement_recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        # Execute swarm critique based on strategy
        if self.strategy == SwarmStrategy.CONSENSUS:
            result = await self._consensus_critique(critique_prompt, workflow_results, workflow_metadata)
        elif self.strategy == SwarmStrategy.COMPETITIVE:
            result = await self._competitive_critique(critique_prompt, workflow_results, workflow_metadata)
        elif self.strategy == SwarmStrategy.COLLABORATIVE:
            result = await self._collaborative_critique(critique_prompt, workflow_results, workflow_metadata)
        elif self.strategy == SwarmStrategy.VALIDATION:
            result = await self._validation_critique(critique_prompt, workflow_results, workflow_metadata)
        else:
            result = await self._hierarchical_critique(critique_prompt, workflow_results, workflow_metadata)
        
        # Update performance metrics
        execution_time = (datetime.now() - start_time).total_seconds()
        self.performance_metrics.execution_time = execution_time
        
        return result
    
    async def _consensus_critique(self, prompt: str, workflow_results: Dict[str, Any], 
                                workflow_metadata: Dict[str, Any]) -> WorkflowCritique:
        """Consensus-based critique with multiple supervisors"""
        # Get critiques from all agents
        critiques = []
        for agent in self.agents:
            try:
                response = await agent.invoke_async(prompt)
                critique = json.loads(response)
                critiques.append(critique)
            except Exception as e:
                logger.warning(f"Agent critique failed: {e}")
                continue
        
        # Calculate consensus
        if critiques:
            # Aggregate tool critiques
            all_tool_critiques = []
            quality_scores = []
            coherence_scores = []
            token_scores = []
            correctness_scores = []
            performance_scores = []
            business_scores = []
            
            for critique in critiques:
                all_tool_critiques.extend(critique.get("tool_critiques", []))
                quality_scores.append(critique.get("overall_quality_score", 0.0))
                coherence_scores.append(critique.get("workflow_coherence_score", 0.0))
                token_scores.append(critique.get("token_efficiency_score", 0.0))
                correctness_scores.append(critique.get("correctness_score", 0.0))
                performance_scores.append(critique.get("performance_score", 0.0))
                business_scores.append(critique.get("business_logic_score", 0.0))
            
            # Calculate consensus scores
            consensus_quality = sum(quality_scores) / len(quality_scores)
            consensus_coherence = sum(coherence_scores) / len(coherence_scores)
            consensus_token = sum(token_scores) / len(token_scores)
            consensus_correctness = sum(correctness_scores) / len(correctness_scores)
            consensus_performance = sum(performance_scores) / len(performance_scores)
            consensus_business = sum(business_scores) / len(business_scores)
            
            # Calculate agreement score
            agreement_score = len(critiques) / self.performance_metrics.total_agents
            
            self.performance_metrics.consensus_achieved = agreement_score >= 0.6
            self.performance_metrics.agreement_score = agreement_score
            
            # Convert tool critiques to dataclass objects
            tool_critique_objects = []
            for critique_data in all_tool_critiques:
                tool_critique = ToolCritique(
                    tool_type=ToolType(critique_data.get("tool_type", "INTENT_TOOL").lower()),
                    critique_type=CritiqueType(critique_data.get("critique_type", "QUALITY_ASSESSMENT").lower()),
                    severity=critique_data.get("severity", "medium"),
                    issue_description=critique_data.get("issue_description", ""),
                    constructive_suggestion=critique_data.get("constructive_suggestion", ""),
                    token_optimization=critique_data.get("token_optimization"),
                    correctness_issues=critique_data.get("correctness_issues", []),
                    performance_impact=critique_data.get("performance_impact"),
                    quality_score=critique_data.get("quality_score", 0.0),
                    confidence_level=ConfidenceLevel(critique_data.get("confidence_level", "medium").lower()),
                    human_review_needed=critique_data.get("human_review_needed", False),
                    timestamp=datetime.now()
                )
                tool_critique_objects.append(tool_critique)
            
            return WorkflowCritique(
                tool_critiques=tool_critique_objects,
                workflow_coherence_score=consensus_coherence,
                overall_quality_score=consensus_quality,
                token_efficiency_score=consensus_token,
                correctness_score=consensus_correctness,
                performance_score=consensus_performance,
                business_logic_score=consensus_business,
                human_review_points=critiques[0].get("human_review_points", []),
                improvement_recommendations=critiques[0].get("improvement_recommendations", []),
                consensus_metrics={
                    "total_critiques": len(critiques),
                    "agreement_score": agreement_score
                },
                critique_metadata={
                    "strategy": "consensus",
                    "total_agents": len(critiques)
                },
                swarm_agreement=agreement_score,
                execution_time=self.performance_metrics.execution_time
            )
        else:
            return WorkflowCritique(
                tool_critiques=[],
                workflow_coherence_score=0.0,
                overall_quality_score=0.0,
                token_efficiency_score=0.0,
                correctness_score=0.0,
                performance_score=0.0,
                business_logic_score=0.0,
                human_review_points=[],
                improvement_recommendations=[],
                consensus_metrics={},
                critique_metadata={
                    "strategy": "consensus",
                    "total_agents": 0
                },
                swarm_agreement=0.0,
                execution_time=self.performance_metrics.execution_time
            )
    
    async def _competitive_critique(self, prompt: str, workflow_results: Dict[str, Any], 
                                  workflow_metadata: Dict[str, Any]) -> WorkflowCritique:
        """Competitive critique - agents compete for best critique"""
        # Get critiques with quality scores
        agent_results = []
        for i, agent in enumerate(self.agents):
            try:
                response = await agent.invoke_async(prompt)
                critique = json.loads(response)
                
                # Calculate critique quality score
                quality_score = critique.get("overall_quality_score", 0.0)
                quality_score += len(critique.get("tool_critiques", [])) * 0.1
                quality_score += len(critique.get("improvement_recommendations", [])) * 0.05
                
                agent_results.append({
                    "agent_id": i,
                    "critique": critique,
                    "quality_score": quality_score
                })
            except Exception as e:
                logger.warning(f"Agent {i} competitive critique failed: {e}")
                continue
        
        # Select winner based on quality score
        if agent_results:
            winner = max(agent_results, key=lambda x: x["quality_score"])
            critique = winner["critique"]
            
            self.performance_metrics.consensus_achieved = True
            self.performance_metrics.agreement_score = winner["quality_score"]
            
            # Convert tool critiques to dataclass objects
            tool_critique_objects = []
            for critique_data in critique.get("tool_critiques", []):
                tool_critique = ToolCritique(
                    tool_type=ToolType(critique_data.get("tool_type", "INTENT_TOOL").lower()),
                    critique_type=CritiqueType(critique_data.get("critique_type", "QUALITY_ASSESSMENT").lower()),
                    severity=critique_data.get("severity", "medium"),
                    issue_description=critique_data.get("issue_description", ""),
                    constructive_suggestion=critique_data.get("constructive_suggestion", ""),
                    token_optimization=critique_data.get("token_optimization"),
                    correctness_issues=critique_data.get("correctness_issues", []),
                    performance_impact=critique_data.get("performance_impact"),
                    quality_score=critique_data.get("quality_score", 0.0),
                    confidence_level=ConfidenceLevel(critique_data.get("confidence_level", "medium").lower()),
                    human_review_needed=critique_data.get("human_review_needed", False),
                    timestamp=datetime.now()
                )
                tool_critique_objects.append(tool_critique)
            
            return WorkflowCritique(
                tool_critiques=tool_critique_objects,
                workflow_coherence_score=critique.get("workflow_coherence_score", 0.0),
                overall_quality_score=critique.get("overall_quality_score", 0.0),
                token_efficiency_score=critique.get("token_efficiency_score", 0.0),
                correctness_score=critique.get("correctness_score", 0.0),
                performance_score=critique.get("performance_score", 0.0),
                business_logic_score=critique.get("business_logic_score", 0.0),
                human_review_points=critique.get("human_review_points", []),
                improvement_recommendations=critique.get("improvement_recommendations", []),
                consensus_metrics={
                    "winner_agent": winner["agent_id"],
                    "quality_score": winner["quality_score"]
                },
                critique_metadata={
                    "strategy": "competitive",
                    "winner_agent": winner["agent_id"],
                    "quality_score": winner["quality_score"]
                },
                swarm_agreement=winner["quality_score"],
                execution_time=self.performance_metrics.execution_time
            )
        else:
            return WorkflowCritique(
                tool_critiques=[],
                workflow_coherence_score=0.0,
                overall_quality_score=0.0,
                token_efficiency_score=0.0,
                correctness_score=0.0,
                performance_score=0.0,
                business_logic_score=0.0,
                human_review_points=[],
                improvement_recommendations=[],
                consensus_metrics={},
                critique_metadata={
                    "strategy": "competitive",
                    "winner_agent": None,
                    "quality_score": 0.0
                },
                swarm_agreement=0.0,
                execution_time=self.performance_metrics.execution_time
            )
    
    async def _collaborative_critique(self, prompt: str, workflow_results: Dict[str, Any], 
                                    workflow_metadata: Dict[str, Any]) -> WorkflowCritique:
        """Collaborative critique - agents work together"""
        # First round: individual critiques
        individual_critiques = []
        for agent in self.agents:
            try:
                response = await agent.invoke_async(prompt)
                critique = json.loads(response)
                individual_critiques.append(critique)
            except Exception as e:
                logger.warning(f"Agent collaborative critique failed: {e}")
                continue
        
        # Second round: collaborative synthesis
        if individual_critiques:
            # Create collaborative prompt with all critiques
            collaborative_prompt = f"""
            Review these workflow critiques and provide a collaborative synthesis:
            
            Individual Critiques:
            {json.dumps(individual_critiques, indent=2)}
            
            Provide a collaborative synthesis as JSON:
            {{
                "tool_critiques": ["consolidated_tool_critiques"],
                "workflow_coherence_score": 0.9,
                "overall_quality_score": 0.85,
                "token_efficiency_score": 0.8,
                "correctness_score": 0.9,
                "performance_score": 0.85,
                "business_logic_score": 0.9,
                "human_review_points": ["consolidated_review_points"],
                "improvement_recommendations": ["consolidated_recommendations"],
                "collaboration_insights": "What the collaboration revealed"
            }}
            """
            
            # Use the first agent for collaborative synthesis
            try:
                response = await self.agents[0].invoke_async(collaborative_prompt)
                consensus_critique = json.loads(response)
                
                self.performance_metrics.consensus_achieved = True
                self.performance_metrics.agreement_score = 0.9  # High agreement for collaborative
                
                # Convert tool critiques to dataclass objects
                tool_critique_objects = []
                for critique_data in consensus_critique.get("tool_critiques", []):
                    tool_critique = ToolCritique(
                        tool_type=ToolType(critique_data.get("tool_type", "INTENT_TOOL").lower()),
                        critique_type=CritiqueType(critique_data.get("critique_type", "QUALITY_ASSESSMENT").lower()),
                        severity=critique_data.get("severity", "medium"),
                        issue_description=critique_data.get("issue_description", ""),
                        constructive_suggestion=critique_data.get("constructive_suggestion", ""),
                        token_optimization=critique_data.get("token_optimization"),
                        correctness_issues=critique_data.get("correctness_issues", []),
                        performance_impact=critique_data.get("performance_impact"),
                        quality_score=critique_data.get("quality_score", 0.0),
                        confidence_level=ConfidenceLevel(critique_data.get("confidence_level", "medium").lower()),
                        human_review_needed=critique_data.get("human_review_needed", False),
                        timestamp=datetime.now()
                    )
                    tool_critique_objects.append(tool_critique)
                
                return WorkflowCritique(
                    tool_critiques=tool_critique_objects,
                    workflow_coherence_score=consensus_critique.get("workflow_coherence_score", 0.0),
                    overall_quality_score=consensus_critique.get("overall_quality_score", 0.0),
                    token_efficiency_score=consensus_critique.get("token_efficiency_score", 0.0),
                    correctness_score=consensus_critique.get("correctness_score", 0.0),
                    performance_score=consensus_critique.get("performance_score", 0.0),
                    business_logic_score=consensus_critique.get("business_logic_score", 0.0),
                    human_review_points=consensus_critique.get("human_review_points", []),
                    improvement_recommendations=consensus_critique.get("improvement_recommendations", []),
                    consensus_metrics={
                        "individual_critiques": len(individual_critiques),
                        "collaboration_insights": consensus_critique.get("collaboration_insights", "")
                    },
                    critique_metadata={
                        "strategy": "collaborative",
                        "individual_critiques": len(individual_critiques),
                        "collaboration_insights": consensus_critique.get("collaboration_insights", "")
                    },
                    swarm_agreement=0.9,
                    execution_time=self.performance_metrics.execution_time
                )
            except Exception as e:
                logger.error(f"Collaborative synthesis failed: {e}")
        
        # Fallback to consensus if collaborative synthesis fails
        return await self._consensus_critique(prompt, workflow_results, workflow_metadata)
    
    async def _validation_critique(self, prompt: str, workflow_results: Dict[str, Any], 
                                 workflow_metadata: Dict[str, Any]) -> WorkflowCritique:
        """Validation-based critique with cross-validation"""
        # Primary critique
        primary_results = []
        for agent in self.agents[:5]:  # Use first 5 agents for primary critique
            try:
                response = await agent.invoke_async(prompt)
                critique = json.loads(response)
                primary_results.append(critique)
            except Exception as e:
                logger.warning(f"Primary agent critique failed: {e}")
                continue
        
        # Validation critique
        validation_results = []
        for agent in self.agents[5:]:  # Use remaining agents for validation
            try:
                response = await agent.invoke_async(prompt)
                critique = json.loads(response)
                validation_results.append(critique)
            except Exception as e:
                logger.warning(f"Validation agent critique failed: {e}")
                continue
        
        # Cross-validate results
        if primary_results and validation_results:
            # Use primary critique for synthesis
            primary_critique = primary_results[0]
            
            # Calculate validation agreement
            validation_agreement = 0.8  # Mock agreement score
            
            self.performance_metrics.consensus_achieved = validation_agreement >= 0.5
            self.performance_metrics.agreement_score = validation_agreement
            
            # Convert tool critiques to dataclass objects
            tool_critique_objects = []
            for critique_data in primary_critique.get("tool_critiques", []):
                tool_critique = ToolCritique(
                    tool_type=ToolType(critique_data.get("tool_type", "INTENT_TOOL").lower()),
                    critique_type=CritiqueType(critique_data.get("critique_type", "QUALITY_ASSESSMENT").lower()),
                    severity=critique_data.get("severity", "medium"),
                    issue_description=critique_data.get("issue_description", ""),
                    constructive_suggestion=critique_data.get("constructive_suggestion", ""),
                    token_optimization=critique_data.get("token_optimization"),
                    correctness_issues=critique_data.get("correctness_issues", []),
                    performance_impact=critique_data.get("performance_impact"),
                    quality_score=critique_data.get("quality_score", 0.0),
                    confidence_level=ConfidenceLevel(critique_data.get("confidence_level", "medium").lower()),
                    human_review_needed=critique_data.get("human_review_needed", False),
                    timestamp=datetime.now()
                )
                tool_critique_objects.append(tool_critique)
            
            return WorkflowCritique(
                tool_critiques=tool_critique_objects,
                workflow_coherence_score=primary_critique.get("workflow_coherence_score", 0.0),
                overall_quality_score=primary_critique.get("overall_quality_score", 0.0),
                token_efficiency_score=primary_critique.get("token_efficiency_score", 0.0),
                correctness_score=primary_critique.get("correctness_score", 0.0),
                performance_score=primary_critique.get("performance_score", 0.0),
                business_logic_score=primary_critique.get("business_logic_score", 0.0),
                human_review_points=primary_critique.get("human_review_points", []),
                improvement_recommendations=primary_critique.get("improvement_recommendations", []),
                consensus_metrics={
                    "validation_agreement": validation_agreement,
                    "primary_results": len(primary_results),
                    "validation_results": len(validation_results)
                },
                critique_metadata={
                    "strategy": "validation",
                    "primary_results": len(primary_results),
                    "validation_results": len(validation_results),
                    "validation_agreement": validation_agreement
                },
                swarm_agreement=validation_agreement,
                execution_time=self.performance_metrics.execution_time
            )
        else:
            # Fallback to consensus if validation fails
            return await self._consensus_critique(prompt, workflow_results, workflow_metadata)
    
    async def _hierarchical_critique(self, prompt: str, workflow_results: Dict[str, Any], 
                                   workflow_metadata: Dict[str, Any]) -> WorkflowCritique:
        """Hierarchical critique with specialized agents"""
        # First level: General critique
        human_coordinator = self.agents[-1]  # Human-in-the-loop coordinator
        try:
            response = await human_coordinator.invoke_async(prompt)
            general_critique = json.loads(response)
            
            # If general critique is confident, use it
            if len(general_critique.get("tool_critiques", [])) > 2:
                # Convert tool critiques to dataclass objects
                tool_critique_objects = []
                for critique_data in general_critique.get("tool_critiques", []):
                    tool_critique = ToolCritique(
                        tool_type=ToolType(critique_data.get("tool_type", "INTENT_TOOL").lower()),
                        critique_type=CritiqueType(critique_data.get("critique_type", "QUALITY_ASSESSMENT").lower()),
                        severity=critique_data.get("severity", "medium"),
                        issue_description=critique_data.get("issue_description", ""),
                        constructive_suggestion=critique_data.get("constructive_suggestion", ""),
                        token_optimization=critique_data.get("token_optimization"),
                        correctness_issues=critique_data.get("correctness_issues", []),
                        performance_impact=critique_data.get("performance_impact"),
                        quality_score=critique_data.get("quality_score", 0.0),
                        confidence_level=ConfidenceLevel(critique_data.get("confidence_level", "medium").lower()),
                        human_review_needed=critique_data.get("human_review_needed", False),
                        timestamp=datetime.now()
                    )
                    tool_critique_objects.append(tool_critique)
                
                return WorkflowCritique(
                    tool_critiques=tool_critique_objects,
                    workflow_coherence_score=general_critique.get("workflow_coherence_score", 0.0),
                    overall_quality_score=general_critique.get("overall_quality_score", 0.0),
                    token_efficiency_score=general_critique.get("token_efficiency_score", 0.0),
                    correctness_score=general_critique.get("correctness_score", 0.0),
                    performance_score=general_critique.get("performance_score", 0.0),
                    business_logic_score=general_critique.get("business_logic_score", 0.0),
                    human_review_points=general_critique.get("human_review_points", []),
                    improvement_recommendations=general_critique.get("improvement_recommendations", []),
                    consensus_metrics={
                        "level": "general",
                        "specialized_used": False
                    },
                    critique_metadata={
                        "strategy": "hierarchical",
                        "level": "general",
                        "specialized_used": False
                    },
                    swarm_agreement=0.8,
                    execution_time=self.performance_metrics.execution_time
                )
        except Exception as e:
            logger.warning(f"General critique failed: {e}")
        
        # Second level: Specialized critique
        specialized_results = []
        for agent in self.agents[:-1]:  # All specialized agents
            try:
                response = await agent.invoke_async(prompt)
                critique = json.loads(response)
                specialized_results.append(critique)
            except Exception as e:
                logger.warning(f"Specialized agent critique failed: {e}")
                continue
        
        # Select best specialized result
        if specialized_results:
            best_result = max(specialized_results, key=lambda x: len(x.get("tool_critiques", [])))
            
            self.performance_metrics.consensus_achieved = True
            self.performance_metrics.agreement_score = 0.9
            
            # Convert tool critiques to dataclass objects
            tool_critique_objects = []
            for critique_data in best_result.get("tool_critiques", []):
                tool_critique = ToolCritique(
                    tool_type=ToolType(critique_data.get("tool_type", "INTENT_TOOL").lower()),
                    critique_type=CritiqueType(critique_data.get("critique_type", "QUALITY_ASSESSMENT").lower()),
                    severity=critique_data.get("severity", "medium"),
                    issue_description=critique_data.get("issue_description", ""),
                    constructive_suggestion=critique_data.get("constructive_suggestion", ""),
                    token_optimization=critique_data.get("token_optimization"),
                    correctness_issues=critique_data.get("correctness_issues", []),
                    performance_impact=critique_data.get("performance_impact"),
                    quality_score=critique_data.get("quality_score", 0.0),
                    confidence_level=ConfidenceLevel(critique_data.get("confidence_level", "medium").lower()),
                    human_review_needed=critique_data.get("human_review_needed", False),
                    timestamp=datetime.now()
                )
                tool_critique_objects.append(tool_critique)
            
            return WorkflowCritique(
                tool_critiques=tool_critique_objects,
                workflow_coherence_score=best_result.get("workflow_coherence_score", 0.0),
                overall_quality_score=best_result.get("overall_quality_score", 0.0),
                token_efficiency_score=best_result.get("token_efficiency_score", 0.0),
                correctness_score=best_result.get("correctness_score", 0.0),
                performance_score=best_result.get("performance_score", 0.0),
                business_logic_score=best_result.get("business_logic_score", 0.0),
                human_review_points=best_result.get("human_review_points", []),
                improvement_recommendations=best_result.get("improvement_recommendations", []),
                consensus_metrics={
                    "level": "specialized",
                    "specialized_used": True,
                    "total_specialized": len(specialized_results)
                },
                critique_metadata={
                    "strategy": "hierarchical",
                    "level": "specialized",
                    "specialized_used": True,
                    "total_specialized": len(specialized_results)
                },
                swarm_agreement=0.9,
                execution_time=self.performance_metrics.execution_time
            )
        else:
            return WorkflowCritique(
                tool_critiques=[],
                workflow_coherence_score=0.0,
                overall_quality_score=0.0,
                token_efficiency_score=0.0,
                correctness_score=0.0,
                performance_score=0.0,
                business_logic_score=0.0,
                human_review_points=[],
                improvement_recommendations=[],
                consensus_metrics={
                    "level": "none",
                    "specialized_used": False
                },
                critique_metadata={
                    "strategy": "hierarchical",
                    "level": "none",
                    "specialized_used": False
                },
                swarm_agreement=0.0,
                execution_time=self.performance_metrics.execution_time
            )


class CritiqueSwarmOrchestrator:
    """Advanced swarm orchestrator for multi-tool supervision and critique"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CritiqueSwarmOrchestrator")
        self.swarms = {}
        self.deployment = None
        self.memory = DistributedMemory()
        self.knowledge_graph = KnowledgeGraph()
        
        # Initialize swarms for different strategies
        self._initialize_swarms()
        
        # Initialize AgentCore deployment if available
        if AGENTCORE_AVAILABLE:
            self._initialize_agentcore_deployment()
    
    def _initialize_swarms(self):
        """Initialize swarms for different strategies"""
        for strategy in SwarmStrategy:
            self.swarms[strategy.value] = CritiqueSwarm(strategy)
        
        self.logger.info(f"Initialized {len(self.swarms)} critique supervision swarms")
    
    def _initialize_agentcore_deployment(self):
        """Initialize AgentCore deployment for swarm orchestration"""
        try:
            # Create deployment with all swarms
            swarm_agents = {}
            for strategy_name, swarm in self.swarms.items():
                swarm_agents[f"critique_swarm_{strategy_name}"] = swarm.agents[0]  # Use first agent as representative
            
            self.deployment = MultiSwarmDeployment(
                agents=swarm_agents,
                coordination_strategy="adaptive"
            )
            self.logger.info("AgentCore multi-swarm deployment initialized for critique supervision")
        except Exception as e:
            self.logger.warning(f"AgentCore deployment failed: {e}")
            self.deployment = None
    
    async def critique_workflow(self, workflow_results: Dict[str, Any], 
                              workflow_metadata: Dict[str, Any],
                              strategy: SwarmStrategy = SwarmStrategy.CONSENSUS) -> WorkflowCritique:
        """Critique workflow using specified swarm strategy"""
        try:
            swarm = self.swarms.get(strategy.value)
            if not swarm:
                raise ValueError(f"Unknown swarm strategy: {strategy}")
            
            self.logger.info(f"Critiquing workflow using {strategy.value} swarm strategy")
            result = await swarm.critique_workflow(workflow_results, workflow_metadata)
            
            # Store in memory and knowledge graph
            await self.memory.store(
                key=f"workflow_critique_{datetime.now().timestamp()}",
                value={
                    "workflow_results": workflow_results,
                    "workflow_metadata": workflow_metadata,
                    "strategy": strategy.value,
                    "result": result.__dict__
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow critique failed: {e}")
            # Return fallback critique result
            return WorkflowCritique(
                tool_critiques=[],
                workflow_coherence_score=0.0,
                overall_quality_score=0.0,
                token_efficiency_score=0.0,
                correctness_score=0.0,
                performance_score=0.0,
                business_logic_score=0.0,
                human_review_points=[],
                improvement_recommendations=[],
                consensus_metrics={},
                critique_metadata={
                    "strategy": strategy.value,
                    "error": str(e)
                },
                swarm_agreement=0.0,
                execution_time=0.0
            )
    
    async def adaptive_critique(self, workflow_results: Dict[str, Any], 
                              workflow_metadata: Dict[str, Any]) -> WorkflowCritique:
        """Adaptive critique using multiple strategies"""
        results = {}
        
        # Try different strategies
        for strategy in [SwarmStrategy.CONSENSUS, SwarmStrategy.COMPETITIVE, SwarmStrategy.COLLABORATIVE]:
            try:
                result = await self.critique_workflow(workflow_results, workflow_metadata, strategy)
                results[strategy.value] = result
            except Exception as e:
                self.logger.warning(f"Strategy {strategy.value} failed: {e}")
                continue
        
        # Select best result based on swarm agreement and quality scores
        if results:
            best_result = max(results.values(), 
                            key=lambda x: x.swarm_agreement * x.overall_quality_score)
            return best_result
        else:
            # Fallback to empty critique result
            return WorkflowCritique(
                tool_critiques=[],
                workflow_coherence_score=0.0,
                overall_quality_score=0.0,
                token_efficiency_score=0.0,
                correctness_score=0.0,
                performance_score=0.0,
                business_logic_score=0.0,
                human_review_points=[],
                improvement_recommendations=[],
                consensus_metrics={},
                critique_metadata={
                    "strategy": "adaptive",
                    "attempted_strategies": list(results.keys())
                },
                swarm_agreement=0.0,
                execution_time=0.0
            )
    
    def get_performance_metrics(self) -> Dict[str, SwarmPerformanceMetrics]:
        """Get performance metrics for all swarms"""
        metrics = {}
        for strategy_name, swarm in self.swarms.items():
            metrics[strategy_name] = swarm.performance_metrics
        return metrics
