#!/usr/bin/env python3
"""
Bedrock AgentCore Proxy for Frontend
====================================

This proxy handles AWS authentication and forwards MCP requests to Bedrock AgentCore.
The frontend can't directly authenticate with Bedrock AgentCore, so this proxy
handles the AWS IAM authentication and forwards requests.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import json
import logging
import asyncio
import boto3
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Bedrock AgentCore Proxy | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DcisionAI Bedrock AgentCore Proxy",
    description="Proxy for frontend to communicate with Bedrock AgentCore Runtime",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bedrock AgentCore configuration
BEDROCK_AGENTCORE_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/bedrock_agentcore_mcp_server-uZ4MxJ2bNZ"
BEDROCK_AGENTCORE_AGENT_ID = BEDROCK_AGENTCORE_ARN.split('/')[-1]  # Extract agent ID from ARN
BEDROCK_AGENTCORE_URL = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{BEDROCK_AGENTCORE_ARN.replace(':', '%3A').replace('/', '%2F')}/invocations?qualifier=DEFAULT"

# Initialize AWS clients
try:
    bedrock_agentcore_client = boto3.client('bedrock-runtime', region_name='us-east-1')
    logger.info("✅ Bedrock AgentCore client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Bedrock AgentCore client: {e}")
    bedrock_agentcore_client = None

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Bedrock AgentCore Proxy",
        "bedrock_agentcore_arn": BEDROCK_AGENTCORE_ARN,
        "bedrock_agentcore_connected": bedrock_agentcore_client is not None
    })

@app.post("/mcp")
async def proxy_mcp_request(request: MCPRequest):
    """
    Proxy MCP requests to Bedrock AgentCore Runtime.
    Handles AWS authentication automatically.
    """
    logger.info(f"🔄 Proxying MCP request: {request.method}")
    
    if not bedrock_agentcore_client:
        raise HTTPException(status_code=503, detail="Bedrock AgentCore client not available")
    
    try:
        # Prepare the request for Bedrock AgentCore
        request_body = {
            "jsonrpc": request.jsonrpc,
            "id": request.id or "1",
            "method": request.method,
            "params": request.params or {}
        }
        
        logger.info(f"📤 Sending to Bedrock AgentCore: {request.method}")
        
        # Call Bedrock AgentCore using the AWS SDK with proper authentication
        # Use boto3 to make the authenticated request
        import boto3
        from botocore.auth import SigV4Auth
        from botocore.awsrequest import AWSRequest
        import requests
        
        # Create a signed request
        session = boto3.Session()
        credentials = session.get_credentials()
        region = 'us-east-1'
        service = 'bedrock-agentcore'
        
        # Create the request
        aws_request = AWSRequest(
            method='POST',
            url=BEDROCK_AGENTCORE_URL,
            data=json.dumps(request_body),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream'
            }
        )
        
        # Sign the request
        SigV4Auth(credentials, service, region).add_auth(aws_request)
        
        # Make the request
        response = requests.post(
            BEDROCK_AGENTCORE_URL,
            data=json.dumps(request_body),
            headers=dict(aws_request.headers),
            timeout=30.0
        )
        
        logger.info(f"📥 Response status: {response.status_code}")
        logger.info(f"📥 Response headers: {dict(response.headers)}")
        logger.info(f"📥 Response content: {response.text[:500]}...")
        
        # Parse the response
        if response.status_code == 200:
            try:
                response_data = response.json() if response.content else {}
                return JSONResponse(response_data)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error: {e}")
                logger.error(f"❌ Raw response: {response.text}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request.id or "1",
                    "result": {
                        "content": [{"type": "text", "text": response.text}]
                    }
                })
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request.id or "1",
                "error": {
                    "code": response.status_code,
                    "message": f"Bedrock AgentCore request failed: {response.text}"
                }
            })
        
    except Exception as e:
        logger.error(f"❌ Bedrock AgentCore request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bedrock AgentCore request failed: {str(e)}")

@app.post("/optimize")
async def optimize_manufacturing(request: Request):
    """
    Direct optimization endpoint that proxies to Bedrock AgentCore.
    """
    try:
        body = await request.json()
        problem_description = body.get("problem_description", "")
        
        logger.info(f"🚀 Optimization request: {problem_description[:100]}...")
        
        # Create MCP request
        mcp_request = MCPRequest(
            method="tools/call",
            params={
                "name": "manufacturing_optimize",
                "arguments": {
                    "problem_description": problem_description,
                    "constraints": body.get("constraints", {}),
                    "optimization_goals": body.get("optimization_goals", [])
                }
            }
        )
        
        # Proxy the request
        return await proxy_mcp_request(mcp_request)
        
    except Exception as e:
        logger.error(f"❌ Optimization request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Bedrock AgentCore Proxy...")
    logger.info(f"🎯 Bedrock AgentCore ARN: {BEDROCK_AGENTCORE_ARN}")
    logger.info("🌐 Proxy will handle AWS authentication for frontend")
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")
