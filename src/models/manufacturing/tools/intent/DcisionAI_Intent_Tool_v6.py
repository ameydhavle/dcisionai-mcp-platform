#!/usr/bin/env python3
"""
DcisionAI Intent Tool v6 - Single Agent with Combined Specialist Prompts
=======================================================================

- Single agent analyzes query from all 6 specialist perspectives
- No HTTP client connection pooling issues
- Faster and more reliable than parallel execution
- Perfect consensus with all specialist viewpoints
- Maintains the same public API as previous versions

Usage:
    tool = create_dcisionai_intent_tool_v6()
    result = tool.classify_intent("Optimize production schedule with energy constraints")
    print(result)

Dependencies:
    - Python 3.9+
    - strands (your framework providing Agent)
"""

import json
import logging
import re
import time
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
    NOT_MY_DOMAIN = "not_my_domain"
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
        "GENERAL": "general_query",
        "UNKNOWN": "general_query",
        "OTHER": "general_query",
    }
    # Keep NOT_MY_DOMAIN as is, don't convert to general_query
    if c == "NOT_MY_DOMAIN":
        return "not_my_domain"
    return mapping.get(c, c.lower())


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

# ======================= CORE TOOL =======================

class DcisionAI_Intent_Tool_v6:
    """
    Single agent with combined specialist prompts for reliable intent classification.
    Analyzes queries from all 6 specialist perspectives in one call.
    """

    def __init__(self) -> None:
        self.logger = logger
        self._cache: Dict[str, IntentClassification] = {}
        self._cache_lock = threading.Lock()
        self._init_combined_agent()
        self.logger.info("✅ DcisionAI Intent Tool v6: initialized with combined specialist agent")

    def _init_combined_agent(self) -> None:
        """Create a single agent that can analyze from all 6 specialist perspectives."""
        self.combined_agent = Agent(
            name="combined_specialist_agent",
            system_prompt="""You are a comprehensive manufacturing optimization specialist with expertise in all domains.

You will analyze manufacturing queries from 6 different specialist perspectives and provide a consensus classification.

SPECIALIST PERSPECTIVES:

1. OPERATIONS RESEARCH SPECIALIST:
   - Mathematical optimization, linear programming
   - Focus: CAPACITY_PLANNING, COST_OPTIMIZATION, PRODUCTION_SCHEDULING
   - Keywords: "capacity", "resources", "allocate", "planning", "cost", "minimize", "ROI", "budget", "schedule", "optimization"
   - NOT_MY_DOMAIN: quality control, supply chain, environmental, maintenance (unless mathematical optimization is primary)

2. PRODUCTION SYSTEMS SPECIALIST:
   - Production planning, scheduling, manufacturing
   - Focus: PRODUCTION_SCHEDULING, QUALITY_CONTROL, CAPACITY_PLANNING
   - Keywords: "production schedule", "manufacturing schedule", "production planning", "quality", "defects", "inspection"
   - NOT_MY_DOMAIN: supply chain, cost optimization, environmental (unless production planning is primary)

3. SUPPLY CHAIN SPECIALIST:
   - Supply chain, logistics, inventory, procurement
   - Focus: SUPPLY_CHAIN, INVENTORY_OPTIMIZATION, DEMAND_FORECASTING
   - Keywords: "supply chain", "logistics", "procurement", "inventory", "stock", "demand", "forecast"
   - NOT_MY_DOMAIN: production scheduling, quality control, cost optimization (unless supply chain is primary)

4. QUALITY CONTROL SPECIALIST:
   - Quality management, defect prevention, inspection
   - Focus: QUALITY_CONTROL, MAINTENANCE
   - Keywords: "quality", "defects", "inspection", "quality control", "maintenance", "repair", "equipment"
   - NOT_MY_DOMAIN: production scheduling, supply chain, cost optimization (unless quality is primary)

5. SUSTAINABILITY SPECIALIST:
   - Environmental optimization, green manufacturing, sustainability
   - Focus: ENVIRONMENTAL_OPTIMIZATION
   - Keywords: "environmental", "sustainability", "green", "carbon", "emissions"
   - NOT_MY_DOMAIN: production scheduling, supply chain, quality control, cost optimization (unless environmental is primary)

6. COST OPTIMIZATION SPECIALIST:
   - Cost reduction, financial optimization, ROI analysis
   - Focus: COST_OPTIMIZATION
   - Keywords: "cost", "minimize", "ROI", "budget", "cost optimization"
   - NOT_MY_DOMAIN: production scheduling, supply chain, quality control, environmental (unless cost optimization is primary)

CLASSIFICATION RULES:
- PRODUCTION_SCHEDULING: "production schedule", "manufacturing schedule", "scheduling optimization"
- CAPACITY_PLANNING: "capacity", "resources", "allocate", "capacity planning"
- INVENTORY_OPTIMIZATION: "inventory", "stock", "inventory optimization"
- QUALITY_CONTROL: "quality", "defects", "inspection", "quality control"
- SUPPLY_CHAIN: "supply chain", "logistics", "procurement", "supply chain optimization"
- MAINTENANCE: "maintenance", "repair", "equipment", "preventive maintenance"
- COST_OPTIMIZATION: "cost", "minimize", "ROI", "budget", "cost optimization"
- DEMAND_FORECASTING: "demand", "forecast", "demand forecasting"
- ENVIRONMENTAL_OPTIMIZATION: "environmental", "sustainability", "green", "carbon", "emissions"
- NOT_MY_DOMAIN: when the query does NOT fall within your specific expertise area
- GENERAL_QUERY: anything not matching the above categories

TASK:
Analyze the given manufacturing query from all 6 perspectives and provide:
1. Individual classifications from each specialist perspective
2. A consensus classification based on majority agreement
3. Confidence scores and reasoning

IMPORTANT: If a specialist's classification is "NOT_MY_DOMAIN", their confidence MUST be 0.0

RESPONSE FORMAT (JSON only):
{
  "specialist_analysis": {
    "ops_research": {"classification": "CLASS", "confidence": 0.85, "reasoning": "..."},
    "production_systems": {"classification": "CLASS", "confidence": 0.85, "reasoning": "..."},
    "supply_chain": {"classification": "CLASS", "confidence": 0.85, "reasoning": "..."},
    "quality": {"classification": "CLASS", "confidence": 0.85, "reasoning": "..."},
    "sustainability": {"classification": "CLASS", "confidence": 0.85, "reasoning": "..."},
    "cost_optimization": {"classification": "CLASS", "confidence": 0.85, "reasoning": "..."}
  },
  "consensus": {
    "primary_intent": "CLASS",
    "confidence": 0.85,
    "entities": ["entity1", "entity2"],
    "objectives": ["objective1", "objective2"],
    "reasoning": "Consensus explanation",
    "agreement_score": 0.83
  }
}"""
        )

    def classify_intent(self, query: str) -> IntentClassification:
        """
        Classify manufacturing intent using single agent with combined specialist analysis.
        """
        start_time = time.time()

        # Cache check
        cache_key = hashlib.md5(query.encode()).hexdigest()
        with self._cache_lock:
            if cache_key in self._cache:
                self.logger.info("🧠 Using cached classification")
                return self._cache[cache_key]

        self.logger.info("🚀 Starting combined specialist analysis")

        try:
            # Single call to the combined agent
            prompt = f"Analyze this manufacturing query from all 6 specialist perspectives: {query}"
            response = self.combined_agent(prompt)
            response_text = getattr(response, "content", None) or str(response)

            # Parse the response
            result_data = _extract_json(response_text)
            if not result_data or not isinstance(result_data, dict):
                raise ValueError(f"Invalid JSON response: {response_text[:200]}...")

            # Extract specialist analysis and consensus
            specialist_analysis = result_data.get("specialist_analysis", {})
            consensus_data = result_data.get("consensus", {})

            # Process specialist results
            specialist_results = {}
            successful_specialists = 0
            
            for spec_name, spec_result in specialist_analysis.items():
                if isinstance(spec_result, dict):
                    classification = _norm_class(spec_result.get("classification", "general_query"))
                    confidence = float(spec_result.get("confidence", 0.0))
                    
                    # Set confidence to 0 for general_query
                    if classification == "general_query":
                        confidence = 0.0
                    
                    specialist_results[spec_name] = {
                        "agent": spec_name,
                        "classification": classification,
                        "confidence": confidence,
                        "entities": spec_result.get("entities", []),
                        "objectives": spec_result.get("objectives", []),
                        "reasoning": (spec_result.get("reasoning", "") or "")[:160],
                        "execution_time": 0.0,  # Single call, so no individual timing
                        "success": True
                    }
                    successful_specialists += 1

            # Build consensus result
            primary_intent = _norm_class(consensus_data.get("primary_intent", "general_query"))
            confidence = float(consensus_data.get("confidence", 0.0))
            entities = consensus_data.get("entities", [])
            objectives = consensus_data.get("objectives", [])
            reasoning = consensus_data.get("reasoning", "")
            agreement_score = float(consensus_data.get("agreement_score", 0.0))

            exec_time = time.time() - start_time

            final = IntentClassification(
                primary_intent=IntentCategory(primary_intent),
                confidence=confidence,
                entities=entities,
                objectives=objectives,
                reasoning=reasoning,
                swarm_agreement=agreement_score,
                classification_metadata={
                    "specialist_consensus": specialist_results,
                    "execution_time": exec_time,
                    "parallel_method": "single_agent_combined",
                    "version": "v6",
                    "agents_used": successful_specialists,
                    "timestamp": _now_iso(),
                }
            )

            # Cache the result
            with self._cache_lock:
                self._cache[cache_key] = final

            self.logger.info(f"✅ Combined specialist analysis completed in {exec_time:.2f}s with {successful_specialists} specialists")
            return final

        except Exception as e:
            exec_time = time.time() - start_time
            self.logger.error(f"❌ Combined specialist analysis failed after {exec_time:.2f}s: {e}")
            
            # Return fallback result
            fallback = IntentClassification(
                primary_intent=IntentCategory("general_query"),
                confidence=0.0,
                entities=[],
                objectives=[],
                reasoning=f"Analysis failed: {e}",
                swarm_agreement=0.0,
                classification_metadata={
                    "specialist_consensus": {},
                    "execution_time": exec_time,
                    "parallel_method": "single_agent_combined",
                    "version": "v6",
                    "agents_used": 0,
                    "timestamp": _now_iso(),
                    "error": str(e)
                }
            )
            return fallback

# ------------------------ FACTORY ------------------------

def create_dcisionai_intent_tool_v6() -> DcisionAI_Intent_Tool_v6:
    return DcisionAI_Intent_Tool_v6()

# ------------------------ DEMO ------------------------

if __name__ == "__main__":
    # Example usage
    tool = create_dcisionai_intent_tool_v6()
    query = "We need to minimize production cost while meeting demand; what capacity should we allocate per line?"
    res = tool.classify_intent(query)
    print(f"Result: {res.primary_intent} (confidence: {res.confidence})")
    print(f"Agreement score: {res.swarm_agreement}")
    print(f"Agents used: {res.classification_metadata.get('agents_used', 0)}")
    print(f"Execution time: {res.classification_metadata.get('execution_time', 0):.2f}s")
