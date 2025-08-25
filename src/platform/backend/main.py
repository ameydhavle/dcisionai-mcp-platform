#!/usr/bin/env python3
"""
DcisionAI Platform Backend API
==============================

Modern FastAPI backend that connects to the existing domain-specific tools.
Provides a clean API interface for the new platform frontend.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path to access existing tools
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime
import uuid

# Import existing tools
try:
    from src.models.manufacturing.tools.intent.DcisionAI_Intent_Tool_v3 import create_dcisionai_intent_tool_v3
    from src.models.manufacturing.tools.data.DcisionAI_Data_Tool_v3 import create_dcisionai_data_tool_v3
    from src.models.manufacturing.tools.model.DcisionAI_Model_Builder_v1 import create_dcisionai_model_builder
    from src.shared.tools.solver import create_shared_solver_tool
    TOOLS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some tools not available: {e}")
    TOOLS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DcisionAI Platform API",
    description="Modern API for DcisionAI optimization platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str = Field(..., description="User's optimization query")
    domain: str = Field(default="manufacturing", description="Target domain")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class SearchResponse(BaseModel):
    search_id: str
    status: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]

class DomainInfo(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    available: bool

# Available domains
DOMAINS = [
    {
        "id": "manufacturing",
        "name": "Manufacturing",
        "description": "Production scheduling, capacity planning, quality control",
        "icon": "🏭",
        "available": True
    },
    {
        "id": "logistics",
        "name": "Logistics",
        "description": "Supply chain optimization, routing, inventory management",
        "icon": "🚚",
        "available": False
    },
    {
        "id": "finance",
        "name": "Finance",
        "description": "Portfolio optimization, risk management, cost analysis",
        "icon": "💰",
        "available": False
    },
    {
        "id": "healthcare",
        "name": "Healthcare",
        "description": "Resource allocation, scheduling, patient flow optimization",
        "icon": "🏥",
        "available": False
    }
]

# Initialize tools
intent_tool = None
data_tool = None
model_builder = None
solver_tool = None

if TOOLS_AVAILABLE:
    try:
        intent_tool = create_dcisionai_intent_tool_v3()
        data_tool = create_dcisionai_data_tool_v3()
        model_builder = create_dcisionai_model_builder()
        solver_tool = create_shared_solver_tool()
        logger.info("✅ All tools initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize tools: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "DcisionAI Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "tools_available": TOOLS_AVAILABLE
    }

@app.get("/api/domains", response_model=List[DomainInfo])
async def get_domains():
    """Get available optimization domains"""
    return DOMAINS

@app.post("/api/search", response_model=SearchResponse)
async def search_optimization(search_request: SearchRequest, background_tasks: BackgroundTasks):
    """Process optimization search query"""
    search_id = str(uuid.uuid4())
    
    try:
        # Start processing in background
        background_tasks.add_task(process_search, search_id, search_request)
        
        return SearchResponse(
            search_id=search_id,
            status="processing",
            results={},
            metadata={
                "query": search_request.query,
                "domain": search_request.domain,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/{search_id}")
async def get_search_results(search_id: str):
    """Get search results by ID"""
    # This would typically query a database or cache
    # For now, return a mock response
    return {
        "search_id": search_id,
        "status": "completed",
        "results": {
            "intent": {
                "classification": "production_scheduling",
                "confidence": 0.95,
                "reasoning": "Production scheduling optimization query"
            },
            "data_requirements": [
                {
                    "element": "production_costs",
                    "category": "COST_DATA",
                    "priority": "critical",
                    "description": "Cost per unit by product-line"
                }
            ],
            "model": {
                "type": "mixed_integer_programming",
                "variables": 15,
                "constraints": 8
            },
            "solution": {
                "status": "optimal",
                "objective_value": 125000,
                "execution_time": 2.3
            }
        },
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "processing_time": 45.2
        }
    }

async def process_search(search_id: str, search_request: SearchRequest):
    """Background task to process the search"""
    try:
        logger.info(f"Processing search {search_id}: {search_request.query}")
        
        # Step 1: Intent Classification
        if intent_tool:
            intent_result = intent_tool.classify_intent(search_request.query)
            logger.info(f"Intent: {intent_result.primary_intent.value} (confidence: {intent_result.confidence})")
        
        # Step 2: Data Analysis
        if data_tool and intent_tool:
            data_result = data_tool.analyze_data_requirements(
                search_request.query, 
                intent_result.primary_intent.value
            )
            logger.info(f"Data requirements: {len(data_result.query_data_requirements)}")
        
        # Step 3: Model Building
        if model_builder and intent_tool and data_tool:
            model_result = model_builder.build_optimization_model(
                intent_result=intent_result,
                data_result=data_result
            )
            logger.info(f"Model built: {model_result.model.model_type}")
        
        # Step 4: Solve (if model available)
        if solver_tool and model_builder:
            # This would use the model from step 3
            logger.info("Solving optimization model...")
        
        logger.info(f"Search {search_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Search {search_id} failed: {e}")

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tools": {
            "intent_tool": intent_tool is not None,
            "data_tool": data_tool is not None,
            "model_builder": model_builder is not None,
            "solver_tool": solver_tool is not None
        },
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
