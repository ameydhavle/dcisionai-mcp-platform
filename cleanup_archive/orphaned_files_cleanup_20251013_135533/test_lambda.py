#!/usr/bin/env python3
"""
Test Lambda Function
===================

Minimal test to debug the JSON parsing error.
"""

import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Test Lambda handler."""
    try:
        logger.info(f"Event received: {type(event)}")
        logger.info(f"Event keys: {list(event.keys()) if event else 'None'}")
        
        # Test JSON parsing
        if 'httpMethod' in event:
            method = event['httpMethod']
            path = event.get('path', '')
            body_str = event.get('body', '{}')
            logger.info(f"Body string: {body_str}")
            
            if body_str is None:
                body_str = '{}'
            
            body = json.loads(body_str)
            logger.info(f"Body parsed: {body}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "method": method,
                    "path": path,
                    "body": body
                })
            }
        else:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "event": event
                })
            }
            
    except Exception as e:
        import traceback
        logger.error(f"Error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        }
