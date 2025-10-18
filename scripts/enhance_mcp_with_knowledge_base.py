#!/usr/bin/env python3
"""
Enhance MCP Server with Knowledge Base Integration
================================================

This script enhances the DcisionAI MCP server by integrating the knowledge base
to provide more accurate and context-aware optimization responses.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class KnowledgeBaseEnhancedMCP:
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load the knowledge base from file."""
        
        with open(self.knowledge_base_path, 'r') as f:
            return json.load(f)
    
    def search_relevant_examples(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant examples in the knowledge base."""
        
        query_lower = query.lower()
        results = []
        
        for example in self.knowledge_base['examples']:
            score = 0
            
            # Check problem description
            if any(word in example['problem_description'].lower() for word in query_lower.split()):
                score += 2
            
            # Check keywords
            for keyword in example['keywords']:
                if keyword in query_lower:
                    score += 1
            
            # Check problem type
            if any(word in query_lower for word in example['problem_type'].split('_')):
                score += 1
            
            if score > 0:
                results.append({
                    'example': example,
                    'score': score
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_context_for_problem(self, problem_description: str) -> str:
        """Get relevant context from knowledge base for a problem."""
        
        relevant_examples = self.search_relevant_examples(problem_description, top_k=3)
        
        if not relevant_examples:
            return "No specific examples found in knowledge base."
        
        context = "Based on similar optimization problems in our knowledge base:\n\n"
        
        for i, result in enumerate(relevant_examples, 1):
            example = result['example']
            context += f"**Example {i}** ({example['problem_type']}):\n"
            context += f"- Variables: {', '.join(example['variables'])}\n"
            context += f"- Complexity: {example['complexity']}\n"
            context += f"- Key approach: {example['solution'][:200]}...\n\n"
        
        return context
    
    def enhance_build_model_prompt(self, original_prompt: str, problem_description: str) -> str:
        """Enhance the build_model prompt with knowledge base context."""
        
        context = self.get_context_for_problem(problem_description)
        
        enhanced_prompt = f"""{original_prompt}

**KNOWLEDGE BASE CONTEXT:**
{context}

**INSTRUCTIONS:**
Use the above examples as reference for similar problem types, but adapt the approach to the specific problem at hand. Focus on the mathematical principles rather than copying exact formulations.
"""
        
        return enhanced_prompt
    
    def get_problem_type_guidance(self, problem_description: str) -> str:
        """Get specific guidance based on problem type."""
        
        relevant_examples = self.search_relevant_examples(problem_description, top_k=1)
        
        if not relevant_examples:
            return "Generic optimization guidance applies."
        
        example = relevant_examples[0]['example']
        problem_type = example['problem_type']
        
        guidance_map = {
            'production_planning': """
**Production Planning Guidance:**
- Decision variables typically represent production quantities or resource allocation
- Constraints often include capacity limits, demand requirements, and resource availability
- Objective is usually cost minimization or profit maximization
- Consider time periods, production lines, and inventory constraints
""",
            'portfolio_optimization': """
**Portfolio Optimization Guidance:**
- Decision variables represent investment allocations or asset weights
- Constraints include budget limits, risk limits, and diversification requirements
- Objective balances return maximization with risk minimization
- Consider correlation matrices, expected returns, and risk measures
""",
            'scheduling': """
**Scheduling Optimization Guidance:**
- Decision variables represent task assignments, start times, or resource allocations
- Constraints include precedence relationships, resource capacity, and deadlines
- Objective is usually makespan minimization or cost optimization
- Consider task dependencies, resource constraints, and time windows
""",
            'generic_optimization': """
**Generic Optimization Guidance:**
- Identify the key decisions to be made (decision variables)
- Determine the limitations and requirements (constraints)
- Define the optimization goal (objective function)
- Ensure all variables are used and constraints are mathematically sound
"""
        }
        
        return guidance_map.get(problem_type, guidance_map['generic_optimization'])

def enhance_mcp_server_tools():
    """Enhance the MCP server tools with knowledge base integration."""
    
    # Path to the knowledge base
    kb_path = "knowledge_base/dcisionai_kb.json"
    
    if not os.path.exists(kb_path):
        print(f"❌ Knowledge base not found at {kb_path}")
        print("Please run the knowledge base creation script first.")
        return
    
    # Initialize knowledge base
    kb_enhancer = KnowledgeBaseEnhancedMCP(kb_path)
    
    print("✅ Knowledge base loaded successfully!")
    print(f"📚 Total examples: {len(kb_enhancer.knowledge_base['examples'])}")
    
    # Test the enhancement
    test_problem = "I need to optimize production scheduling for 5 machines with different capacities and processing times."
    
    print(f"\n🔍 Testing with problem: {test_problem}")
    
    # Get context
    context = kb_enhancer.get_context_for_problem(test_problem)
    print(f"\n📖 Context:\n{context}")
    
    # Get guidance
    guidance = kb_enhancer.get_problem_type_guidance(test_problem)
    print(f"\n💡 Guidance:\n{guidance}")
    
    return kb_enhancer

def create_enhanced_tools_patch():
    """Create a patch file to enhance the MCP server tools."""
    
    patch_content = '''
# Enhanced MCP Server Tools with Knowledge Base Integration

## Usage in MCP Server

Add this to your MCP server tools.py:

```python
from scripts.enhance_mcp_with_knowledge_base import KnowledgeBaseEnhancedMCP

# Initialize knowledge base
kb_enhancer = KnowledgeBaseEnhancedMCP("knowledge_base/dcisionai_kb.json")

# In build_model function, enhance the prompt:
def build_model(problem_description: str, ...):
    # Get enhanced prompt with knowledge base context
    enhanced_prompt = kb_enhancer.enhance_build_model_prompt(
        original_prompt, 
        problem_description
    )
    
    # Get problem-specific guidance
    guidance = kb_enhancer.get_problem_type_guidance(problem_description)
    
    # Use enhanced prompt and guidance in your model building
    ...
```

## Benefits

1. **Context-Aware Responses**: Uses similar problems from knowledge base
2. **Problem-Type Guidance**: Provides specific guidance based on problem category
3. **Improved Accuracy**: Leverages 450+ optimization examples
4. **Consistent Approach**: Maintains consistent methodology across problems
'''
    
    with open("MCP_KNOWLEDGE_BASE_INTEGRATION.md", "w") as f:
        f.write(patch_content)
    
    print("📝 Created MCP_KNOWLEDGE_BASE_INTEGRATION.md with integration instructions")

if __name__ == "__main__":
    print("🚀 Enhancing MCP Server with Knowledge Base...")
    
    # Test the knowledge base integration
    kb_enhancer = enhance_mcp_server_tools()
    
    if kb_enhancer:
        # Create integration documentation
        create_enhanced_tools_patch()
        
        print("\n✅ MCP Server enhancement ready!")
        print("📋 Next steps:")
        print("1. Review MCP_KNOWLEDGE_BASE_INTEGRATION.md")
        print("2. Integrate the knowledge base into your MCP server tools")
        print("3. Test with real optimization problems")
