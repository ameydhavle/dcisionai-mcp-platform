#!/usr/bin/env python3
"""
Backend server for DcisionAI Manufacturing Web App
================================================

Simple Flask server to proxy requests to the MCP server and handle CORS.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# MCP Server URL
MCP_SERVER_URL = "http://localhost:8000"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check if MCP server is running
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "mcp_server": "connected",
                "message": "Web app and MCP server are running"
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "mcp_server": "error",
                "message": "MCP server returned error"
            }), 503
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to MCP server: {e}")
        return jsonify({
            "status": "unhealthy",
            "mcp_server": "disconnected",
            "message": "Cannot connect to MCP server"
        }), 503

@app.route('/mcp', methods=['POST'])
def proxy_mcp_request():
    """Proxy MCP requests to the actual MCP server."""
    try:
        # Get the request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        logger.info(f"Proxying MCP request: {data.get('method', 'unknown')}")
        
        # Forward the request to the MCP server
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=60  # 60 second timeout for optimization requests
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            logger.error(f"MCP server error: {response.status_code} - {response.text}")
            return jsonify({
                "error": f"MCP server error: {response.status_code}",
                "details": response.text
            }), response.status_code
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return jsonify({
            "error": "Request timeout",
            "message": "The optimization request took too long to process"
        }), 408
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return jsonify({
            "error": "Request failed",
            "message": "Cannot connect to MCP server"
        }), 503
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example manufacturing optimization queries."""
    examples = [
        {
            "id": 1,
            "title": "Production Line Optimization",
            "description": "Optimize production line efficiency with 50 workers across 3 manufacturing lines, considering skill sets, line capacities, and cost constraints",
            "category": "production",
            "complexity": "intermediate"
        },
        {
            "id": 2,
            "title": "Supply Chain Optimization",
            "description": "Optimize supply chain for 5 warehouses across different regions, considering demand forecasting, inventory costs, and transportation constraints",
            "category": "supply_chain",
            "complexity": "advanced"
        },
        {
            "id": 3,
            "title": "Quality Control Optimization",
            "description": "Optimize quality control processes for electronic component production, balancing quality standards with production costs and throughput",
            "category": "quality",
            "complexity": "advanced"
        },
        {
            "id": 4,
            "title": "Sustainable Manufacturing",
            "description": "Optimize manufacturing processes for environmental sustainability, balancing production efficiency with carbon footprint reduction and energy consumption",
            "category": "sustainability",
            "complexity": "advanced"
        }
    ]
    
    return jsonify(examples)

if __name__ == '__main__':
    print("Starting DcisionAI Manufacturing Web App Backend...")
    print("Proxying requests to MCP server at:", MCP_SERVER_URL)
    print("Web app will be available at: http://localhost:3000")
    print("Backend API available at: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
