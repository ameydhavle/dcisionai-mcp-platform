#!/usr/bin/env python3
"""
Test script to verify problem type detection logic
"""

def detect_problem_type(problem_description: str, intent_data: dict) -> str:
    """
    Detect problem type from description and intent
    """
    text = problem_description.lower()
    intent = intent_data.get("intent", "").lower()
    industry = intent_data.get("industry", "").lower()
    
    print(f"Text: {text[:100]}...")
    print(f"Intent: {intent}")
    print(f"Industry: {industry}")
    
    if "manufacturing" in industry or "production" in intent:
        if "line" in text and "units/hour" in text:
            print("✅ Detected manufacturing_production_planning")
            return "manufacturing_production_planning"
    
    if "healthcare" in industry or "staff" in intent:
        print("✅ Detected healthcare_staffing")
        return "healthcare_staffing"
    
    if "portfolio" in intent or "allocation" in text:
        print("✅ Detected portfolio_optimization")
        return "portfolio_optimization"
    
    print("❌ No specific problem type detected")
    return "unknown"

# Test with our manufacturing example
problem_description = """I manage a manufacturing facility that produces 3 products: Widget A, Widget B, and Widget C. I have 2 production lines with different capacities and costs. Line 1 can produce 100 units/hour of Widget A, 80 units/hour of Widget B, and 60 units/hour of Widget C. Line 2 can produce 90 units/hour of Widget A, 100 units/hour of Widget B, and 70 units/hour of Widget C. The operating costs are $50/hour for Line 1 and $60/hour for Line 2. I need to meet demand of 500 Widget A, 400 Widget B, and 300 Widget C in the next 8 hours. I want to minimize total production costs while meeting all demand requirements."""

intent_data = {
    "intent": "production_planning",
    "industry": "manufacturing",
    "complexity": "medium",
    "confidence": 0.9
}

result = detect_problem_type(problem_description, intent_data)
print(f"\n🎯 Final Result: {result}")
