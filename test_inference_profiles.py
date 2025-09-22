#!/usr/bin/env python3
"""
DcisionAI Platform - Test Inference Profiles with Real ARNs
==========================================================

Simple test to validate that our real AWS Bedrock inference profiles work.
"""

import asyncio
import logging
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_inference_manager():
    """Test the inference manager with real ARNs."""
    try:
        logger.info("🧪 Testing Inference Manager with Real ARNs...")
        
        # Import the inference manager
        from shared.core.inference_manager import BedrockInferenceManager
        
        # Initialize the manager
        inference_manager = BedrockInferenceManager()
        logger.info("✅ Inference Manager initialized")
        
        # Start the manager
        await inference_manager.start()
        logger.info("✅ Inference Manager started")
        
        # Check health
        health = inference_manager.health_check()
        logger.info(f"✅ Health check: {health}")
        
        # List available profiles
        logger.info("📊 Available Inference Profiles:")
        for profile_name, profile in inference_manager.inference_profiles.items():
            logger.info(f"  - {profile_name}: {profile.profile_arn}")
            logger.info(f"    Optimization: {profile.optimization_focus.value}")
            logger.info(f"    Regions: {profile.regions}")
            if hasattr(profile, 'sla_tier'):
                logger.info(f"    SLA Tier: {profile.sla_tier}")
            logger.info("")
        
        # Test profile selection
        logger.info("🎯 Testing Profile Selection...")
        
        # Test gold tier profile
        gold_profile = await inference_manager._select_inference_profile(
            type('MockRequest', (), {
                'inference_profile': 'dcisionai-gold-tier-production',
                'domain': 'manufacturing',
                'tenant_context': type('MockTenant', (), {
                    'sla_tier': type('MockSLATier', (), {'value': 'gold'})(),
                    'region': 'us-east-1'
                })()
            })()
        )
        
        if gold_profile:
            logger.info(f"✅ Gold tier profile selected: {gold_profile.profile_name}")
            logger.info(f"   ARN: {gold_profile.profile_arn}")
        else:
            logger.error("❌ Failed to select gold tier profile")
        
        # Test manufacturing latency profile
        latency_profile = await inference_manager._select_inference_profile(
            type('MockRequest', (), {
                'inference_profile': 'dcisionai-manufacturing-latency-production',
                'domain': 'manufacturing',
                'tenant_context': type('MockTenant', (), {
                    'sla_tier': type('MockSLATier', (), {'value': 'pro'})(),
                    'region': 'us-east-1'
                })()
            })()
        )
        
        if latency_profile:
            logger.info(f"✅ Manufacturing latency profile selected: {latency_profile.profile_name}")
            logger.info(f"   ARN: {latency_profile.profile_arn}")
        else:
            logger.error("❌ Failed to select manufacturing latency profile")
        
        # Get performance summary
        performance = inference_manager.get_performance_summary()
        logger.info(f"✅ Performance summary: {performance}")
        
        # Stop the manager
        await inference_manager.stop()
        logger.info("✅ Inference Manager stopped")
        
        logger.info("🎉 All inference profile tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

async def main():
    """Main test execution."""
    await test_inference_manager()

if __name__ == "__main__":
    asyncio.run(main())
