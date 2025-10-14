#!/usr/bin/env python3
"""
AgentCore Production Startup Script
===================================

This script starts the AgentCore runtime in production mode with
all optimizations and monitoring enabled.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import os
import sys
import logging
import signal
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | AgentCore Production | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agentcore_production.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup production environment."""
    logger.info("🔧 Setting up production environment...")
    
    # Set production environment variables
    os.environ['AGENTCORE_ENV'] = 'production'
    os.environ['AGENTCORE_LOG_LEVEL'] = 'INFO'
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    logger.info("✅ Production environment configured")

def check_aws_credentials():
    """Check AWS credentials for Bedrock access."""
    logger.info("🔍 Checking AWS credentials...")
    
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials:
            logger.info("✅ AWS credentials found")
            return True
        else:
            logger.warning("⚠️ AWS credentials not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ AWS credentials check failed: {e}")
        return False

def start_agentcore():
    """Start the AgentCore runtime."""
    logger.info("🚀 Starting AgentCore Production Runtime...")
    
    try:
        from agentcore_runtime import agentcore
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
            agentcore._graceful_shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start AgentCore
        logger.info("🎯 Starting AgentCore with full capabilities:")
        logger.info("   - Cross-session learning")
        logger.info("   - Model caching (10-100x faster)")
        logger.info("   - Intelligent coordination")
        logger.info("   - Deduplication")
        logger.info("   - Parallel processing")
        
        agentcore.run(host="0.0.0.0", port=8080, workers=1)
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ AgentCore startup failed: {e}")
        raise

def main():
    """Main startup function."""
    logger.info("🎯 DcisionAI AgentCore Production Startup")
    logger.info("=" * 50)
    
    try:
        # Setup environment
        setup_environment()
        
        # Check AWS credentials
        if not check_aws_credentials():
            logger.warning("⚠️ AWS credentials not configured - some features may not work")
        
        # Start AgentCore
        start_agentcore()
        
    except Exception as e:
        logger.error(f"❌ Production startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
