#!/usr/bin/env python3
"""
Direct Bedrock Test
==================

Test direct Bedrock invocation to verify if Claude can generate proper optimization models.
"""

import boto3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

def test_bedrock_model_generation(model_id):
    """Test direct Bedrock model generation for optimization models."""
    
    prompt = """
    You are an expert operations research scientist. Design a mathematical optimization model for this problem:
    
    Problem: "Minimize supply chain costs for 5 warehouses across different regions with 20 suppliers and 100 products"
    Intent: supply_chain_optimization
    Scale: large
    Entities: ["warehouses", "suppliers", "products"]
    Quantities: [5, 20, 100]
    Data Complexity: high
    
    CRITICAL: Return ONLY valid JSON. No explanations, no markdown, no additional text.
    
    Create a realistic large-scale model with:
    - 5 warehouse variables (x_wh1 to x_wh5)
    - 100 supplier-warehouse variables (x_s1_w1 to x_s20_w5)
    - 20 product variables (x_p1 to x_p20)
    - Realistic constraints for capacity, demand, and supplier limits
    
    JSON format:
    {
        "model_type": "linear_programming",
        "variables": [
            {"name": "x_wh1", "type": "continuous", "bounds": [0, 10000], "description": "Total flow through warehouse 1"},
            {"name": "x_wh2", "type": "continuous", "bounds": [0, 10000], "description": "Total flow through warehouse 2"}
        ],
        "constraints": [
            "x_wh1 + x_wh2 <= 10000",
            "x_wh1 >= 100"
        ],
        "objective_function": "minimize total_supply_chain_cost",
        "complexity": "large",
        "estimated_solve_time": 2.5,
        "model_notes": "Large-scale supply chain optimization model"
    }
    """
    
    try:
        logger.info(f"Testing Bedrock model: {model_id}")
        logger.info(f"Prompt length: {len(prompt)}")
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        result_text = response_body['content'][0]['text']
        
        logger.info(f"Bedrock response length: {len(result_text)}")
        logger.info(f"Bedrock response preview: {result_text[:500]}...")
        
        # Try to parse as JSON
        try:
            parsed_result = json.loads(result_text)
            logger.info(f"✅ Successfully parsed JSON with {len(parsed_result.get('variables', []))} variables")
            logger.info(f"Model type: {parsed_result.get('model_type', 'unknown')}")
            logger.info(f"Variables: {len(parsed_result.get('variables', []))}")
            logger.info(f"Constraints: {len(parsed_result.get('constraints', []))}")
            return parsed_result
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            logger.error(f"Raw response: {result_text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Bedrock invocation failed: {e}")
        return None

def test_multiple_models():
    """Test multiple Bedrock models to see which works best."""
    
    models_to_test = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0"
    ]
    
    for model_id in models_to_test:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing model: {model_id}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_bedrock_model_generation(model_id)
            if result:
                logger.info(f"✅ Model {model_id} SUCCESS")
            else:
                logger.info(f"❌ Model {model_id} FAILED")
        except Exception as e:
            logger.error(f"❌ Model {model_id} ERROR: {e}")

if __name__ == "__main__":
    logger.info("Starting direct Bedrock test...")
    test_multiple_models()
