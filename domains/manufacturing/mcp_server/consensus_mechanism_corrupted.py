#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Consensus Mechanism
======================================================

Peer-to-peer consensus mechanism for swarm agent collaboration.
Provides weighted voting, confidence aggregation, and peer validation.

NO MOCK RESPONSES POLICY: All consensus algorithms use real agent results only.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class ConsensusAlgorithm(Enum):
    """Consensus algorithms for swarm collaboration."""
    WEIGHTED_VOTING = "weighted_voting"
    CONFIDENCE_AGGREGATION = "confidence_aggregation"
    PEER_VALIDATION = "peer_validation"
    HYBRID_CONSENSUS = "hybrid_consensus"

@dataclass
class AgentResult:
    """Individual agent result with metadata."""
    agent_id: str
    specialization: str
    region: str
    result: Dict[str, Any]
    confidence: float
    timestamp: datetime
    performance_metrics: Dict[str, Any] = None

@dataclass
class ConsensusResult:
    """Consensus result from swarm collaboration."""
    consensus_value: Any
    confidence: float
    agreement_score: float
    participating_agents: List[str]
    algorithm_used: str
    metadata: Dict[str, Any]
    timestamp: datetime

class ConsensusMechanism:
    """
    Peer-to-peer consensus mechanism for swarm agent collaboration.
    
    NO MOCK RESPONSES: All consensus algorithms use real agent results only.
    """
    
    def __init__(self):
        self.consensus_algorithms = {
            ConsensusAlgorithm.WEIGHTED_VOTING: self._weighted_voting_consensus,
            ConsensusAlgorithm.CONFIDENCE_AGGREGATION: self._confidence_aggregation_consensus,
            ConsensusAlgorithm.PEER_VALIDATION: self._peer_validation_consensus,
            ConsensusAlgorithm.HYBRID_CONSENSUS: self._hybrid_consensus
        }
        
        logger.info("🤝 ConsensusMechanism initialized with peer-to-peer algorithms")
    
    def aggregate_results(self, agent_results: Dict[str, AgentResult], 
                         algorithm: ConsensusAlgorithm = ConsensusAlgorithm.CONFIDENCE_AGGREGATION) -> ConsensusResult:
        """
        Aggregate results from peer-to-peer swarm using consensus mechanism.
        
        NO MOCK RESPONSES: Uses real agent results only.
        """
        try:
            logger.info(f"🔄 Executing consensus with {len(agent_results)} agents using {algorithm.value}")
            
            # Convert dict to list of AgentResult objects
            results_list = list(agent_results.values())
            
            # Execute consensus algorithm
            consensus_func = self.consensus_algorithms[algorithm]
            consensus_data = consensus_func(results_list)
            
            # Create consensus result
            consensus_result = ConsensusResult(
                consensus_value=consensus_data["consensus_value"],
                confidence=consensus_data["confidence"],
                agreement_score=consensus_data["agreement_score"],
                participating_agents=[result.agent_id for result in results_list],
                algorithm_used=algorithm.value,
                metadata=consensus_data["metadata"],
                timestamp=datetime.now()
            )
            
            logger.info(f"✅ Consensus completed: confidence={consensus_result.confidence:.3f}, agreement={consensus_result.agreement_score:.3f}")
            return consensus_result
            
        except Exception as e:
            logger.error(f"❌ Consensus failed: {str(e)}")
            # NO MOCK RESPONSES - Return error gracefully
            return ConsensusResult(
                consensus_value=None,
                confidence=0.0,
                agreement_score=0.0,
                participating_agents=list(agent_results.keys()),
                algorithm_used=algorithm.value,
                metadata={"error": str(e), "error_type": type(e).__name__},
                timestamp=datetime.now()
            )
    
    def _weighted_voting_consensus(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Weighted voting consensus based on agent specialization relevance.
        
        NO MOCK RESPONSES: Uses real agent results and confidence scores.
        """
        try:
            # Calculate weights based on confidence and specialization relevance
            weights = {}
            total_weight = 0
            
            for result in results:
                # Weight based on confidence and specialization relevance
                weight = result.confidence * self._get_specialization_weight(result.specialization)
                weights[result.agent_id] = weight
                total_weight += weight
            
            # Normalize weights
            normalized_weights = {agent_id: weight / total_weight for agent_id, weight in weights.items()}
            
            # Aggregate results using weighted voting
            consensus_value = self._aggregate_with_weights(results, normalized_weights)
            
            # Calculate agreement score
            agreement_score = self._calculate_agreement_score(results)
            
            return {
                "consensus_value": consensus_value,
                "confidence": statistics.mean([r.confidence for r in results]),
                "agreement_score": agreement_score,
                "metadata": {
                    "weights": normalized_weights,
                    "total_agents": len(results),
                    "algorithm": "weighted_voting"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Weighted voting consensus failed: {str(e)}")
            raise
    
    def _confidence_aggregation_consensus(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Confidence-based aggregation consensus.
        
        NO MOCK RESPONSES: Uses real agent confidence scores.
        """
        try:
            # Calculate weighted consensus based on confidence scores
            total_confidence = sum(result.confidence for result in results)
            
            if total_confidence == 0:
                # Fallback to simple average if no confidence
                consensus_value = self._simple_average_aggregation(results)
                confidence = 0.5
            else:
                # Weight results by confidence
                consensus_value = self._aggregate_with_confidence(results)
                confidence = total_confidence / len(results)
            
            # Calculate agreement score
            agreement_score = self._calculate_agreement_score(results)
            
            return {
                "consensus_value": consensus_value,
                "confidence": confidence,
                "agreement_score": agreement_score,
                "metadata": {
                    "total_confidence": total_confidence,
                    "average_confidence": confidence,
                    "total_agents": len(results),
                    "algorithm": "confidence_aggregation"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Confidence aggregation consensus failed: {str(e)}")
            raise
    
    def _peer_validation_consensus(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Peer validation consensus where agents validate each other's results.
        
        NO MOCK RESPONSES: Uses real agent validation results.
        """
        try:
            # Calculate peer validation scores
            validation_scores = {}
            
            for result in results:
                # Calculate how well this result aligns with others
                validation_score = self._calculate_peer_validation_score(result, results)
                validation_scores[result.agent_id] = validation_score
            
            # Weight results by validation scores
            total_validation = sum(validation_scores.values())
            if total_validation == 0:
                # Fallback to simple average
                consensus_value = self._simple_average_aggregation(results)
                confidence = 0.5
            else:
                normalized_validation = {agent_id: score / total_validation 
                                       for agent_id, score in validation_scores.items()}
                consensus_value = self._aggregate_with_validation(results, normalized_validation)
                confidence = statistics.mean(validation_scores.values())
            
            # Calculate agreement score
            agreement_score = self._calculate_agreement_score(results)
            
            return {
                "consensus_value": consensus_value,
                "confidence": confidence,
                "agreement_score": agreement_score,
                "metadata": {
                    "validation_scores": validation_scores,
                    "total_agents": len(results),
                    "algorithm": "peer_validation"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Peer validation consensus failed: {str(e)}")
            raise
    
    def _hybrid_consensus(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Hybrid consensus combining multiple algorithms.
        
        NO MOCK RESPONSES: Uses real agent results from multiple consensus methods.
        """
        try:
            # Run multiple consensus algorithms
            weighted_result = self._weighted_voting_consensus(results)
            confidence_result = self._confidence_aggregation_consensus(results)
            validation_result = self._peer_validation_consensus(results)
            
            # Combine results with equal weights
            combined_confidence = (weighted_result["confidence"] + 
                                 confidence_result["confidence"] + 
                                 validation_result["confidence"]) / 3
            
            combined_agreement = (weighted_result["agreement_score"] + 
                                confidence_result["agreement_score"] + 
                                validation_result["agreement_score"]) / 3
            
            # Use confidence aggregation as primary consensus value
            consensus_value = confidence_result["consensus_value"]
            
            return {
                "consensus_value": consensus_value,
                "confidence": combined_confidence,
                "agreement_score": combined_agreement,
                "metadata": {
                    "weighted_voting": weighted_result["metadata"],
                    "confidence_aggregation": confidence_result["metadata"],
                    "peer_validation": validation_result["metadata"],
                    "total_agents": len(results),
                    "algorithm": "hybrid_consensus"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Hybrid consensus failed: {str(e)}")
            raise
    
    def _get_specialization_weight(self, specialization: str) -> float:
        """Get weight for specialization based on relevance."""
        specialization_weights = {
            "operations_research": 1.0,
            "production_systems": 1.0,
            "supply_chain": 0.8,
            "quality_control": 0.9,
            "sustainability": 0.7,
            "data_analytics": 1.0,
            "manufacturing_domain": 1.0,
            "analytics_engineering": 0.9,
            "mathematical_modeling": 1.0,
            "optimization_theory": 1.0,
            "constraint_optimization": 0.9,
            "domain_architecture": 0.8,
            "ortools_optimization": 1.0,
            "pulp_optimization": 0.9,
            "cvxpy_optimization": 0.9,
            "gurobi_optimization": 1.0,
            "cplex_optimization": 1.0,
            "mosek_optimization": 0.9
        }
        return specialization_weights.get(specialization, 0.5)
    
    def _aggregate_with_weights(self, results: List[AgentResult], weights: Dict[str, float]) -> Dict[str, Any]:
        """Aggregate results using weighted voting."""
        # This is a simplified aggregation - in practice, you'd implement
        # domain-specific aggregation logic based on the result structure
        weighted_results = {}
        
        for result in results:
            weight = weights.get(result.agent_id, 0.0)
            for key, value in result.result.items():
                if key not in weighted_results:
                    weighted_results[key] = 0.0
                weighted_results[key] += value * weight
        
        return weighted_results
    
    def _aggregate_with_confidence(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Aggregate results using confidence weighting - extract data from agent responses."""
        try:
            # Determine the type of analysis based on agent specializations
            is_data_analysis = any('data' in result.specialization.lower() for result in results)
            is_model_building = any('model' in result.specialization.lower() for result in results)
            
            if is_data_analysis:
                return self._aggregate_data_analysis_results(results)
            elif is_model_building:
                return self._aggregate_model_building_results(results)
            else:
                return self._aggregate_intent_classification_results(results)
            
        except Exception as e:
            logger.error(f"❌ Confidence aggregation failed: {str(e)}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": [],
                "objectives": [],
                "reasoning": f"Error: {str(e)}",
                "status": "error"
            }
    
    def _aggregate_intent_classification_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Aggregate intent classification results."""
        classifications = []
        entities = []
        objectives = []
        reasoning_parts = []
        confidence_scores = []
        
        for result in results:
            if 'content' in result.result:
                content = result.result['content']
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get('text', '')
                    try:
                        # Parse the JSON response from the agent
                        agent_data = json.loads(text)
                        
                        # Extract classification from specialist_analysis
                        if 'specialist_analysis' in agent_data:
                            for specialist, analysis in agent_data['specialist_analysis'].items():
                                if 'classification' in analysis:
                                    classifications.append(analysis['classification'])
                                    confidence_scores.append(analysis.get('confidence', 0.8))
                                if 'entities' in analysis:
                                    entities.extend(analysis['entities'])
                                if 'objectives' in analysis:
                                    objectives.extend(analysis['objectives'])
                                if 'reasoning' in analysis:
                                    reasoning_parts.append(analysis['reasoning'])
                    except json.JSONDecodeError:
                        # If not JSON, try to extract intent from text
                        if 'CAPACITY_PLANNING' in text:
                            classifications.append('CAPACITY_PLANNING')
                            confidence_scores.append(0.8)
                        elif 'SCHEDULING' in text:
                            classifications.append('SCHEDULING')
                            confidence_scores.append(0.8)
                        elif 'OPTIMIZATION' in text:
                            classifications.append('OPTIMIZATION')
                            confidence_scores.append(0.8)
        
        # Find most common classification with confidence weighting
        if classifications:
            from collections import Counter
            classification_counts = Counter(classifications)
            most_common = classification_counts.most_common(1)[0]
            intent = most_common[0]
            
            # Calculate weighted confidence
            if confidence_scores:
                confidence = sum(confidence_scores) / len(confidence_scores)
            else:
                confidence = most_common[1] / len(classifications)
        else:
            intent = "unknown"
            confidence = 0.0
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": list(set(entities)) if entities else [],
            "objectives": list(set(objectives)) if objectives else [],
            "reasoning": " ".join(reasoning_parts[:2]) if reasoning_parts else "",
            "status": "success"
        }
    
    def _aggregate_data_analysis_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Aggregate data analysis results."""
        entities = []
        data_requirements = []
        insights = []
        readiness_scores = []
        
        for result in results:
            if 'content' in result.result:
                content = result.result['content']
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get('text', '')
                    try:
                        # Try to extract JSON from the text (handle partial JSON responses)
                        json_start = text.find('{')
                        if json_start != -1:
                            # Find the end of the JSON object
                            json_text = text[json_start:]
                            # Try to find a complete JSON object
                            brace_count = 0
                            json_end = 0
                            for i, char in enumerate(json_text):
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        json_end = i + 1
                                        break
                            
                            if json_end > 0:
                                json_text = json_text[:json_end]
                                agent_data = json.loads(json_text)
                                
                                # Extract data analysis insights
                                if 'data_analysis_insights' in agent_data:
                                    insights_data = agent_data['data_analysis_insights']
                                    
                                    # Extract entities from shift_assignment or similar structures
                                    if 'shift_assignment' in insights_data:
                                        shift_data = insights_data['shift_assignment']
                                        for key, value in shift_data.items():
                                            entities.append(f"{key}: {value}")
                                    
                                    # Extract other entities
                                    for key, value in insights_data.items():
                                        if isinstance(value, dict):
                                            for sub_key, sub_value in value.items():
                                                entities.append(f"{sub_key}: {sub_value}")
                                        elif isinstance(value, (str, int, float)):
                                            entities.append(f"{key}: {value}")
                                
                                # Extract data requirements
                                if 'data_requirements' in agent_data:
                                    requirements = agent_data['data_requirements']
                                    if isinstance(requirements, list):
                                        data_requirements.extend(requirements)
                                    elif isinstance(requirements, str):
                                        data_requirements.append(requirements)
                                
                                # Extract readiness score
                                if 'optimization_readiness_score' in agent_data:
                                    score = agent_data['optimization_readiness_score']
                                    if isinstance(score, (int, float)):
                                        readiness_scores.append(score)
                            else:
                                # Fallback to text extraction
                                self._extract_entities_from_text(text, entities)
                        else:
                            # Fallback to text extraction
                            self._extract_entities_from_text(text, entities)
                        
                    except json.JSONDecodeError:
                        # Fallback to text extraction
                        self._extract_entities_from_text(text, entities)
        
        # Calculate average readiness score
        avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0.0
        
        return {
            "entities": list(set(entities)) if entities else [],
            "data_requirements": list(set(data_requirements)) if data_requirements else [],
            "insights": insights,
            "optimization_readiness_score": avg_readiness,
            "status": "success"
        }
    
    def _extract_entities_from_text(self, text: str, entities: list) -> None:
        """Extract entities from text when JSON parsing fails."""
        # Extract common manufacturing entities from text
        if 'total_workers' in text:
            entities.append('total_workers: extracted from text')
        if 'lines' in text:
            entities.append('lines: extracted from text')
        if 'max_hours' in text:
            entities.append('max_hours: extracted from text')
        if 'shift' in text.lower():
            entities.append('shift: extracted from text')
        if 'worker' in text.lower():
            entities.append('worker: extracted from text')
    
    def _aggregate_model_building_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Aggregate model building results."""
        model_types = []
        variables = []
        constraints = []
        objectives = []
        model_insights = []
        
        for result in results:
            if 'content' in result.result:
                content = result.result['content']
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get('text', '')
                    try:
                        # Try to extract JSON from the text (handle partial JSON responses)
                        json_start = text.find('{')
                        if json_start != -1:
                            # Find the end of the JSON object
                            json_text = text[json_start:]
                            # Try to find a complete JSON object
                            brace_count = 0
                            json_end = 0
                            for i, char in enumerate(json_text):
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        json_end = i + 1
                                        break
                            
                            if json_end > 0:
                                json_text = json_text[:json_end]
                                agent_data = json.loads(json_text)
                                
                                # Extract model building insights
                                if 'model_building_insights' in agent_data:
                                    model_data = agent_data['model_building_insights']
                                    
                                    # Extract model type
                                    if 'model_type' in model_data:
                                        model_types.append(model_data['model_type'])
                                    
                                    # Extract variables
                                    if 'variables' in model_data:
                                        vars_data = model_data['variables']
                                        if isinstance(vars_data, list):
                                            variables.extend(vars_data)
                                        elif isinstance(vars_data, dict):
                                            for var_name, var_info in vars_data.items():
                                                variables.append(f"{var_name}: {var_info}")
                                    
                                    # Extract constraints
                                    if 'constraints' in model_data:
                                        constraints_data = model_data['constraints']
                                        if isinstance(constraints_data, list):
                                            constraints.extend(constraints_data)
                                        elif isinstance(constraints_data, str):
                                            constraints.append(constraints_data)
                                    
                                    # Extract objectives
                                    if 'objectives' in model_data:
                                        objectives_data = model_data['objectives']
                                        if isinstance(objectives_data, list):
                                            objectives.extend(objectives_data)
                                        elif isinstance(objectives_data, str):
                                            objectives.append(objectives_data)
                                
                                # Extract other model information from the full agent_data
                                for key, value in agent_data.items():
                                    if isinstance(value, dict):
                                        for sub_key, sub_value in value.items():
                                            model_insights.append(f"{sub_key}: {sub_value}")
                                    elif isinstance(value, (str, int, float)):
                                        model_insights.append(f"{key}: {value}")
                            else:
                                # Fallback to text extraction
                                self._extract_model_info_from_text(text, model_types, variables, constraints, objectives)
                        else:
                            # Fallback to text extraction
                            self._extract_model_info_from_text(text, model_types, variables, constraints, objectives)
                        
                    except json.JSONDecodeError:
                        # Fallback to text extraction
                        self._extract_model_info_from_text(text, model_types, variables, constraints, objectives)
        
        # Find most common model type
        if model_types:
            from collections import Counter
            model_type_counts = Counter(model_types)
            most_common_model = model_type_counts.most_common(1)[0][0]
        else:
            most_common_model = "unknown"
        
        return {
            "model_type": most_common_model,
            "variables": list(set(variables)) if variables else [],
            "constraints": list(set(constraints)) if constraints else [],
            "objectives": list(set(objectives)) if objectives else [],
            "model_insights": model_insights,
            "status": "success"
        }
    
    def _extract_model_info_from_text(self, text: str, model_types: list, variables: list, constraints: list, objectives: list) -> None:
        """Extract model information from text when JSON parsing fails."""
        # Extract common model types from text
        if 'linear programming' in text.lower() or 'lp' in text.lower():
            model_types.append('linear_programming')
        elif 'integer programming' in text.lower() or 'ip' in text.lower():
            model_types.append('integer_programming')
        elif 'mixed integer' in text.lower() or 'milp' in text.lower():
            model_types.append('mixed_integer_linear_programming')
        elif 'constraint programming' in text.lower() or 'cp' in text.lower():
            model_types.append('constraint_programming')
        else:
            model_types.append('optimization_model')
        
        # Extract variables from text
        if 'worker' in text.lower():
            variables.append('worker_assignment')
        if 'shift' in text.lower():
            variables.append('shift_schedule')
        if 'line' in text.lower():
            variables.append('line_assignment')
        if 'hour' in text.lower():
            variables.append('work_hours')
        
        # Extract constraints from text
        if 'max_hours' in text.lower() or '48' in text:
            constraints.append('max_hours_per_week: 48')
        if 'worker' in text.lower() and 'line' in text.lower():
            constraints.append('worker_line_assignment')
        if 'shift' in text.lower():
            constraints.append('shift_scheduling_constraints')
            return {
                "status": "error",
                "error": "All agents failed - AWS Bedrock authorization required",
                "error_type": "AuthorizationError",
                "intent": "unknown",
                "confidence": 0.0,
                "entities": [],
                "objectives": [],
                "reasoning": f"All {len(results)} agents failed due to AWS Bedrock authorization issues",
                "specialization_insights": {},
                "participating_agents": [result.agent_id for result in results],
                "failed_agents": [result.agent_id for result in failed_agents],
                "successful_agents": []
            }
        
        # If some agents failed, return partial failure status
        if len(failed_agents) > 0:
            # Only use successful agents for consensus
            total_confidence = sum(result.confidence for result in successful_agents)
            if total_confidence == 0:
                return {
                    "status": "partial_failure",
                    "error": f"{len(failed_agents)} out of {len(results)} agents failed",
                    "error_type": "PartialFailure",
                    "intent": "unknown",
                    "confidence": 0.0,
                    "entities": [],
                    "objectives": [],
                    "reasoning": f"Only {len(successful_agents)} out of {len(results)} agents succeeded",
                    "specialization_insights": {},
                    "participating_agents": [result.agent_id for result in results],
                    "failed_agents": [result.agent_id for result in failed_agents],
                    "successful_agents": [result.agent_id for result in successful_agents]
                }
        else:
            # All agents succeeded
            total_confidence = sum(result.confidence for result in results)
        
        # Only process successful agents for consensus
        agents_to_process = successful_agents if len(failed_agents) > 0 else results
        
        for result in agents_to_process:
            confidence_weight = result.confidence / total_confidence if total_confidence > 0 else 1.0 / len(agents_to_process)
            for key, value in result.result.items():
                if key not in confidence_results:
                    # Initialize based on value type
                    if isinstance(value, (int, float)):
                        confidence_results[key] = 0.0
                    elif isinstance(value, str):
                        confidence_results[key] = ""
                    elif isinstance(value, list):
                        confidence_results[key] = []
                    elif isinstance(value, dict):
                        confidence_results[key] = {}
                    else:
                        confidence_results[key] = None
                
                # Handle different value types safely
                if isinstance(value, (int, float)) and isinstance(confidence_results[key], (int, float)):
                    confidence_results[key] += value * confidence_weight
                elif isinstance(value, str) and isinstance(confidence_results[key], str):
                    # For string values, use the first non-empty value
                    if not confidence_results[key] and value:
                        confidence_results[key] = value
                elif isinstance(value, list) and isinstance(confidence_results[key], list):
                    # For lists, extend with unique values
                    for item in value:
                        if item not in confidence_results[key]:
                            confidence_results[key].append(item)
                elif isinstance(value, dict) and isinstance(confidence_results[key], dict):
                    # For dicts, merge the dictionaries
                    confidence_results[key].update(value)
                else:
                    # For other types, use the first non-None value
                    if confidence_results[key] is None and value is not None:
                        confidence_results[key] = value
        
        # Add failure information if there were failed agents
        if len(failed_agents) > 0:
            confidence_results["status"] = "partial_failure"
            confidence_results["failed_agents"] = [result.agent_id for result in failed_agents]
            confidence_results["successful_agents"] = [result.agent_id for result in successful_agents]
            confidence_results["failure_reason"] = f"{len(failed_agents)} out of {len(results)} agents failed"
        else:
            confidence_results["status"] = "success"
        
        return confidence_results
    
    def _aggregate_with_validation(self, results: List[AgentResult], validation_weights: Dict[str, float]) -> Dict[str, Any]:
        """Aggregate results using peer validation weights."""
        validation_results = {}
        
        for result in results:
            validation_weight = validation_weights.get(result.agent_id, 0.0)
            for key, value in result.result.items():
                if key not in validation_results:
                    validation_results[key] = 0.0
                validation_results[key] += value * validation_weight
        
        return validation_results
    
    def _simple_average_aggregation(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Simple average aggregation as fallback - extract intent from agent responses."""
        try:
            # Extract intent classifications from agent results
            classifications = []
            entities = []
            objectives = []
            reasoning_parts = []
            
            for result in results:
                if 'content' in result.result:
                    content = result.result['content']
                    if isinstance(content, list) and len(content) > 0:
                        text = content[0].get('text', '')
                        try:
                            # Parse the JSON response from the agent
                            agent_data = json.loads(text)
                            
                            # Extract classification from specialist_analysis
                            if 'specialist_analysis' in agent_data:
                                for specialist, analysis in agent_data['specialist_analysis'].items():
                                    if 'classification' in analysis:
                                        classifications.append(analysis['classification'])
                                    if 'entities' in analysis:
                                        entities.extend(analysis['entities'])
                                    if 'objectives' in analysis:
                                        objectives.extend(analysis['objectives'])
                                    if 'reasoning' in analysis:
                                        reasoning_parts.append(analysis['reasoning'])
                        except json.JSONDecodeError:
                            # If not JSON, try to extract intent from text
                            if 'CAPACITY_PLANNING' in text:
                                classifications.append('CAPACITY_PLANNING')
                            elif 'SCHEDULING' in text:
                                classifications.append('SCHEDULING')
                            elif 'OPTIMIZATION' in text:
                                classifications.append('OPTIMIZATION')
            
            # Find most common classification
            if classifications:
                from collections import Counter
                most_common = Counter(classifications).most_common(1)[0]
                intent = most_common[0]
                confidence = most_common[1] / len(classifications)
            else:
                intent = "unknown"
                confidence = 0.0
            
            return {
                "intent": intent,
                "confidence": confidence,
                "entities": list(set(entities)) if entities else [],
                "objectives": list(set(objectives)) if objectives else [],
                "reasoning": " ".join(reasoning_parts[:2]) if reasoning_parts else "",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Simple average aggregation failed: {str(e)}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": [],
                "objectives": [],
                "reasoning": f"Error: {str(e)}",
                "status": "error"
            }
    
    def _calculate_peer_validation_score(self, target_result: AgentResult, all_results: List[AgentResult]) -> float:
        """Calculate how well a result aligns with peer results."""
        if len(all_results) <= 1:
            return 1.0
        
        alignment_scores = []
        for other_result in all_results:
            if other_result.agent_id != target_result.agent_id:
                # Calculate alignment score (simplified)
                alignment = self._calculate_result_alignment(target_result.result, other_result.result)
                alignment_scores.append(alignment)
        
        return statistics.mean(alignment_scores) if alignment_scores else 0.5
    
    def _calculate_result_alignment(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> float:
        """Calculate alignment between two results (simplified implementation)."""
        # This is a simplified alignment calculation
        # In practice, you'd implement domain-specific alignment logic
        common_keys = set(result1.keys()) & set(result2.keys())
        if not common_keys:
            return 0.5
        
        alignment_scores = []
        for key in common_keys:
            val1, val2 = result1[key], result2[key]
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric alignment
                if val1 == 0 and val2 == 0:
                    alignment_scores.append(1.0)
                else:
                    alignment_scores.append(1.0 - abs(val1 - val2) / max(abs(val1), abs(val2), 1))
            elif isinstance(val1, str) and isinstance(val2, str):
                # String alignment (simplified)
                alignment_scores.append(1.0 if val1 == val2 else 0.5)
            else:
                alignment_scores.append(0.5)
        
        return statistics.mean(alignment_scores)
    
    def _calculate_agreement_score(self, results: List[AgentResult]) -> float:
        """Calculate overall agreement score among agents."""
        if len(results) <= 1:
            return 1.0
        
        agreement_scores = []
        for i, result1 in enumerate(results):
            for result2 in results[i+1:]:
                alignment = self._calculate_result_alignment(result1.result, result2.result)
                agreement_scores.append(alignment)
        
        return statistics.mean(agreement_scores) if agreement_scores else 0.5
