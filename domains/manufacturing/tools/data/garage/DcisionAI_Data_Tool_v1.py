#!/usr/bin/env python3
"""
DcisionAI Data Tool v1 - AWS-Style Agent-as-Tool Pattern
=======================================================

Three-stage data analysis for optimization model building:
1. NL Query Data Extraction - Identify required data elements from query
2. Customer Data Source Analysis - Check configured data connectors (roadmap)
3. External Data Source Recommendations - Suggest external data to enhance model

Version: 1.0
Changes: Original implementation with sequential execution and manager-worker pattern

INTEGRATED WITH: Enhanced DcisionAI Intent Tool for intent-aware data analysis

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

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

# Intent Tool Integration
try:
    from ..intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool, IntentClassification
    INTENT_TOOL_AVAILABLE = True
except ImportError:
    INTENT_TOOL_AVAILABLE = False
    logging.warning("Intent tool not available - will use default intent classification")
    # Create a fallback type for IntentClassification
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        IntentClassification = Any
    else:
        IntentClassification = type('IntentClassification', (), {})

logger = logging.getLogger(__name__)

# Model Configuration
CLAUDE_MODEL_ID = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"


class DataCategory(Enum):
    """Data categories for optimization models"""
    DEMAND_DATA = "demand_data"
    CAPACITY_DATA = "capacity_data"
    COST_DATA = "cost_data"
    INVENTORY_DATA = "inventory_data"
    PRODUCTION_DATA = "production_data"
    SUPPLY_CHAIN_DATA = "supply_chain_data"
    QUALITY_DATA = "quality_data"
    ENVIRONMENTAL_DATA = "environmental_data"
    FINANCIAL_DATA = "financial_data"
    EXTERNAL_MARKET_DATA = "external_market_data"


class DataSource(Enum):
    """Data source types"""
    INTERNAL_DATABASE = "internal_database"
    ERP_SYSTEM = "erp_system"
    MANUFACTURING_EXECUTION_SYSTEM = "mes"
    SENSOR_DATA = "sensor_data"
    EXTERNAL_API = "external_api"
    PUBLIC_DATASET = "public_dataset"
    MARKET_DATA_PROVIDER = "market_data_provider"
    GOVERNMENT_DATA = "government_data"
    INDUSTRY_BENCHMARK = "industry_benchmark"


@dataclass
class DataRequirement:
    """Individual data requirement"""
    element: str
    category: DataCategory
    priority: str  # "critical", "important", "optional"
    data_type: str  # "numerical", "categorical", "time_series", "constraint"
    description: str
    examples: List[str]


@dataclass
class DataSourceRecommendation:
    """External data source recommendation"""
    source_name: str
    source_type: DataSource
    data_elements: List[str]
    access_method: str
    cost_estimate: str
    reliability: str
    update_frequency: str
    integration_complexity: str
    business_value: str


@dataclass
class DataAnalysisResult:
    """Complete data analysis result"""
    query_data_requirements: List[DataRequirement]
    customer_data_availability: Dict[str, Any]
    external_data_recommendations: List[DataSourceRecommendation]
    data_gaps: List[str]
    optimization_readiness: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    intent_classification: Optional[IntentClassification] = None


# ==================== WORKER AGENT TOOLS ====================

@tool
def query_data_extractor(query: str, intent_classification: str = "unknown") -> str:
    """Extract data requirements from natural language query."""
    try:
        agent = Agent(
            model=CLAUDE_MODEL_ID,
            name="query_data_extraction_specialist",
            system_prompt="""You are a Data Extraction specialist for manufacturing optimization queries.

EXPERTISE: Analyzing natural language queries to identify required data elements for optimization models
FOCUS: Extract specific data requirements, constraints, and parameters from user queries

EXTRACTION CATEGORIES:
- DEMAND_DATA: Customer demand, sales forecasts, order quantities
- CAPACITY_DATA: Production capacity, line capabilities, resource limits
- COST_DATA: Production costs, material costs, labor costs, overhead
- INVENTORY_DATA: Stock levels, holding costs, safety stock, lead times
- PRODUCTION_DATA: Processing times, setup times, efficiency rates, yields
- SUPPLY_CHAIN_DATA: Supplier data, logistics costs, delivery times
- QUALITY_DATA: Quality metrics, defect rates, compliance requirements
- ENVIRONMENTAL_DATA: Carbon footprint, emissions, sustainability metrics
- FINANCIAL_DATA: Budgets, ROI targets, financial constraints

DATA PRIORITY LEVELS:
- CRITICAL: Essential for model functionality (hard constraints, objectives)
- IMPORTANT: Significantly improves model accuracy
- OPTIONAL: Nice-to-have for enhanced modeling

INTENT-AWARE EXTRACTION:
- Use intent classification to focus on relevant data categories
- PRODUCTION_SCHEDULING: Focus on capacity, demand, processing times
- CAPACITY_PLANNING: Focus on resource limits, demand forecasts, costs
- ENVIRONMENTAL_OPTIMIZATION: Focus on carbon data, sustainability metrics
- COST_OPTIMIZATION: Focus on cost structures, financial constraints
- SUPPLY_CHAIN: Focus on logistics, inventory, supplier data

RESPONSE FORMAT (JSON only):
{
    "data_requirements": [
        {
            "element": "weekly_demand_by_product",
            "category": "DEMAND_DATA",
            "priority": "critical",
            "data_type": "numerical",
            "description": "Weekly demand quantities for each product",
            "examples": ["G1: 100 units/week", "G2: 150 units/week"],
            "extraction_source": "explicitly_stated|implicitly_required|derived_constraint",
            "intent_relevance": "high|medium|low"
        }
    ],
    "optimization_parameters": {
        "objective_function": "maximize_production|minimize_cost|optimize_efficiency",
        "constraints_identified": ["carbon_limit", "demand_requirements", "capacity_constraints"],
        "decision_variables": ["production_quantities", "line_assignments"],
        "time_horizon": "weekly|monthly|daily|unknown"
    },
    "intent_specific_focus": {
        "primary_data_categories": ["DEMAND_DATA", "CAPACITY_DATA"],
        "critical_constraints": ["demand_requirements", "capacity_limits"],
        "optimization_objectives": ["minimize_makespan", "maximize_efficiency"]
    },
    "data_completeness": {
        "critical_data_present": 0.8,
        "important_data_present": 0.6,
        "overall_completeness": 0.7
    },
    "missing_critical_data": ["unit_costs", "capacity_limits"],
    "reasoning": "Clear explanation of what data was extracted and what's missing"
}

CRITICAL: Be thorough in identifying ALL data elements mentioned or implied in the query. Use intent classification to focus extraction."""
        )
        
        prompt = f"""
        Analyze this query for data requirements:
        Query: "{query}"
        Intent Classification: {intent_classification}
        
        Extract all data elements needed for optimization modeling, focusing on intent-relevant categories.
        """
        
        response = agent(prompt)
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "data_requirements": [],
            "optimization_parameters": {},
            "intent_specific_focus": {},
            "data_completeness": {"critical_data_present": 0.0, "important_data_present": 0.0, "overall_completeness": 0.0},
            "missing_critical_data": ["analysis_failed"],
            "reasoning": f"Query data extraction failed: {str(e)}",
            "error": True
        })


@tool
def customer_data_analyzer(data_requirements: str, session_id: str = "default") -> str:
    """Analyze customer's configured data sources and availability."""
    try:
        agent = Agent(
            model=CLAUDE_MODEL_ID,
            name="customer_data_specialist",
            system_prompt="""You are a Customer Data Analysis specialist for DcisionAI platform.

EXPERTISE: Analyzing customer's configured data sources and data availability
FOCUS: Match required data elements with customer's available data connectors

CURRENT STATUS: NO data connectors configured - platform is in early stage
TASK: Provide HONEST assessment of current data availability (which is NONE)

REALITY CHECK:
- NO ERP systems connected
- NO MES systems connected  
- NO database connections configured
- NO automated data feeds available
- ALL data must be manually provided by customer

RESPONSE FORMAT (JSON only):
{
    "customer_data_sources": [],
    "data_coverage_analysis": {
        "critical_data_covered": 0.0,
        "important_data_covered": 0.0,
        "total_coverage": 0.0
    },
    "missing_data_sources": [
        {
            "required_for": "ALL_DATA_REQUIREMENTS",
            "recommended_connector": "MANUAL_DATA_UPLOAD",
            "business_impact": "high"
        }
    ],
    "roadmap_status": {
        "data_connectors_available": false,
        "estimated_availability": "ROADMAP_TBD",
        "current_workaround": "customer_must_provide_all_data_manually"
    },
    "recommendations": [
        "Customer must provide all required data manually",
        "No automated data sources available currently",
        "Data connectors are on future roadmap"
    ],
    "reasoning": "HONEST ASSESSMENT: No data connectors are currently configured. Customer must provide all data manually."
}

CRITICAL: Be completely honest - NO fake data sources or coverage percentages."""
        )
        
        prompt = f"""
        Analyze customer's data sources for these requirements:
        Data Requirements: {data_requirements}
        Session ID: {session_id}
        
        CRITICAL: NO data connectors are configured. Customer must provide ALL data manually.
        """
        
        response = agent(prompt)
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "customer_data_sources": [],
            "data_coverage_analysis": {"critical_data_covered": 0.0, "important_data_covered": 0.0, "total_coverage": 0.0},
            "missing_data_sources": [],
            "roadmap_status": {"data_connectors_available": False, "estimated_availability": "Q2_2025", "current_workaround": "manual_data_upload"},
            "recommendations": [],
            "reasoning": f"Customer data analysis failed: {str(e)}",
            "error": True
        })


@tool
def external_data_recommender(query: str, intent_classification: str, data_gaps: str) -> str:
    """Recommend external data sources to enhance optimization model."""
    try:
        agent = Agent(
            model=CLAUDE_MODEL_ID,
            name="external_data_specialist",
            system_prompt="""You are an External Data Sources specialist for optimization model enhancement.

EXPERTISE: Identifying valuable external data sources to improve optimization models
FOCUS: Recommend specific external datasets, APIs, and data providers

EXTERNAL DATA CATEGORIES:
- MARKET_DATA: Demand trends, price indices, economic indicators
- INDUSTRY_BENCHMARKS: Performance standards, best practices data
- GOVERNMENT_DATA: Regulations, environmental standards, economic data
- WEATHER_DATA: Climate impact on production, logistics
- SUPPLY_CHAIN_DATA: Supplier performance, logistics networks
- COMMODITY_PRICES: Raw material costs, energy prices
- CARBON_DATA: Emission factors, carbon credit prices
- DEMOGRAPHIC_DATA: Population trends, consumer behavior

INTENT-SPECIFIC RECOMMENDATIONS:
- PRODUCTION_SCHEDULING: Market demand data, industry benchmarks, weather data
- CAPACITY_PLANNING: Economic indicators, industry trends, regulatory data
- ENVIRONMENTAL_OPTIMIZATION: Carbon data, emission factors, sustainability benchmarks
- COST_OPTIMIZATION: Commodity prices, market indices, financial data
- SUPPLY_CHAIN: Logistics data, supplier benchmarks, trade data

RECOMMENDATION CRITERIA:
- Business Value: High impact on optimization model performance
- Accessibility: Easy to integrate and obtain
- Cost-Effectiveness: Reasonable cost vs. value
- Reliability: Trustworthy and regularly updated sources
- Integration Complexity: Feasible to implement

RESPONSE FORMAT (JSON only):
{
    "external_data_recommendations": [
        {
            "source_name": "EPA_Carbon_Emission_Factors",
            "source_type": "GOVERNMENT_DATA",
            "data_elements": ["carbon_emission_factors", "industry_benchmarks"],
            "access_method": "API|download|subscription",
            "cost_estimate": "free|low|medium|high",
            "reliability": "high|medium|low",
            "update_frequency": "daily|weekly|monthly|annually",
            "integration_complexity": "low|medium|high",
            "business_value": "high|medium|low",
            "description": "Detailed description of data source and benefits",
            "specific_use_case": "How this data enhances the optimization model",
            "intent_relevance": "high|medium|low"
        }
    ],
    "intent_specific_opportunities": {
        "primary_intent": "ENVIRONMENTAL_OPTIMIZATION",
        "high_value_sources": ["carbon_data", "emission_factors"],
        "model_enhancement_areas": ["carbon_constraints", "sustainability_objectives"]
    },
    "data_enhancement_opportunities": {
        "model_accuracy_improvement": 0.25,
        "new_optimization_constraints": ["environmental_compliance"],
        "enhanced_objective_functions": ["carbon_cost_optimization"],
        "risk_mitigation": ["supply_chain_disruption", "regulatory_compliance"]
    },
    "implementation_priority": [
        {
            "data_source": "carbon_emission_database",
            "priority": "high",
            "rationale": "Critical for environmental optimization"
        }
    ],
    "integration_roadmap": {
        "immediate": ["free_government_datasets"],
        "short_term": ["industry_benchmark_subscriptions"],
        "long_term": ["real_time_market_data_feeds"]
    },
    "reasoning": "Explanation of why these external sources were recommended"
}

CRITICAL: Focus on practical, valuable external data sources that significantly enhance optimization models."""
        )
        
        prompt = f"""
        Recommend external data sources for this optimization scenario:
        Query: "{query}"
        Intent Classification: {intent_classification}
        Data Gaps: {data_gaps}
        
        Identify external data that would significantly improve the optimization model.
        """
        
        response = agent(prompt)
        return str(response)
        
    except Exception as e:
        return json.dumps({
            "external_data_recommendations": [],
            "intent_specific_opportunities": {},
            "data_enhancement_opportunities": {},
            "implementation_priority": [],
            "integration_roadmap": {},
            "reasoning": f"External data recommendation failed: {str(e)}",
            "error": True
        })


# ==================== ENHANCED DATA TOOL ====================

class DcisionAI_Data_Tool:
    """
    DcisionAI Data Tool using AWS-style manager-worker pattern.
    
    Three-stage data analysis with intent tool integration:
    1. Query data extraction (intent-aware)
    2. Customer data source analysis  
    3. External data recommendations (intent-specific)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DcisionAI_Data_Tool")
        self.throttle_manager = get_platform_throttle_manager()
        
        # Initialize intent tool integration
        self._initialize_intent_tool()
        
        # Initialize manager agent with worker tools
        self._initialize_manager_agent()
        
        self.logger.info("✅ DcisionAI Data Tool initialized with 3-stage analysis and intent integration")
    
    def _initialize_intent_tool(self):
        """Initialize intent tool for intent-aware data analysis"""
        try:
            if INTENT_TOOL_AVAILABLE:
                self.intent_tool = create_dcisionai_intent_tool()
                self.logger.info("✅ Intent tool integration initialized")
            else:
                self.intent_tool = None
                self.logger.warning("⚠️ Intent tool not available - using default intent classification")
        except Exception as e:
            self.intent_tool = None
            self.logger.warning(f"⚠️ Intent tool initialization failed: {e}")
    
    def _initialize_manager_agent(self):
        """Initialize manager agent with data analysis worker tools"""
        try:
            self.manager_agent = Agent(
                model=CLAUDE_MODEL_ID,
                name="data_analysis_manager",
                tools=[query_data_extractor, customer_data_analyzer, external_data_recommender],
                system_prompt="""You are a Data Analysis Manager for manufacturing optimization problems.

You coordinate a team of 3 data specialists to comprehensively analyze data requirements:
1. query_data_extractor: Extract data requirements from natural language queries (intent-aware)
2. customer_data_analyzer: Analyze customer's configured data sources (roadmap feature)
3. external_data_recommender: Recommend external data sources for model enhancement (intent-specific)

THREE-STAGE ANALYSIS PROCESS:
1. QUERY ANALYSIS: Extract all data requirements from the user's query using intent classification
2. CUSTOMER DATA: Assess customer's available data sources and coverage
3. EXTERNAL DATA: Recommend external sources to fill gaps and enhance models (intent-specific)

INTENT INTEGRATION:
- Use intent classification to focus data extraction on relevant categories
- PRODUCTION_SCHEDULING: Focus on capacity, demand, processing times
- CAPACITY_PLANNING: Focus on resource limits, demand forecasts, costs
- ENVIRONMENTAL_OPTIMIZATION: Focus on carbon data, sustainability metrics
- COST_OPTIMIZATION: Focus on cost structures, financial constraints
- SUPPLY_CHAIN: Focus on logistics, inventory, supplier data

COORDINATION STRATEGY:
- Always execute all 3 stages in sequence
- Pass results from stage 1 to stages 2 and 3
- Build comprehensive data strategy combining all analyses
- Identify critical data gaps and enhancement opportunities
- Leverage intent classification for focused recommendations

RESPONSE FORMAT (JSON only):
{
    "data_analysis_summary": {
        "query_data_requirements": "summary of extracted requirements",
        "customer_data_coverage": "percentage of requirements covered",
        "external_data_opportunities": "count of valuable external sources",
        "optimization_readiness": "assessment of data completeness for modeling",
        "intent_influence": "how intent classification guided the analysis"
    },
    "stage_1_query_analysis": "results from query_data_extractor",
    "stage_2_customer_analysis": "results from customer_data_analyzer", 
    "stage_3_external_recommendations": "results from external_data_recommender",
    "critical_data_gaps": ["list of missing critical data"],
    "recommended_next_steps": ["actionable recommendations"],
    "model_building_readiness": {
        "can_build_basic_model": true,
        "data_completeness_score": 0.75,
        "recommended_enhancements": ["specific improvements"],
        "intent_specific_requirements": ["intent-focused data needs"]
    },
    "execution_metadata": {
        "stages_completed": 3,
        "analysis_depth": "comprehensive",
        "roadmap_considerations": "data connector limitations noted",
        "intent_integration": "intent-aware analysis performed"
    }
}

CRITICAL RULES:
- Execute all 3 stages sequentially 
- Provide comprehensive data strategy
- Note roadmap limitations honestly
- Give practical next steps for model building
- Use intent classification to focus analysis"""
            )
            
            self.logger.info("✅ Data analysis manager initialized with 3 specialist tools")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize data analysis manager: {e}")
            raise Exception(f"Data analysis manager initialization failed: {e}")
    
    def analyze_data_requirements(self, query: str, intent_classification: str = "unknown", session_id: str = "default") -> DataAnalysisResult:
        """Perform comprehensive 3-stage data analysis with intent integration"""
        start_time = datetime.now()
        
        try:
            self.logger.info("🚀 Starting comprehensive 3-stage data analysis with intent integration")
            
            # Get intent classification if intent tool is available
            intent_result = None
            if self.intent_tool:
                try:
                    intent_result = self.intent_tool.classify_intent(query)
                    intent_classification = intent_result.primary_intent
                    self.logger.info(f"🎯 Intent classification: {intent_classification}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Intent classification failed: {e}")
            
            analysis_task = f"""
            Perform comprehensive 3-stage data analysis for this manufacturing optimization query:
            
            Query: "{query}"
            Intent Classification: {intent_classification}
            Session ID: {session_id}
            
            Execute all 3 stages with intent-aware focus:
            1. Extract data requirements from the query (focus on intent-relevant categories)
            2. Analyze customer's data source configuration and coverage
            3. Recommend external data sources for model enhancement (intent-specific)
            
            Provide comprehensive data strategy and model building recommendations.
            """
            
            # Execute manager agent (coordinates all 3 stages)
            response = self.manager_agent(analysis_task)
            
            # Parse manager's comprehensive response
            analysis_result = self._parse_data_analysis_response(response)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return DataAnalysisResult(
                query_data_requirements=self._extract_data_requirements(analysis_result),
                customer_data_availability=analysis_result.get("stage_2_customer_analysis", {}),
                external_data_recommendations=self._extract_external_recommendations(analysis_result),
                data_gaps=analysis_result.get("critical_data_gaps", []),
                optimization_readiness=analysis_result.get("model_building_readiness", {}),
                execution_metadata={
                    "strategy": "three_stage_data_analysis",
                    "stages_completed": 3,
                    "execution_time": execution_time,
                    "manager_agent": "data_analysis_manager",
                    "worker_tools": ["query_data_extractor", "customer_data_analyzer", "external_data_recommender"],
                    "throttle_status": self.throttle_manager.get_status(),
                    "intent_classification": intent_classification,
                    "session_id": session_id,
                    "intent_tool_used": intent_result is not None,
                    "intent_integration": "intent-aware analysis performed"
                },
                intent_classification=intent_result
            )
            
        except Exception as e:
            self.logger.error(f"❌ Data analysis failed: {e}")
            return DataAnalysisResult(
                query_data_requirements=[],
                customer_data_availability={},
                external_data_recommendations=[],
                data_gaps=[f"Analysis failed: {str(e)}"],
                optimization_readiness={"can_build_basic_model": False, "data_completeness_score": 0.0},
                execution_metadata={
                    "strategy": "three_stage_data_analysis",
                    "error": True,
                    "error_message": str(e)
                }
            )
    
    def analyze_data_requirements_with_intent(self, query: str, intent_result, session_id: str = "default") -> DataAnalysisResult:
        """Perform comprehensive 3-stage data analysis using provided intent result (no duplicate intent classification)"""
        start_time = datetime.now()
        
        try:
            self.logger.info("🚀 Starting comprehensive 3-stage data analysis with provided intent result")
            
            # Use the provided intent result instead of calling intent tool again
            intent_classification = intent_result.primary_intent.value if intent_result else "unknown"
            self.logger.info(f"🎯 Using provided intent classification: {intent_classification}")
            
            analysis_task = f"""
            Perform comprehensive 3-stage data analysis for this manufacturing optimization query:
            
            Query: "{query}"
            Intent Classification: {intent_classification}
            Session ID: {session_id}
            
            Execute all 3 stages with intent-aware focus:
            1. Extract data requirements from the query (focus on intent-relevant categories)
            2. Analyze customer's data source configuration and coverage
            3. Recommend external data sources for model enhancement (intent-specific)
            
            Provide comprehensive data strategy and model building recommendations.
            """
            
            # Execute manager agent (coordinates all 3 stages)
            response = self.manager_agent(analysis_task)
            
            # Parse manager's comprehensive response
            analysis_result = self._parse_data_analysis_response(response)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return DataAnalysisResult(
                query_data_requirements=self._extract_data_requirements(analysis_result),
                customer_data_availability=analysis_result.get("stage_2_customer_analysis", {}),
                external_data_recommendations=self._extract_external_recommendations(analysis_result),
                data_gaps=analysis_result.get("critical_data_gaps", []),
                optimization_readiness=analysis_result.get("model_building_readiness", {}),
                execution_metadata={
                    "strategy": "three_stage_data_analysis_with_provided_intent",
                    "stages_completed": 3,
                    "execution_time": execution_time,
                    "manager_agent": "data_analysis_manager",
                    "worker_tools": ["query_data_extractor", "customer_data_analyzer", "external_data_recommender"],
                    "throttle_status": self.throttle_manager.get_status(),
                    "intent_classification": intent_classification,
                    "session_id": session_id,
                    "intent_tool_used": False,  # We used provided intent result
                    "intent_integration": "provided_intent_analysis_performed",
                    "duplicate_intent_avoided": True
                },
                intent_classification=intent_result
            )
            
        except Exception as e:
            self.logger.error(f"❌ Data analysis with provided intent failed: {e}")
            return DataAnalysisResult(
                query_data_requirements=[],
                customer_data_availability={},
                external_data_recommendations=[],
                data_gaps=[f"Analysis failed: {str(e)}"],
                optimization_readiness={"can_build_basic_model": False, "data_completeness_score": 0.0},
                execution_metadata={
                    "strategy": "three_stage_data_analysis_with_provided_intent",
                    "error": True,
                    "error_message": str(e)
                }
            )
    
    def _parse_data_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse comprehensive data analysis response"""
        try:
            # Handle Strands AgentResult format
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Extract JSON from response
            parsed = self._extract_json_from_text(response_text)
            
            if parsed and "data_analysis_summary" in parsed:
                return parsed
            else:
                return {
                    "data_analysis_summary": {},
                    "stage_1_query_analysis": {},
                    "stage_2_customer_analysis": {},
                    "stage_3_external_recommendations": {},
                    "critical_data_gaps": ["Failed to parse analysis response"],
                    "model_building_readiness": {"can_build_basic_model": False, "data_completeness_score": 0.0},
                    "error": True
                }
                
        except Exception as e:
            return {
                "data_analysis_summary": {},
                "critical_data_gaps": [f"Response parsing failed: {str(e)}"],
                "model_building_readiness": {"can_build_basic_model": False, "data_completeness_score": 0.0},
                "error": True
            }
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text response"""
        import re
        
        try:
            # Clean markdown formatting
            cleaned_text = re.sub(r'```json\s*', '', text)
            cleaned_text = re.sub(r'```\s*', '', cleaned_text)
            
            # Try direct JSON parse
            return json.loads(cleaned_text.strip())
        except:
            pass
        
        try:
            # Extract JSON with regex
            json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\})*)*\})*)*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            if matches:
                return json.loads(matches[-1])
        except:
            pass
        
        return None
    
    def _extract_data_requirements(self, analysis_result: Dict[str, Any]) -> List[DataRequirement]:
        """Extract structured data requirements from analysis"""
        try:
            stage_1 = analysis_result.get("stage_1_query_analysis", {})
            if isinstance(stage_1, str):
                stage_1 = json.loads(stage_1)
            
            requirements = []
            for req in stage_1.get("data_requirements", []):
                requirements.append(DataRequirement(
                    element=req.get("element", "unknown"),
                    category=DataCategory(req.get("category", "PRODUCTION_DATA").lower()),
                    priority=req.get("priority", "important"),
                    data_type=req.get("data_type", "numerical"),
                    description=req.get("description", ""),
                    examples=req.get("examples", [])
                ))
            
            return requirements
        except Exception as e:
            self.logger.warning(f"Failed to extract data requirements: {e}")
            return []
    
    def _extract_external_recommendations(self, analysis_result: Dict[str, Any]) -> List[DataSourceRecommendation]:
        """Extract structured external data recommendations"""
        try:
            stage_3 = analysis_result.get("stage_3_external_recommendations", {})
            if isinstance(stage_3, str):
                stage_3 = json.loads(stage_3)
            
            recommendations = []
            for rec in stage_3.get("external_data_recommendations", []):
                recommendations.append(DataSourceRecommendation(
                    source_name=rec.get("source_name", "unknown"),
                    source_type=DataSource(rec.get("source_type", "external_api").lower()),
                    data_elements=rec.get("data_elements", []),
                    access_method=rec.get("access_method", "unknown"),
                    cost_estimate=rec.get("cost_estimate", "unknown"),
                    reliability=rec.get("reliability", "unknown"),
                    update_frequency=rec.get("update_frequency", "unknown"),
                    integration_complexity=rec.get("integration_complexity", "unknown"),
                    business_value=rec.get("business_value", "unknown")
                ))
            
            return recommendations
        except Exception as e:
            self.logger.warning(f"Failed to extract external recommendations: {e}")
            return []


# Factory function for easy integration
def create_dcisionai_data_tool() -> DcisionAI_Data_Tool:
    """Create DcisionAI Data Tool with 3-stage analysis and intent integration"""
    return DcisionAI_Data_Tool()
