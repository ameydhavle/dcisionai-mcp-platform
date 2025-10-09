"""
Parallel Execution Strategy for AWS Bedrock Swarm Agents

This module provides intelligent parallel execution strategies that work within
AWS Bedrock service quotas while maximizing performance.

AWS Bedrock Claude 3.5 Sonnet V2 Quotas (Current):
- On-demand requests per minute: 1
- On-demand tokens per minute: 400,000
- Cross-region inference profiles: Available (distributes across regions)

Strategies:
1. Cross-Region Parallel Execution (Current)
2. Quota Increase Request (Recommended for production)
3. Provisioned Throughput (For high-volume production)
4. Hybrid Approach (Combination of strategies)
"""

import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExecutionStrategy:
    """Configuration for parallel execution strategy."""
    name: str
    max_parallel_requests: int
    delay_between_batches: float
    use_cross_region: bool
    description: str

class ParallelExecutionStrategies:
    """Available parallel execution strategies for swarm agents."""
    
    # Current AWS Bedrock Claude 3.5 Sonnet V2 quotas
    CURRENT_QUOTAS = {
        "requests_per_minute": 1,
        "tokens_per_minute": 400000,
        "cross_region_available": True
    }
    
    # Available strategies
    STRATEGIES = {
        "cross_region_parallel": ExecutionStrategy(
            name="Cross-Region Parallel",
            max_parallel_requests=5,  # 5 agents across different regions
            delay_between_batches=0.0,  # No delay needed with cross-region
            use_cross_region=True,
            description="Use cross-region inference profiles for parallel execution"
        ),
        
        "quota_increase_parallel": ExecutionStrategy(
            name="Quota Increase Parallel",
            max_parallel_requests=10,  # Assuming quota increase to 10 RPM
            delay_between_batches=6.0,  # 60s / 10 requests = 6s between requests
            use_cross_region=True,
            description="Parallel execution with increased quotas (requires AWS support request)"
        ),
        
        "provisioned_throughput": ExecutionStrategy(
            name="Provisioned Throughput",
            max_parallel_requests=50,  # High throughput with provisioned capacity
            delay_between_batches=0.0,  # No delays needed with provisioned throughput
            use_cross_region=False,
            description="High-performance parallel execution with provisioned throughput"
        ),
        
        "hybrid_approach": ExecutionStrategy(
            name="Hybrid Approach",
            max_parallel_requests=3,  # Conservative parallel execution
            delay_between_batches=20.0,  # 20s between batches
            use_cross_region=True,
            description="Balanced approach combining cross-region and batching"
        )
    }
    
    @classmethod
    def get_strategy(cls, strategy_name: str = "cross_region_parallel") -> ExecutionStrategy:
        """Get execution strategy by name."""
        if strategy_name not in cls.STRATEGIES:
            logger.warning(f"Unknown strategy '{strategy_name}', using default 'cross_region_parallel'")
            strategy_name = "cross_region_parallel"
        
        return cls.STRATEGIES[strategy_name]
    
    @classmethod
    def list_strategies(cls) -> Dict[str, str]:
        """List all available strategies with descriptions."""
        return {name: strategy.description for name, strategy in cls.STRATEGIES.items()}
    
    @classmethod
    def get_quota_recommendations(cls) -> Dict[str, Any]:
        """Get recommendations for quota increases based on swarm requirements."""
        return {
            "current_limitations": {
                "requests_per_minute": cls.CURRENT_QUOTAS["requests_per_minute"],
                "impact": "Sequential execution only, 5+ minute execution times"
            },
            "recommended_quotas": {
                "requests_per_minute": 10,  # Allow 10 parallel requests
                "expected_improvement": "5-10x faster execution (30-60 seconds vs 5+ minutes)"
            },
            "quota_increase_request": {
                "service_code": "bedrock",
                "quota_code": "L-79E773B3",  # Claude 3.5 Sonnet V2 requests per minute
                "current_value": 1,
                "requested_value": 10,
                "justification": "Manufacturing optimization swarm requires parallel agent execution for real-time decision making"
            },
            "provisioned_throughput_alternative": {
                "description": "For production workloads requiring consistent high throughput",
                "benefits": ["Dedicated capacity", "No throttling", "Predictable performance"],
                "cost_consideration": "Higher cost but guaranteed performance"
            }
        }

class IntelligentParallelExecutor:
    """Intelligent parallel executor that adapts to AWS Bedrock quotas."""
    
    def __init__(self, strategy_name: str = "cross_region_parallel"):
        self.strategy = ParallelExecutionStrategies.get_strategy(strategy_name)
        self.logger = logging.getLogger(__name__)
        
    def execute_agents_parallel(self, agents: Dict[str, Any], task: Any) -> Dict[str, Any]:
        """
        Execute agents in parallel using the configured strategy.
        
        Args:
            agents: Dictionary of agent_id -> agent objects
            task: Task to execute on each agent
            
        Returns:
            Dictionary of agent_id -> results
        """
        agent_results = {}
        agent_list = list(agents.items())
        total_agents = len(agent_list)
        
        self.logger.info(f"🚀 Executing {total_agents} agents using '{self.strategy.name}' strategy")
        self.logger.info(f"   Max parallel requests: {self.strategy.max_parallel_requests}")
        self.logger.info(f"   Cross-region enabled: {self.strategy.use_cross_region}")
        self.logger.info(f"   Delay between batches: {self.strategy.delay_between_batches}s")
        
        try:
            if self.strategy.max_parallel_requests >= total_agents:
                # Execute all agents in parallel
                return self._execute_fully_parallel(agent_list, task)
            else:
                # Execute in batches
                return self._execute_batched(agent_list, task)
                
        except Exception as e:
            self.logger.error(f"❌ Parallel execution failed: {str(e)}")
            raise
    
    def _execute_fully_parallel(self, agent_list: List[tuple], task: Any) -> Dict[str, Any]:
        """Execute all agents in parallel."""
        agent_results = {}
        
        with ThreadPoolExecutor(max_workers=len(agent_list)) as executor:
            # Submit all tasks
            future_to_agent = {}
            for agent_id, agent in agent_list:
                future = executor.submit(self._execute_agent_task, agent, task)
                future_to_agent[future] = agent_id
            
            # Collect results as they complete
            completed_count = 0
            for future in as_completed(future_to_agent):
                agent_id = future_to_agent[future]
                completed_count += 1
                
                try:
                    result = future.result()
                    agent_results[agent_id] = result
                    self.logger.info(f"✅ Agent {agent_id} completed ({completed_count}/{len(agent_list)})")
                except Exception as e:
                    self.logger.error(f"❌ Agent {agent_id} execution failed: {str(e)}")
                    agent_results[agent_id] = self._create_error_result(agent_id, agents[agent_id], str(e))
        
        return agent_results
    
    def _execute_batched(self, agent_list: List[tuple], task: Any) -> Dict[str, Any]:
        """Execute agents in batches to respect quotas."""
        agent_results = {}
        batch_size = self.strategy.max_parallel_requests
        
        for i in range(0, len(agent_list), batch_size):
            batch = agent_list[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(agent_list) + batch_size - 1) // batch_size
            
            self.logger.info(f"🔄 Executing batch {batch_num}/{total_batches} ({len(batch)} agents)")
            
            # Execute batch in parallel
            batch_results = self._execute_fully_parallel(batch, task)
            agent_results.update(batch_results)
            
            # Wait between batches if not the last batch
            if i + batch_size < len(agent_list) and self.strategy.delay_between_batches > 0:
                self.logger.info(f"⏳ Waiting {self.strategy.delay_between_batches}s before next batch...")
                time.sleep(self.strategy.delay_between_batches)
        
        return agent_results
    
    def _execute_agent_task(self, agent: Any, task: Any) -> Any:
        """Execute task on individual agent - delegates to the agent's inference profile."""
        try:
            # Use the agent's inference profile to execute the task
            if hasattr(agent, 'inference_profile') and hasattr(agent.inference_profile, 'execute_inference'):
                # Create a prompt for the agent based on the task
                prompt = self._create_agent_prompt(agent, task)
                result = agent.inference_profile.execute_inference(prompt)
                
                # Import AgentResult here to avoid circular imports
                from consensus_mechanism import AgentResult
                
                # Return proper AgentResult object
                return AgentResult(
                    agent_id=agent.agent_id,
                    specialization=agent.specialization,
                    region=agent.region,
                    result=result,
                    confidence=0.8,  # Default confidence, could be extracted from result
                    timestamp=datetime.now(),
                    performance_metrics={"execution_time": 0.0}  # Could be measured
                )
            else:
                raise ValueError(f"Agent {agent.agent_id} does not have proper inference profile")
                
        except Exception as e:
            self.logger.error(f"❌ Agent {agent.agent_id} task execution failed: {str(e)}")
            return self._create_error_result(agent.agent_id, agent, str(e))
    
    def _create_agent_prompt(self, agent: Any, task: Any) -> str:
        """Create a specialized prompt for the agent based on the task."""
        # This is a simplified version - the actual implementation should be more sophisticated
        if hasattr(task, 'query'):
            return f"Task: {task.query}\nSpecialization: {agent.specialization}\nRegion: {agent.region}"
        else:
            return f"Task: {str(task)}\nSpecialization: {agent.specialization}\nRegion: {agent.region}"
    
    def _create_error_result(self, agent_id: str, agent: Any, error: str) -> Any:
        """Create error result for failed agent execution."""
        from consensus_mechanism import AgentResult
        
        return AgentResult(
            agent_id=agent_id,
            specialization=getattr(agent, 'specialization', 'unknown'),
            region=getattr(agent, 'region', 'unknown'),
            result={"error": error, "error_type": "ExecutionError"},
            confidence=0.0,
            timestamp=datetime.now(),
            performance_metrics={"error": error}
        )

def get_quota_increase_instructions() -> str:
    """Get instructions for requesting AWS Bedrock quota increases."""
    return """
🚀 AWS Bedrock Quota Increase Instructions:

1. **Service Quotas Console**:
   - Go to AWS Service Quotas console
   - Search for "bedrock"
   - Find "On-demand model inference requests per minute for Anthropic Claude 3.5 Sonnet V2"

2. **Request Details**:
   - Current Value: 1 request per minute
   - Requested Value: 10 requests per minute (or higher based on needs)
   - Use Case: Manufacturing optimization swarm requiring parallel agent execution

3. **Justification**:
   - Real-time manufacturing decision making
   - Parallel agent execution for swarm intelligence
   - Production workload requiring consistent performance

4. **Alternative: Provisioned Throughput**:
   - For guaranteed high throughput
   - Higher cost but no throttling
   - Suitable for production workloads

5. **Expected Improvement**:
   - Current: 5+ minutes (sequential execution)
   - With quota increase: 30-60 seconds (parallel execution)
   - 5-10x performance improvement
"""

if __name__ == "__main__":
    # Example usage
    strategies = ParallelExecutionStrategies()
    print("Available Strategies:")
    for name, description in strategies.list_strategies().items():
        print(f"  - {name}: {description}")
    
    print("\nQuota Recommendations:")
    recommendations = strategies.get_quota_recommendations()
    print(f"Current limitations: {recommendations['current_limitations']}")
    print(f"Recommended quotas: {recommendations['recommended_quotas']}")
    
    print("\nQuota Increase Instructions:")
    print(get_quota_increase_instructions())
