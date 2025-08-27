#!/usr/bin/env python3
"""
DcisionAI Intent Tool v4 - True Parallel Execution with Strands Agents
=====================================================================

Optimized using ThreadPoolExecutor with individual Strands agents.
All specialists run truly in parallel instead of sequentially.

Version: 4.0
Changes: True parallel execution with ThreadPoolExecutor and Strands agents

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import time
import hashlib
import uuid
import re
import asyncio
import inspect
import contextvars
from typing import Dict, Any, List, Optional, Awaitable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import threading

# Strands framework imports
try:
    from strands import Agent, tool
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    logging.error("Strands framework not available - intent tool requires Strands")
    raise Exception("Strands framework is required but not available")

# Platform throttling imports
try:
    from src.shared.throttling import get_platform_throttle_manager
except Exception:
    def get_platform_throttle_manager():
        class _NullT: 
            def get_status(self): return {"enabled": False}
        return _NullT()

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


# ==================== UTILITIES ====================

def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Robust JSON extraction from LLM text."""
    def _clean(s: str) -> str:
        s = re.sub(r'```json\s*', '', s)
        s = re.sub(r'```\s*', '', s)
        return s.strip()

    # Strategy 1: direct
    try:
        return json.loads(_clean(text))
    except:
        pass

    # Strategy 2: find JSON block
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(_clean(match.group()))
    except:
        pass

    # Strategy 3: extract key-value pairs
    try:
        result = {}
        lines = text.split('\n')
        for line in lines:
            if ':' in line and not line.strip().startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip().strip('"\'')
                value = value.strip().strip('"\'')
                if key and value:
                    result[key] = value
        if result:
            return result
    except:
        pass

    return None


def _norm_class(classification: str) -> str:
    """Normalize classification string"""
    if not classification:
        return "general_query"
    
    classification = classification.upper().strip()
    
    # Map variations to standard categories
    mapping = {
        "NOT_MY_DOMAIN": "general_query",
        "GENERAL": "general_query",
        "UNKNOWN": "general_query",
        "OTHER": "general_query"
    }
    
    return mapping.get(classification, classification.lower())


# ==================== TRUE PARALLEL INTENT TOOL ====================

# Context var to keep trace ids separate per task if you want
_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("_trace_id", default="")


class DcisionAI_Intent_Tool_v4:
    """DcisionAI Intent Tool v4 - True parallel execution with asyncio"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._cache_lock = threading.Lock()
        
        # Create individual agents for true parallel execution
        self.agents = {
            "ops_research": Agent(
                name="ops_research_specialist",
                system_prompt="""You are an Operations Research specialist.

EXPERTISE: Mathematical optimization, linear programming
FOCUS: CAPACITY_PLANNING, COST_OPTIMIZATION, PRODUCTION_SCHEDULING

CLASSIFICATION RULES:
- CAPACITY_PLANNING: "capacity", "resources", "allocate", "planning"
- COST_OPTIMIZATION: "cost", "minimize", "ROI", "budget"
- PRODUCTION_SCHEDULING: "schedule", "optimization", "production planning"
- NOT_MY_DOMAIN: quality, supply chain, environmental, maintenance

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only):
{
    "classification": "CAPACITY_PLANNING|COST_OPTIMIZATION|PRODUCTION_SCHEDULING|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
            ),
            "production_systems": Agent(
                name="production_systems_specialist",
                system_prompt="""You are a Production Systems specialist.

EXPERTISE: Production planning, scheduling, manufacturing
FOCUS: PRODUCTION_SCHEDULING, QUALITY_CONTROL, CAPACITY_PLANNING

CLASSIFICATION RULES:
- PRODUCTION_SCHEDULING: "production schedule", "manufacturing schedule", "production planning"
- QUALITY_CONTROL: "quality", "defects", "inspection", "quality control"
- CAPACITY_PLANNING: "production capacity", "throughput", "capacity planning"
- NOT_MY_DOMAIN: supply chain, cost optimization, environmental

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only):
{
    "classification": "PRODUCTION_SCHEDULING|QUALITY_CONTROL|CAPACITY_PLANNING|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
            ),
            "supply_chain": Agent(
                name="supply_chain_specialist",
                system_prompt="""You are a Supply Chain specialist.

EXPERTISE: Supply chain, logistics, inventory, procurement
FOCUS: SUPPLY_CHAIN, INVENTORY_OPTIMIZATION, DEMAND_FORECASTING

CLASSIFICATION RULES:
- SUPPLY_CHAIN: "supply chain", "logistics", "procurement", "supply chain optimization"
- INVENTORY_OPTIMIZATION: "inventory", "stock", "inventory optimization"
- DEMAND_FORECASTING: "demand", "forecast", "demand forecasting"
- NOT_MY_DOMAIN: production scheduling, quality control, cost optimization

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only):
{
    "classification": "SUPPLY_CHAIN|INVENTORY_OPTIMIZATION|DEMAND_FORECASTING|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
            ),
            "quality": Agent(
                name="quality_specialist",
                system_prompt="""You are a Quality Control specialist.

EXPERTISE: Quality management, defect prevention, inspection
FOCUS: QUALITY_CONTROL, MAINTENANCE

CLASSIFICATION RULES:
- QUALITY_CONTROL: "quality", "defects", "inspection", "quality control"
- MAINTENANCE: "maintenance", "repair", "equipment", "preventive maintenance"
- NOT_MY_DOMAIN: production scheduling, supply chain, cost optimization

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only):
{
    "classification": "QUALITY_CONTROL|MAINTENANCE|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
            ),
            "sustainability": Agent(
                name="sustainability_specialist",
                system_prompt="""You are a Sustainability specialist.

EXPERTISE: Environmental optimization, green manufacturing, sustainability
FOCUS: ENVIRONMENTAL_OPTIMIZATION

CLASSIFICATION RULES:
- ENVIRONMENTAL_OPTIMIZATION: "environmental", "sustainability", "green", "carbon", "emissions"
- NOT_MY_DOMAIN: production scheduling, supply chain, quality control, cost optimization

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only):
{
    "classification": "ENVIRONMENTAL_OPTIMIZATION|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
            ),
            "cost_optimization": Agent(
                name="cost_optimization_specialist",
                system_prompt="""You are a Cost Optimization specialist.

EXPERTISE: Cost reduction, financial optimization, ROI analysis
FOCUS: COST_OPTIMIZATION

CLASSIFICATION RULES:
- COST_OPTIMIZATION: "cost", "minimize", "ROI", "budget", "cost optimization"
- NOT_MY_DOMAIN: production scheduling, supply chain, quality control, environmental

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only):
{
    "classification": "COST_OPTIMIZATION|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
            )
        }
        
        self.logger.info("✅ DcisionAI Intent Tool v4 initialized with 6 parallel agents")

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(query.encode()).hexdigest()

    async def _maybe_await(self, value) -> Any:
        """Await if awaitable; otherwise run sync code in a worker thread (non-blocking)."""
        if inspect.isawaitable(value):
            return await value
        return await asyncio.to_thread(lambda: value)

    async def _invoke_agent_async(
        self,
        agent_name: str,
        agent: Agent,
        query: str,
        timeout_s: float,
    ) -> Dict[str, Any]:
        start_time = time.time()
        try:
            # isolate context per task
            _trace_id.set(str(uuid.uuid4()))

            # Call the agent; works whether agent(...) is sync or async
            resp = await self._maybe_await(agent(f"Classify the intent of this manufacturing query: {query}"))
            response_text = getattr(resp, "content", None) or str(resp)

            result_data = _extract_json(response_text)
            if result_data and isinstance(result_data, dict):
                classification = _norm_class(result_data.get("classification", "general_query"))
                confidence = float(result_data.get("confidence", 0.0))
                if classification == "general_query":
                    confidence = 0.0
                return {
                    "classification": classification,
                    "confidence": confidence,
                    "entities": result_data.get("entities", []),
                    "objectives": result_data.get("objectives", []),
                    "reasoning": (result_data.get("reasoning", "") or "")[:100],
                    "execution_time": time.time() - start_time,
                    "success": True,
                    "agent": agent_name,
                }
        except Exception as e:
            self.logger.warning(f"[{agent_name}] failed: {e}")

        return {
            "classification": "general_query",
            "confidence": 0.0,
            "entities": [],
            "objectives": [],
            "reasoning": f"Error in {agent_name}",
            "execution_time": time.time() - start_time,
            "success": False,
            "agent": agent_name,
        }

    async def _classify_intent_async(self, query: str) -> IntentClassification:
        start_time = time.time()

        cache_key = self._get_cache_key(query)
        with self._cache_lock:
            if cache_key in self._cache:
                self.logger.info("Using cached result")
                return self._cache[cache_key]

        self.logger.info("🚀 Starting true parallel intent classification with 6 agents (asyncio)")

        # Determine concurrency from platform throttle (fallback to len(agents))
        throttle = get_platform_throttle_manager().get_status() or {}
        max_concurrency = min(len(self.agents), int(throttle.get("max_concurrency", len(self.agents))))
        timeout_per_agent = float(throttle.get("per_request_timeout_s", 45.0))  # Increased timeout
        overall_timeout = float(throttle.get("overall_timeout_s", 120.0))  # Increased overall timeout

        sem = asyncio.Semaphore(max_concurrency)

        async def guarded(agent_name: str, agent: Agent):
            async with sem:
                return await asyncio.wait_for(
                    self._invoke_agent_async(agent_name, agent, query, timeout_per_agent),
                    timeout=timeout_per_agent
                )

        # Fire all tasks concurrently
        tasks = [asyncio.create_task(guarded(name, agent)) for name, agent in self.agents.items()]
        try:
            # If you want early-stop on quorum, flip this flag to True
            early_stop = False
            if not early_stop:
                results: List[Dict[str, Any]] = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=False),
                                                                       timeout=overall_timeout)
            else:
                results = []
                done, pending = await asyncio.wait(tasks, timeout=overall_timeout, return_when=asyncio.FIRST_COMPLETED)
                results.extend([t.result() for t in done if not t.cancelled() and not t.exception()])

                # simple quorum: if 3+ agree on same non-general category, cancel the rest
                counts = {}
                for r in results:
                    c = r["classification"]
                    if c != "general_query":
                        counts[c] = counts.get(c, 0) + 1
                winner, votes = (None, 0)
                if counts:
                    winner, votes = max(counts.items(), key=lambda kv: kv[1])

                if winner and votes >= 3:
                    for p in pending: p.cancel()
                    # also collect any already finished pending (rare)
                    for p in pending:
                        try:
                            if not p.cancelled():
                                results.append(await p)
                        except asyncio.CancelledError:
                            pass
                else:
                    # no quorum: wait for all (within overall timeout)
                    more_done, more_pending = await asyncio.wait(pending, timeout=max(0.0, overall_timeout - (time.time() - start_time)))
                    results.extend([t.result() for t in more_done if not t.cancelled() and not t.exception()])
                    for p in more_pending: p.cancel()

        except asyncio.TimeoutError:
            self.logger.warning("⏰ Overall timeout reached; using completed agent results only")
            results = []
            for t in tasks:
                if t.done() and not t.cancelled():
                    try:
                        result = t.result()
                        if result:
                            results.append(result)
                    except Exception as e:
                        self.logger.warning(f"Task result failed: {e}")

        # Fold list to your expected dict form
        specialist_results = {r["agent"]: r for r in results}

        # Build consensus using your existing method
        consensus = self._build_competitive_consensus(specialist_results)

        exec_time = time.time() - start_time
        final = IntentClassification(
            primary_intent=IntentCategory(consensus["primary_intent"]),
            confidence=consensus["confidence"],
            entities=consensus.get("entities", []),
            objectives=consensus.get("objectives", []),
            reasoning=consensus["reasoning"],
            swarm_agreement=consensus["agreement_score"],
            classification_metadata={
                "specialist_consensus": specialist_results,
                "execution_time": exec_time,
                "parallel_method": "asyncio_gather",
                "version": "v4",
                "agents_used": len(specialist_results)
            }
        )
        with self._cache_lock:
            self._cache[cache_key] = final
        self.logger.info(f"✅ Parallel intent classification completed in {exec_time:.1f}s with {len(specialist_results)} agents")
        return final

    def classify_intent(self, query: str) -> IntentClassification:
        """Sync wrapper so your external API stays the same."""
        try:
            return asyncio.run(self._classify_intent_async(query))
        except RuntimeError:
            # If already inside an event loop (e.g., FastAPI/Notebook), reuse it
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._classify_intent_async(query))

    def _build_competitive_consensus(self, specialist_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Build competitive consensus with succinct reasoning"""
        # Filter out NOT_MY_DOMAIN responses
        valid_results = {
            name: data for name, data in specialist_results.items()
            if data["classification"] != "general_query"
        }
        
        if not valid_results:
            return {
                "primary_intent": "general_query",
                "confidence": 0.0,
                "reasoning": "No valid classifications",
                "agreement_score": 0.0
            }
        
        # Calculate competitive scores (confidence + speed bonus)
        competitive_scores = {}
        for name, data in valid_results.items():
            confidence = data["confidence"]
            speed_bonus = max(0, 0.1 - (data["execution_time"] / 100))  # Speed bonus up to 0.1
            competitive_score = confidence + speed_bonus
            competitive_scores[name] = competitive_score
        
        # Sort by competitive score
        sorted_scores = sorted(
            competitive_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Group by classification
        classifications = {}
        for specialist_name, score in sorted_scores:
            classification = valid_results[specialist_name]["classification"]
            if classification not in classifications:
                classifications[classification] = {
                    "total_score": 0.0,
                    "specialists": [],
                    "avg_confidence": 0.0
                }
            
            classifications[classification]["total_score"] += score
            classifications[classification]["specialists"].append(specialist_name)
        
        # Calculate average confidence for each classification
        for classification, data in classifications.items():
            confidences = [
                valid_results[spec]["confidence"] 
                for spec in data["specialists"]
            ]
            data["avg_confidence"] = sum(confidences) / len(confidences)
        
        # Find winning classification
        winning_classification = max(
            classifications.items(),
            key=lambda x: x[1]["total_score"]
        )
        
        # Calculate agreement score
        total_specialists = len(specialist_results)
        agreeing_specialists = len(winning_classification[1]["specialists"])
        agreement_score = agreeing_specialists / total_specialists
        
        return {
            "primary_intent": winning_classification[0],
            "confidence": winning_classification[1]["avg_confidence"],
            "entities": list(set([
                entity for spec_name in winning_classification[1]["specialists"]
                for entity in valid_results[spec_name]["entities"]
            ])),
            "objectives": list(set([
                obj for spec_name in winning_classification[1]["specialists"]
                for obj in valid_results[spec_name]["objectives"]
            ])),
            "reasoning": f"Competitive consensus: {winning_classification[0]} (score: {winning_classification[1]['total_score']:.2f}, agreement: {agreement_score:.2f})",
            "agreement_score": agreement_score
        }


# Factory function
def create_dcisionai_intent_tool_v4() -> DcisionAI_Intent_Tool_v4:
    """Create DcisionAI Intent Tool v4 with true parallel execution"""
    return DcisionAI_Intent_Tool_v4()
