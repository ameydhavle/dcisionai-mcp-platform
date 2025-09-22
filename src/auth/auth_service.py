#!/usr/bin/env python3
"""
DcisionAI Authentication Service
===============================

Authentication service for the DcisionAI platform.
Handles API key management, customer authentication, and authorization.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Auth Service | %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="DcisionAI Authentication Service",
    description="Authentication and authorization service for DcisionAI platform",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Pydantic models
class Customer(BaseModel):
    customer_id: str
    email: str
    name: str
    company: Optional[str] = None
    tier: str = "free"
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "active"

class APIKey(BaseModel):
    key_id: str
    customer_id: str
    key_hash: str
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    status: str = "active"

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# In-memory storage (in production, use a database)
customers: Dict[str, Customer] = {}
api_keys: Dict[str, APIKey] = {}
key_to_customer: Dict[str, str] = {}  # Maps API key hash to customer ID

class APIKeyManager:
    """API Key management system."""
    
    def __init__(self):
        self.customers = customers
        self.api_keys = api_keys
        self.key_to_customer = key_to_customer
    
    def generate_api_key(self, customer_id: str, name: str) -> str:
        """Generate a new API key for a customer."""
        api_key = f"dai_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        key_id = f"key_{secrets.token_urlsafe(16)}"
        
        api_key_info = APIKey(
            key_id=key_id,
            customer_id=customer_id,
            key_hash=key_hash,
            name=name
        )
        
        self.api_keys[key_id] = api_key_info
        self.key_to_customer[key_hash] = customer_id
        
        logger.info(f"Generated API key for customer {customer_id}")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Customer:
        """Validate an API key and return customer information."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash not in self.key_to_customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        customer_id = self.key_to_customer[key_hash]
        
        if customer_id not in self.customers:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Customer not found"
            )
        
        customer = self.customers[customer_id]
        
        if customer.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Customer account is inactive"
            )
        
        # Update usage statistics
        for key_info in self.api_keys.values():
            if key_info.key_hash == key_hash:
                key_info.last_used = datetime.now()
                key_info.usage_count += 1
                break
        
        return customer

# Initialize API key manager
api_key_manager = APIKeyManager()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DcisionAI Authentication Service",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "DcisionAI Authentication Service",
        "version": "1.0.0",
        "description": "Authentication and authorization service for DcisionAI platform",
        "endpoints": {
            "health": "/health",
            "customers": "/customers",
            "api-keys": "/api-keys"
        }
    }

@app.post("/customers", response_model=AuthResponse)
async def create_customer(customer: Customer):
    """Create a new customer."""
    try:
        customers[customer.customer_id] = customer
        logger.info(f"Created customer: {customer.customer_id}")
        
        return AuthResponse(
            success=True,
            message="Customer created successfully",
            data={"customer_id": customer.customer_id}
        )
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail="Failed to create customer")

@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    """Get a specific customer."""
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customers[customer_id]

@app.post("/api-keys", response_model=AuthResponse)
async def create_api_key(customer_id: str, name: str):
    """Create a new API key for a customer."""
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        api_key = api_key_manager.generate_api_key(customer_id, name)
        
        return AuthResponse(
            success=True,
            message="API key created successfully",
            data={"api_key": api_key, "name": name}
        )
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")

@app.get("/api-keys/{customer_id}", response_model=List[APIKey])
async def list_customer_api_keys(customer_id: str):
    """List API keys for a specific customer."""
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_keys = [key for key in api_keys.values() if key.customer_id == customer_id]
    return customer_keys

async def get_current_customer(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Customer:
    """Get current customer from API key."""
    api_key = credentials.credentials
    return api_key_manager.validate_api_key(api_key)

@app.get("/me", response_model=Customer)
async def get_current_customer_info(customer: Customer = Depends(get_current_customer)):
    """Get current customer information."""
    return customer

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
