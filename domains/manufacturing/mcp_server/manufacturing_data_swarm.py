"""
Manufacturing Data Swarm Implementation

This module implements a 3-agent peer-to-peer swarm for manufacturing data analysis
using AWS Bedrock inference profiles with cross-region optimization.

Agents:
1. Data Requirements Specialist (us-east-1)
2. Business Context Specialist (us-west-2) 
3. Sample Data Generator (eu-west-1)

NO MOCK RESPONSES: All agents use real AWS Bedrock inference profiles.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from inference_profile_enhanced_swarm import InferenceProfileEnhancedSwarm
from swarm_inference_profile import SwarmInferenceProfile, AgentRole

logger = logging.getLogger(__name__)

class ManufacturingDataSwarm(InferenceProfileEnhancedSwarm):
    """
    3-agent peer-to-peer swarm for manufacturing data analysis.
    
    Specializations:
    - Data Requirements Specialist: Extracts data entities and requirements
    - Business Context Specialist: Provides business reasoning and industry context
    - Sample Data Generator: Generates realistic sample data with assumptions
    """
    
    def __init__(self):
        super().__init__(
            swarm_id="manufacturing_data_swarm",
            agent_count=3
        )
        
        # Initialize 3 specialized data analysis agents
        self._initialize_data_agents()
        
        logger.info("🎯 ManufacturingDataSwarm initialized with 3 specialized agents")
    
    def _initialize_data_agents(self):
        """Initialize 3 specialized data analysis agents with different specializations."""
        try:
            agents_config = [
                ("data_requirements_agent", "data_requirements", AgentRole.DATA_ANALYST, "us-east-1"),
                ("business_context_agent", "business_context", AgentRole.DATA_ANALYST, "us-west-2"),
                ("sample_data_agent", "sample_data_generation", AgentRole.DATA_ANALYST, "eu-west-1")
            ]
            
            for agent_id, specialization, agent_role, region in agents_config:
                self.add_agent(agent_id, specialization, agent_role, region)
            
            logger.info("✅ All 3 data analysis agents initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize data swarm agents: {str(e)}")
            raise
    
    def analyze_data_requirements(
        self, 
        user_query: str, 
        intent_result: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze data requirements using 3-agent peer-to-peer swarm collaboration.
        
        Args:
            user_query: Original user query
            intent_result: Results from intent classification
            context: Additional context for analysis
            
        Returns:
            Comprehensive data analysis result with consensus
        """
        logger.info(f"📊 Analyzing data requirements using 3-agent peer-to-peer swarm")
        logger.info(f"   Query: {user_query[:100]}...")
        logger.info(f"   Intent: {intent_result.get('intent', 'unknown')}")
        
        # Create specialized task for data analysis
        task = self._create_data_analysis_task(user_query, intent_result, context)
        
        # Execute swarm task
        result = self.execute_swarm_task(task)
        
        # Handle SwarmResult object
        if hasattr(result, 'individual_results') and hasattr(result, 'consensus_result'):
            agent_count = len(result.individual_results)
            # Convert SwarmResult to dictionary for compatibility
            result_dict = {
                "status": "success" if result.consensus_result.confidence > 0 else "error",
                "consensus_result": {
                    "consensus_value": result.consensus_result.consensus_value,
                    "confidence": result.consensus_result.confidence,
                    "agreement_score": result.consensus_result.agreement_score,
                    "participating_agents": result.consensus_result.participating_agents,
                    "algorithm_used": result.consensus_result.algorithm_used
                },
                "individual_agent_results": result.individual_results,
                "execution_time": result.execution_time,
                "swarm_id": result.swarm_metadata.get('swarm_id', 'unknown')
            }
        else:
            # Handle dictionary result
            agent_count = len(result.get('individual_agent_results', {}))
            result_dict = result
        
        logger.info(f"✅ Data analysis completed with {agent_count} agents")
        return result_dict
    
    def _create_data_analysis_task(
        self, 
        user_query: str, 
        intent_result: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create specialized task for data analysis."""
        task_id = f"data_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(user_query) % 10000:04x}"
        return {
            "task_id": task_id,
            "task_type": "data_analysis",
            "user_query": user_query,
            "intent_result": intent_result,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "swarm_id": self.swarm_id
        }
    
    def _create_agent_prompt(self, agent: Any, task: Dict[str, Any]) -> str:
        """Create specialized prompt for data analysis agent."""
        user_query = task.get("user_query", "")
        intent_result = task.get("intent_result", {})
        context = task.get("context", {})
        
        # Create specialized prompt based on agent specialization
        if agent.specialization == "data_requirements":
            return f"""Human: Analyze the data requirements for this manufacturing optimization query.

Query: {user_query}
Intent Analysis: {intent_result.get('intent', 'unknown')} (confidence: {intent_result.get('confidence', 0)})
Entities: {intent_result.get('entities', [])}
Objectives: {intent_result.get('objectives', [])}

Focus on:
1. Extracting all data entities needed for optimization
2. Identifying missing data with business reasoning
3. Explaining the optimization role of each data entity
4. Categorizing data by priority and business impact

Provide comprehensive data requirement analysis in JSON format.

Assistant:"""
        
        elif agent.specialization == "business_context":
            return f"""Human: Provide business context and industry insights for this manufacturing optimization query.

Query: {user_query}
Intent Analysis: {intent_result.get('intent', 'unknown')} (confidence: {intent_result.get('confidence', 0)})
Entities: {intent_result.get('entities', [])}
Objectives: {intent_result.get('objectives', [])}

Focus on:
1. Industry-specific context and benchmarks
2. Business impact assessment of data requirements
3. Market analysis and competitive factors
4. Data reliability and quality factors

Provide business-focused analysis with industry insights in JSON format.

Assistant:"""
        
        elif agent.specialization == "sample_data_generation":
            return f"""Human: Generate realistic sample data for this manufacturing optimization query.

Query: {user_query}
Intent Analysis: {intent_result.get('intent', 'unknown')} (confidence: {intent_result.get('confidence', 0)})
Entities: {intent_result.get('entities', [])}
Objectives: {intent_result.get('objectives', [])}

Focus on:
1. Generating realistic sample data with proper distributions
2. Applying industry-specific benchmarks and standards
3. Ensuring data consistency and feasibility
4. Validating data against business constraints

Provide comprehensive sample data generation in JSON format.

Assistant:"""
        
        else:
            return f"""Human: Analyze data requirements for this manufacturing optimization query: {user_query}

Intent: {intent_result.get('intent', 'unknown')}
Entities: {intent_result.get('entities', [])}
Objectives: {intent_result.get('objectives', [])}

Provide comprehensive data analysis in JSON format.

Assistant:"""
