#!/usr/bin/env python3
"""
DcisionAI Intent Tool v3 - Succinct Responses
=============================================

Optimized for speed AND brevity. Reduces verbose outputs while maintaining accuracy.
Focuses on essential classification information only.

Version: 3.0
Changes: Succinct responses, minimal verbosity, essential classification only

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import time
import hashlib
import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
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


@dataclass
class SwarmPerformanceMetrics:
    """Performance metrics for swarm execution"""
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
    except Exception:
        pass

    # Strategy 2: find JSON blocks
    try:
        start = text.find('{')
        if start != -1:
            brace_count = 0
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        block = text[start:i+1]
                        return json.loads(_clean(block))
    except Exception:
        pass

    # Strategy 3: light repairs
    try:
        s = _clean(text)
        s = re.sub(r',\s*}', '}', s)
        s = re.sub(r',\s*]', ']', s)
        s = re.sub(r'([{\s,])([A-Za-z0-9_]+)\s*:', r'\1"\2":', s)
        return json.loads(s)
    except Exception:
        pass
    return None


def _norm_class(label: str) -> str:
    """Normalize classification label"""
    label = (label or "").strip().upper()
    if label in {"NOT_MY_DOMAIN", "OTHER", "UNKNOWN"}:
        return "GENERAL_QUERY"
    return label


def _intent_to_enum(label: str) -> IntentCategory:
    """Convert label to enum"""
    try:
        return IntentCategory(label.lower())
    except Exception:
        return IntentCategory.GENERAL_QUERY


def _hash(s: str) -> str:
    """Generate hash for tracking"""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    """Get current time in ISO format"""
    return datetime.utcnow().isoformat() + "Z"


# ==================== SUCCINCT SPECIALIST AGENTS ====================

@tool
def succinct_ops_research_classifier(query: str) -> str:
    """Succinct Operations Research specialist"""
    agent = Agent(
        name="succinct_ops_research_specialist",
        system_prompt="""You are a SUCCINCT Operations Research specialist.

EXPERTISE: Mathematical optimization, linear programming
FOCUS: CAPACITY_PLANNING, COST_OPTIMIZATION, PRODUCTION_SCHEDULING

SUCCINCT RULES:
- CAPACITY_PLANNING: "capacity", "resources", "allocate"
- COST_OPTIMIZATION: "cost", "minimize", "ROI"
- PRODUCTION_SCHEDULING: "schedule" + "optimization"
- NOT_MY_DOMAIN: quality, supply chain, environmental

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only, minimal):
{
    "classification": "CAPACITY_PLANNING|COST_OPTIMIZATION|PRODUCTION_SCHEDULING|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
    )
    
    response = agent(f"Classify: {query}")
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    parsed = _extract_json(response_text)
    if parsed and isinstance(parsed, dict):
        return json.dumps(parsed, separators=(",", ":"))
    
    return json.dumps({
        "classification": "NOT_MY_DOMAIN",
        "confidence": 0.0,
        "entities": [],
        "objectives": [],
        "reasoning": "Failed to parse"
    }, separators=(",", ":"))


@tool
def succinct_production_systems_classifier(query: str) -> str:
    """Succinct Production Systems specialist"""
    agent = Agent(
        name="succinct_production_systems_specialist",
        system_prompt="""You are a SUCCINCT Production Systems specialist.

EXPERTISE: Production planning, scheduling, manufacturing
FOCUS: PRODUCTION_SCHEDULING, QUALITY_CONTROL, CAPACITY_PLANNING

SUCCINCT RULES:
- PRODUCTION_SCHEDULING: "production schedule", "manufacturing schedule"
- QUALITY_CONTROL: "quality", "defects", "inspection"
- CAPACITY_PLANNING: "production capacity", "throughput"
- NOT_MY_DOMAIN: supply chain, cost optimization, environmental

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only, minimal):
{
    "classification": "PRODUCTION_SCHEDULING|QUALITY_CONTROL|CAPACITY_PLANNING|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
    )
    
    response = agent(f"Classify: {query}")
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    parsed = _extract_json(response_text)
    if parsed and isinstance(parsed, dict):
        return json.dumps(parsed, separators=(",", ":"))
    
    return json.dumps({
        "classification": "NOT_MY_DOMAIN",
        "confidence": 0.0,
        "entities": [],
        "objectives": [],
        "reasoning": "Failed to parse"
    }, separators=(",", ":"))


@tool
def succinct_supply_chain_classifier(query: str) -> str:
    """Succinct Supply Chain specialist"""
    agent = Agent(
        name="succinct_supply_chain_specialist",
        system_prompt="""You are a SUCCINCT Supply Chain specialist.

EXPERTISE: Supply chain, logistics, inventory, procurement
FOCUS: SUPPLY_CHAIN, INVENTORY_OPTIMIZATION, DEMAND_FORECASTING

SUCCINCT RULES:
- SUPPLY_CHAIN: "supply chain", "logistics", "procurement"
- INVENTORY_OPTIMIZATION: "inventory", "stock", "warehouse"
- DEMAND_FORECASTING: "demand forecast", "sales forecast"
- NOT_MY_DOMAIN: production scheduling, quality control, cost optimization

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only, minimal):
{
    "classification": "SUPPLY_CHAIN|INVENTORY_OPTIMIZATION|DEMAND_FORECASTING|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
    )
    
    response = agent(f"Classify: {query}")
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    parsed = _extract_json(response_text)
    if parsed and isinstance(parsed, dict):
        return json.dumps(parsed, separators=(",", ":"))
    
    return json.dumps({
        "classification": "NOT_MY_DOMAIN",
        "confidence": 0.0,
        "entities": [],
        "objectives": [],
        "reasoning": "Failed to parse"
    }, separators=(",", ":"))


@tool
def succinct_quality_classifier(query: str) -> str:
    """Succinct Quality Control specialist"""
    agent = Agent(
        name="succinct_quality_specialist",
        system_prompt="""You are a SUCCINCT Quality Control specialist.

EXPERTISE: Quality management, defect prevention, inspection
FOCUS: QUALITY_CONTROL, MAINTENANCE

SUCCINCT RULES:
- QUALITY_CONTROL: "quality", "defects", "inspection", "Six Sigma"
- MAINTENANCE: "maintenance", "equipment", "reliability"
- NOT_MY_DOMAIN: supply chain, cost optimization, environmental

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only, minimal):
{
    "classification": "QUALITY_CONTROL|MAINTENANCE|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
    )
    
    response = agent(f"Classify: {query}")
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    parsed = _extract_json(response_text)
    if parsed and isinstance(parsed, dict):
        return json.dumps(parsed, separators=(",", ":"))
    
    return json.dumps({
        "classification": "NOT_MY_DOMAIN",
        "confidence": 0.0,
        "entities": [],
        "objectives": [],
        "reasoning": "Failed to parse"
    }, separators=(",", ":"))


@tool
def succinct_sustainability_classifier(query: str) -> str:
    """Succinct Sustainability specialist"""
    agent = Agent(
        name="succinct_sustainability_specialist",
        system_prompt="""You are a SUCCINCT Sustainability specialist.

EXPERTISE: Environmental optimization, green manufacturing
FOCUS: ENVIRONMENTAL_OPTIMIZATION, COST_OPTIMIZATION

SUCCINCT RULES:
- ENVIRONMENTAL_OPTIMIZATION: "environmental", "sustainability", "green"
- COST_OPTIMIZATION: "energy costs", "environmental costs"
- NOT_MY_DOMAIN: quality control, supply chain, general management

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only, minimal):
{
    "classification": "ENVIRONMENTAL_OPTIMIZATION|COST_OPTIMIZATION|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
    )
    
    response = agent(f"Classify: {query}")
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    parsed = _extract_json(response_text)
    if parsed and isinstance(parsed, dict):
        return json.dumps(parsed, separators=(",", ":"))
    
    return json.dumps({
        "classification": "NOT_MY_DOMAIN",
        "confidence": 0.0,
        "entities": [],
        "objectives": [],
        "reasoning": "Failed to parse"
    }, separators=(",", ":"))


@tool
def succinct_cost_optimization_classifier(query: str) -> str:
    """Succinct Cost Optimization specialist"""
    agent = Agent(
        name="succinct_cost_optimization_specialist",
        system_prompt="""You are a SUCCINCT Cost Optimization specialist.

EXPERTISE: Cost reduction, financial optimization, ROI analysis
FOCUS: COST_OPTIMIZATION, DEMAND_FORECASTING, CAPACITY_PLANNING

SUCCINCT RULES:
- COST_OPTIMIZATION: "minimize costs", "cost reduction", "ROI"
- DEMAND_FORECASTING: "demand forecast", "sales forecast"
- CAPACITY_PLANNING: "capacity" + "cost" context
- NOT_MY_DOMAIN: quality control, supply chain, environmental

IMPORTANT: If classification is "NOT_MY_DOMAIN", confidence MUST be 0.0

RESPONSE FORMAT (JSON only, minimal):
{
    "classification": "COST_OPTIMIZATION|DEMAND_FORECASTING|CAPACITY_PLANNING|NOT_MY_DOMAIN",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Brief explanation"
}"""
    )
    
    response = agent(f"Classify: {query}")
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    parsed = _extract_json(response_text)
    if parsed and isinstance(parsed, dict):
        return json.dumps(parsed, separators=(",", ":"))
    
    return json.dumps({
        "classification": "NOT_MY_DOMAIN",
        "confidence": 0.0,
        "entities": [],
        "objectives": [],
        "reasoning": "Failed to parse"
    }, separators=(",", ":"))


# ==================== MAIN TOOL WITH SUCCINCT OUTPUT ====================

class DcisionAI_Intent_Tool_v3:
    """Intent classifier with succinct responses"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.IntentTool_v3")
        self.throttle_manager = get_platform_throttle_manager()
        self._cache = {}
        self._cache_lock = threading.Lock()
        
        # Performance tracking
        self.perf = SwarmPerformanceMetrics(
            total_agents=6,
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

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        key_terms = ["schedule", "capacity", "cost", "optimize", "carbon", "environmental", "quality", "maintenance"]
        query_lower = query.lower()
        term_matches = [term for term in key_terms if term in query_lower]
        return f"{len(query)}_{'_'.join(sorted(term_matches))}"

    def _execute_specialists_parallel(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Execute all specialists in parallel with succinct output"""
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            # Submit all specialist tasks
            future_to_specialist = {
                executor.submit(succinct_ops_research_classifier, query): "ops_research",
                executor.submit(succinct_production_systems_classifier, query): "production_systems",
                executor.submit(succinct_supply_chain_classifier, query): "supply_chain",
                executor.submit(succinct_quality_classifier, query): "quality",
                executor.submit(succinct_sustainability_classifier, query): "sustainability",
                executor.submit(succinct_cost_optimization_classifier, query): "cost_optimization"
            }
            
            specialist_results = {}
            
            # Collect results as they complete
            for future in as_completed(future_to_specialist, timeout=300):
                specialist_name = future_to_specialist[future]
                try:
                    result_text = future.result(timeout=60)
                    result_data = json.loads(result_text)
                    
                    # Extract essential info only
                    classification = _norm_class(result_data.get("classification", "GENERAL_QUERY"))
                    confidence = float(result_data.get("confidence", 0.0))
                    
                    # Ensure NOT_MY_DOMAIN has 0.0 confidence
                    if classification == "GENERAL_QUERY":
                        confidence = 0.0
                    
                    specialist_results[specialist_name] = {
                        "classification": classification,
                        "confidence": confidence,
                        "entities": result_data.get("entities", []),
                        "objectives": result_data.get("objectives", []),
                        "reasoning": result_data.get("reasoning", "")[:100],  # Truncate reasoning
                        "execution_time": time.time() - start_time
                    }
                except Exception as e:
                    self.logger.warning(f"Specialist {specialist_name} failed: {e}")
                    specialist_results[specialist_name] = {
                        "classification": "GENERAL_QUERY",
                        "confidence": 0.0,
                        "entities": [],
                        "objectives": [],
                        "reasoning": f"Error: {str(e)}",
                        "execution_time": time.time() - start_time
                    }
        
        execution_time = time.time() - start_time
        self.logger.info(f"Parallel execution completed in {execution_time:.1f}s")
        
        return specialist_results

    def _build_competitive_consensus(self, specialist_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Build competitive consensus with succinct reasoning"""
        # Filter out NOT_MY_DOMAIN responses
        valid_results = {
            name: data for name, data in specialist_results.items()
            if data["classification"] != "GENERAL_QUERY"
        }
        
        if not valid_results:
            return {
                "primary_intent": "GENERAL_QUERY",
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
        
        # Find winner
        winner_classification = max(classifications.items(), key=lambda x: x[1]["total_score"])[0]
        winner_data = classifications[winner_classification]
        
        # Calculate final confidence
        confidences = [valid_results[name]["confidence"] for name in winner_data["specialists"]]
        final_confidence = sum(confidences) / len(confidences)
        
        # Build succinct reasoning
        top_specialist = sorted_scores[0][0]
        reasoning = f"{winner_classification} (top: {top_specialist}, conf: {final_confidence:.2f})"
        
        return {
            "primary_intent": winner_classification,
            "confidence": final_confidence,
            "reasoning": reasoning,
            "agreement_score": len(winner_data["specialists"]) / len(valid_results)
        }

    def classify_intent(self, query: str, domain: str = "manufacturing") -> IntentClassification:
        """Classify intent with succinct output"""
        t0 = time.perf_counter()
        run_id = uuid.uuid4().hex
        input_hash = _hash(query)

        # Check cache
        cache_key = self._get_cache_key(query)
        with self._cache_lock:
            if cache_key in self._cache:
                self.logger.info("Using cached result")
                return self._cache[cache_key]

        try:
            self.perf.swarm_status = "running"
            self.perf.active_agents = 6

            # Execute specialists in parallel
            specialist_results = self._execute_specialists_parallel(query)
            
            # Build competitive consensus
            consensus = self._build_competitive_consensus(specialist_results)

            elapsed = time.perf_counter() - t0
            self.perf.execution_time = elapsed
            self.perf.worker_responses = len(specialist_results)
            self.perf.consensus_achieved = True
            self.perf.agreement_score = consensus.get("agreement_score", consensus.get("confidence", 0.0))
            self.perf.swarm_status = "completed"
            self.perf.handoffs_performed = len(specialist_results)

            # Build minimal metadata
            meta = {
                "run_id": run_id,
                "input_hash": input_hash,
                "latency_ms": int(elapsed * 1000),
                "env": {"mode": "succinct_parallel"},
                "version": "v3_succinct"
            }

            result = IntentClassification(
                primary_intent=_intent_to_enum(consensus["primary_intent"]),
                confidence=float(consensus["confidence"]),
                entities=[],
                objectives=[],
                reasoning=str(consensus.get("reasoning", "")),
                swarm_agreement=float(consensus.get("agreement_score", consensus["confidence"])),
                classification_metadata=meta
            )

            # Cache result
            with self._cache_lock:
                self._cache[cache_key] = result

            return result

        except Exception as e:
            elapsed = time.perf_counter() - t0
            self.perf.swarm_status = "error"
            self.logger.exception("Intent classification failed")
            return IntentClassification(
                primary_intent=IntentCategory.GENERAL_QUERY,
                confidence=0.0,
                entities=[],
                objectives=[],
                reasoning=f"Error: {e}",
                swarm_agreement=0.0,
                classification_metadata={
                    "run_id": run_id,
                    "input_hash": input_hash,
                    "latency_ms": int(elapsed*1000),
                    "error": str(e),
                    "version": "v3_succinct"
                }
            )

    def get_performance_metrics(self) -> SwarmPerformanceMetrics:
        return self.perf


# Factory
def create_dcisionai_intent_tool_v3() -> DcisionAI_Intent_Tool_v3:
    return DcisionAI_Intent_Tool_v3()
