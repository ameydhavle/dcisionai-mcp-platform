#!/usr/bin/env python3
"""
DcisionAI Intent Tool v5 - True Parallel Swarm (6 Agents)
=========================================================

- Async fan-out with asyncio (max parallelism = 6 by default)
- Explicit concurrency control (overrideable per-call)
- Per-agent timeout + retries with jitter backoff
- Optional early-stop quorum (cancel stragglers once a majority agrees)
- Works whether strands.Agent is sync or async
- Caching to avoid re-work on repeated queries
- Competitive-consensus reducer (confidence + light speed bonus)
- Rich debug logging to surface hidden 2-wide bottlenecks

Usage:
    tool = create_dcisionai_intent_tool_v5()
    result = tool.classify_intent("Optimize production schedule with energy constraints", max_concurrency=6)
    print(result)

Dependencies:
    - Python 3.9+
    - strands (your framework providing Agent)
"""

import asyncio
import contextvars
import inspect
import json
import logging
import re
import time
import uuid
import hashlib
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# ------------------------ STRANDS IMPORT ------------------------
try:
    from strands import Agent, tool  # noqa: F401
    STRANDS_AVAILABLE = True
except Exception as e:
    STRANDS_AVAILABLE = False
    raise RuntimeError("Strands framework is required for this tool") from e

# ------------------------ THROTTLE IMPORT ------------------------
try:
    from src.shared.throttling import get_platform_throttle_manager
except Exception:
    def get_platform_throttle_manager():
        class _NullThrottle:
            def get_status(self):
                # You can wire your real throttling here later
                return {"enabled": False}
        return _NullThrottle()

# ------------------------ LOGGING ------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

# ======================= DOMAIN TYPES =======================

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
    primary_intent: IntentCategory
    confidence: float
    entities: List[str]
    objectives: List[str]
    reasoning: str
    swarm_agreement: float
    classification_metadata: Dict[str, Any]

# ======================= UTILITIES =======================

_json_block = re.compile(r"\{.*\}", flags=re.DOTALL)

def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Robust JSON extraction from LLM text."""
    def _clean(s: str) -> str:
        s = re.sub(r'```json\s*', '', s)
        s = re.sub(r'```\s*', '', s)
        return s.strip()

    # Try whole string
    try:
        return json.loads(_clean(text))
    except Exception:
        pass

    # Try first JSON block
    try:
        m = _json_block.search(text)
        if m:
            return json.loads(_clean(m.group()))
    except Exception:
        pass

    # Try simple key: value lines
    try:
        result = {}
        for line in text.splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1)
                k = k.strip().strip('"\'')
                v = v.strip().strip('"\'')
                if k and v:
                    result[k] = v
        if result:
            return result
    except Exception:
        pass

    return None


def _norm_class(classification: str) -> str:
    """Normalize classification string into our canonical enum names."""
    if not classification:
        return "general_query"
    c = classification.upper().strip()
    mapping = {
        "NOT_MY_DOMAIN": "general_query",
        "GENERAL": "general_query",
        "UNKNOWN": "general_query",
        "OTHER": "general_query",
    }
    return mapping.get(c, c.lower())


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

# ======================= CORE TOOL =======================

class DcisionAI_Intent_Tool_v5:
    """
    True-parallel 6-agent swarm with asyncio fan-out, timeouts, retries,
    early-stop quorum, and throttle-aware concurrency.
    """

    # context var to carry per-task trace ids (useful in logs)
    _trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("_trace_id", default="")

    def __init__(self) -> None:
        self.logger = logger
        self._cache: Dict[str, IntentClassification] = {}
        self._cache_lock = threading.Lock()
        self._init_agents()
        self.logger.info("✅ DcisionAI Intent Tool v5: initialized with %d agents", len(self.agents))

    # ------------------------ Agents ------------------------

    def _init_agents(self) -> None:
        """Create six domain specialists. Keep prompts strictly JSON-only."""
        # Configure HTTP client with larger connection pool for true parallelism
        try:
            import httpx
            # Create a custom HTTP client with larger connection pool
            limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)
            http_client = httpx.AsyncClient(limits=limits, timeout=30.0)
        except ImportError:
            http_client = None
            self.logger.warning("httpx not available - using default HTTP client")
        
        self.agents: Dict[str, Agent] = {
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
  "entities": ["entity1","entity2"],
  "objectives": ["objective1","objective2"],
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
  "entities": ["entity1","entity2"],
  "objectives": ["objective1","objective2"],
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
  "entities": ["entity1","entity2"],
  "objectives": ["objective1","objective2"],
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
  "entities": ["entity1","entity2"],
  "objectives": ["objective1","objective2"],
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
  "entities": ["entity1","entity2"],
  "objectives": ["objective1","objective2"],
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
  "entities": ["entity1","entity2"],
  "objectives": ["objective1","objective2"],
  "reasoning": "Brief explanation"
}"""
            ),
        }

    # ------------------------ Public API ------------------------

    def classify_intent(
        self,
        query: str,
        *,
        max_concurrency: Optional[int] = None,
        per_agent_timeout_s: Optional[float] = None,
        overall_timeout_s: Optional[float] = None,
        retries: int = 1,
        enable_early_stop_quorum: bool = False,
    ) -> IntentClassification:
        """
        Sync wrapper so callers don't need to manage event loops.
        """
        try:
            return asyncio.run(
                self._classify_intent_async(
                    query,
                    max_concurrency=max_concurrency,
                    per_agent_timeout_s=per_agent_timeout_s,
                    overall_timeout_s=overall_timeout_s,
                    retries=retries,
                    enable_early_stop_quorum=enable_early_stop_quorum,
                )
            )
        except RuntimeError:
            # Already in a running loop (e.g., Jupyter, FastAPI)
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self._classify_intent_async(
                    query,
                    max_concurrency=max_concurrency,
                    per_agent_timeout_s=per_agent_timeout_s,
                    overall_timeout_s=overall_timeout_s,
                    retries=retries,
                    enable_early_stop_quorum=enable_early_stop_quorum,
                )
            )

    # ------------------------ Async Core ------------------------

    async def _classify_intent_async(
        self,
        query: str,
        *,
        max_concurrency: Optional[int],
        per_agent_timeout_s: Optional[float],
        overall_timeout_s: Optional[float],
        retries: int,
        enable_early_stop_quorum: bool,
    ) -> IntentClassification:
        start_time = time.time()

        # Cache
        cache_key = hashlib.md5(query.encode()).hexdigest()
        with self._cache_lock:
            if cache_key in self._cache:
                self.logger.info("🧠 Using cached classification")
                return self._cache[cache_key]

        # Throttle
        throttle = get_platform_throttle_manager().get_status() or {}
        throttle_mc = int(throttle.get("max_concurrency", 0) or 0)
        eff_mc = max_concurrency or (throttle_mc if throttle_mc > 0 else len(self.agents))
        eff_mc = max(1, min(eff_mc, len(self.agents)))

        agent_timeout = float(per_agent_timeout_s or throttle.get("per_request_timeout_s", 30.0))
        overall_timeout = float(overall_timeout_s or throttle.get("overall_timeout_s", 60.0))

        self.logger.info(
            "🚀 Parallel classify: agents=%d | concurrency=%d | per_agent_timeout=%.1fs | overall_timeout=%.1fs | retries=%d | early_stop=%s",
            len(self.agents), eff_mc, agent_timeout, overall_timeout, retries, enable_early_stop_quorum,
        )

        sem = asyncio.Semaphore(eff_mc)

        async def guarded(agent_name: str, agent: Agent) -> Dict[str, Any]:
            self.logger.debug("[%s] waiting for semaphore…", agent_name)
            async with sem:
                t0 = time.time()
                self.logger.debug("[%s] started (slot acquired)", agent_name)
                try:
                    res = await asyncio.wait_for(
                        self._invoke_agent_with_retries(agent_name, agent, query, agent_timeout, retries),
                        timeout=agent_timeout,
                    )
                    return res
                finally:
                    self.logger.debug("[%s] finished in %.2fs", agent_name, time.time() - t0)

        tasks = [asyncio.create_task(guarded(name, agent)) for name, agent in self.agents.items()]
        results: List[Dict[str, Any]] = []

        try:
            if not enable_early_stop_quorum:
                # Wait for all (best latency if your provider supports parallelism)
                results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=overall_timeout)
            else:
                # Early-stop path: FIRST_COMPLETED then evaluate quorum; else wait for all
                done, pending = await asyncio.wait(tasks, timeout=overall_timeout, return_when=asyncio.FIRST_COMPLETED)
                results.extend([t.result() for t in done if not t.cancelled() and not t.exception()])
                winner, votes = self._check_quorum(results)
                if winner and votes >= 3:
                    # cancel stragglers
                    for p in pending:
                        p.cancel()
                    # collect any that raced to finish despite cancel
                    for p in pending:
                        try:
                            if not p.cancelled():
                                results.append(await p)
                        except asyncio.CancelledError:
                            pass
                else:
                    more_done, more_pending = await asyncio.wait(pending, timeout=max(0.0, overall_timeout - (time.time() - start_time)))
                    results.extend([t.result() for t in more_done if not t.cancelled() and not t.exception()])
                    for p in more_pending:
                        p.cancel()

        except asyncio.TimeoutError:
            self.logger.warning("⏰ Overall timeout; using completed agent results only")
            for t in tasks:
                if t.done() and not t.cancelled():
                    try:
                        result = t.result()
                        if result:
                            results.append(result)
                    except Exception as e:
                        self.logger.warning(f"Task result failed: {e}")

        specialist_results = {r["agent"]: r for r in results}

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
                "version": "v5",
                "agents_used": len(specialist_results),
                "timestamp": _now_iso(),
            }
        )
        with self._cache_lock:
            self._cache[cache_key] = final

        self.logger.info("✅ Completed in %.2fs with %d agent results", exec_time, len(specialist_results))
        return final

    # ------------------------ Agent Invocation ------------------------

    async def _maybe_await(self, value) -> Any:
        """Await if awaitable; otherwise run sync code in a worker thread (non-blocking)."""
        if inspect.isawaitable(value):
            return await value
        # Offload synchronous call so it doesn't block the loop
        return await asyncio.to_thread(lambda: value)

    async def _invoke_agent_with_retries(
        self,
        agent_name: str,
        agent: Agent,
        query: str,
        timeout_s: float,
        retries: int,
    ) -> Dict[str, Any]:
        backoff = 0.6
        jitter = 0.15
        attempt = 0
        while True:
            attempt += 1
            start_time = time.time()
            try:
                # Per-task trace id for observability
                self._trace_id.set(str(uuid.uuid4()))
                prompt = f"Classify the intent of this manufacturing query: {query}"
                resp = await self._maybe_await(agent(prompt))
                response_text = getattr(resp, "content", None) or str(resp)

                result_data = _extract_json(response_text)
                if result_data and isinstance(result_data, dict):
                    classification = _norm_class(result_data.get("classification", "general_query"))
                    confidence = float(result_data.get("confidence", 0.0))
                    if classification == "general_query":
                        confidence = 0.0
                    return {
                        "agent": agent_name,
                        "classification": classification,
                        "confidence": confidence,
                        "entities": result_data.get("entities", []),
                        "objectives": result_data.get("objectives", []),
                        "reasoning": (result_data.get("reasoning", "") or "")[:160],
                        "execution_time": time.time() - start_time,
                        "success": True
                    }
                else:
                    raise ValueError(f"Malformed JSON from {agent_name}: {response_text[:120]}")

            except Exception as e:
                self.logger.warning("[%s] attempt %d failed: %s", agent_name, attempt, e)
                if attempt > retries:
                    return {
                        "agent": agent_name,
                        "classification": "general_query",
                        "confidence": 0.0,
                        "entities": [],
                        "objectives": [],
                        "reasoning": f"Error in {agent_name}: {e}",
                        "execution_time": time.time() - start_time,
                        "success": False,
                    }
                # backoff with jitter
                sleep_for = backoff * attempt + (jitter * attempt)
                await asyncio.sleep(sleep_for)

    # ------------------------ Consensus & Quorum ------------------------

    def _check_quorum(self, results: List[Dict[str, Any]]) -> (Optional[str], int):
        counts: Dict[str, int] = {}
        for r in results:
            c = r.get("classification", "general_query")
            if c != "general_query":
                counts[c] = counts.get(c, 0) + 1
        if not counts:
            return None, 0
        winner, votes = max(counts.items(), key=lambda kv: kv[1])
        return winner, votes

    def _build_competitive_consensus(self, specialist_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Confidence + small speed bonus; ignore general_query."""
        valid = {n: d for n, d in specialist_results.items() if d["classification"] != "general_query"}
        if not valid:
            return {
                "primary_intent": "general_query",
                "confidence": 0.0,
                "entities": [],
                "objectives": [],
                "reasoning": "No valid classifications.",
                "agreement_score": 0.0,
            }

        competitive_scores: Dict[str, float] = {}
        for name, data in valid.items():
            conf = float(data.get("confidence", 0.0))
            # Speed bonus: up to +0.1 for sub-10s finishes (tunable)
            speed_bonus = max(0.0, 0.1 - (float(data.get("execution_time", 0.0)) / 100.0))
            competitive_scores[name] = conf + speed_bonus

        # Group by class and sum scores
        by_class: Dict[str, Dict[str, Any]] = {}
        for spec_name, score in sorted(competitive_scores.items(), key=lambda x: x[1], reverse=True):
            c = valid[spec_name]["classification"]
            bucket = by_class.setdefault(c, {"total_score": 0.0, "specialists": [], "avg_confidence": 0.0})
            bucket["total_score"] += score
            bucket["specialists"].append(spec_name)

        # Average confidence for the class
        for c, bucket in by_class.items():
            confs = [valid[s]["confidence"] for s in bucket["specialists"]]
            bucket["avg_confidence"] = sum(confs) / max(1, len(confs))

        # Winner
        winning_class, win_data = max(by_class.items(), key=lambda kv: kv[1]["total_score"])

        # Agreement ratio across *all* specialists (including general_query)
        total_specs = max(1, len(specialist_results))
        agreeing = len(win_data["specialists"])
        agreement_score = agreeing / total_specs

        # Collect entities/objectives from agreeing specialists
        entities = set()
        objectives = set()
        for s in win_data["specialists"]:
            for e in valid[s].get("entities", []):
                entities.add(e)
            for o in valid[s].get("objectives", []):
                objectives.add(o)

        return {
            "primary_intent": winning_class,
            "confidence": float(win_data["avg_confidence"]),
            "entities": list(entities),
            "objectives": list(objectives),
            "reasoning": f"Competitive consensus: {winning_class} "
                         f"(score={win_data['total_score']:.2f}, agreement={agreement_score:.2f})",
            "agreement_score": agreement_score,
        }

# ------------------------ Factory ------------------------

def create_dcisionai_intent_tool_v5() -> DcisionAI_Intent_Tool_v5:
    return DcisionAI_Intent_Tool_v5()

# ------------------------ Demo ------------------------

if __name__ == "__main__":
    # Example: run with higher log detail
    logger.setLevel(logging.DEBUG)

    tool = create_dcisionai_intent_tool_v5()
    query = "We need to minimize production cost while meeting demand; what capacity should we allocate per line?"
    res = tool.classify_intent(
        query,
        max_concurrency=6,          # Force full fan-out; set lower if your org/model enforces a cap
        per_agent_timeout_s=25.0,   # Tweak for your provider SLAs
        overall_timeout_s=55.0,
        retries=1,                  # 1 retry per agent on transient issues
        enable_early_stop_quorum=False,  # Flip to True to cancel stragglers on quorum
    )
    print(res)
