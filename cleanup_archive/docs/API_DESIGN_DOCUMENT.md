# 🚀 DcisionAI Platform - API Design Document

## 🎯 **Document Overview**

**This document defines the complete API surface for the DcisionAI Platform, enabling customer integration through RESTful endpoints, comprehensive authentication, and enterprise-grade features.**

**Status**: Phase 3A - Customer Experience (SDK/API)  
**Priority**: 🔥 HIGH PRIORITY  
**Target**: Enterprise customers, CIOs, CTOs  

## 🏗️ **API Architecture Overview**

### **High-Level Architecture**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Customer      │    │   API Gateway    │    │   DcisionAI     │
│   Applications  │───▶│   (AWS Gateway)  │───▶│   MCP Server    │
│   (SDK/API)    │    │                  │    │   (Port 8000)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **API Layers**
1. **Runtime API** - Tool invocation, job management, real-time execution
2. **Control Plane API** - Tenant management, policies, quotas, monitoring
3. **Observability API** - Metrics, health checks, audit logs, performance
4. **Management API** - Configuration, deployment, scaling

## 🌐 **API Base URLs**

### **Environment-Specific Endpoints**
- **Development**: `https://api-dev.dcisionai.com`
- **Staging**: `https://api-staging.dcisionai.com`
- **Production**: `https://api.dcisionai.com`
- **Enterprise**: `https://api-enterprise.dcisionai.com`

### **API Versioning**
- **Current Version**: `v1`
- **Version Header**: `X-API-Version: v1`
- **URL Pattern**: `/v1/{resource}`

## 🔐 **Authentication & Security**

### **Authentication Methods**

#### **1. API Key Authentication (Primary)**
```http
Authorization: Bearer dcisionai_live_1234567890abcdef
X-API-Key: dcisionai_live_1234567890abcdef
```

#### **2. OAuth 2.0 (Enterprise)**
```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### **3. JWT Tokens (Custom)**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Security Features**
- **TLS 1.3** - End-to-end encryption
- **Rate Limiting** - Per-tenant, per-endpoint throttling
- **IP Whitelisting** - Enterprise IP restrictions
- **Request Signing** - HMAC-SHA256 for sensitive operations
- **CORS** - Configurable cross-origin policies

## 📡 **Runtime API Endpoints**

### **1. Tool Invocation API**

#### **Invoke Tool**
```http
POST /v1/invoke
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "tool_name": "dcisionai_intent_tool",
  "parameters": {
    "query": "Analyze manufacturing efficiency",
    "context": "automotive_industry",
    "constraints": ["cost_optimization", "quality_maintenance"]
  },
  "execution_mode": "synchronous",
  "timeout": 300,
  "metadata": {
    "request_id": "req_123456",
    "customer_id": "cust_789",
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "execution_id": "exec_123456",
  "result": {
    "intent": "optimize_manufacturing_process",
    "confidence": 0.95,
    "recommendations": [
      "Implement predictive maintenance",
      "Optimize supply chain logistics",
      "Enhance quality control automation"
    ],
    "estimated_impact": {
      "cost_reduction": "15-20%",
      "efficiency_gain": "25-30%",
      "quality_improvement": "10-15%"
    }
  },
  "execution_time": 2.45,
  "timestamp": "2025-09-02T20:48:46Z"
}
```

#### **Async Tool Execution**
```http
POST /v1/invoke/async
Content-Type: application/json

{
  "tool_name": "dcisionai_model_builder",
  "parameters": {
    "model_type": "manufacturing_optimization",
    "training_data": "s3://bucket/data/manufacturing.csv",
    "hyperparameters": {
      "learning_rate": 0.001,
      "epochs": 1000,
      "batch_size": 32
    }
  },
  "callback_url": "https://customer.com/webhooks/dcisionai",
  "webhook_secret": "webhook_secret_123"
}
```

**Response:**
```json
{
  "status": "accepted",
  "job_id": "job_123456",
  "estimated_completion": "2025-09-02T21:48:46Z",
  "status_url": "/v1/jobs/job_123456",
  "webhook_url": "/v1/webhooks/job_123456"
}
```

### **2. Job Management API**

#### **Get Job Status**
```http
GET /v1/jobs/{job_id}
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "job_id": "job_123456",
  "status": "in_progress",
  "progress": {
    "current_step": "model_training",
    "percentage": 65,
    "estimated_remaining": "00:15:30"
  },
  "result": null,
  "error": null,
  "created_at": "2025-09-02T20:48:46Z",
  "updated_at": "2025-09-02T21:03:16Z"
}
```

#### **List Jobs**
```http
GET /v1/jobs?status=completed&limit=50&offset=0
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "job_123456",
      "tool_name": "dcisionai_model_builder",
      "status": "completed",
      "created_at": "2025-09-02T20:48:46Z",
      "completed_at": "2025-09-02T21:18:46Z",
      "execution_time": 1800
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### **3. Tool Discovery API**

#### **List Available Tools**
```http
GET /v1/tools
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "tools": [
    {
      "name": "dcisionai_intent_tool",
      "display_name": "Intent Analysis Tool",
      "description": "Analyzes user queries to determine intent and provide recommendations",
      "version": "1.0.0",
      "category": "analysis",
      "capabilities": ["intent_detection", "recommendation_generation"],
      "input_schema": {
        "type": "object",
        "properties": {
          "query": {"type": "string", "required": true},
          "context": {"type": "string"},
          "constraints": {"type": "array", "items": {"type": "string"}}
        }
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "intent": {"type": "string"},
          "confidence": {"type": "number"},
          "recommendations": {"type": "array", "items": {"type": "string"}}
        }
      },
      "rate_limit": "1000/hour",
      "timeout": 300
    }
  ]
}
```

#### **Get Tool Details**
```http
GET /v1/tools/{tool_name}
Authorization: Bearer {api_key}
```

## 🎛️ **Control Plane API Endpoints**

### **1. Tenant Management**

#### **Create Tenant**
```http
POST /v1/tenants
Content-Type: application/json
Authorization: Bearer {admin_api_key}

{
  "tenant_id": "acme_corp",
  "name": "ACME Corporation",
  "contact_email": "admin@acme.com",
  "plan": "enterprise",
  "settings": {
    "max_concurrent_jobs": 100,
    "rate_limit": "10000/hour",
    "storage_limit_gb": 1000,
    "custom_domain": "api.acme.com"
  }
}
```

#### **Update Tenant**
```http
PUT /v1/tenants/{tenant_id}
Content-Type: application/json

{
  "settings": {
    "max_concurrent_jobs": 150,
    "rate_limit": "15000/hour"
  }
}
```

### **2. API Key Management**

#### **Create API Key**
```http
POST /v1/tenants/{tenant_id}/api-keys
Content-Type: application/json

{
  "name": "Production API Key",
  "permissions": ["read", "write", "admin"],
  "expires_at": "2026-09-02T00:00:00Z",
  "ip_restrictions": ["192.168.1.0/24", "10.0.0.0/8"]
}
```

**Response:**
```json
{
  "api_key": "dcisionai_live_1234567890abcdef",
  "api_key_id": "key_123456",
  "created_at": "2025-09-02T20:48:46Z",
  "expires_at": "2026-09-02T00:00:00Z"
}
```

#### **List API Keys**
```http
GET /v1/tenants/{tenant_id}/api-keys
Authorization: Bearer {api_key}
```

### **3. Rate Limiting & Quotas**

#### **Get Current Usage**
```http
GET /v1/tenants/{tenant_id}/usage
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "current_period": "2025-09",
  "api_calls": {
    "used": 45000,
    "limit": 100000,
    "remaining": 55000
  },
  "storage": {
    "used_gb": 250.5,
    "limit_gb": 1000,
    "remaining_gb": 749.5
  },
  "concurrent_jobs": {
    "current": 15,
    "limit": 100,
    "available": 85
  }
}
```

## 📊 **Observability API Endpoints**

### **1. Health Checks**

#### **Service Health**
```http
GET /v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-02T20:48:46Z",
  "version": "1.0.0",
  "services": {
    "api_gateway": "healthy",
    "mcp_server": "healthy",
    "database": "healthy",
    "cache": "healthy"
  },
  "uptime": "99.98%",
  "response_time": "45ms"
}
```

#### **Detailed Health Check**
```http
GET /v1/health/detailed
Authorization: Bearer {api_key}
```

### **2. Metrics & Analytics**

#### **Get Metrics**
```http
GET /v1/metrics?metric=api_calls&period=24h&granularity=1h
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "metric": "api_calls",
  "period": "24h",
  "granularity": "1h",
  "data": [
    {
      "timestamp": "2025-09-02T00:00:00Z",
      "value": 1250,
      "tenant_id": "acme_corp"
    },
    {
      "timestamp": "2025-09-02T01:00:00Z",
      "value": 980,
      "tenant_id": "acme_corp"
    }
  ]
}
```

### **3. Audit Logs**

#### **Get Audit Logs**
```http
GET /v1/audit-logs?action=api_call&tenant_id=acme_corp&limit=100
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-09-02T20:48:46Z",
      "action": "api_call",
      "tenant_id": "acme_corp",
      "user_id": "user_123",
      "ip_address": "192.168.1.100",
      "endpoint": "/v1/invoke",
      "status": "success",
      "execution_time": 2450,
      "request_id": "req_123456"
    }
  ],
  "pagination": {
    "total": 1500,
    "limit": 100,
    "offset": 0
  }
}
```

## 🔄 **Webhook Integration**

### **Webhook Configuration**

#### **Create Webhook**
```http
POST /v1/webhooks
Content-Type: application/json

{
  "name": "Job Completion Webhook",
  "url": "https://customer.com/webhooks/dcisionai",
  "events": ["job.completed", "job.failed"],
  "secret": "webhook_secret_123",
  "retry_policy": {
    "max_retries": 3,
    "backoff_multiplier": 2,
    "initial_delay": 1000
  }
}
```

#### **Webhook Payload Example**
```json
{
  "event": "job.completed",
  "timestamp": "2025-09-02T21:18:46Z",
  "data": {
    "job_id": "job_123456",
    "tool_name": "dcisionai_model_builder",
    "status": "completed",
    "result": {
      "model_id": "model_789",
      "accuracy": 0.95,
      "training_time": 1800
    }
  },
  "signature": "sha256=abc123..."
}
```

## 📋 **Error Handling**

### **Standard Error Response Format**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Limit: 1000/hour, Used: 1000, Reset: 2025-09-02T21:00:00Z",
    "details": {
      "limit": 1000,
      "used": 1000,
      "reset_at": "2025-09-02T21:00:00Z"
    },
    "request_id": "req_123456",
    "timestamp": "2025-09-02T20:48:46Z"
  }
}
```

### **HTTP Status Codes**
- **200** - Success
- **201** - Created
- **400** - Bad Request
- **401** - Unauthorized
- **403** - Forbidden
- **404** - Not Found
- **429** - Too Many Requests
- **500** - Internal Server Error
- **503** - Service Unavailable

### **Error Codes**
- **AUTHENTICATION_FAILED** - Invalid API key or token
- **RATE_LIMIT_EXCEEDED** - Rate limit exceeded
- **QUOTA_EXCEEDED** - Storage or job quota exceeded
- **TOOL_NOT_FOUND** - Requested tool doesn't exist
- **INVALID_PARAMETERS** - Invalid input parameters
- **EXECUTION_TIMEOUT** - Tool execution timed out
- **SERVICE_UNAVAILABLE** - Service temporarily unavailable

## 📈 **Rate Limiting & Quotas**

### **Rate Limiting Strategy**
- **Per-Tenant Limits**: Configurable per tenant
- **Per-Endpoint Limits**: Different limits for different endpoints
- **Burst Allowance**: Allow short bursts above limit
- **Sliding Window**: Rolling time window for rate calculation

### **Quota Management**
- **API Calls**: Monthly API call limits
- **Storage**: GB storage limits
- **Concurrent Jobs**: Maximum concurrent job execution
- **Data Transfer**: Monthly data transfer limits

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 750
X-RateLimit-Reset: 2025-09-02T21:00:00Z
X-RateLimit-Reset-In: 671
```

## 🔒 **Security & Compliance**

### **Data Protection**
- **Encryption at Rest**: AES-256 encryption for stored data
- **Encryption in Transit**: TLS 1.3 for all communications
- **Data Residency**: Configurable data storage locations
- **Data Retention**: Configurable data retention policies

### **Access Control**
- **Role-Based Access Control (RBAC)**: Fine-grained permissions
- **API Key Scopes**: Limited API key permissions
- **IP Restrictions**: Configurable IP whitelisting
- **Audit Logging**: Comprehensive access logging

### **Compliance**
- **SOC 2 Type II**: Security and availability controls
- **GDPR**: Data protection and privacy compliance
- **HIPAA**: Healthcare data protection (enterprise plans)
- **ISO 27001**: Information security management

## 🚀 **Performance & Scalability**

### **Performance Targets**
- **API Response Time**: < 100ms for simple operations
- **Tool Execution**: < 5 seconds for most tools
- **Availability**: 99.9% uptime SLA
- **Throughput**: 10,000+ requests per second

### **Scalability Features**
- **Auto-scaling**: Automatic scaling based on load
- **Load Balancing**: Global load balancing
- **Caching**: Multi-layer caching strategy
- **CDN**: Global content delivery network

## 📚 **SDK Support**

### **Supported Languages**
- **TypeScript/Node.js** - Full SDK with types
- **Python** - Full SDK with async support
- **Java** - Enterprise SDK
- **Go** - High-performance SDK
- **C#/.NET** - Windows ecosystem support

### **SDK Features**
- **Type Safety**: Full TypeScript definitions
- **Async Support**: Promise-based async operations
- **Error Handling**: Comprehensive error handling
- **Retry Logic**: Automatic retry with backoff
- **Rate Limiting**: Built-in rate limit handling

## 🔧 **Configuration & Deployment**

### **Environment Configuration**
```json
{
  "api_base_url": "https://api.dcisionai.com",
  "api_version": "v1",
  "timeout": 30000,
  "retry_attempts": 3,
  "retry_delay": 1000,
  "rate_limit_handling": "automatic"
}
```

### **Deployment Options**
- **Public Cloud**: AWS, Azure, GCP
- **Private Cloud**: On-premises deployment
- **Hybrid**: Mixed cloud and on-premises
- **Edge**: Edge computing deployment

## 📅 **Implementation Timeline**

### **Week 1: API Design & Architecture** ✅
- [x] **API Design Document** - Complete endpoint specification
- [x] **OpenAPI Schema** - Generate OpenAPI 3.0 specification
- [x] **Authentication Flow** - OIDC/SAML integration design
- [x] **Rate Limiting** - Design tenant-based rate limiting

### **Week 2: API Gateway Implementation**
- [ ] **AWS API Gateway Setup** - Configure API Gateway with Lambda authorizers
- [ ] **Authentication Middleware** - Implement OIDC/SAML validation
- [ ] **Rate Limiting** - Implement tenant-based throttling
- [ ] **Request Validation** - Input/output validation middleware

### **Week 3: Core API Endpoints**
- [ ] **Runtime API** - `/v1/invoke`, `/v1/jobs`, `/v1/tools`
- [ ] **Control Plane API** - Tenant management, policies, quotas
- [ ] **Observability API** - Metrics, health, audit logs
- [ ] **Error Handling** - Comprehensive error responses

### **Week 4: SDK Development**
- [ ] **TypeScript SDK** - Core functionality and error handling
- [ ] **Python SDK** - Core functionality and error handling
- [ ] **SDK Testing** - Unit tests and integration tests
- [ ] **Documentation** - SDK usage guides and examples

## 🎯 **Success Criteria**

### **API Requirements**
- **Endpoint Coverage**: 100% of planned endpoints implemented
- **Response Time**: < 100ms for 95% of requests
- **Availability**: 99.9% uptime during testing
- **Error Rate**: < 1% error rate

### **SDK Requirements**
- **Language Coverage**: TypeScript and Python SDKs complete
- **Feature Parity**: SDKs support all API features
- **Documentation**: Complete API and SDK documentation
- **Examples**: Working code examples for all features

### **Integration Requirements**
- **Authentication**: OAuth 2.0 and API key support
- **Rate Limiting**: Per-tenant rate limiting working
- **Webhooks**: Webhook delivery system operational
- **Monitoring**: Metrics and health checks working

---

**Document Version**: 1.0.0  
**Last Updated**: September 2, 2025  
**Next Review**: September 9, 2025  
**Status**: Ready for implementation
