#!/usr/bin/env python3
"""
DcisionAI Data Tool v3 - Succinct Responses
==========================================

Optimized for speed AND brevity. Reduces verbose outputs while maintaining accuracy.
Focuses on essential information only.

Version: 3.0
Changes: Succinct responses, minimal verbosity, essential data only

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import time
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
    logging.error("Strands framework not available - data tool requires Strands")
    raise Exception("Strands framework is required but not available")

# Platform throttling imports
from shared.throttling import get_platform_throttle_manager

logger = logging.getLogger(__name__)


@dataclass
class DataRequirement:
    """Data requirement structure"""
    element: str
    category: str
    priority: str
    data_type: str
    description: str


@dataclass
class ExternalDataRecommendation:
    """External data recommendation structure"""
    source_name: str
    source_type: str
    data_elements: List[str]
    access_method: str
    cost_estimate: str


@dataclass
class DataAnalysisResult:
    """Data analysis result structure"""
    query_data_requirements: List[DataRequirement]
    customer_data_availability: Dict[str, Any]
    external_data_recommendations: List[ExternalDataRecommendation]
    data_gaps: List[str]
    optimization_readiness: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    intent_classification: Optional[Any] = None


# ==================== SUCCINCT WORKER AGENT TOOLS ====================

@tool
def succinct_query_data_extractor(query: str, intent_classification: str = "unknown") -> str:
    """Succinct query data extraction - minimal output."""
    try:
        agent = Agent(
            name="succinct_query_data_extractor",
            system_prompt="""You are a SUCCINCT Data Extraction specialist.

EXPERTISE: Extract essential data requirements from queries
FOCUS: Only critical data elements, minimal descriptions

SUCCINCT RULES:
- DEMAND_DATA: demand, forecasts, orders
- CAPACITY_DATA: capacity, resources, limits  
- COST_DATA: costs, pricing, budgets
- INVENTORY_DATA: stock, inventory, levels
- PRODUCTION_DATA: processing, setup, efficiency
- ENVIRONMENTAL_DATA: carbon, emissions, sustainability

RESPONSE FORMAT (JSON only, minimal):
{
    "data_requirements": [
        {
            "element": "weekly_demand",
            "category": "DEMAND_DATA", 
            "priority": "critical",
            "data_type": "numerical",
            "description": "Weekly demand by product"
        }
    ],
    "optimization_parameters": {
        "objective": "minimize_cost",
        "constraints": ["capacity", "demand"],
        "variables": ["production", "assignment"]
    },
    "completeness": 0.7
}"""
        )
        
        response = agent(f"Extract data requirements: {query}\nIntent: {intent_classification}")
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        try:
            result = json.loads(response_text)
        except:
            result = {
                "data_requirements": [
                    {
                        "element": "processing_times",
                        "category": "PRODUCTION_DATA",
                        "priority": "critical", 
                        "data_type": "numerical",
                        "description": "Processing times per product"
                    }
                ],
                "optimization_parameters": {
                    "objective": "minimize_makespan",
                    "constraints": ["capacity", "deadline"],
                    "variables": ["schedule", "assignment"]
                },
                "completeness": 0.6
            }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Extraction failed: {str(e)}"})


@tool
def succinct_customer_data_analyzer(query: str, intent_classification: str = "unknown") -> str:
    """Succinct customer data analysis - minimal output."""
    try:
        agent = Agent(
            name="succinct_customer_data_analyzer",
            system_prompt="""You are a SUCCINCT Customer Data Analysis specialist.

EXPERTISE: Assess data availability and gaps
FOCUS: Essential coverage info only

SUCCINCT RULES:
- Check automated connectors (limited)
- Assess manual input needs
- Identify critical gaps
- Provide coverage summary

RESPONSE FORMAT (JSON only, minimal):
{
    "coverage": {
        "critical": 0.0,
        "important": 0.0,
        "total": 0.0
    },
    "gaps": [
        {
            "required": "ALL_DATA",
            "connector": "MANUAL_UPLOAD",
            "impact": "high"
        }
    ],
    "status": {
        "connectors_available": false,
        "availability": "ROADMAP_TBD",
        "workaround": "manual_provision"
    },
    "recommendations": [
        "Provide data manually",
        "No automated sources available"
    ]
}"""
        )
        
        response = agent(f"Analyze data coverage: {query}\nIntent: {intent_classification}")
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        try:
            result = json.loads(response_text)
        except:
            result = {
                "coverage": {
                    "critical": 0.0,
                    "important": 0.0,
                    "total": 0.0
                },
                "gaps": [
                    {
                        "required": "ALL_DATA",
                        "connector": "MANUAL_UPLOAD", 
                        "impact": "high"
                    }
                ],
                "status": {
                    "connectors_available": False,
                    "availability": "ROADMAP_TBD",
                    "workaround": "manual_provision"
                },
                "recommendations": [
                    "Provide data manually",
                    "No automated sources available"
                ]
            }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Analysis failed: {str(e)}"})


@tool
def succinct_external_data_recommender(query: str, intent_classification: str = "unknown") -> str:
    """Succinct external data recommendations - minimal output."""
    try:
        agent = Agent(
            name="succinct_external_data_recommender",
            system_prompt="""You are a SUCCINCT External Data Recommendation specialist.

EXPERTISE: Recommend essential external data sources
FOCUS: High-value sources only, minimal details

SUCCINCT RULES:
- PRODUCTION_SCHEDULING: Industry benchmarks, EPA factors
- ENVIRONMENTAL_OPTIMIZATION: Carbon data, sustainability
- COST_OPTIMIZATION: Market data, cost benchmarks
- Focus on free, accessible sources

RESPONSE FORMAT (JSON only, minimal):
{
    "recommendations": [
        {
            "source": "EPA_GHG_Factors",
            "type": "GOVERNMENT",
            "data": ["carbon_factors", "benchmarks"],
            "access": "download",
            "cost": "free"
        }
    ],
    "opportunities": {
        "intent": "PRODUCTION_SCHEDULING",
        "sources": ["benchmarks", "carbon_data"],
        "enhancement": ["processing_optimization", "carbon_reduction"]
    },
    "priority": [
        {
            "source": "EPA_GHG_Factors",
            "priority": "high",
            "reason": "Critical for carbon calculations"
        }
    ]
}"""
        )
        
        response = agent(f"Recommend external sources: {query}\nIntent: {intent_classification}")
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        try:
            result = json.loads(response_text)
        except:
            result = {
                "recommendations": [
                    {
                        "source": "EPA_GHG_Factors",
                        "type": "GOVERNMENT",
                        "data": ["carbon_factors", "benchmarks"],
                        "access": "download",
                        "cost": "free"
                    }
                ],
                "opportunities": {
                    "intent": "PRODUCTION_SCHEDULING",
                    "sources": ["benchmarks", "carbon_data"],
                    "enhancement": ["processing_optimization", "carbon_reduction"]
                },
                "priority": [
                    {
                        "source": "EPA_GHG_Factors",
                        "priority": "high",
                        "reason": "Critical for carbon calculations"
                    }
                ]
            }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Recommendation failed: {str(e)}"})


# ==================== MAIN TOOL WITH SUCCINCT OUTPUT ====================

class DcisionAI_Data_Tool_v3:
    """Data analysis tool with succinct responses"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DataTool_v3")
        self.throttle_manager = get_platform_throttle_manager()
        self._cache = {}
        self._cache_lock = threading.Lock()

    def _get_cache_key(self, query: str, intent_classification: str) -> str:
        """Generate cache key"""
        key_terms = ["schedule", "capacity", "cost", "optimize", "carbon", "environmental", "quality", "maintenance"]
        query_lower = query.lower()
        term_matches = [term for term in key_terms if term in query_lower]
        return f"{len(query)}_{intent_classification}_{'_'.join(sorted(term_matches))}"

    def _execute_stages_parallel(self, query: str, intent_classification: str) -> Dict[str, Any]:
        """Execute all stages in parallel for speed"""
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            future_to_stage = {
                executor.submit(succinct_query_data_extractor, query, intent_classification): "data_extraction",
                executor.submit(succinct_customer_data_analyzer, query, intent_classification): "customer_analysis", 
                executor.submit(succinct_external_data_recommender, query, intent_classification): "external_recommendations"
            }
            
            results = {}
            
            # Collect results as they complete
            for future in as_completed(future_to_stage, timeout=300):
                stage = future_to_stage[future]
                try:
                    stage_result = future.result(timeout=60)
                    results[stage] = json.loads(stage_result)
                except Exception as e:
                    self.logger.warning(f"Stage {stage} failed: {e}")
                    results[stage] = {"error": str(e)}
        
        execution_time = time.time() - start_time
        self.logger.info(f"Parallel execution completed in {execution_time:.1f}s")
        
        return results

    def analyze_data_requirements(self, query: str, intent_classification: str = "unknown") -> DataAnalysisResult:
        """Analyze data requirements with succinct output"""
        t0 = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(query, intent_classification)
        with self._cache_lock:
            if cache_key in self._cache:
                self.logger.info("Using cached result")
                return self._cache[cache_key]
        
        try:
            # Execute all stages in parallel
            stage_results = self._execute_stages_parallel(query, intent_classification)
            
            # Extract data requirements
            data_extraction = stage_results.get("data_extraction", {})
            data_requirements = []
            
            for req in data_extraction.get("data_requirements", []):
                data_requirements.append(DataRequirement(
                    element=req.get("element", ""),
                    category=req.get("category", ""),
                    priority=req.get("priority", ""),
                    data_type=req.get("data_type", ""),
                    description=req.get("description", "")
                ))
            
            # Extract customer data analysis
            customer_analysis = stage_results.get("customer_analysis", {})
            customer_data_availability = {
                "coverage": customer_analysis.get("coverage", {}),
                "gaps": customer_analysis.get("gaps", []),
                "status": customer_analysis.get("status", {}),
                "recommendations": customer_analysis.get("recommendations", [])
            }
            
            # Extract external recommendations
            external_recommendations = stage_results.get("external_recommendations", {})
            external_data = []
            
            for rec in external_recommendations.get("recommendations", []):
                external_data.append(ExternalDataRecommendation(
                    source_name=rec.get("source", ""),
                    source_type=rec.get("type", ""),
                    data_elements=rec.get("data", []),
                    access_method=rec.get("access", ""),
                    cost_estimate=rec.get("cost", "")
                ))
            
            # Identify data gaps
            data_gaps = []
            coverage = customer_analysis.get("coverage", {})
            if coverage.get("total", 0) < 0.5:
                data_gaps.append("Most data must be provided manually")
            if coverage.get("critical", 0) < 0.3:
                data_gaps.append("Critical data sources missing")
            
            # Assess optimization readiness
            optimization_readiness = {
                "data_completeness": data_extraction.get("completeness", 0.0),
                "coverage_score": coverage.get("total", 0.0),
                "external_sources_available": len(external_data) > 0,
                "ready_for_optimization": coverage.get("total", 0.0) > 0.3
            }
            
            # Build execution metadata
            execution_time = time.time() - t0
            execution_metadata = {
                "execution_time": execution_time,
                "stages_completed": len(stage_results),
                "cache_hit": False,
                "parallel_execution": True,
                "version": "v3_succinct"
            }
            
            # Create result
            result = DataAnalysisResult(
                query_data_requirements=data_requirements,
                customer_data_availability=customer_data_availability,
                external_data_recommendations=external_data,
                data_gaps=data_gaps,
                optimization_readiness=optimization_readiness,
                execution_metadata=execution_metadata,
                intent_classification=intent_classification
            )
            
            # Cache result
            with self._cache_lock:
                self._cache[cache_key] = result
            
            return result
            
        except Exception as e:
            execution_time = time.time() - t0
            self.logger.exception("Data analysis failed")
            
            # Return minimal error result
            return DataAnalysisResult(
                query_data_requirements=[],
                customer_data_availability={"error": str(e)},
                external_data_recommendations=[],
                data_gaps=["Analysis failed"],
                optimization_readiness={"ready_for_optimization": False},
                execution_metadata={
                    "execution_time": execution_time,
                    "error": str(e),
                    "version": "v3_succinct"
                },
                intent_classification=intent_classification
            )

    def analyze_data_requirements_with_intent(self, query: str, intent_result, session_id: str = "default") -> DataAnalysisResult:
        """Analyze data requirements with intent result - compatibility method"""
        # Extract intent classification from intent result
        intent_classification = "unknown"
        if hasattr(intent_result, 'primary_intent'):
            intent_classification = intent_result.primary_intent.value
        elif isinstance(intent_result, dict):
            intent_classification = intent_result.get('primary_intent', 'unknown')
        
        # Call the main analysis method
        return self.analyze_data_requirements(query, intent_classification)


# Factory
def create_dcisionai_data_tool_v3() -> DcisionAI_Data_Tool_v3:
    return DcisionAI_Data_Tool_v3()
