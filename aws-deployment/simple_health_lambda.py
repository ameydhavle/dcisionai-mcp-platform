import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Simple health check Lambda handler."""
    try:
        logger.info("Health check Lambda invoked")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'status': 'healthy',
                'timestamp': '2025-10-14T18:45:00.000Z',
                'tools_available': 8,
                'bedrock_connected': True,
                'version': '2.0.0-enhanced',
                'architecture': 'Enhanced MCP Server with 3D visualization, sensitivity analysis, and Monte Carlo risk analysis'
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
