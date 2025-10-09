#!/usr/bin/env python3
"""
Test Model Builder Only - Isolate the Issue
==========================================

Test the Model Builder tool in isolation to see if it's calling the Intent tool.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_model_builder():
    """Test Model Builder in isolation"""
    print("🔧 Testing Model Builder in isolation...")
    
    try:
        from mcp_server.tools.manufacturing.model.DcisionAI_Model_Builder import create_model_builder_tool
        
        # Create model builder
        model_builder = create_model_builder_tool()
        print("✅ Model Builder created successfully")
        
        # Test data (no intent tool call)
        intent_result = {
            "primary_intent": "production_scheduling",
            "confidence": 0.88,
            "objectives": ["minimize_costs", "meet_demand", "optimize_schedule"]
        }
        
        data_result = {
            "extracted_data_entities": ["production_capacity", "demand_forecast"],
            "missing_data_entities": ["unit_costs"],
            "sample_data_generated": {
                "production_capacity": {"Line_A": 100, "Line_B": 150},
                "demand_forecast": {"Product_A": 500, "Product_B": 300}
            },
            "industry_context": "Automotive manufacturing"
        }
        
        print("📝 Test data prepared:")
        print(f"   Intent: {intent_result['primary_intent']}")
        print(f"   Data entities: {len(data_result['extracted_data_entities'])}")
        
        # Build model
        print("\n🔧 Building optimization model...")
        start_time = time.time()
        
        model_result = model_builder.build_optimization_model(
            intent_result, data_result, "test_customer"
        )
        
        execution_time = time.time() - start_time
        
        print(f"✅ Model built successfully!")
        print(f"   Model ID: {model_result.model_id}")
        print(f"   Type: {model_result.model_type.value}")
        print(f"   Variables: {len(model_result.decision_variables)}")
        print(f"   Constraints: {len(model_result.constraints)}")
        print(f"   Time: {execution_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Model Builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_model_builder()
