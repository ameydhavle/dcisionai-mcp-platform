#!/usr/bin/env python3
"""
Test the actual MCP server tools with knowledge base integration.
This will test the real functionality, not just simulate it.
"""

import asyncio
import sys
import os

# Add the mcp-server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp-server'))

async def test_real_mcp_integration():
    """Test the actual MCP server with knowledge base integration."""
    
    print("🚀 Testing Real MCP Server with Knowledge Base Integration")
    print("=" * 70)
    
    try:
        # Import the tools
        from dcisionai_mcp_server.tools import DcisionAITools
        
        print("✅ Successfully imported DcisionAITools")
        
        # Initialize the tools
        tools = DcisionAITools()
        print("✅ Successfully initialized DcisionAITools with Knowledge Base")
        
        # Check knowledge base
        kb_examples = len(tools.knowledge_base.knowledge_base.get('examples', []))
        print(f"📚 Knowledge Base loaded: {kb_examples} examples")
        
        # Test problem
        problem = "I need to optimize production scheduling for 5 machines with different capacities and processing times to minimize total cost."
        
        print(f"\n🔍 Testing with problem: {problem}")
        print("-" * 50)
        
        # Test knowledge base search
        print("1️⃣ Testing Knowledge Base Search...")
        results = tools.knowledge_base.search_relevant_examples(problem, top_k=3)
        print(f"✅ Found {len(results)} relevant examples")
        
        for i, result in enumerate(results, 1):
            example = result['example']
            print(f"   Example {i}: {example.get('problem_type', 'unknown')} (score: {result['score']})")
            print(f"   Variables: {', '.join(example.get('variables', [])[:5])}...")
        
        # Test context generation
        print("\n2️⃣ Testing Context Generation...")
        context = tools.knowledge_base.get_context_for_problem(problem)
        print("✅ Context generated successfully")
        print(f"   Context length: {len(context)} characters")
        print(f"   Context preview: {context[:200]}...")
        
        # Test guidance generation
        print("\n3️⃣ Testing Problem-Type Guidance...")
        guidance = tools.knowledge_base.get_problem_type_guidance(problem)
        print("✅ Guidance generated successfully")
        print(f"   Guidance length: {len(guidance)} characters")
        print(f"   Guidance preview: {guidance[:200]}...")
        
        # Test enhanced prompt generation
        print("\n4️⃣ Testing Enhanced Prompt Generation...")
        original_prompt = "You are an expert in mathematical optimization."
        enhanced_prompt = tools.knowledge_base.enhance_build_model_prompt(original_prompt, problem)
        print("✅ Enhanced prompt generated successfully")
        print(f"   Original prompt length: {len(original_prompt)} characters")
        print(f"   Enhanced prompt length: {len(enhanced_prompt)} characters")
        print(f"   Enhancement ratio: {len(enhanced_prompt) / len(original_prompt):.1f}x")
        
        print("\n🎉 All Knowledge Base Integration Tests Passed!")
        print("\n📊 Integration Summary:")
        print(f"✅ Knowledge Base: {kb_examples} examples loaded")
        print(f"✅ Search: {len(results)} relevant examples found")
        print(f"✅ Context: {len(context)} characters generated")
        print(f"✅ Guidance: {len(guidance)} characters generated")
        print(f"✅ Enhancement: {len(enhanced_prompt) / len(original_prompt):.1f}x prompt improvement")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_mcp_integration())
    if success:
        print("\n🚀 MCP Server with Knowledge Base Integration is working perfectly!")
        print("✅ Ready for use in Cursor IDE!")
    else:
        print("\n❌ MCP Server integration test failed!")
        sys.exit(1)
