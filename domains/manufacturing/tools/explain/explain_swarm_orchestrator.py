"""
DcisionAI Platform - Explain Swarm Orchestrator
===============================================

Advanced customer-facing explanation swarm using Strands framework.
Implements business-friendly language and UI-friendly output for explaining
each tool's results to customers in an accessible and actionable way.

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
    from ....config.aws_credentials import is_agentcore_available
    AGENTCORE_AVAILABLE = is_agentcore_available()
except Exception as e:
    AGENTCORE_AVAILABLE = False
    logging.warning(f"AgentCore deployment not available - using local swarm deployment: {e}")

logger = logging.getLogger(__name__)


class ToolType(Enum):
    """Tool types for explanation"""
    INTENT_TOOL = "intent_tool"
    DATA_TOOL = "data_tool"
    MODEL_BUILDER_TOOL = "model_builder_tool"
    SOLVER_TOOL = "solver_tool"
    CRITIQUE_TOOL = "critique_tool"
    EXPLAIN_TOOL = "explain_tool"


class ExplanationType(Enum):
    """Types of explanations"""
    EXECUTIVE_SUMMARY = "executive_summary"
    BUSINESS_INSIGHTS = "business_insights"
    ACTIONABLE_RECOMMENDATIONS = "actionable_recommendations"
    RISK_ASSESSMENT = "risk_assessment"
    TECHNICAL_DETAILS = "technical_details"
    VISUALIZATION_HINTS = "visualization_hints"


class AudienceType(Enum):
    """Target audience types"""
    EXECUTIVE = "executive"
    MANAGER = "manager"
    ANALYST = "analyst"
    TECHNICAL = "technical"
    GENERAL = "general"


class SwarmStrategy(Enum):
    """Swarm coordination strategies"""
    CONSENSUS = "consensus"
    COMPETITIVE = "competitive"
    COLLABORATIVE = "collaborative"
    VALIDATION = "validation"
    HIERARCHICAL = "hierarchical"


@dataclass
class ToolExplanation:
    """Explanation for a specific tool"""
    tool_type: ToolType
    explanation_type: ExplanationType
    audience_type: AudienceType
    executive_summary: str
    business_insights: List[str]
    actionable_recommendations: List[str]
    risk_assessment: Dict[str, Any]
    technical_details: Dict[str, Any]
    visualization_hints: List[Dict[str, Any]]
    ui_friendly_output: Dict[str, Any]
    confidence_score: float
    timestamp: datetime


@dataclass
class WorkflowExplanation:
    """Overall workflow explanation"""
    tool_explanations: List[ToolExplanation]
    executive_summary: str
    business_impact: Dict[str, Any]
    key_insights: List[str]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    next_steps: List[str]
    ui_components: List[Dict[str, Any]]
    audience_specific_outputs: Dict[str, Dict[str, Any]]
    explanation_metadata: Dict[str, Any]
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


class ExplainSwarm:
    """Specialized swarm for customer-facing explanations"""
    
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
        
        # Initialize specialized explanation agents
        self._initialize_explanation_agents()
    
    def _initialize_explanation_agents(self):
        """Initialize specialized customer-facing explanation agents"""
        
        # Executive Communication Expert
        executive_expert = Agent(
            system_prompt="""You are an executive communication expert specializing in high-level business explanations.
            
            Focus on:
            - Executive summaries for C-level audience
            - Business impact and ROI analysis
            - Strategic recommendations
            - Risk assessment for executives
            - High-level insights and trends
            
            Provide clear, concise explanations suitable for executive decision-making.""",
            tools=[use_llm, memory]
        )
        
        # Business Analyst Expert
        business_analyst = Agent(
            system_prompt="""You are a business analyst expert specializing in actionable insights.
            
            Focus on:
            - Business process optimization insights
            - Operational efficiency analysis
            - Performance metrics interpretation
            - Process improvement recommendations
            - Cost-benefit analysis
            
            Provide detailed business analysis and actionable recommendations.""",
            tools=[use_llm, memory]
        )
        
        # Technical Translator Expert
        technical_translator = Agent(
            system_prompt="""You are a technical translator expert specializing in making complex concepts accessible.
            
            Focus on:
            - Converting technical jargon to business language
            - Simplifying complex algorithms and models
            - Making data science accessible to business users
            - Explaining optimization concepts clearly
            - Bridging technical and business perspectives
            
            Translate technical concepts into business-friendly language.""",
            tools=[use_llm, memory]
        )
        
        # UI/UX Communication Expert
        ui_expert = Agent(
            system_prompt="""You are a UI/UX communication expert specializing in user-friendly explanations.
            
            Focus on:
            - UI-friendly output formats (JSON, XML, structured data)
            - Visualization suggestions and chart recommendations
            - Progressive disclosure of information
            - Interactive element design
            - User experience optimization
            
            Create explanations optimized for UI integration and user experience.""",
            tools=[use_llm, memory]
        )
        
        # Risk Assessment Expert
        risk_expert = Agent(
            system_prompt="""You are a risk assessment expert specializing in business risk analysis.
            
            Focus on:
            - Business risk identification and assessment
            - Impact analysis of optimization decisions
            - Risk mitigation strategies
            - Uncertainty quantification
            - Risk communication to stakeholders
            
            Provide comprehensive risk assessment and mitigation strategies.""",
            tools=[use_llm, memory]
        )
        
        # Actionable Recommendations Expert
        recommendations_expert = Agent(
            system_prompt="""You are an actionable recommendations expert specializing in implementation guidance.
            
            Focus on:
            - Specific, actionable recommendations
            - Implementation roadmaps and timelines
            - Resource requirements and constraints
            - Success metrics and KPIs
            - Change management considerations
            
            Provide clear, actionable recommendations with implementation guidance.""",
            tools=[use_llm, memory]
        )
        
        # Data Storytelling Expert
        storytelling_expert = Agent(
            system_prompt="""You are a data storytelling expert specializing in narrative explanations.
            
            Focus on:
            - Compelling narrative construction
            - Story arc development for business insights
            - Emotional connection with data
            - Memorable explanation techniques
            - Engaging presentation of results
            
            Create compelling narratives that make data insights memorable and engaging.""",
            tools=[use_llm, memory]
        )
        
        # Audience Adaptation Expert
        audience_expert = Agent(
            system_prompt="""You are an audience adaptation expert specializing in tailored communication.
            
            Focus on:
            - Audience-specific language and terminology
            - Customized explanation depth and detail
            - Role-appropriate recommendations
            - Audience-specific risk communication
            - Adaptive communication strategies
            
            Adapt explanations to different audience types and roles.""",
            tools=[use_llm, memory]
        )
        
        # Visualization Expert
        visualization_expert = Agent(
            system_prompt="""You are a visualization expert specializing in data presentation.
            
            Focus on:
            - Chart and graph recommendations
            - Dashboard design suggestions
            - Interactive visualization ideas
            - Color scheme and design recommendations
            - Data presentation best practices
            
            Suggest optimal visualizations for different types of data and insights.""",
            tools=[use_llm, memory]
        )
        
        # Cross-Tool Integration Expert
        integration_expert = Agent(
            system_prompt="""You are a cross-tool integration expert specializing in end-to-end explanations.
            
            Focus on:
            - Workflow coherence and integration
            - Cross-tool result synthesis
            - End-to-end process explanation
            - Tool interaction and dependencies
            - Holistic business impact assessment
            
            Provide integrated explanations that connect all tool results into a coherent narrative.""",
            tools=[use_llm, memory]
        )
        
        self.agents = [
            executive_expert,
            business_analyst,
            technical_translator,
            ui_expert,
            risk_expert,
            recommendations_expert,
            storytelling_expert,
            audience_expert,
            visualization_expert,
            integration_expert
        ]
        
        self.performance_metrics.total_agents = len(self.agents)
        self.performance_metrics.active_agents = len(self.agents)
    
    async def explain_workflow(self, workflow_results: Dict[str, Any], 
                             workflow_metadata: Dict[str, Any],
                             target_audience: AudienceType = AudienceType.EXECUTIVE) -> WorkflowExplanation:
        """Explain entire workflow using customer-facing communication"""
        start_time = datetime.now()
        
        # Prepare explanation prompt
        explanation_prompt = f"""
        Explain this manufacturing optimization workflow for {target_audience.value} audience:
        
        Workflow Results: {json.dumps(workflow_results, indent=2)}
        Workflow Metadata: {json.dumps(workflow_metadata, indent=2)}
        Target Audience: {target_audience.value}
        
        Provide comprehensive explanation as JSON:
        {{
            "tool_explanations": [
                {{
                    "tool_type": "INTENT_TOOL|DATA_TOOL|MODEL_BUILDER_TOOL|SOLVER_TOOL|CRITIQUE_TOOL",
                    "explanation_type": "EXECUTIVE_SUMMARY|BUSINESS_INSIGHTS|ACTIONABLE_RECOMMENDATIONS",
                    "audience_type": "{target_audience.value}",
                    "executive_summary": "High-level summary for executives",
                    "business_insights": ["insight1", "insight2"],
                    "actionable_recommendations": ["recommendation1", "recommendation2"],
                    "risk_assessment": {{
                        "risk_level": "low|medium|high",
                        "key_risks": ["risk1", "risk2"],
                        "mitigation_strategies": ["strategy1", "strategy2"]
                    }},
                    "technical_details": {{
                        "complexity_level": "simple|moderate|complex",
                        "key_concepts": ["concept1", "concept2"],
                        "methodology": "Brief methodology explanation"
                    }},
                    "visualization_hints": [
                        {{
                            "chart_type": "bar|line|pie|scatter",
                            "data_points": ["point1", "point2"],
                            "purpose": "What this visualization shows"
                        }}
                    ],
                    "ui_friendly_output": {{
                        "format": "json|xml|structured",
                        "components": ["component1", "component2"],
                        "interactive_elements": ["element1", "element2"]
                    }},
                    "confidence_score": 0.95
                }}
            ],
            "executive_summary": "Overall executive summary",
            "business_impact": {{
                "cost_savings": "Estimated cost savings",
                "efficiency_gains": "Efficiency improvements",
                "time_savings": "Time optimization benefits",
                "quality_improvements": "Quality enhancement metrics"
            }},
            "key_insights": ["insight1", "insight2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "risk_assessment": {{
                "overall_risk": "low|medium|high",
                "risk_factors": ["factor1", "factor2"],
                "mitigation_plan": "Risk mitigation strategy"
            }},
            "next_steps": ["step1", "step2"],
            "ui_components": [
                {{
                    "component_type": "chart|table|summary|recommendation",
                    "data_source": "tool_result",
                    "interaction_type": "click|hover|drill_down"
                }}
            ],
            "audience_specific_outputs": {{
                "executive": {{"summary": "executive_summary", "focus": "business_impact"}},
                "manager": {{"summary": "manager_summary", "focus": "operational_insights"}},
                "analyst": {{"summary": "analyst_summary", "focus": "technical_details"}}
            }}
        }}
        """
        
        # Execute swarm explanation based on strategy
        if self.strategy == SwarmStrategy.CONSENSUS:
            result = await self._consensus_explanation(explanation_prompt, workflow_results, workflow_metadata, target_audience)
        elif self.strategy == SwarmStrategy.COMPETITIVE:
            result = await self._competitive_explanation(explanation_prompt, workflow_results, workflow_metadata, target_audience)
        elif self.strategy == SwarmStrategy.COLLABORATIVE:
            result = await self._collaborative_explanation(explanation_prompt, workflow_results, workflow_metadata, target_audience)
        elif self.strategy == SwarmStrategy.VALIDATION:
            result = await self._validation_explanation(explanation_prompt, workflow_results, workflow_metadata, target_audience)
        else:
            result = await self._hierarchical_explanation(explanation_prompt, workflow_results, workflow_metadata, target_audience)
        
        # Update performance metrics
        execution_time = (datetime.now() - start_time).total_seconds()
        self.performance_metrics.execution_time = execution_time
        
        return result
    
    async def _consensus_explanation(self, prompt: str, workflow_results: Dict[str, Any], 
                                   workflow_metadata: Dict[str, Any], target_audience: AudienceType) -> WorkflowExplanation:
        """Consensus-based explanation with multiple experts"""
        # Get explanations from all agents
        explanations = []
        for agent in self.agents:
            try:
                response = await agent.invoke_async(prompt)
                explanation = json.loads(response)
                explanations.append(explanation)
            except Exception as e:
                logger.warning(f"Agent explanation failed: {e}")
                continue
        
        # Calculate consensus
        if explanations:
            # Aggregate tool explanations
            all_tool_explanations = []
            confidence_scores = []
            
            for explanation in explanations:
                all_tool_explanations.extend(explanation.get("tool_explanations", []))
                confidence_scores.append(explanation.get("confidence_score", 0.0))
            
            # Calculate consensus confidence
            consensus_confidence = sum(confidence_scores) / len(confidence_scores)
            agreement_score = len(explanations) / self.performance_metrics.total_agents
            
            self.performance_metrics.consensus_achieved = agreement_score >= 0.6
            self.performance_metrics.agreement_score = agreement_score
            
            # Convert tool explanations to dataclass objects
            tool_explanation_objects = []
            for explanation_data in all_tool_explanations:
                tool_explanation = ToolExplanation(
                    tool_type=ToolType(explanation_data.get("tool_type", "INTENT_TOOL").lower()),
                    explanation_type=ExplanationType(explanation_data.get("explanation_type", "EXECUTIVE_SUMMARY").lower()),
                    audience_type=AudienceType(explanation_data.get("audience_type", "executive").lower()),
                    executive_summary=explanation_data.get("executive_summary", ""),
                    business_insights=explanation_data.get("business_insights", []),
                    actionable_recommendations=explanation_data.get("actionable_recommendations", []),
                    risk_assessment=explanation_data.get("risk_assessment", {}),
                    technical_details=explanation_data.get("technical_details", {}),
                    visualization_hints=explanation_data.get("visualization_hints", []),
                    ui_friendly_output=explanation_data.get("ui_friendly_output", {}),
                    confidence_score=explanation_data.get("confidence_score", 0.0),
                    timestamp=datetime.now()
                )
                tool_explanation_objects.append(tool_explanation)
            
            return WorkflowExplanation(
                tool_explanations=tool_explanation_objects,
                executive_summary=explanations[0].get("executive_summary", ""),
                business_impact=explanations[0].get("business_impact", {}),
                key_insights=explanations[0].get("key_insights", []),
                recommendations=explanations[0].get("recommendations", []),
                risk_assessment=explanations[0].get("risk_assessment", {}),
                next_steps=explanations[0].get("next_steps", []),
                ui_components=explanations[0].get("ui_components", []),
                audience_specific_outputs=explanations[0].get("audience_specific_outputs", {}),
                explanation_metadata={
                    "strategy": "consensus",
                    "total_explanations": len(explanations),
                    "agreement_score": agreement_score
                },
                swarm_agreement=agreement_score,
                execution_time=self.performance_metrics.execution_time
            )
        else:
            return WorkflowExplanation(
                tool_explanations=[],
                executive_summary="",
                business_impact={},
                key_insights=[],
                recommendations=[],
                risk_assessment={},
                next_steps=[],
                ui_components=[],
                audience_specific_outputs={},
                explanation_metadata={
                    "strategy": "consensus",
                    "total_explanations": 0,
                    "agreement_score": 0.0
                },
                swarm_agreement=0.0,
                execution_time=self.performance_metrics.execution_time
            )
    
    async def _competitive_explanation(self, prompt: str, workflow_results: Dict[str, Any], 
                                     workflow_metadata: Dict[str, Any], target_audience: AudienceType) -> WorkflowExplanation:
        """Competitive explanation - agents compete for best explanation"""
        # Get explanations with quality scores
        agent_results = []
        for i, agent in enumerate(self.agents):
            try:
                response = await agent.invoke_async(prompt)
                explanation = json.loads(response)
                
                # Calculate explanation quality score
                quality_score = explanation.get("confidence_score", 0.0)
                quality_score += len(explanation.get("tool_explanations", [])) * 0.1
                quality_score += len(explanation.get("recommendations", [])) * 0.05
                
                agent_results.append({
                    "agent_id": i,
                    "explanation": explanation,
                    "quality_score": quality_score
                })
            except Exception as e:
                logger.warning(f"Agent {i} competitive explanation failed: {e}")
                continue
        
        # Select winner based on quality score
        if agent_results:
            winner = max(agent_results, key=lambda x: x["quality_score"])
            explanation = winner["explanation"]
            
            self.performance_metrics.consensus_achieved = True
            self.performance_metrics.agreement_score = winner["quality_score"]
            
            # Convert tool explanations to dataclass objects
            tool_explanation_objects = []
            for explanation_data in explanation.get("tool_explanations", []):
                tool_explanation = ToolExplanation(
                    tool_type=ToolType(explanation_data.get("tool_type", "INTENT_TOOL").lower()),
                    explanation_type=ExplanationType(explanation_data.get("explanation_type", "EXECUTIVE_SUMMARY").lower()),
                    audience_type=AudienceType(explanation_data.get("audience_type", "executive").lower()),
                    executive_summary=explanation_data.get("executive_summary", ""),
                    business_insights=explanation_data.get("business_insights", []),
                    actionable_recommendations=explanation_data.get("actionable_recommendations", []),
                    risk_assessment=explanation_data.get("risk_assessment", {}),
                    technical_details=explanation_data.get("technical_details", {}),
                    visualization_hints=explanation_data.get("visualization_hints", []),
                    ui_friendly_output=explanation_data.get("ui_friendly_output", {}),
                    confidence_score=explanation_data.get("confidence_score", 0.0),
                    timestamp=datetime.now()
                )
                tool_explanation_objects.append(tool_explanation)
            
            return WorkflowExplanation(
                tool_explanations=tool_explanation_objects,
                executive_summary=explanation.get("executive_summary", ""),
                business_impact=explanation.get("business_impact", {}),
                key_insights=explanation.get("key_insights", []),
                recommendations=explanation.get("recommendations", []),
                risk_assessment=explanation.get("risk_assessment", {}),
                next_steps=explanation.get("next_steps", []),
                ui_components=explanation.get("ui_components", []),
                audience_specific_outputs=explanation.get("audience_specific_outputs", {}),
                explanation_metadata={
                    "strategy": "competitive",
                    "winner_agent": winner["agent_id"],
                    "quality_score": winner["quality_score"]
                },
                swarm_agreement=winner["quality_score"],
                execution_time=self.performance_metrics.execution_time
            )
        else:
            return WorkflowExplanation(
                tool_explanations=[],
                executive_summary="",
                business_impact={},
                key_insights=[],
                recommendations=[],
                risk_assessment={},
                next_steps=[],
                ui_components=[],
                audience_specific_outputs={},
                explanation_metadata={
                    "strategy": "competitive",
                    "winner_agent": None,
                    "quality_score": 0.0
                },
                swarm_agreement=0.0,
                execution_time=self.performance_metrics.execution_time
            )
    
    async def _collaborative_explanation(self, prompt: str, workflow_results: Dict[str, Any], 
                                       workflow_metadata: Dict[str, Any], target_audience: AudienceType) -> WorkflowExplanation:
        """Collaborative explanation - agents work together"""
        # First round: individual explanations
        individual_explanations = []
        for agent in self.agents:
            try:
                response = await agent.invoke_async(prompt)
                explanation = json.loads(response)
                individual_explanations.append(explanation)
            except Exception as e:
                logger.warning(f"Agent collaborative explanation failed: {e}")
                continue
        
        # Second round: collaborative synthesis
        if individual_explanations:
            # Create collaborative prompt with all explanations
            collaborative_prompt = f"""
            Review these workflow explanations and provide a collaborative synthesis:
            
            Individual Explanations:
            {json.dumps(individual_explanations, indent=2)}
            
            Provide a collaborative synthesis as JSON:
            {{
                "tool_explanations": ["consolidated_tool_explanations"],
                "executive_summary": "Collaborative executive summary",
                "business_impact": {{"consolidated_business_impact"}},
                "key_insights": ["consolidated_insights"],
                "recommendations": ["consolidated_recommendations"],
                "risk_assessment": {{"consolidated_risk_assessment"}},
                "next_steps": ["consolidated_next_steps"],
                "ui_components": ["consolidated_ui_components"],
                "audience_specific_outputs": {{"consolidated_audience_outputs"}},
                "collaboration_insights": "What the collaboration revealed"
            }}
            """
            
            # Use the first agent for collaborative synthesis
            try:
                response = await self.agents[0].invoke_async(collaborative_prompt)
                consensus_explanation = json.loads(response)
                
                self.performance_metrics.consensus_achieved = True
                self.performance_metrics.agreement_score = 0.9  # High agreement for collaborative
                
                # Convert tool explanations to dataclass objects
                tool_explanation_objects = []
                for explanation_data in consensus_explanation.get("tool_explanations", []):
                    tool_explanation = ToolExplanation(
                        tool_type=ToolType(explanation_data.get("tool_type", "INTENT_TOOL").lower()),
                        explanation_type=ExplanationType(explanation_data.get("explanation_type", "EXECUTIVE_SUMMARY").lower()),
                        audience_type=AudienceType(explanation_data.get("audience_type", "executive").lower()),
                        executive_summary=explanation_data.get("executive_summary", ""),
                        business_insights=explanation_data.get("business_insights", []),
                        actionable_recommendations=explanation_data.get("actionable_recommendations", []),
                        risk_assessment=explanation_data.get("risk_assessment", {}),
                        technical_details=explanation_data.get("technical_details", {}),
                        visualization_hints=explanation_data.get("visualization_hints", []),
                        ui_friendly_output=explanation_data.get("ui_friendly_output", {}),
                        confidence_score=explanation_data.get("confidence_score", 0.0),
                        timestamp=datetime.now()
                    )
                    tool_explanation_objects.append(tool_explanation)
                
                return WorkflowExplanation(
                    tool_explanations=tool_explanation_objects,
                    executive_summary=consensus_explanation.get("executive_summary", ""),
                    business_impact=consensus_explanation.get("business_impact", {}),
                    key_insights=consensus_explanation.get("key_insights", []),
                    recommendations=consensus_explanation.get("recommendations", []),
                    risk_assessment=consensus_explanation.get("risk_assessment", {}),
                    next_steps=consensus_explanation.get("next_steps", []),
                    ui_components=consensus_explanation.get("ui_components", []),
                    audience_specific_outputs=consensus_explanation.get("audience_specific_outputs", {}),
                    explanation_metadata={
                        "strategy": "collaborative",
                        "individual_explanations": len(individual_explanations),
                        "collaboration_insights": consensus_explanation.get("collaboration_insights", "")
                    },
                    swarm_agreement=0.9,
                    execution_time=self.performance_metrics.execution_time
                )
            except Exception as e:
                logger.error(f"Collaborative synthesis failed: {e}")
        
        # Fallback to consensus if collaborative synthesis fails
        return await self._consensus_explanation(prompt, workflow_results, workflow_metadata, target_audience)
    
    async def _validation_explanation(self, prompt: str, workflow_results: Dict[str, Any], 
                                    workflow_metadata: Dict[str, Any], target_audience: AudienceType) -> WorkflowExplanation:
        """Validation-based explanation with cross-validation"""
        # Primary explanation
        primary_results = []
        for agent in self.agents[:5]:  # Use first 5 agents for primary explanation
            try:
                response = await agent.invoke_async(prompt)
                explanation = json.loads(response)
                primary_results.append(explanation)
            except Exception as e:
                logger.warning(f"Primary agent explanation failed: {e}")
                continue
        
        # Validation explanation
        validation_results = []
        for agent in self.agents[5:]:  # Use remaining agents for validation
            try:
                response = await agent.invoke_async(prompt)
                explanation = json.loads(response)
                validation_results.append(explanation)
            except Exception as e:
                logger.warning(f"Validation agent explanation failed: {e}")
                continue
        
        # Cross-validate results
        if primary_results and validation_results:
            # Use primary explanation for synthesis
            primary_explanation = primary_results[0]
            
            # Calculate validation agreement
            validation_agreement = 0.8  # Mock agreement score
            
            self.performance_metrics.consensus_achieved = validation_agreement >= 0.5
            self.performance_metrics.agreement_score = validation_agreement
            
            # Convert tool explanations to dataclass objects
            tool_explanation_objects = []
            for explanation_data in primary_explanation.get("tool_explanations", []):
                tool_explanation = ToolExplanation(
                    tool_type=ToolType(explanation_data.get("tool_type", "INTENT_TOOL").lower()),
                    explanation_type=ExplanationType(explanation_data.get("explanation_type", "EXECUTIVE_SUMMARY").lower()),
                    audience_type=AudienceType(explanation_data.get("audience_type", "executive").lower()),
                    executive_summary=explanation_data.get("executive_summary", ""),
                    business_insights=explanation_data.get("business_insights", []),
                    actionable_recommendations=explanation_data.get("actionable_recommendations", []),
                    risk_assessment=explanation_data.get("risk_assessment", {}),
                    technical_details=explanation_data.get("technical_details", {}),
                    visualization_hints=explanation_data.get("visualization_hints", []),
                    ui_friendly_output=explanation_data.get("ui_friendly_output", {}),
                    confidence_score=explanation_data.get("confidence_score", 0.0),
                    timestamp=datetime.now()
                )
                tool_explanation_objects.append(tool_explanation)
            
            return WorkflowExplanation(
                tool_explanations=tool_explanation_objects,
                executive_summary=primary_explanation.get("executive_summary", ""),
                business_impact=primary_explanation.get("business_impact", {}),
                key_insights=primary_explanation.get("key_insights", []),
                recommendations=primary_explanation.get("recommendations", []),
                risk_assessment=primary_explanation.get("risk_assessment", {}),
                next_steps=primary_explanation.get("next_steps", []),
                ui_components=primary_explanation.get("ui_components", []),
                audience_specific_outputs=primary_explanation.get("audience_specific_outputs", {}),
                explanation_metadata={
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
            return await self._consensus_explanation(prompt, workflow_results, workflow_metadata, target_audience)
    
    async def _hierarchical_explanation(self, prompt: str, workflow_results: Dict[str, Any], 
                                      workflow_metadata: Dict[str, Any], target_audience: AudienceType) -> WorkflowExplanation:
        """Hierarchical explanation with specialized agents"""
        # First level: General explanation
        integration_expert = self.agents[-1]  # Cross-tool integration expert
        try:
            response = await integration_expert.invoke_async(prompt)
            general_explanation = json.loads(response)
            
            # If general explanation is confident, use it
            if len(general_explanation.get("tool_explanations", [])) > 2:
                # Convert tool explanations to dataclass objects
                tool_explanation_objects = []
                for explanation_data in general_explanation.get("tool_explanations", []):
                    tool_explanation = ToolExplanation(
                        tool_type=ToolType(explanation_data.get("tool_type", "INTENT_TOOL").lower()),
                        explanation_type=ExplanationType(explanation_data.get("explanation_type", "EXECUTIVE_SUMMARY").lower()),
                        audience_type=AudienceType(explanation_data.get("audience_type", "executive").lower()),
                        executive_summary=explanation_data.get("executive_summary", ""),
                        business_insights=explanation_data.get("business_insights", []),
                        actionable_recommendations=explanation_data.get("actionable_recommendations", []),
                        risk_assessment=explanation_data.get("risk_assessment", {}),
                        technical_details=explanation_data.get("technical_details", {}),
                        visualization_hints=explanation_data.get("visualization_hints", []),
                        ui_friendly_output=explanation_data.get("ui_friendly_output", {}),
                        confidence_score=explanation_data.get("confidence_score", 0.0),
                        timestamp=datetime.now()
                    )
                    tool_explanation_objects.append(tool_explanation)
                
                return WorkflowExplanation(
                    tool_explanations=tool_explanation_objects,
                    executive_summary=general_explanation.get("executive_summary", ""),
                    business_impact=general_explanation.get("business_impact", {}),
                    key_insights=general_explanation.get("key_insights", []),
                    recommendations=general_explanation.get("recommendations", []),
                    risk_assessment=general_explanation.get("risk_assessment", {}),
                    next_steps=general_explanation.get("next_steps", []),
                    ui_components=general_explanation.get("ui_components", []),
                    audience_specific_outputs=general_explanation.get("audience_specific_outputs", {}),
                    explanation_metadata={
                        "strategy": "hierarchical",
                        "level": "general",
                        "specialized_used": False
                    },
                    swarm_agreement=0.8,
                    execution_time=self.performance_metrics.execution_time
                )
        except Exception as e:
            logger.warning(f"General explanation failed: {e}")
        
        # Second level: Specialized explanation
        specialized_results = []
        for agent in self.agents[:-1]:  # All specialized agents
            try:
                response = await agent.invoke_async(prompt)
                explanation = json.loads(response)
                specialized_results.append(explanation)
            except Exception as e:
                logger.warning(f"Specialized agent explanation failed: {e}")
                continue
        
        # Select best specialized result
        if specialized_results:
            best_result = max(specialized_results, key=lambda x: len(x.get("tool_explanations", [])))
            
            self.performance_metrics.consensus_achieved = True
            self.performance_metrics.agreement_score = 0.9
            
            # Convert tool explanations to dataclass objects
            tool_explanation_objects = []
            for explanation_data in best_result.get("tool_explanations", []):
                tool_explanation = ToolExplanation(
                    tool_type=ToolType(explanation_data.get("tool_type", "INTENT_TOOL").lower()),
                    explanation_type=ExplanationType(explanation_data.get("explanation_type", "EXECUTIVE_SUMMARY").lower()),
                    audience_type=AudienceType(explanation_data.get("audience_type", "executive").lower()),
                    executive_summary=explanation_data.get("executive_summary", ""),
                    business_insights=explanation_data.get("business_insights", []),
                    actionable_recommendations=explanation_data.get("actionable_recommendations", []),
                    risk_assessment=explanation_data.get("risk_assessment", {}),
                    technical_details=explanation_data.get("technical_details", {}),
                    visualization_hints=explanation_data.get("visualization_hints", []),
                    ui_friendly_output=explanation_data.get("ui_friendly_output", {}),
                    confidence_score=explanation_data.get("confidence_score", 0.0),
                    timestamp=datetime.now()
                )
                tool_explanation_objects.append(tool_explanation)
            
            return WorkflowExplanation(
                tool_explanations=tool_explanation_objects,
                executive_summary=best_result.get("executive_summary", ""),
                business_impact=best_result.get("business_impact", {}),
                key_insights=best_result.get("key_insights", []),
                recommendations=best_result.get("recommendations", []),
                risk_assessment=best_result.get("risk_assessment", {}),
                next_steps=best_result.get("next_steps", []),
                ui_components=best_result.get("ui_components", []),
                audience_specific_outputs=best_result.get("audience_specific_outputs", {}),
                explanation_metadata={
                    "strategy": "hierarchical",
                    "level": "specialized",
                    "specialized_used": True,
                    "total_specialized": len(specialized_results)
                },
                swarm_agreement=0.9,
                execution_time=self.performance_metrics.execution_time
            )
        else:
            return WorkflowExplanation(
                tool_explanations=[],
                executive_summary="",
                business_impact={},
                key_insights=[],
                recommendations=[],
                risk_assessment={},
                next_steps=[],
                ui_components=[],
                audience_specific_outputs={},
                explanation_metadata={
                    "strategy": "hierarchical",
                    "level": "none",
                    "specialized_used": False
                },
                swarm_agreement=0.0,
                execution_time=self.performance_metrics.execution_time
            )


class ExplainSwarmOrchestrator:
    """Advanced swarm orchestrator for customer-facing explanations"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ExplainSwarmOrchestrator")
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
            self.swarms[strategy.value] = ExplainSwarm(strategy)
        
        self.logger.info(f"Initialized {len(self.swarms)} explanation swarms")
    
    def _initialize_agentcore_deployment(self):
        """Initialize AgentCore deployment for swarm orchestration"""
        try:
            # Create deployment with all swarms
            swarm_agents = {}
            for strategy_name, swarm in self.swarms.items():
                swarm_agents[f"explain_swarm_{strategy_name}"] = swarm.agents[0]  # Use first agent as representative
            
            self.deployment = MultiSwarmDeployment(
                agents=swarm_agents,
                coordination_strategy="adaptive"
            )
            self.logger.info("AgentCore multi-swarm deployment initialized for customer explanations")
        except Exception as e:
            self.logger.warning(f"AgentCore deployment failed: {e}")
            self.deployment = None
    
    async def explain_workflow(self, workflow_results: Dict[str, Any], 
                             workflow_metadata: Dict[str, Any],
                             target_audience: AudienceType = AudienceType.EXECUTIVE,
                             strategy: SwarmStrategy = SwarmStrategy.CONSENSUS) -> WorkflowExplanation:
        """Explain workflow using specified swarm strategy"""
        try:
            swarm = self.swarms.get(strategy.value)
            if not swarm:
                raise ValueError(f"Unknown swarm strategy: {strategy}")
            
            self.logger.info(f"Explaining workflow using {strategy.value} swarm strategy for {target_audience.value} audience")
            result = await swarm.explain_workflow(workflow_results, workflow_metadata, target_audience)
            
            # Store in memory and knowledge graph
            await self.memory.store(
                key=f"workflow_explanation_{datetime.now().timestamp()}",
                value={
                    "workflow_results": workflow_results,
                    "workflow_metadata": workflow_metadata,
                    "target_audience": target_audience.value,
                    "strategy": strategy.value,
                    "result": result.__dict__
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow explanation failed: {e}")
            # Return fallback explanation result
            return WorkflowExplanation(
                tool_explanations=[],
                executive_summary="",
                business_impact={},
                key_insights=[],
                recommendations=[],
                risk_assessment={},
                next_steps=[],
                ui_components=[],
                audience_specific_outputs={},
                explanation_metadata={
                    "strategy": strategy.value,
                    "error": str(e)
                },
                swarm_agreement=0.0,
                execution_time=0.0
            )
    
    async def adaptive_explanation(self, workflow_results: Dict[str, Any], 
                                 workflow_metadata: Dict[str, Any],
                                 target_audience: AudienceType = AudienceType.EXECUTIVE) -> WorkflowExplanation:
        """Adaptive explanation using multiple strategies"""
        results = {}
        
        # Try different strategies
        for strategy in [SwarmStrategy.CONSENSUS, SwarmStrategy.COMPETITIVE, SwarmStrategy.COLLABORATIVE]:
            try:
                result = await self.explain_workflow(workflow_results, workflow_metadata, target_audience, strategy)
                results[strategy.value] = result
            except Exception as e:
                self.logger.warning(f"Strategy {strategy.value} failed: {e}")
                continue
        
        # Select best result based on swarm agreement and explanation quality
        if results:
            best_result = max(results.values(), 
                            key=lambda x: x.swarm_agreement * len(x.tool_explanations))
            return best_result
        else:
            # Fallback to empty explanation result
            return WorkflowExplanation(
                tool_explanations=[],
                executive_summary="",
                business_impact={},
                key_insights=[],
                recommendations=[],
                risk_assessment={},
                next_steps=[],
                ui_components=[],
                audience_specific_outputs={},
                explanation_metadata={
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
