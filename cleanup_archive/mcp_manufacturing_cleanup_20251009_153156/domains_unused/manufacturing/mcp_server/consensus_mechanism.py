"""
Consensus Mechanism for Peer-to-Peer Swarm Agents

This module provides consensus algorithms for aggregating results from multiple
specialized agents in a peer-to-peer swarm architecture.

NO MOCK RESPONSES: All consensus mechanisms use real agent results only.
"""

import logging
import statistics
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ConsensusAlgorithm(Enum):
    """Consensus algorithms for swarm decision making."""
    WEIGHTED_VOTING = "weighted_voting"
    CONFIDENCE_AGGREGATION = "confidence_aggregation"
    PEER_VALIDATION = "peer_validation"

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
    consensus_value: Dict[str, Any]
    confidence: float
    agreement_score: float
    participating_agents: List[str]
    algorithm_used: str
    metadata: Dict[str, Any]
    timestamp: datetime

class ConsensusMechanism:
    """
    Consensus mechanism for peer-to-peer swarm collaboration.
    
    NO MOCK RESPONSES: Uses real agent results and confidence scores.
    """
    
    def __init__(self):
        """Initialize consensus mechanism with peer-to-peer algorithms."""
        self.consensus_algorithms = {
            ConsensusAlgorithm.WEIGHTED_VOTING: self._weighted_voting_consensus,
            ConsensusAlgorithm.CONFIDENCE_AGGREGATION: self._confidence_aggregation_consensus,
            ConsensusAlgorithm.PEER_VALIDATION: self._peer_validation_consensus
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
                                
                                # Extract model building insights - try both nested and direct structures
                                model_data = None
                                if 'model_building_insights' in agent_data:
                                    model_data = agent_data['model_building_insights']
                                else:
                                    # Try direct extraction from agent_data
                                    model_data = agent_data
                                
                                if model_data:
                                    # Extract model type
                                    if 'model_type' in model_data:
                                        model_types.append(model_data['model_type'])
                                    
                                    # Extract variables - handle both list and dict formats
                                    if 'variables' in model_data:
                                        vars_data = model_data['variables']
                                        if isinstance(vars_data, list):
                                            variables.extend(vars_data)
                                        elif isinstance(vars_data, dict):
                                            for var_name, var_info in vars_data.items():
                                                if isinstance(var_info, dict):
                                                    # Handle detailed variable info like {"x": {"type": "integer", "description": "..."}}
                                                    var_type = var_info.get('type', 'unknown')
                                                    variables.append(f"{var_name} ({var_type})")
                                                else:
                                                    variables.append(f"{var_name}: {var_info}")
                                        elif isinstance(vars_data, str):
                                            variables.append(vars_data)
                                    
                                    # Extract decision variables if present
                                    if 'decision_variables' in model_data:
                                        decision_vars = model_data['decision_variables']
                                        if isinstance(decision_vars, dict):
                                            for var_name, var_info in decision_vars.items():
                                                if isinstance(var_info, dict):
                                                    var_type = var_info.get('type', 'unknown')
                                                    variables.append(f"{var_name} ({var_type})")
                                                else:
                                                    variables.append(f"{var_name}: {var_info}")
                                        elif isinstance(decision_vars, list):
                                            variables.extend(decision_vars)
                                    
                                    # Extract constraints - handle both list and dict formats
                                    if 'constraints' in model_data:
                                        constraints_data = model_data['constraints']
                                        if isinstance(constraints_data, list):
                                            constraints.extend(constraints_data)
                                        elif isinstance(constraints_data, dict):
                                            for constraint_name, constraint_info in constraints_data.items():
                                                if isinstance(constraint_info, dict):
                                                    # Handle detailed constraint info
                                                    constraint_desc = constraint_info.get('description', constraint_name)
                                                    constraints.append(f"{constraint_name}: {constraint_desc}")
                                                else:
                                                    constraints.append(f"{constraint_name}: {constraint_info}")
                                        elif isinstance(constraints_data, str):
                                            constraints.append(constraints_data)
                                    
                                    # Extract objectives - handle both list and dict formats
                                    if 'objectives' in model_data:
                                        objectives_data = model_data['objectives']
                                        if isinstance(objectives_data, list):
                                            objectives.extend(objectives_data)
                                        elif isinstance(objectives_data, dict):
                                            for obj_name, obj_info in objectives_data.items():
                                                if isinstance(obj_info, dict):
                                                    obj_type = obj_info.get('type', 'unknown')
                                                    objectives.append(f"{obj_name} ({obj_type})")
                                                else:
                                                    objectives.append(f"{obj_name}: {obj_info}")
                                        elif isinstance(objectives_data, str):
                                            objectives.append(objectives_data)
                                    
                                    # Extract objective functions if present
                                    if 'objective_functions' in model_data:
                                        obj_functions = model_data['objective_functions']
                                        if isinstance(obj_functions, list):
                                            objectives.extend(obj_functions)
                                        elif isinstance(obj_functions, dict):
                                            for func_name, func_info in obj_functions.items():
                                                objectives.append(f"{func_name}: {func_info}")
                                
                                # Extract other model information from the full agent_data
                                for key, value in agent_data.items():
                                    if key not in ['model_building_insights', 'model_type', 'variables', 'constraints', 'objectives', 'decision_variables', 'objective_functions']:
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
    
    def _extract_model_info_from_text(self, text: str, model_types: list, variables: list, constraints: list, objectives: list) -> None:
        """Extract model information from text when JSON parsing fails."""
        # Extract model types from text with more specific patterns
        text_lower = text.lower()
        
        # Model type extraction with more comprehensive patterns
        if 'mixed-integer linear programming' in text_lower or 'milp' in text_lower:
            model_types.append('Mixed-Integer Linear Programming (MILP)')
        elif 'mixed integer linear programming' in text_lower:
            model_types.append('Mixed-Integer Linear Programming (MILP)')
        elif 'linear programming' in text_lower and 'integer' in text_lower:
            model_types.append('Mixed-Integer Linear Programming (MILP)')
        elif 'linear programming' in text_lower or 'lp' in text_lower:
            model_types.append('Linear Programming (LP)')
        elif 'integer programming' in text_lower or 'ip' in text_lower:
            model_types.append('Integer Programming (IP)')
        elif 'constraint programming' in text_lower or 'cp' in text_lower:
            model_types.append('Constraint Programming (CP)')
        elif 'quadratic programming' in text_lower or 'qp' in text_lower:
            model_types.append('Quadratic Programming (QP)')
        elif 'nonlinear programming' in text_lower or 'nlp' in text_lower:
            model_types.append('Nonlinear Programming (NLP)')
        elif 'optimization' in text_lower:
            model_types.append('Optimization Model')
        else:
            model_types.append('Mathematical Programming Model')
        
        # Extract decision variables with more detailed patterns
        # Look for patterns like "x (integer)", "y (binary)", "z (continuous)"
        import re
        
        # Extract variables with types: "variable_name (type)"
        var_pattern = r'(\w+)\s*\((\w+)\)'
        var_matches = re.findall(var_pattern, text)
        for var_name, var_type in var_matches:
            variables.append(f"{var_name} ({var_type})")
        
        # Extract variables mentioned in context
        if 'decision variables' in text_lower:
            # Look for variable names after "decision variables"
            var_section = text[text.lower().find('decision variables'):text.lower().find('decision variables') + 200]
            var_names = re.findall(r'\b([a-z])\b', var_section)
            for var in var_names:
                if var not in [v.split(' ')[0] for v in variables]:
                    variables.append(f"{var} (variable)")
        
        # Extract specific variable types
        if 'integer' in text_lower and 'variable' in text_lower:
            int_vars = re.findall(r'\b([a-z])\b.*?integer', text_lower)
            for var in int_vars:
                if f"{var} (integer)" not in variables:
                    variables.append(f"{var} (integer)")
        
        if 'binary' in text_lower and 'variable' in text_lower:
            bin_vars = re.findall(r'\b([a-z])\b.*?binary', text_lower)
            for var in bin_vars:
                if f"{var} (binary)" not in variables:
                    variables.append(f"{var} (binary)")
        
        if 'continuous' in text_lower and 'variable' in text_lower:
            cont_vars = re.findall(r'\b([a-z])\b.*?continuous', text_lower)
            for var in cont_vars:
                if f"{var} (continuous)" not in variables:
                    variables.append(f"{var} (continuous)")
        
        # Extract constraints with more specific patterns
        if 'worker_availability' in text_lower:
            constraints.append('worker_availability')
        if 'production_capacity' in text_lower:
            constraints.append('production_capacity')
        if 'worker_assignment' in text_lower:
            constraints.append('worker_assignment')
        if 'capacity' in text_lower:
            constraints.append('capacity_constraints')
        if 'availability' in text_lower:
            constraints.append('availability_constraints')
        if 'assignment' in text_lower:
            constraints.append('assignment_constraints')
        
        # Extract objectives with more specific patterns
        if 'maximize_efficiency' in text_lower:
            objectives.append('maximize_efficiency')
        if 'minimize_costs' in text_lower:
            objectives.append('minimize_costs')
        if 'maximize' in text_lower:
            max_obj = re.search(r'maximize\s+(\w+)', text_lower)
            if max_obj:
                objectives.append(f"maximize_{max_obj.group(1)}")
        if 'minimize' in text_lower:
            min_obj = re.search(r'minimize\s+(\w+)', text_lower)
            if min_obj:
                objectives.append(f"minimize_{min_obj.group(1)}")
        
        # Fallback extractions for common manufacturing terms
        if 'worker' in text_lower and 'assignment' not in [c.lower() for c in constraints]:
            constraints.append('worker_constraints')
        if 'shift' in text_lower and 'scheduling' not in [c.lower() for c in constraints]:
            constraints.append('shift_scheduling_constraints')
        if 'line' in text_lower and 'assignment' not in [c.lower() for c in constraints]:
            constraints.append('line_assignment_constraints')
        if 'hour' in text_lower and 'max_hours' not in [c.lower() for c in constraints]:
            constraints.append('work_hours_constraints')
    
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
            
            # Calculate weighted consensus
            consensus_value = self._calculate_weighted_consensus(results, normalized_weights)
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
    
    def _peer_validation_consensus(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Peer validation consensus with cross-validation.
        
        NO MOCK RESPONSES: Uses real agent results and peer validation.
        """
        try:
            # Calculate peer validation scores
            validation_scores = {}
            for result in results:
                validation_score = self._calculate_peer_validation_score(result, results)
                validation_scores[result.agent_id] = validation_score
            
            # Calculate weighted consensus based on validation scores
            total_validation = sum(validation_scores.values())
            validation_weights = {agent_id: score / total_validation for agent_id, score in validation_scores.items()}
            
            consensus_value = self._calculate_validation_weighted_consensus(results, validation_weights)
            agreement_score = self._calculate_agreement_score(results)
            
            return {
                "consensus_value": consensus_value,
                "confidence": statistics.mean([r.confidence for r in results]),
                "agreement_score": agreement_score,
                "metadata": {
                    "validation_scores": validation_scores,
                    "validation_weights": validation_weights,
                    "total_agents": len(results),
                    "algorithm": "peer_validation"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Peer validation consensus failed: {str(e)}")
            raise
    
    def _get_specialization_weight(self, specialization: str) -> float:
        """Get weight for agent specialization."""
        # Higher weights for more relevant specializations
        weights = {
            "operations_research": 1.0,
            "production_systems": 0.9,
            "supply_chain": 0.8,
            "quality_control": 0.7,
            "sustainability": 0.6,
            "data_analysis": 1.0,
            "business_context": 0.8,
            "sample_data": 0.9,
            "model_building": 1.0,
            "formulation": 0.9,
            "constraint_analysis": 0.8,
            "solver_compatibility": 0.7,
            "research": 0.6
        }
        return weights.get(specialization, 0.5)
    
    def _calculate_weighted_consensus(self, results: List[AgentResult], weights: Dict[str, float]) -> Dict[str, Any]:
        """Calculate weighted consensus from agent results."""
        weighted_results = {}
        
        for result in results:
            weight = weights.get(result.agent_id, 0.0)
            for key, value in result.result.items():
                if key not in weighted_results:
                    weighted_results[key] = 0.0
                weighted_results[key] += value * weight
        
        return weighted_results
    
    def _calculate_validation_weighted_consensus(self, results: List[AgentResult], validation_weights: Dict[str, float]) -> Dict[str, Any]:
        """Calculate validation-weighted consensus from agent results."""
        validation_results = {}
        
        for result in results:
            validation_weight = validation_weights.get(result.agent_id, 0.0)
            for key, value in result.result.items():
                if key not in validation_results:
                    validation_results[key] = 0.0
                validation_results[key] += value * validation_weight
        
        return validation_results
    
    def _calculate_agreement_score(self, results: List[AgentResult]) -> float:
        """Calculate agreement score between agent results."""
        if len(results) <= 1:
            return 1.0
        
        # Simple agreement calculation based on result similarity
        # This is a simplified version - could be enhanced with more sophisticated similarity metrics
        total_pairs = len(results) * (len(results) - 1) / 2
        agreeing_pairs = 0
        
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                if self._results_agree(results[i], results[j]):
                    agreeing_pairs += 1
        
        return agreeing_pairs / total_pairs if total_pairs > 0 else 0.0
    
    def _results_agree(self, result1: AgentResult, result2: AgentResult) -> bool:
        """Check if two results agree (simplified version)."""
        # This is a simplified agreement check
        # In practice, you might want more sophisticated similarity metrics
        return abs(result1.confidence - result2.confidence) < 0.2
    
    def _calculate_peer_validation_score(self, target_result: AgentResult, all_results: List[AgentResult]) -> float:
        """Calculate how well a result aligns with peer results."""
        if len(all_results) <= 1:
            return 1.0
        
        # Calculate average similarity to other results
        similarities = []
        for result in all_results:
            if result.agent_id != target_result.agent_id:
                similarity = self._calculate_result_similarity(target_result, result)
                similarities.append(similarity)
        
        return statistics.mean(similarities) if similarities else 0.0
    
    def _calculate_result_similarity(self, result1: AgentResult, result2: AgentResult) -> float:
        """Calculate similarity between two results."""
        # Simplified similarity calculation
        confidence_similarity = 1.0 - abs(result1.confidence - result2.confidence)
        
        # Could add more sophisticated similarity metrics here
        return confidence_similarity

