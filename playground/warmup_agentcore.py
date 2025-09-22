#!/usr/bin/env python3
"""
AgentCore Runtime Warm-up Script
===============================

Keep the AgentCore runtime warm to prevent cold start issues.
"""

import json
import boto3
import time
import logging
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AgentCore runtime ARN
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v1_1756943746-0OgdtC2Je6"

def warm_up_agentcore():
    """Warm up the AgentCore runtime using AWS CLI."""
    try:
        # Create warm-up payload
        warm_up_payload = {
            "jsonrpc": "2.0",
            "id": f"warmup-{int(time.time())}",
            "method": "invoke",
            "params": {
                "prompt": "warmup test",
                "tenantContext": {
                    "tenant_id": "warmup_tenant",
                    "sla_tier": "free",
                    "region": "us-east-1"
                },
                "session_id": f"warmup-session-{int(time.time())}"
            }
        }
        
        # Convert to base64
        import base64
        payload_json = json.dumps(warm_up_payload)
        payload_base64 = base64.b64encode(payload_json.encode()).decode()
        
        # Create output file
        import tempfile
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False).name
        
        # Use AWS CLI to invoke AgentCore
        cmd = [
            'aws', 'bedrock-agentcore', 'invoke-agent-runtime',
            '--agent-runtime-arn', AGENT_RUNTIME_ARN,
            '--qualifier', 'DEFAULT',
            '--payload', payload_base64,
            '--content-type', 'application/json',
            '--accept', 'application/json',
            '--region', 'us-east-1',
            output_file
        ]
        
        logger.info("Warming up AgentCore runtime...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Clean up temp files
        import os
        if os.path.exists(output_file):
            os.unlink(output_file)
        
        if result.returncode == 0:
            logger.info("✅ AgentCore runtime warmed up successfully")
            return True
        else:
            logger.error(f"❌ Warm-up failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Warm-up error: {e}")
        return False

def keep_warm(interval_minutes=5):
    """Keep the runtime warm by calling it periodically."""
    logger.info(f"Starting AgentCore warm-up service (interval: {interval_minutes} minutes)")
    
    while True:
        try:
            success = warm_up_agentcore()
            if success:
                logger.info(f"✅ Runtime is warm. Next warm-up in {interval_minutes} minutes...")
            else:
                logger.warning("⚠️ Warm-up failed, will retry in 1 minute...")
                time.sleep(60)
                continue
                
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("🛑 Warm-up service stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Single warm-up
        warm_up_agentcore()
    else:
        # Continuous warm-up
        keep_warm()
