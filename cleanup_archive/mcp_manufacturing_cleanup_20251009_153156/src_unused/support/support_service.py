#!/usr/bin/env python3
"""
DcisionAI Support Service
========================

Customer support service for the DcisionAI platform.
Handles support tickets, knowledge base, and customer assistance.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Support Service | %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="DcisionAI Support Service",
    description="Customer support service for DcisionAI platform",
    version="1.0.0"
)

# Pydantic models
class SupportTicket(BaseModel):
    ticket_id: str
    customer_id: str
    subject: str
    description: str
    priority: str = "medium"
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class SupportResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# In-memory storage (in production, use a database)
support_tickets: Dict[str, SupportTicket] = {}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DcisionAI Support Service",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "DcisionAI Support Service",
        "version": "1.0.0",
        "description": "Customer support service for DcisionAI platform",
        "endpoints": {
            "health": "/health",
            "tickets": "/tickets",
            "knowledge_base": "/knowledge-base"
        }
    }

@app.post("/tickets", response_model=SupportResponse)
async def create_support_ticket(ticket: SupportTicket):
    """Create a new support ticket."""
    try:
        support_tickets[ticket.ticket_id] = ticket
        logger.info(f"Created support ticket: {ticket.ticket_id}")
        
        return SupportResponse(
            success=True,
            message="Support ticket created successfully",
            data={"ticket_id": ticket.ticket_id}
        )
    except Exception as e:
        logger.error(f"Error creating support ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to create support ticket")

@app.get("/tickets/{ticket_id}", response_model=SupportTicket)
async def get_support_ticket(ticket_id: str):
    """Get a specific support ticket."""
    if ticket_id not in support_tickets:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    
    return support_tickets[ticket_id]

@app.get("/tickets", response_model=List[SupportTicket])
async def list_support_tickets(customer_id: Optional[str] = None):
    """List support tickets, optionally filtered by customer."""
    tickets = list(support_tickets.values())
    
    if customer_id:
        tickets = [t for t in tickets if t.customer_id == customer_id]
    
    return tickets

@app.get("/knowledge-base")
async def get_knowledge_base():
    """Get knowledge base articles."""
    return {
        "articles": [
            {
                "id": "getting-started",
                "title": "Getting Started with DcisionAI MCP Server",
                "category": "onboarding",
                "content": "Learn how to connect to and use the DcisionAI MCP server..."
            },
            {
                "id": "api-keys",
                "title": "Managing API Keys",
                "category": "authentication",
                "content": "How to generate, rotate, and manage your API keys..."
            },
            {
                "id": "troubleshooting",
                "title": "Common Issues and Solutions",
                "category": "troubleshooting",
                "content": "Solutions to common problems and error messages..."
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
