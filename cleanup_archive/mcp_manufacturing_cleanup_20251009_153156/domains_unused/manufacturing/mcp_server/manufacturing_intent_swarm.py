#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Manufacturing Intent Swarm
==============================================================

5-agent peer-to-peer swarm for manufacturing intent classification.
Specialized agents with inference profiles for comprehensive intent analysis.

NO MOCK RESPONSES POLICY: All implementations use real AWS Bedrock calls only.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from inference_profile_enhanced_swarm import InferenceProfileEnhancedSwarm, SwarmTask
from swarm_inference_profile import AgentRole
from consensus_mechanism import ConsensusAlgorithm

logger = logging.getLogger(__name__)

class ManufacturingIntentSwarm(InferenceProfileEnhancedSwarm):
    """
    5-agent peer-to-peer swarm for manufacturing intent classification.
    
    NO MOCK RESPONSES: All agents use real AWS Bedrock inference profiles.
    """
    
    def __init__(self):
        super().__init__("manufacturing_intent_swarm", 5)
        self._initialize_specialized_agents()
        
        logger.info("🎯 ManufacturingIntentSwarm initialized with 5 specialized agents")
    
    def _initialize_specialized_agents(self):
        """Initialize 5 specialized agents with inference profiles."""
        try:
            agents_config = [
                ("ops_research_agent", "operations_research", AgentRole.INTENT_CLASSIFIER, "us-east-1"),
                ("production_systems_agent", "production_systems", AgentRole.INTENT_CLASSIFIER, "us-west-2"),
                ("supply_chain_agent", "supply_chain", AgentRole.INTENT_CLASSIFIER, "eu-west-1"),
                ("quality_agent", "quality_control", AgentRole.INTENT_CLASSIFIER, "ap-southeast-1"),
                ("sustainability_agent", "sustainability", AgentRole.INTENT_CLASSIFIER, "us-east-1")
            ]
            
            for agent_id, specialization, agent_role, region in agents_config:
                self.add_agent(agent_id, specialization, agent_role, region)
            
            logger.info("✅ All 5 intent classification agents initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize intent swarm agents: {str(e)}")
            raise
    
    def classify_intent(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify manufacturing intent using 5-agent peer-to-peer swarm collaboration.
        
        NO MOCK RESPONSES: All agents use real AWS Bedrock calls.
        """
        try:
            # Create swarm task as dictionary (consistent with data swarm)
            task_id = f"intent_classification_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            task = {
                "task_id": task_id,
                "task_type": "intent_classification",
                "query": query,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "swarm_id": self.swarm_id
            }
            
            logger.info(f"🎯 Executing intent classification with 5-agent peer-to-peer swarm")
            logger.info(f"   Query: {query[:100]}...")
            
            # Execute swarm task with confidence aggregation consensus
            swarm_result = self.execute_swarm_task(task, ConsensusAlgorithm.CONFIDENCE_AGGREGATION)
            
            # Handle SwarmResult object
            if hasattr(swarm_result, 'individual_results') and hasattr(swarm_result, 'consensus_result'):
                # Process consensus result
                if swarm_result.consensus_result.consensus_value is None:
                    # Handle error case - NO MOCK RESPONSES
                    return {
                        "error": "Intent classification failed",
                        "error_details": swarm_result.consensus_result.metadata.get("error", "Unknown error"),
                        "participating_agents": swarm_result.consensus_result.participating_agents,
                        "timestamp": datetime.now().isoformat(),
                        "status": "error"
                    }
                
                # Extract intent classification from consensus result
                consensus_data = swarm_result.consensus_result.consensus_value
                
                # Structure the response
                intent_result = {
                    "intent": consensus_data.get("intent", "unknown"),
                    "confidence": swarm_result.consensus_result.confidence,
                    "agreement_score": swarm_result.consensus_result.agreement_score,
                    "entities": consensus_data.get("entities", []),
                    "objectives": consensus_data.get("objectives", []),
                    "reasoning": consensus_data.get("reasoning", ""),
                    "specialization_insights": consensus_data.get("specialization_insights", {}),
                    "consensus_metadata": {
                        "algorithm_used": swarm_result.consensus_result.algorithm_used,
                        "participating_agents": swarm_result.consensus_result.participating_agents,
                        "execution_time": swarm_result.execution_time,
                        "swarm_id": self.swarm_id
                    },
                    "individual_agent_results": self._extract_agent_results(swarm_result.individual_results),
                    "timestamp": datetime.now().isoformat(),
                    "status": consensus_data.get("status", "success")
                }
            else:
                # Handle dictionary result
                intent_result = swarm_result
            
            logger.info(f"✅ Intent classified: {intent_result['intent']} (confidence: {intent_result['confidence']:.3f})")
            logger.info(f"   Agreement score: {intent_result['agreement_score']:.3f}")
            execution_time = swarm_result.execution_time if hasattr(swarm_result, 'execution_time') else intent_result.get('consensus_metadata', {}).get('execution_time', 0)
            logger.info(f"   Execution time: {execution_time:.2f}s")
            
            return intent_result
            
        except Exception as e:
            logger.error(f"❌ Intent classification failed: {str(e)}")
            # NO MOCK RESPONSES - Return error gracefully
            return {
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def _create_agent_prompt(self, agent, task: SwarmTask) -> str:
        """Create specialized prompt for intent classification agent."""
        query = task.payload.get("query", "")
        context = task.context
        
        # Create role-specific prompt based on agent specialization
        if agent.specialization == "operations_research":
            return f"""
            You are an Operations Research specialist for manufacturing intent classification.
            
            Manufacturing Query: {query}
            Context: {json.dumps(context, indent=2)}
            
            Analyze this query from an operations research perspective:
            1. Identify mathematical optimization aspects
            2. Classify the primary intent (e.g., PRODUCTION_SCHEDULING, INVENTORY_OPTIMIZATION, etc.)
            3. Provide confidence score (0.0-1.0)
            4. Extract key entities and variables
            5. Identify optimization objectives
            6. Provide detailed reasoning from OR perspective
            
            Focus on: Mathematical modeling, optimization problems, constraint satisfaction, algorithmic approaches.
            
            Format response as JSON with: intent, confidence, entities, objectives, reasoning, specialization_insights.
            """
        
        elif agent.specialization == "production_systems":
            return f"""
            You are a Production Systems specialist for manufacturing intent classification.
            
            Manufacturing Query: {query}
            Context: {json.dumps(context, indent=2)}
            
            Analyze this query from a production systems perspective:
            1. Identify production line and manufacturing process aspects
            2. Classify the primary intent (e.g., PRODUCTION_SCHEDULING, QUALITY_CONTROL, etc.)
            3. Provide confidence score (0.0-1.0)
            4. Extract key entities and processes
            5. Identify production objectives
            6. Provide detailed reasoning from production systems perspective
            
            Focus on: Production lines, manufacturing processes, equipment, throughput, efficiency.
            
            Format response as JSON with: intent, confidence, entities, objectives, reasoning, specialization_insights.
            """
        
        elif agent.specialization == "supply_chain":
            return f"""
            You are a Supply Chain specialist for manufacturing intent classification.
            
            Manufacturing Query: {query}
            Context: {json.dumps(context, indent=2)}
            
            Analyze this query from a supply chain perspective:
            1. Identify supply chain and logistics aspects
            2. Classify the primary intent (e.g., INVENTORY_OPTIMIZATION, SUPPLY_CHAIN_OPTIMIZATION, etc.)
            3. Provide confidence score (0.0-1.0)
            4. Extract key entities and supply chain components
            5. Identify supply chain objectives
            6. Provide detailed reasoning from supply chain perspective
            
            Focus on: Inventory, suppliers, logistics, distribution, procurement, demand forecasting.
            
            Format response as JSON with: intent, confidence, entities, objectives, reasoning, specialization_insights.
            """
        
        elif agent.specialization == "quality_control":
            return f"""
            You are a Quality Control specialist for manufacturing intent classification.
            
            Manufacturing Query: {query}
            Context: {json.dumps(context, indent=2)}
            
            Analyze this query from a quality control perspective:
            1. Identify quality and compliance aspects
            2. Classify the primary intent (e.g., QUALITY_CONTROL, DEFECT_ANALYSIS, etc.)
            3. Provide confidence score (0.0-1.0)
            4. Extract key entities and quality metrics
            5. Identify quality objectives
            6. Provide detailed reasoning from quality control perspective
            
            Focus on: Quality standards, defect analysis, compliance, testing, quality metrics.
            
            Format response as JSON with: intent, confidence, entities, objectives, reasoning, specialization_insights.
            """
        
        elif agent.specialization == "sustainability":
            return f"""
            You are a Sustainability specialist for manufacturing intent classification.
            
            Manufacturing Query: {query}
            Context: {json.dumps(context, indent=2)}
            
            Analyze this query from a sustainability perspective:
            1. Identify environmental and sustainability aspects
            2. Classify the primary intent (e.g., ENVIRONMENTAL_OPTIMIZATION, ENERGY_EFFICIENCY, etc.)
            3. Provide confidence score (0.0-1.0)
            4. Extract key entities and environmental factors
            5. Identify sustainability objectives
            6. Provide detailed reasoning from sustainability perspective
            
            Focus on: Energy efficiency, waste reduction, carbon footprint, environmental impact, green manufacturing.
            
            Format response as JSON with: intent, confidence, entities, objectives, reasoning, specialization_insights.
            """
        
        else:
            # Generic prompt for unknown specializations
            return f"""
            You are a Manufacturing specialist for intent classification.
            
            Manufacturing Query: {query}
            Context: {json.dumps(context, indent=2)}
            
            Analyze this manufacturing query and provide:
            1. Primary intent classification
            2. Confidence score (0.0-1.0)
            3. Key entities identified
            4. Objectives and goals
            5. Detailed reasoning
            
            Format response as JSON with: intent, confidence, entities, objectives, reasoning, specialization_insights.
            """
    
    def _extract_agent_results(self, individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure individual agent results."""
        agent_results = {}
        
        for agent_id, agent_result in individual_results.items():
            try:
                agent_results[agent_id] = {
                    "specialization": agent_result.specialization,
                    "region": agent_result.region,
                    "confidence": agent_result.confidence,
                    "result": agent_result.result,
                    "execution_time": agent_result.performance_metrics.get("execution_time", 0),
                    "timestamp": agent_result.timestamp.isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Failed to extract result for agent {agent_id}: {str(e)}")
                agent_results[agent_id] = {
                    "error": str(e),
                    "specialization": "unknown",
                    "region": "unknown",
                    "confidence": 0.0
                }
        
        return agent_results
    
    def get_swarm_insights(self) -> Dict[str, Any]:
        """Get insights about the intent classification swarm performance."""
        try:
            swarm_status = self.get_swarm_status()
            
            # Calculate specialization performance
            specialization_performance = {}
            for agent in self.agents.values():
                spec = agent.specialization
                if spec not in specialization_performance:
                    specialization_performance[spec] = {
                        "agent_count": 0,
                        "total_tasks": 0,
                        "average_confidence": 0.0,
                        "regions": set()
                    }
                
                specialization_performance[spec]["agent_count"] += 1
                specialization_performance[spec]["total_tasks"] += len(agent.task_history)
                specialization_performance[spec]["regions"].add(agent.region)
                
                if agent.performance_metrics:
                    avg_conf = agent.performance_metrics.get("average_confidence", 0.5)
                    specialization_performance[spec]["average_confidence"] += avg_conf
            
            # Calculate averages
            for spec_data in specialization_performance.values():
                if spec_data["agent_count"] > 0:
                    spec_data["average_confidence"] /= spec_data["agent_count"]
                spec_data["regions"] = list(spec_data["regions"])
            
            return {
                "swarm_status": swarm_status,
                "specialization_performance": specialization_performance,
                "consensus_algorithms_available": [alg.value for alg in ConsensusAlgorithm],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get swarm insights: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
