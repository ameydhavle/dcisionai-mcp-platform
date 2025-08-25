"""
Bedrock Throttling Solutions for All DcisionAI Tools
===================================================

Centralized throttling management for AWS Bedrock across all manufacturing tools.
NO FALLBACKS - Production-ready throttling with proper error handling.
"""

import asyncio
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from contextlib import asynccontextmanager

# =============================================================================
# CORE THROTTLING COMPONENTS
# =============================================================================

@dataclass
class BedrockLimits:
    """AWS Bedrock service limits"""
    requests_per_minute: int = 1000  # Default RPM limit
    tokens_per_minute: int = 200000  # Default TPM limit
    concurrent_requests: int = 10    # Default concurrent limit
    burst_capacity: int = 50         # Burst allowance

class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        async with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def time_until_available(self, tokens: int = 1) -> float:
        """Calculate time until tokens are available"""
        self._refill()
        if self.tokens >= tokens:
            return 0
        needed_tokens = tokens - self.tokens
        return needed_tokens / self.refill_rate
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

class CircuitBreaker:
    """Circuit breaker pattern for Bedrock requests"""
    
    def __init__(self, failure_threshold: int = 3, timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.throttle_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return False
            return True
        return False
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.throttle_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def record_throttle(self):
        """Record throttling event"""
        self.throttle_count += 1
        self.last_failure_time = time.time()
        # Open circuit faster for throttling
        if self.throttle_count >= 2:
            self.state = "OPEN"

class BedrockThrottleException(Exception):
    """Custom exception for Bedrock throttling - NO FALLBACKS"""
    pass

# =============================================================================
# CENTRALIZED THROTTLE MANAGER
# =============================================================================

class BedrockThrottleManager:
    """Centralized throttling management for ALL tools"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls, limits: BedrockLimits = None):
        """Singleton pattern for platform-wide throttling"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, limits: BedrockLimits = None):
        if hasattr(self, '_initialized'):
            return
            
        self.limits = limits or BedrockThrottleConfig.get_production_limits()
        self.request_queue = asyncio.Queue()
        self.active_requests = 0
        self.request_times = []
        self.token_bucket = TokenBucket(
            capacity=self.limits.requests_per_minute,
            refill_rate=self.limits.requests_per_minute / 60  # per second
        )
        self.circuit_breaker = CircuitBreaker()
        self.logger = logging.getLogger("platform.throttling")
        self._initialized = True
        
        self.logger.info(f"Initialized platform-wide throttling: RPM={self.limits.requests_per_minute}, "
                        f"Concurrent={self.limits.concurrent_requests}")
    
    @asynccontextmanager
    async def request_context(self, tool_name: str, estimated_tokens: int = 1000):
        """Context manager for rate-limited Bedrock requests"""
        
        # Wait for rate limit allowance
        await self._wait_for_rate_limit()
        
        # Check circuit breaker
        if self.circuit_breaker.is_open():
            raise BedrockThrottleException(f"Circuit breaker is open for {tool_name}")
        
        try:
            self.active_requests += 1
            start_time = time.time()
            
            self.logger.debug(f"Starting request for {tool_name} (active: {self.active_requests})")
            
            yield
            
            # Success - record timing
            self.circuit_breaker.record_success()
            
        except Exception as e:
            # Handle different types of errors
            if self._is_throttling_error(e):
                self.circuit_breaker.record_throttle()
                raise BedrockThrottleException(f"Bedrock throttling in {tool_name}: {e}")
            else:
                self.circuit_breaker.record_failure()
                raise
        finally:
            self.active_requests -= 1
            self.request_times.append(time.time())
            
            # Clean old request times (keep last minute)
            cutoff = time.time() - 60
            self.request_times = [t for t in self.request_times if t > cutoff]
    
    async def _wait_for_rate_limit(self):
        """Wait if we're approaching rate limits"""
        
        # Check token bucket
        if not await self.token_bucket.consume(1):
            wait_time = self.token_bucket.time_until_available()
            self.logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        # Check concurrent request limit
        while self.active_requests >= self.limits.concurrent_requests:
            self.logger.debug(f"Concurrent limit reached ({self.active_requests}), waiting...")
            await asyncio.sleep(0.1)
        
        # Check requests per minute
        recent_requests = len([t for t in self.request_times if t > time.time() - 60])
        if recent_requests >= self.limits.requests_per_minute:
            wait_time = 60 - (time.time() - min(self.request_times))
            self.logger.warning(f"RPM limit reached, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
    
    def _is_throttling_error(self, error: Exception) -> bool:
        """Check if error is due to throttling"""
        error_str = str(error).lower()
        throttling_indicators = [
            'throttlingexception',
            'rate exceeded',
            'too many requests',
            'quota exceeded',
            'service unavailable',
            'request limit exceeded',
            'modelthrottledexception'
        ]
        return any(indicator in error_str for indicator in throttling_indicators)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current throttling status"""
        return {
            "active_requests": self.active_requests,
            "circuit_breaker_state": self.circuit_breaker.state,
            "tokens_available": self.token_bucket.tokens,
            "recent_requests": len([t for t in self.request_times if t > time.time() - 60]),
            "limits": {
                "requests_per_minute": self.limits.requests_per_minute,
                "concurrent_requests": self.limits.concurrent_requests
            }
        }

# =============================================================================
# THROTTLE-AWARE STRANDS INTEGRATION
# =============================================================================

class ThrottleAwareAgent:
    """Strands agent with centralized throttling"""
    
    def __init__(self, name: str, system_prompt: str, tool_name: str = "unknown"):
        self.name = name
        self.tool_name = tool_name
        self.throttle_manager = BedrockThrottleManager()
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Initialize Strands agent
        try:
            from strands.agent import Agent

            
            self.agent = Agent(
                system_prompt=system_prompt
            )
            
        except ImportError:
            self.logger.warning("Strands not available - using mock agent")
            self.agent = None
    
    async def invoke_async(self, prompt: str, max_retries: int = 3) -> str:
        """Invoke agent with centralized throttling"""
        
        if not self.agent:
            raise Exception("Strands agent not available - NO FALLBACKS")
        
        for attempt in range(max_retries + 1):
            try:
                async with self.throttle_manager.request_context(self.tool_name, estimated_tokens=1000):
                    response = await self.agent.invoke_async(prompt)
                    return response
                    
            except BedrockThrottleException as e:
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(f"Throttled, retrying in {wait_time:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise e
            except Exception as e:
                self.logger.error(f"Agent request failed: {e}")
                raise
        
        raise Exception(f"Agent failed after {max_retries} retries - NO FALLBACKS")

class ThrottleAwareSwarm:
    """Swarm with centralized throttling for any tool"""
    
    def __init__(self, tool_name: str, swarm_name: str):
        self.tool_name = tool_name
        self.swarm_name = swarm_name
        self.throttle_manager = BedrockThrottleManager()
        self.agents: List[ThrottleAwareAgent] = []
        self.logger = logging.getLogger(f"swarm.{tool_name}.{swarm_name}")
    
    def add_agent(self, name: str, system_prompt: str) -> ThrottleAwareAgent:
        """Add throttle-aware agent to swarm"""
        agent = ThrottleAwareAgent(name, system_prompt, self.tool_name)
        self.agents.append(agent)
        self.logger.info(f"Added agent {name} to {self.swarm_name}")
        return agent
    
    async def execute_single_agent(self, agent_index: int, prompt: str) -> str:
        """Execute single agent with throttling - NO PARALLEL CHAOS"""
        if agent_index >= len(self.agents):
            raise Exception(f"Agent index {agent_index} out of range")
        
        agent = self.agents[agent_index]
        return await agent.invoke_async(prompt)
    
    async def execute_sequential(self, prompts: List[str], max_agents: int = 3) -> List[str]:
        """Execute agents sequentially with throttling"""
        results = []
        agents_to_use = self.agents[:min(max_agents, len(self.agents))]
        
        for i, prompt in enumerate(prompts):
            if i >= len(agents_to_use):
                break
                
            try:
                result = await agents_to_use[i].invoke_async(prompt)
                results.append(result)
                
                # Small delay between sequential requests
                if i < len(prompts) - 1:
                    await asyncio.sleep(0.2)
                    
            except Exception as e:
                self.logger.error(f"Agent {i} failed: {e}")
                raise Exception(f"Sequential execution failed at agent {i} - NO FALLBACKS: {e}")
        
        return results

# =============================================================================
# PRODUCTION CONFIGURATION
# =============================================================================

class BedrockThrottleConfig:
    """Production configuration for all tools"""
    
    @staticmethod
    def get_production_limits() -> BedrockLimits:
        """Conservative production limits for all tools"""
        return BedrockLimits(
            requests_per_minute=300,   # Conservative across all tools
            tokens_per_minute=80000,   # Conservative across all tools
            concurrent_requests=5,     # Conservative concurrent limit
            burst_capacity=10          # Small burst allowance
        )
    
    @staticmethod
    def get_development_limits() -> BedrockLimits:
        """Development limits"""
        return BedrockLimits(
            requests_per_minute=50,    # Very conservative for dev
            tokens_per_minute=10000,   # Very conservative for dev
            concurrent_requests=2,     # Low concurrency for dev
            burst_capacity=3           # Small burst for dev
        )
    
    @staticmethod
    def get_tool_specific_limits(tool_name: str) -> BedrockLimits:
        """Get tool-specific limits if needed"""
        base_limits = BedrockThrottleConfig.get_production_limits()
        
        # Tool-specific adjustments
        tool_multipliers = {
            "intent_tool": 0.2,      # Intent needs fewer requests
            "data_tool": 0.3,        # Data tool moderate usage
            "model_builder": 0.4,    # Model builder heavy usage
            "solver_tool": 0.1,      # Solver minimal LLM usage
            "critique_tool": 0.3,    # Critique moderate usage
            "explain_tool": 0.4      # Explain heavy usage (business text)
        }
        
        multiplier = tool_multipliers.get(tool_name, 0.3)
        
        return BedrockLimits(
            requests_per_minute=int(base_limits.requests_per_minute * multiplier),
            tokens_per_minute=int(base_limits.tokens_per_minute * multiplier),
            concurrent_requests=max(1, int(base_limits.concurrent_requests * multiplier)),
            burst_capacity=max(1, int(base_limits.burst_capacity * multiplier))
        )

# =============================================================================
# PLATFORM INTEGRATION
# =============================================================================

def get_platform_throttle_manager() -> BedrockThrottleManager:
    """Get the singleton platform throttle manager"""
    return BedrockThrottleManager()

def create_throttled_swarm_for_tool(tool_name: str, swarm_name: str) -> ThrottleAwareSwarm:
    """Create a throttle-aware swarm for any tool"""
    return ThrottleAwareSwarm(tool_name, swarm_name)
