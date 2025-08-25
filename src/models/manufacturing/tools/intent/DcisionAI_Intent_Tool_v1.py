#!/usr/bin/env python3
"""
DcisionAI Intent Tool v1 - AWS-Style Agent-as-Tool Pattern
=========================================================

TRUE swarm intelligence using manager-worker pattern with 6 specialized workers.
Enhanced consensus building, robust error handling, and comprehensive coverage.

Version: 1.0
Changes: Original implementation with sequential execution

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import re

# Strands framework imports
try:
    from strands import Agent, tool
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    logging.error("Strands framework not available - intent tool requires Strands")
    raise Exception("Strands framework is required but not available")

# Platform throttling imports
from src.shared.throttling import get_platform_throttle_manager

logger = logging.getLogger(__name__)


class IntentCategory(Enum):
    """Manufacturing intent categories"""
    PRODUCTION_SCHEDULING = "production_scheduling"
    CAPACITY_PLANNING = "capacity_planning"
    INVENTORY_OPTIMIZATION = "inventory_optimization"
    QUALITY_CONTROL = "quality_control"
    SUPPLY_CHAIN = "supply_chain"
    MAINTENANCE = "maintenance"
    COST_OPTIMIZATION = "cost_optimization"
    DEMAND_FORECASTING = "demand_forecasting"
    ENVIRONMENTAL_OPTIMIZATION = "environmental_optimization"
    GENERAL_QUERY = "general_query"


@dataclass
class IntentClassification:
    """Intent classification result"""
    primary_intent: IntentCategory
    confidence: float
    entities: List[str]
    objectives: List[str]
    reasoning: str
    swarm_agreement: float
    classification_metadata: Dict[str, Any]


@dataclass
class SwarmPerformanceMetrics:
    """Real swarm performance tracking"""
    total_agents: int
    active_agents: int
    consensus_achieved: bool
    agreement_score: float
    execution_time: float
    swarm_status: str
    handoffs_performed: int
    manager_delegations: int
    worker_responses: int
    swarm_metadata: Dict[str, Any]


# ==================== WORKER AGENT TOOLS ====================

@tool
def ops_research_classifier(query: str) -> str:
    """Mathematical optimization and operations research specialist."""
    try:
        agent = Agent(
            name="ops_research_specialist",
            system_prompt="""You are an Operations Research specialist for manufacturing intent classification.

EXPERTISE: Mathematical optimization, linear programming, constraint optimization, OR models
PRIMARY CLASSIFICATIONS: CAPACITY_PLANNING, COST_OPTIMIZATION
SECONDARY: PRODUCTION_SCHEDULING (when mathematical optimization is primary focus)

STRICT CLASSIFICATION RULES:
- CAPACITY_PLANNING: ONLY if the core question is "how much capacity do we need" or "how to allocate limited resources"
- COST_OPTIMIZATION: ONLY if the primary objective is minimizing costs or maximizing financial ROI
- PRODUCTION_SCHEDULING: ONLY if primary focus is mathematical scheduling optimization with clear constraints
- NOT_MY_DOMAIN: If the problem is primarily about quality, supply chain, environmental compliance, or general management

CONFIDENCE RULES:
- High confidence (0.85-0.95): Clear mathematical optimization with constraints and objective functions
- Medium confidence (0.6-0.8): Some optimization elements but other factors dominate
- Low confidence (0.3-0.6): Minimal optimization content
- Very low confidence (0.1-0.3): Clearly not an OR problem

RESPONSE FORMAT (JSON only):
{
    "classification": "CAPACITY_PLANNING|COST_OPTIMIZATION|PRODUCTION_SCHEDULING|NOT_MY_DOMAIN",
    "confidence": 0.XX,
    "mathematical_elements": ["constraints", "objective_function"],
    "primary_problem_type": "resource_allocation|cost_minimization|scheduling|quality|environmental|other",
    "reasoning": "Explain why this is/isn't primarily a mathematical optimization problem"
}

CRITICAL: Be conservative! Only claim high confidence if this is CLEARLY your domain."""
        )
        
        response = agent(f"Analyze this query from OR perspective: {query}")
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "classification": "NOT_MY_DOMAIN",
            "confidence": 0.0,
            "mathematical_elements": [],
            "primary_problem_type": "error",
            "reasoning": f"Analysis failed: {str(e)}",
            "error": True
        })


@tool
def production_systems_classifier(query: str) -> str:
    """Production systems and workflow specialist."""
    try:
        agent = Agent(
            name="production_systems_specialist",
            system_prompt="""You are a Production Systems specialist for manufacturing intent classification.

EXPERTISE: Production workflows, manufacturing processes, line operations, scheduling
PRIMARY CLASSIFICATIONS: PRODUCTION_SCHEDULING, QUALITY_CONTROL
SECONDARY: CAPACITY_PLANNING (when production process focus)

STRICT CLASSIFICATION RULES:
- PRODUCTION_SCHEDULING: ONLY if the core question is "when to produce" or "how to sequence production"
- QUALITY_CONTROL: ONLY if the primary focus is quality metrics, defect management, or process control
- CAPACITY_PLANNING: ONLY if focus is on production line capacity/utilization optimization
- NOT_MY_DOMAIN: If the problem is primarily about costs, supply chain, environmental compliance, or general management

CONFIDENCE RULES:
- High confidence (0.85-0.95): Clear production workflow or quality control focus
- Medium confidence (0.6-0.8): Some production elements but other factors dominate
- Low confidence (0.3-0.6): Minimal production content
- Very low confidence (0.1-0.3): Clearly not a production systems problem

RESPONSE FORMAT (JSON only):
{
    "classification": "PRODUCTION_SCHEDULING|QUALITY_CONTROL|CAPACITY_PLANNING|NOT_MY_DOMAIN",
    "confidence": 0.XX,
    "production_elements": ["workflow", "line_operations"],
    "primary_problem_type": "scheduling|quality_control|capacity|cost|environmental|other",
    "reasoning": "Explain why this is/isn't primarily a production systems problem"
}

CRITICAL: Be conservative! Only claim high confidence if this is CLEARLY your domain."""
        )
        
        response = agent(f"Analyze this query from production systems perspective: {query}")
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "classification": "NOT_MY_DOMAIN",
            "confidence": 0.0,
            "production_elements": [],
            "primary_problem_type": "error",
            "reasoning": f"Analysis failed: {str(e)}",
            "error": True
        })


@tool
def supply_chain_classifier(query: str) -> str:
    """Supply chain and logistics specialist."""
    try:
        agent = Agent(
            name="supply_chain_specialist",
            system_prompt="""You are a Supply Chain specialist for manufacturing intent classification.

EXPERTISE: Supply chain management, logistics, inventory, procurement, distribution
PRIMARY CLASSIFICATIONS: SUPPLY_CHAIN, INVENTORY_OPTIMIZATION
SECONDARY: DEMAND_FORECASTING

STRICT CLASSIFICATION RULES:
- SUPPLY_CHAIN: ONLY if the core question is about logistics, distribution, or supplier management
- INVENTORY_OPTIMIZATION: ONLY if the primary focus is stock management or inventory levels
- DEMAND_FORECASTING: ONLY if the primary focus is demand prediction or sales forecasting
- NOT_MY_DOMAIN: If the problem is primarily about production scheduling, quality, costs, or environmental compliance

CONFIDENCE RULES:
- High confidence (0.85-0.95): Clear supply chain or inventory focus
- Medium confidence (0.6-0.8): Some supply chain elements but other factors dominate
- Low confidence (0.3-0.6): Minimal supply chain content
- Very low confidence (0.1-0.3): Clearly not a supply chain problem

RESPONSE FORMAT (JSON only):
{
    "classification": "SUPPLY_CHAIN|INVENTORY_OPTIMIZATION|DEMAND_FORECASTING|NOT_MY_DOMAIN",
    "confidence": 0.XX,
    "supply_chain_elements": ["logistics", "inventory"],
    "primary_problem_type": "logistics|inventory|forecasting|production|quality|other",
    "reasoning": "Explain why this is/isn't primarily a supply chain problem"
}

CRITICAL: Be conservative! Only claim high confidence if this is CLEARLY your domain."""
        )
        
        response = agent(f"Analyze this query from supply chain perspective: {query}")
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "classification": "NOT_MY_DOMAIN",
            "confidence": 0.0,
            "supply_chain_elements": [],
            "primary_problem_type": "error",
            "reasoning": f"Analysis failed: {str(e)}",
            "error": True
        })


@tool
def quality_classifier(query: str) -> str:
    """Quality control and compliance specialist."""
    try:
        agent = Agent(
            name="quality_specialist",
            system_prompt="""You are a Quality Control specialist for manufacturing intent classification.

EXPERTISE: Quality systems, compliance frameworks, standards, maintenance, reliability
PRIMARY CLASSIFICATIONS: QUALITY_CONTROL, MAINTENANCE
SECONDARY: None (highly specialized)

STRICT CLASSIFICATION RULES:
- QUALITY_CONTROL: ONLY if the core question is about quality metrics, defect rates, or process control
- MAINTENANCE: ONLY if the primary focus is equipment maintenance, reliability, or downtime
- NOT_MY_DOMAIN: If the problem is primarily about production scheduling, costs, supply chain, or environmental compliance

CONFIDENCE RULES:
- High confidence (0.85-0.95): Clear quality control or maintenance focus
- Medium confidence (0.6-0.8): Some quality/maintenance elements but other factors dominate
- Low confidence (0.3-0.6): Minimal quality/maintenance content
- Very low confidence (0.1-0.3): Clearly not a quality/maintenance problem

RESPONSE FORMAT (JSON only):
{
    "classification": "QUALITY_CONTROL|MAINTENANCE|NOT_MY_DOMAIN",
    "confidence": 0.XX,
    "quality_elements": ["quality_standards", "compliance"],
    "primary_problem_type": "quality_control|maintenance|production|cost|environmental|other",
    "reasoning": "Explain why this is/isn't primarily a quality/maintenance problem"
}

CRITICAL: Be conservative! Only claim high confidence if this is CLEARLY your domain."""
        )
        
        response = agent(f"Analyze this query from quality control perspective: {query}")
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "classification": "NOT_MY_DOMAIN",
            "confidence": 0.0,
            "quality_elements": [],
            "primary_problem_type": "error",
            "reasoning": f"Analysis failed: {str(e)}",
            "error": True
        })


@tool
def sustainability_classifier(query: str) -> str:
    """Environmental and sustainability specialist."""
    try:
        agent = Agent(
            name="sustainability_specialist",
            system_prompt="""You are a Sustainability specialist for manufacturing intent classification.

EXPERTISE: Environmental impact, carbon footprint, green manufacturing, sustainability metrics
PRIMARY CLASSIFICATIONS: ENVIRONMENTAL_OPTIMIZATION
SECONDARY: COST_OPTIMIZATION (when environmental costs involved)

STRICT CLASSIFICATION RULES:
- ENVIRONMENTAL_OPTIMIZATION: ONLY if the core question is about carbon management, emission reduction, or environmental constraints
- COST_OPTIMIZATION: ONLY if environmental costs/carbon pricing are the primary concern
- NOT_MY_DOMAIN: If the problem is primarily about production scheduling, quality, supply chain, or general cost optimization

CONFIDENCE RULES:
- High confidence (0.85-0.95): Clear environmental/sustainability focus with explicit constraints
- Medium confidence (0.6-0.8): Some environmental elements but other factors dominate
- Low confidence (0.3-0.6): Minimal environmental content
- Very low confidence (0.1-0.3): Clearly not an environmental problem

RESPONSE FORMAT (JSON only):
{
    "classification": "ENVIRONMENTAL_OPTIMIZATION|COST_OPTIMIZATION|NOT_MY_DOMAIN",
    "confidence": 0.XX,
    "environmental_elements": ["carbon_footprint", "sustainability"],
    "primary_problem_type": "carbon_management|emission_reduction|cost|production|quality|other",
    "reasoning": "Explain why this is/isn't primarily an environmental/sustainability problem"
}

CRITICAL: Be conservative! Only claim high confidence if this is CLEARLY your domain."""
        )
        
        response = agent(f"Analyze this query from sustainability perspective: {query}")
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "classification": "NOT_MY_DOMAIN",
            "confidence": 0.0,
            "environmental_elements": [],
            "primary_problem_type": "error",
            "reasoning": f"Analysis failed: {str(e)}",
            "error": True
        })


@tool
def cost_optimization_classifier(query: str) -> str:
    """Cost optimization and financial analysis specialist."""
    try:
        agent = Agent(
            name="cost_optimization_specialist",
            system_prompt="""You are a Cost Optimization specialist for manufacturing intent classification.

EXPERTISE: Cost accounting, financial modeling, economic optimization, ROI analysis
PRIMARY CLASSIFICATIONS: COST_OPTIMIZATION, DEMAND_FORECASTING
SECONDARY: CAPACITY_PLANNING (when cost/financial focus)

STRICT CLASSIFICATION RULES:
- COST_OPTIMIZATION: ONLY if the core question is about cost reduction, financial optimization, or ROI maximization
- DEMAND_FORECASTING: ONLY if the primary focus is financial forecasting or revenue planning
- CAPACITY_PLANNING: ONLY if primary focus is cost-based capacity decisions
- NOT_MY_DOMAIN: If the problem is primarily about production scheduling, quality, supply chain, or environmental compliance

CONFIDENCE RULES:
- High confidence (0.85-0.95): Clear cost/financial optimization focus
- Medium confidence (0.6-0.8): Some cost elements but other factors dominate
- Low confidence (0.3-0.6): Minimal cost/financial content
- Very low confidence (0.1-0.3): Clearly not a cost optimization problem

RESPONSE FORMAT (JSON only):
{
    "classification": "COST_OPTIMIZATION|DEMAND_FORECASTING|CAPACITY_PLANNING|NOT_MY_DOMAIN",
    "confidence": 0.XX,
    "cost_elements": ["financial_optimization", "cost_reduction"],
    "primary_problem_type": "cost_reduction|ROI_optimization|forecasting|production|environmental|other",
    "reasoning": "Explain why this is/isn't primarily a cost/financial optimization problem"
}

CRITICAL: Be conservative! Only claim high confidence if this is CLEARLY your domain."""
        )
        
        response = agent(f"Analyze this query from cost optimization perspective: {query}")
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "classification": "NOT_MY_DOMAIN",
            "confidence": 0.0,
            "cost_elements": [],
            "primary_problem_type": "error",
            "reasoning": f"Analysis failed: {str(e)}",
            "error": True
        })


# ==================== ENHANCED INTENT TOOL ====================

class DcisionAI_Intent_Tool:
    """
    Enhanced DcisionAI Intent Classification Tool using AWS-style manager-worker pattern.
    
    Features:
    - 6 specialized worker agents for comprehensive coverage
    - Advanced consensus building with expertise weighting
    - Robust error handling and JSON parsing
    - Comprehensive performance tracking
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DcisionAI_Intent_Tool")
        self.throttle_manager = get_platform_throttle_manager()
        
        # Expertise weights for different intent types
        self.expertise_weights = {
            "CAPACITY_PLANNING": {"ops_research": 2.0, "production_systems": 1.5, "cost_optimization": 1.2},
            "PRODUCTION_SCHEDULING": {"production_systems": 2.0, "ops_research": 1.5, "quality": 1.2},
            "ENVIRONMENTAL_OPTIMIZATION": {"sustainability": 2.0, "ops_research": 1.5, "cost_optimization": 1.2},
            "QUALITY_CONTROL": {"quality": 2.0, "production_systems": 1.5},
            "COST_OPTIMIZATION": {"cost_optimization": 2.0, "ops_research": 1.5},
            "SUPPLY_CHAIN": {"supply_chain": 2.0, "ops_research": 1.5},
            "INVENTORY_OPTIMIZATION": {"supply_chain": 2.0, "ops_research": 1.5},
            "MAINTENANCE": {"quality": 2.0, "production_systems": 1.5},
            "DEMAND_FORECASTING": {"cost_optimization": 2.0, "supply_chain": 1.5}
        }
        
        # Initialize manager agent with all worker tools
        self._initialize_manager_agent()
        
        # Performance tracking
        self.performance_metrics = SwarmPerformanceMetrics(
            total_agents=7,  # 1 manager + 6 workers
            active_agents=0,
            consensus_achieved=False,
            agreement_score=0.0,
            execution_time=0.0,
            swarm_status="initialized",
            handoffs_performed=0,
            manager_delegations=0,
            worker_responses=0,
            swarm_metadata={}
        )
        
        self.logger.info("✅ Enhanced DcisionAI Intent Tool initialized with 6 specialist workers")
    
    def _initialize_manager_agent(self):
        """Initialize manager agent with all 6 worker tools"""
        try:
            self.manager_agent = Agent(
                name="enhanced_intent_classification_manager",
                tools=[
                    ops_research_classifier, 
                    production_systems_classifier, 
                    supply_chain_classifier,
                    quality_classifier,
                    sustainability_classifier,
                    cost_optimization_classifier
                ],
                system_prompt="""You are an Enhanced Intent Classification Manager for manufacturing optimization problems.

You coordinate a team of 6 specialist agents to accurately classify manufacturing queries:
1. ops_research_classifier: Mathematical optimization, OR models, capacity planning
2. production_systems_classifier: Production workflows, scheduling, line operations
3. supply_chain_classifier: Logistics, inventory, distribution, procurement
4. quality_classifier: Quality control, compliance, standards, maintenance
5. sustainability_classifier: Environmental constraints, carbon management, green manufacturing
6. cost_optimization_classifier: Financial optimization, cost reduction, ROI analysis

DELEGATION STRATEGY:
- Manufacturing optimization problems: ops_research + production_systems + relevant specialist
- Environmental/sustainability problems: sustainability + ops_research + production_systems
- Quality/compliance problems: quality + production_systems
- Supply chain problems: supply_chain + ops_research
- Cost problems: cost_optimization + ops_research
- Complex problems: ALL specialists for comprehensive analysis

CONSENSUS BUILDING RULES:
1. Unanimous agreement (all agree): confidence = min(0.95, average_confidence)
2. Strong majority (4+ agree): confidence = min(0.85, average_confidence * 0.9)
3. Simple majority (3+ agree): confidence = min(0.75, average_confidence * 0.8)
4. Split decision (tied): confidence = min(0.65, average_confidence * 0.7)

EXPERTISE WEIGHTING:
Apply 2.0x weight to primary experts and 1.5x to secondary experts for specific intent types.

RESPONSE FORMAT (JSON only):
{
    "primary_intent": "PRODUCTION_SCHEDULING|CAPACITY_PLANNING|INVENTORY_OPTIMIZATION|QUALITY_CONTROL|SUPPLY_CHAIN|MAINTENANCE|COST_OPTIMIZATION|DEMAND_FORECASTING|ENVIRONMENTAL_OPTIMIZATION|GENERAL_QUERY",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Synthesis of specialist analyses with clear consensus reasoning",
    "specialist_consensus": {
        "ops_research": {"classification": "INTENT", "confidence": 0.9},
        "production_systems": {"classification": "INTENT", "confidence": 0.8},
        "supply_chain": {"classification": "INTENT", "confidence": 0.7},
        "quality": {"classification": "INTENT", "confidence": 0.9},
        "sustainability": {"classification": "INTENT", "confidence": 0.8},
        "cost_optimization": {"classification": "INTENT", "confidence": 0.85}
    },
    "consensus_method": "unanimous|strong_majority|simple_majority|expertise_weighted",
    "agreement_score": 0.85,
    "handoffs_performed": 6
}

CRITICAL RULES:
- ALWAYS delegate to at least 3 specialists for non-trivial queries
- Use expertise weighting for final classification
- Calculate consensus confidence using the rules above
- NO fake responses - if delegation fails, report error honestly
- Provide transparent reasoning showing how consensus was reached"""
            )
            
            self.logger.info("✅ Enhanced manager agent initialized with 6 specialist worker tools")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize enhanced manager agent: {e}")
            raise Exception(f"Enhanced manager agent initialization failed: {e}")
    
    def classify_intent(self, query: str, domain: str = "manufacturing") -> IntentClassification:
        """Classify intent using enhanced AWS-style manager-worker delegation"""
        start_time = datetime.now()
        
        try:
            self.logger.info("🚀 Starting enhanced intent classification with 6-specialist delegation")
            
            # Manager delegates to worker specialists
            classification_task = f"""
            Classify this manufacturing query using your 6-specialist team:
            
            Query: "{query}"
            Domain: {domain}
            
            Delegate to ALL 6 specialists and build robust consensus from their analyses.
            Use expertise weighting and transparent consensus building.
            Provide comprehensive classification with detailed reasoning.
            
            IMPORTANT: Wait for ALL 6 specialists to respond before building consensus.
            """
            
            # Execute manager agent with timeout handling
            try:
                response = self.manager_agent(classification_task)
            except Exception as e:
                self.logger.error(f"Manager agent execution failed: {e}")
                # Fallback: try individual agent calls
                return self._fallback_classification(query, domain)
            
            # Parse manager's synthesized response
            classification_result = self._parse_manager_response(response)
            
            # Validate that we have responses from all 6 specialists
            specialist_consensus = classification_result.get("specialist_consensus", {})
            if len(specialist_consensus) < 6:
                self.logger.warning(f"Only {len(specialist_consensus)}/6 specialists responded. Using fallback.")
                return self._fallback_classification(query, domain)
            
            # Apply expertise weighting to final classification
            final_result = self._apply_expertise_weighting(classification_result)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update performance metrics
            self._update_performance_metrics(final_result, execution_time)
            
            return IntentClassification(
                primary_intent=IntentCategory(final_result["primary_intent"].lower()),
                confidence=final_result["confidence"],
                entities=final_result.get("entities", []),
                objectives=final_result.get("objectives", []),
                reasoning=final_result["reasoning"],
                swarm_agreement=final_result.get("agreement_score", final_result["confidence"]),
                classification_metadata={
                    "strategy": "enhanced_aws_style_manager_worker",
                    "manager_agent": "enhanced_intent_classification_manager",
                    "worker_tools": [
                        "ops_research_classifier", 
                        "production_systems_classifier", 
                        "supply_chain_classifier",
                        "quality_classifier",
                        "sustainability_classifier",
                        "cost_optimization_classifier"
                    ],
                    "handoffs_performed": final_result.get("handoffs_performed", 0),
                    "consensus_method": final_result.get("consensus_method", "enhanced_manager_synthesis"),
                    "specialist_consensus": final_result.get("specialist_consensus", {}),
                    "expertise_weighting_applied": True,
                    "throttle_status": self.throttle_manager.get_status(),
                    "execution_time": execution_time,
                    "all_specialists_responded": len(specialist_consensus) == 6
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced intent classification failed: {e}")
            # NO FAKE RESPONSES - Return honest error classification
            return IntentClassification(
                primary_intent=IntentCategory.GENERAL_QUERY,
                confidence=0.0,
                entities=[],
                objectives=[],
                reasoning=f"Enhanced intent classification failed: {str(e)}",
                swarm_agreement=0.0,
                classification_metadata={
                    "strategy": "enhanced_aws_style_manager_worker",
                    "error": True,
                    "error_message": str(e)
                }
            )
    
    def _fallback_classification(self, query: str, domain: str) -> IntentClassification:
        """Fallback classification when manager delegation fails"""
        self.logger.info("🔄 Using fallback classification with direct agent calls")
        
        start_time = datetime.now()
        
        try:
            # Call each specialist directly with timeout
            specialist_results = {}
            
            # Define specialists with their tools
            specialists = [
                ("ops_research", ops_research_classifier),
                ("production_systems", production_systems_classifier),
                ("supply_chain", supply_chain_classifier),
                ("quality", quality_classifier),
                ("sustainability", sustainability_classifier),
                ("cost_optimization", cost_optimization_classifier)
            ]
            
            for name, tool_func in specialists:
                try:
                    self.logger.info(f"Calling {name} specialist...")
                    result = tool_func(query)
                    specialist_results[name] = self._parse_agent_result(result)
                    self.logger.info(f"✅ {name} responded")
                except Exception as e:
                    self.logger.error(f"❌ {name} failed: {e}")
                    specialist_results[name] = {
                        "classification": "GENERAL_QUERY",
                        "confidence": 0.0,
                        "error": True,
                        "error_message": str(e)
                    }
            
            # Build consensus from actual responses
            final_result = self._build_fallback_consensus(specialist_results)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return IntentClassification(
                primary_intent=IntentCategory(final_result["primary_intent"].lower()),
                confidence=final_result["confidence"],
                entities=final_result.get("entities", []),
                objectives=final_result.get("objectives", []),
                reasoning=final_result["reasoning"],
                swarm_agreement=final_result.get("agreement_score", final_result["confidence"]),
                classification_metadata={
                    "strategy": "fallback_direct_agent_calls",
                    "specialist_results": specialist_results,
                    "consensus_method": "fallback_majority_vote",
                    "execution_time": execution_time,
                    "fallback_used": True
                }
            )
            
        except Exception as e:
            self.logger.error(f"Fallback classification failed: {e}")
            return IntentClassification(
                primary_intent=IntentCategory.GENERAL_QUERY,
                confidence=0.0,
                entities=[],
                objectives=[],
                reasoning=f"Fallback classification failed: {str(e)}",
                swarm_agreement=0.0,
                classification_metadata={
                    "strategy": "fallback_direct_agent_calls",
                    "error": True,
                    "error_message": str(e)
                }
            )
    
    def _parse_agent_result(self, result: str) -> Dict[str, Any]:
        """Parse individual agent result"""
        try:
            parsed = self._extract_json_from_text(result)
            if parsed and "classification" in parsed:
                return parsed
            else:
                return {
                    "classification": "GENERAL_QUERY",
                    "confidence": 0.0,
                    "error": True,
                    "error_message": "Failed to parse agent response"
                }
        except Exception as e:
            return {
                "classification": "GENERAL_QUERY",
                "confidence": 0.0,
                "error": True,
                "error_message": str(e)
            }
    
    def _build_fallback_consensus(self, specialist_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Build consensus from direct agent responses"""
        try:
            # Count classifications
            classifications = {}
            total_confidence = 0
            valid_responses = 0
            
            for specialist, result in specialist_results.items():
                if not result.get("error", False):
                    classification = result.get("classification", "GENERAL_QUERY")
                    confidence = result.get("confidence", 0.0)
                    
                    if classification not in classifications:
                        classifications[classification] = {"count": 0, "confidence_sum": 0, "specialists": []}
                    
                    classifications[classification]["count"] += 1
                    classifications[classification]["confidence_sum"] += confidence
                    classifications[classification]["specialists"].append(specialist)
                    
                    total_confidence += confidence
                    valid_responses += 1
            
            if not classifications:
                return {
                    "primary_intent": "GENERAL_QUERY",
                    "confidence": 0.0,
                    "entities": [],
                    "objectives": [],
                    "reasoning": "No valid specialist responses received",
                    "specialist_consensus": specialist_results
                }
            
            # Find most common classification
            most_common = max(classifications.items(), key=lambda x: x[1]["count"])
            primary_intent = most_common[0]
            avg_confidence = most_common[1]["confidence_sum"] / most_common[1]["count"]
            
            # Extract entities and objectives
            entities = []
            objectives = []
            for result in specialist_results.values():
                if not result.get("error", False):
                    entities.extend(result.get("entities", []))
                    objectives.extend(result.get("objectives", []))
            
            # Remove duplicates
            entities = list(set(entities))
            objectives = list(set(objectives))
            
            reasoning = f"Fallback consensus: {most_common[1]['count']}/{valid_responses} specialists chose {primary_intent}. "
            reasoning += f"Specialists: {', '.join(most_common[1]['specialists'])}. "
            reasoning += f"Average confidence: {avg_confidence:.3f}"
            
            return {
                "primary_intent": primary_intent,
                "confidence": avg_confidence,
                "entities": entities,
                "objectives": objectives,
                "reasoning": reasoning,
                "specialist_consensus": specialist_results,
                "consensus_method": "fallback_majority_vote",
                "agreement_score": avg_confidence
            }
            
        except Exception as e:
            self.logger.error(f"Fallback consensus building failed: {e}")
            return {
                "primary_intent": "GENERAL_QUERY",
                "confidence": 0.0,
                "entities": [],
                "objectives": [],
                "reasoning": f"Fallback consensus building failed: {str(e)}",
                "specialist_consensus": specialist_results
            }
    
    def _parse_manager_response(self, response: str) -> Dict[str, Any]:
        """Enhanced manager response parsing with robust JSON extraction"""
        try:
            # Handle Strands AgentResult format
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Enhanced JSON extraction
            parsed = self._extract_json_from_text(response_text)
            
            if parsed and "primary_intent" in parsed:
                return parsed
            else:
                # NO FAKE RESPONSES - Return honest parsing failure
                return {
                    "primary_intent": "GENERAL_QUERY",
                    "confidence": 0.0,
                    "entities": [],
                    "objectives": [],
                    "reasoning": "Failed to parse manager response - invalid JSON format",
                    "error": True
                }
                
        except Exception as e:
            # NO FAKE RESPONSES - Return honest error
            return {
                "primary_intent": "GENERAL_QUERY", 
                "confidence": 0.0,
                "entities": [],
                "objectives": [],
                "reasoning": f"Manager response parsing failed: {str(e)}",
                "error": True
            }
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Enhanced JSON extraction with multiple strategies"""
        try:
            # Strategy 1: Direct JSON parse
            cleaned_text = self._clean_json_response(text)
            return json.loads(cleaned_text)
        except:
            pass
        
        try:
            # Strategy 2: Extract JSON block with better regex
            json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\})*)*\})*)*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            if matches:
                # Try each match, starting with the most complete one
                for match in reversed(matches):
                    try:
                        return json.loads(match)
                    except:
                        continue
        except:
            pass
        
        try:
            # Strategy 3: Fix common JSON issues and retry
            fixed_text = re.sub(r',\s*}', '}', text)
            fixed_text = re.sub(r',\s*]', ']', fixed_text)
            fixed_text = re.sub(r'(\w+):', r'"\1":', fixed_text)  # Quote unquoted keys
            
            json_match = re.search(json_pattern, fixed_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # NO FAKE RESPONSES - Return None if all strategies fail
        return None
    
    def _clean_json_response(self, response_text: str) -> str:
        """Enhanced JSON cleaning"""
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        
        # Remove markdown formatting
        response_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', response_text)
        response_text = re.sub(r'\*([^*]+)\*', r'\1', response_text)
        
        # Remove leading/trailing whitespace and newlines
        response_text = response_text.strip()
        
        return response_text
    
    def _apply_expertise_weighting(self, classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply expertise weighting to improve classification accuracy"""
        try:
            if classification_result.get("error", False):
                return classification_result
            
            primary_intent = classification_result.get("primary_intent", "").upper()
            specialist_consensus = classification_result.get("specialist_consensus", {})
            
            if primary_intent in self.expertise_weights and specialist_consensus:
                # Get weights for this intent type
                weights = self.expertise_weights[primary_intent]
                
                # Recalculate confidence with expertise weighting
                weighted_scores = {}
                total_weight = 0
                
                for specialist, result in specialist_consensus.items():
                    if isinstance(result, dict) and "confidence" in result:
                        weight = weights.get(specialist, 1.0)
                        confidence = result["confidence"]
                        weighted_score = confidence * weight
                        
                        if result.get("classification", "").upper() == primary_intent:
                            weighted_scores[specialist] = weighted_score
                            total_weight += weight
                
                if total_weight > 0:
                    # Calculate expertise-weighted confidence
                    weighted_confidence = sum(weighted_scores.values()) / total_weight
                    classification_result["confidence"] = min(0.95, weighted_confidence)
                    classification_result["consensus_method"] = "expertise_weighted"
            
            return classification_result
            
        except Exception as e:
            self.logger.warning(f"Expertise weighting failed: {e}")
            return classification_result
    
    def _update_performance_metrics(self, classification_result: Dict[str, Any], execution_time: float):
        """Update performance metrics with comprehensive data"""
        self.performance_metrics.execution_time = execution_time
        self.performance_metrics.swarm_status = "completed"
        self.performance_metrics.handoffs_performed = classification_result.get("handoffs_performed", 6)
        self.performance_metrics.manager_delegations = 1
        self.performance_metrics.worker_responses = len(classification_result.get("specialist_consensus", {}))
        self.performance_metrics.consensus_achieved = not classification_result.get("error", False)
        self.performance_metrics.agreement_score = classification_result.get("agreement_score", classification_result.get("confidence", 0.0))
        
        self.performance_metrics.swarm_metadata = {
            "manager_delegations": self.performance_metrics.manager_delegations,
            "worker_responses": self.performance_metrics.worker_responses,
            "handoffs_performed": self.performance_metrics.handoffs_performed,
            "consensus_method": classification_result.get("consensus_method", "enhanced_manager_synthesis"),
            "specialist_consensus": classification_result.get("specialist_consensus", {}),
            "enhanced_aws_style_pattern": True,
            "expertise_weighting_applied": True,
            "real_handoffs": True,
            "worker_count": 6
        }
    
    def get_performance_metrics(self) -> SwarmPerformanceMetrics:
        """Get comprehensive performance metrics"""
        return self.performance_metrics


# Factory function for easy integration
def create_dcisionai_intent_tool() -> DcisionAI_Intent_Tool:
    """Create Enhanced DcisionAI Intent Tool with 6-specialist AWS-style pattern"""
    return DcisionAI_Intent_Tool()
