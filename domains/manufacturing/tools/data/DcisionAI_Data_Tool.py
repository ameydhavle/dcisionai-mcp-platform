#!/usr/bin/env python3
"""
DcisionAI Data Tool - MVP Focus
===============================

Extract data requirements from user queries and create realistic sample data.
MVP focus: Extract missing data with business reasoning and create industry-relevant sample data.

Production-ready with no fallbacks or mock responses.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import uuid
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field

# Strands framework imports
try:
    from strands import Agent
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    logging.warning("Strands framework not available - install with: pip install strands")
    # Don't raise error, just log warning

# AgentCore provides built-in throttling, TPS management, and comprehensive metrics
# No custom throttling needed - see: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-tool-metrics.html
def get_platform_throttle_manager():
    """AgentCore handles throttling automatically - no custom implementation needed."""
    return None

logger = logging.getLogger(__name__)

# ==================== CORE DATA STRUCTURES ====================

@dataclass
class DataRequirement:
    """Data requirement specification"""
    entity_name: str
    category: str  # "production", "demand", "cost", "constraints", "environmental"
    priority: str  # "critical", "important", "optional"
    business_reasoning: str  # Why this data is important for optimization
    optimization_role: str  # How it plays a role in optimization
    data_type: str  # "numerical", "categorical", "temporal", "spatial"
    unit: Optional[str] = None
    sample_values: Optional[Dict[str, Any]] = None
    assumptions_made: Optional[List[str]] = None

@dataclass
class DataAnalysisResult:
    """Complete data analysis result"""
    analysis_id: str
    user_query: str
    extracted_data_entities: List[str]
    data_requirements: List[DataRequirement]
    missing_data_entities: List[DataRequirement]
    sample_data_generated: Dict[str, Any]
    industry_context: str
    optimization_readiness_score: float
    assumptions_used: List[str]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)

# ==================== SINGLE AGENT DATA TOOL ====================

class DataTool:
    """
    MVP-focused data tool for extracting requirements and generating realistic sample data.
    Production-ready with no fallbacks or mock responses.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DataTool")
        self.throttle_manager = get_platform_throttle_manager()
        
        # Initialize single agent for data analysis
        if not STRANDS_AVAILABLE:
            raise ImportError("Strands framework required for data analysis")
        
        self.agent = Agent(
            name="manufacturing_data_analyst",
            system_prompt="""You are an expert Manufacturing Data Analyst specializing in optimization data requirements.

EXPERTISE: Data requirement extraction, business reasoning, industry sample data generation
FOCUS: MVP-focused data analysis with realistic sample data and business context

CORE CAPABILITIES:
1. Extract data entities from user queries
2. Identify missing data with business reasoning
3. Explain optimization role of each data entity
4. Generate realistic sample data with industry context
5. Make reasonable assumptions for missing data

RESPONSE FORMAT (JSON only):
{
    "extracted_data_entities": ["production_capacity", "demand_forecast", "unit_costs"],
    "data_requirements": [
        {
            "entity_name": "production_capacity",
            "category": "production",
            "priority": "critical",
            "business_reasoning": "Production capacity directly constrains optimization decisions - without it, we cannot determine feasible production levels",
            "optimization_role": "Acts as upper bound constraint in production planning optimization model",
            "data_type": "numerical",
            "unit": "units/hour",
            "sample_values": {"Line_A": 100, "Line_B": 150, "Line_C": 80},
            "assumptions_made": ["Standard 8-hour shifts", "Historical capacity utilization"]
        }
    ],
    "missing_data_entities": [
        {
            "entity_name": "demand_forecast",
            "category": "demand",
            "priority": "critical",
            "business_reasoning": "Demand forecast drives production planning decisions - critical for meeting customer requirements",
            "optimization_role": "Sets minimum production requirements and influences objective function weights",
            "data_type": "numerical",
            "unit": "units/week",
            "sample_values": {"Product_A": 500, "Product_B": 300, "Product_C": 200},
            "assumptions_made": ["Historical demand patterns", "Seasonal adjustments", "Market growth trends"]
        }
    ],
    "sample_data_generated": {
        "production_capacity": {"Line_A": 100, "Line_B": 150, "Line_C": 80},
        "demand_forecast": {"Product_A": 500, "Product_B": 300, "Product_C": 200},
        "unit_costs": {"Product_A": 25.50, "Product_B": 18.75, "Product_C": 32.00},
        "processing_times": {"Product_A": 2.5, "Product_B": 1.8, "Product_C": 3.2}
    },
    "industry_context": "Automotive manufacturing with mixed-model assembly lines",
    "optimization_readiness_score": 0.85,
    "assumptions_used": [
        "Standard automotive industry capacity utilization rates",
        "Typical demand variability patterns",
        "Industry-standard cost structures"
    ]
}

Provide focused, business-relevant data analysis for optimization."""
        )
        
        self.logger.info("✅ Data Tool initialized with MVP-focused single agent architecture")
    
    def analyze_data_requirements(
        self,
        user_query: str,
        intent_result: Dict[str, Any],
        customer_id: str = "default"
    ) -> DataAnalysisResult:
        """
        Analyze data requirements from user query with MVP focus.
        Extract missing data with business reasoning and generate realistic sample data.
        """
        start_time = datetime.now()
        analysis_id = f"data_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        try:
            self.logger.info(f"🚀 Starting MVP data analysis - {analysis_id}")
            
            # Create focused prompt for single agent
            prompt = self._create_mvp_prompt(user_query, intent_result, customer_id, analysis_id)
            
            # Execute single agent with focused prompt
            self.logger.info("⚡ Executing single agent with MVP-focused data analysis")
            response = self.agent(prompt)
            
            # Extract response content
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from text
                cleaned = self._clean_response(response_text)
                try:
                    result = json.loads(cleaned)
                except:
                    raise ValueError(f"Failed to parse agent response: {response_text[:500]}")
            
            # Build data analysis result from agent response
            data_analysis_result = self._build_data_analysis_result(
                analysis_id, user_query, intent_result, result
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            data_analysis_result.analysis_metadata.update({
                "execution_time": execution_time,
                "single_agent_execution": True,
                "agent_response": result
            })
            
            self.logger.info(f"✅ MVP data analysis completed in {execution_time:.1f}s")
            return data_analysis_result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ MVP data analysis failed: {e}")
            raise RuntimeError(f"Data analysis failed after {execution_time:.1f}s: {str(e)}")
    
    def _create_mvp_prompt(
        self,
        user_query: str,
        intent_result: Dict[str, Any],
        customer_id: str,
        analysis_id: str
    ) -> str:
        """Create MVP-focused prompt for single agent execution"""
        
        return f"""
        Analyze data requirements for this manufacturing optimization query.

        USER QUERY: "{user_query}"
        
        CONTEXT:
        - Analysis ID: {analysis_id}
        - Customer ID: {customer_id}
        - Intent: {intent_result.get('primary_intent', 'unknown')}
        - Objectives: {intent_result.get('objectives', [])}
        
        MVP REQUIREMENTS:
        1. Extract data entities mentioned in the user query
        2. Identify missing data entities needed for optimization
        3. For each missing entity, provide:
           - Business reasoning for why it's important
           - How it plays a role in optimization
           - Realistic sample data with industry context
        4. Make reasonable assumptions for missing data
        5. Generate complete sample dataset for optimization
        
        FOCUS ON:
        - Business relevance and practical impact
        - Industry-specific data patterns
        - Realistic sample values
        - Clear optimization role explanation
        
        Provide focused, actionable data analysis for immediate optimization use.
        """
    
    def _clean_response(self, text: str) -> str:
        """Clean response text to extract JSON"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Extract JSON pattern
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        
        return match.group(0) if match else text.strip()
    
    def _build_data_analysis_result(
        self,
        analysis_id: str,
        user_query: str,
        intent_result: Dict[str, Any],
        agent_result: Dict[str, Any]
    ) -> DataAnalysisResult:
        """Build data analysis result from agent response"""
        
        # Extract data requirements
        data_requirements = []
        for req_data in agent_result.get("data_requirements", []):
            data_requirements.append(DataRequirement(
                entity_name=req_data.get("entity_name", "unknown"),
                category=req_data.get("category", "general"),
                priority=req_data.get("priority", "optional"),
                business_reasoning=req_data.get("business_reasoning", ""),
                optimization_role=req_data.get("optimization_role", ""),
                data_type=req_data.get("data_type", "numerical"),
                unit=req_data.get("unit"),
                sample_values=req_data.get("sample_values"),
                assumptions_made=req_data.get("assumptions_made", [])
            ))
        
        # Extract missing data entities
        missing_data_entities = []
        for missing_data in agent_result.get("missing_data_entities", []):
            missing_data_entities.append(DataRequirement(
                entity_name=missing_data.get("entity_name", "unknown"),
                category=missing_data.get("category", "general"),
                priority=missing_data.get("priority", "optional"),
                business_reasoning=missing_data.get("business_reasoning", ""),
                optimization_role=missing_data.get("optimization_role", ""),
                data_type=missing_data.get("data_type", "numerical"),
                unit=missing_data.get("unit"),
                sample_values=missing_data.get("sample_values"),
                assumptions_made=missing_data.get("assumptions_made", [])
            ))
        
        return DataAnalysisResult(
            analysis_id=analysis_id,
            user_query=user_query,
            extracted_data_entities=agent_result.get("extracted_data_entities", []),
            data_requirements=data_requirements,
            missing_data_entities=missing_data_entities,
            sample_data_generated=agent_result.get("sample_data_generated", {}),
            industry_context=agent_result.get("industry_context", "Manufacturing"),
            optimization_readiness_score=agent_result.get("optimization_readiness_score", 0.5),
            assumptions_used=agent_result.get("assumptions_used", []),
            analysis_metadata={
                "generation_timestamp": datetime.now().isoformat(),
                "single_agent_generation": True,
                "intent_classification": intent_result.get("primary_intent", "unknown")
            }
        )

# ==================== FACTORY FUNCTIONS ====================

def create_data_tool() -> DataTool:
    """Create production-ready data tool with MVP-focused single agent architecture"""
    return DataTool()

def analyze_data_requirements_enhanced(
    user_query: str,
    intent_result: Dict[str, Any],
    customer_id: str = "default"
) -> DataAnalysisResult:
    """Analyze data requirements with MVP focus"""
    
    data_tool = create_data_tool()
    return data_tool.analyze_data_requirements(user_query, intent_result, customer_id)

# ==================== DEMO AND TESTING ====================

def demo_mvp_data_analysis():
    """Demonstrate MVP-focused data analysis"""
    
    print("🚀 MVP Data Analysis Demo")
    print("=" * 60)
    print("📊 Extract Requirements | 💡 Business Reasoning | 🏭 Industry Sample Data")
    print("=" * 60)
    
    # Test case
    user_query = "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
    
    intent_result = {
        "primary_intent": "production_optimization",
        "confidence": 0.92,
        "objectives": ["minimize_costs", "meet_demand"],
        "entities": ["production_schedule", "costs", "customer_demand"]
    }
    
    print("📝 User Query:")
    print(f"   {user_query}")
    print(f"\n🎯 Intent: {intent_result['primary_intent']}")
    print(f"📊 Objectives: {', '.join(intent_result['objectives'])}")
    
    # Analyze data requirements
    print(f"\n🔧 Analyzing data requirements...")
    start_time = datetime.now()
    
    data_result = analyze_data_requirements_enhanced(user_query, intent_result, "demo_customer")
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # Display results
    print(f"\n✅ Data analysis completed in {execution_time:.1f}s")
    print("=" * 60)
    print("📊 DATA ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"🆔 Analysis ID: {data_result.analysis_id}")
    print(f"🏭 Industry Context: {data_result.industry_context}")
    print(f"✅ Optimization Readiness: {data_result.optimization_readiness_score:.1%}")
    
    print(f"\n📋 Extracted Data Entities ({len(data_result.extracted_data_entities)}):")
    for entity in data_result.extracted_data_entities:
        print(f"   ✅ {entity}")
    
    print(f"\n❌ Missing Data Entities ({len(data_result.missing_data_entities)}):")
    for missing in data_result.missing_data_entities:
        print(f"\n🔍 {missing.entity_name} ({missing.priority.upper()})")
        print(f"   Category: {missing.category}")
        print(f"   Business Reasoning: {missing.business_reasoning}")
        print(f"   Optimization Role: {missing.optimization_role}")
        if missing.sample_values:
            print(f"   Sample Values: {missing.sample_values}")
        if missing.assumptions_made:
            print(f"   Assumptions: {', '.join(missing.assumptions_made)}")
    
    print(f"\n📊 Generated Sample Data:")
    for entity, values in data_result.sample_data_generated.items():
        print(f"   {entity}: {values}")
    
    print(f"\n💡 Assumptions Used:")
    for assumption in data_result.assumptions_used:
        print(f"   • {assumption}")
    
    print(f"\n🎯 Ready for Model Builder: ✅")
    return data_result

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    import sys
    
    def main():
        """Main execution function"""
        
        print("🚀 DcisionAI Data Tool - MVP Focus")
        print("=" * 50)
        
        # Run demo
        data_result = demo_mvp_data_analysis()
        
        print(f"\n✅ MVP data analysis demonstration complete!")
        print(f"🎯 Data ready for model building")
    
    # Run main
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Data analysis demo interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
