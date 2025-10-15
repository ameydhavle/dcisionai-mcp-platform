#!/usr/bin/env python3
"""
Memory Setup for DcisionAI AgentCore
===================================

This script creates memory resources for the DcisionAI agent to enable
user preference learning and optimization history persistence.
"""

import os
import uuid
from bedrock_agentcore.memory import MemoryClient

def setup_dcisionai_memory():
    """Set up memory resources for DcisionAI agent."""
    
    # Connect to AgentCore Memory service
    client = MemoryClient(region_name='us-east-1')
    
    print("Creating memory resources for DcisionAI...\n")
    
    # === SHORT-TERM MEMORY ===
    # Stores raw conversation turns within sessions
    stm = client.create_memory_and_wait(
        name=f"DcisionAI_STM_{uuid.uuid4().hex[:8]}",
        strategies=[],  # Empty = no extraction strategies
        event_expiry_days=7  # Keep conversations for 7 days
    )
    print(f"✅ STM Memory Created: {stm['id']}")
    print("   What it does:")
    print("   - Stores exact conversation messages")
    print("   - Remembers within the same session only")
    print("   - Instant retrieval (no processing needed)")
    
    # === LONG-TERM MEMORY ===
    # Intelligently extracts user preferences and optimization patterns
    ltm = client.create_memory_and_wait(
        name=f"DcisionAI_LTM_{uuid.uuid4().hex[:8]}",
        strategies=[
            # Extracts user preferences like "I prefer Python" or "I need fast solutions"
            {
                "userPreferenceMemoryStrategy": {
                    "name": "optimization_preferences",
                    "namespaces": ["/user/optimization_preferences"]
                }
            },
            # Extracts optimization patterns and preferences
            {
                "semanticMemoryStrategy": {
                    "name": "optimization_patterns",
                    "namespaces": ["/user/optimization_patterns"]
                }
            }
        ],
        event_expiry_days=30  # Keep for 30 days
    )
    print(f"\n✅ LTM Memory Created: {ltm['id']}")
    print("   What it does:")
    print("   - Everything STM does PLUS:")
    print("   - Extracts optimization preferences automatically")
    print("   - Remembers industry preferences across sessions")
    print("   - Learns problem-solving approaches")
    print("   - Needs 5-10 seconds to process extractions")
    
    # === WORKFLOW MEMORY ===
    # Specialized memory for workflow execution patterns
    workflow_memory = client.create_memory_and_wait(
        name=f"DcisionAI_Workflow_{uuid.uuid4().hex[:8]}",
        strategies=[
            # Extracts workflow usage patterns and optimization outcomes
            {
                "semanticMemoryStrategy": {
                    "name": "workflow_patterns",
                    "namespaces": ["/workflows/usage_patterns"]
                }
            }
        ],
        event_expiry_days=60  # Keep workflow patterns longer
    )
    print(f"\n✅ Workflow Memory Created: {workflow_memory['id']}")
    print("   What it does:")
    print("   - Tracks workflow usage patterns")
    print("   - Remembers optimization outcomes")
    print("   - Learns industry-specific preferences")
    print("   - Provides workflow recommendations")
    
    # Save memory configuration
    memory_config = {
        "stm_id": stm['id'],
        "ltm_id": ltm['id'],
        "workflow_memory_id": workflow_memory['id'],
        "region": "us-east-1"
    }
    
    with open("memory_config.json", "w") as f:
        import json
        json.dump(memory_config, f, indent=2)
    
    print("\n" + "="*60)
    print("Memory Configuration:")
    print(f"  export STM_MEMORY_ID={stm['id']}")
    print(f"  export LTM_MEMORY_ID={ltm['id']}")
    print(f"  export WORKFLOW_MEMORY_ID={workflow_memory['id']}")
    print("\nConfiguration saved to: memory_config.json")
    print("="*60)
    
    return memory_config

if __name__ == "__main__":
    setup_dcisionai_memory()
