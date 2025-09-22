# 🚀 DcisionAI Platform - Public API Reference

## 🎯 **API Overview**

**The DcisionAI Platform Public API provides secure, enterprise-grade access to AI agent capabilities across multiple domains. This API is designed for customer integration, not internal MCP operations.**

## 🔐 **Authentication & Security**

### **Authentication Methods**

#### **1. OIDC/SAML SSO (Enterprise)**
```http
Authorization: Bearer <oidc_token>
X-Tenant-ID: <tenant_id>
```

#### **2. API Key Authentication (Standard)**
```http
X-API-Key: <api_key>
X-Tenant-ID: <tenant_id>
```

#### **3. JWT Token (Legacy)**
```http
Authorization: Bearer <jwt_token>
X-Tenant-ID: <tenant_id>
```

### **Security Headers**
```http
X-Request-ID: <uuid>          # Request correlation
X-Idempotency-Key: <uuid>     # Idempotency control
X-Deadline: <timestamp>        # Request timeout
X-Stream: true                 # Streaming response
```

## 🌐 **API Endpoints**

### **Base URL**
```
Production: https://api.dcisionai.com/v1
Staging:    https://staging-api.dcisionai.com/v1
```

### **1. Runtime API (Core Functionality)**

#### **Invoke Tool/Agent**
```http
POST /v1/invoke
```

**Request Body:**
```json
{
  "domain": "manufacturing",
  "tool": "solver.optimizeSchedule",
  "payload": {
    "plantId": "NJ-01",
    "horizonDays": 7,
    "constraints": ["capacity", "deadlines"]
  },
  "options": {
    "timeout": 30000,
    "stream": false,
    "region": "auto"
  }
}
```

**Response:**
```json
{
  "requestId": "req-9c1f8e2a-4b3d-4e5f-8a9b-1c2d3e4f5a6b",
  "status": "success",
  "result": {
    "schedule": {...},
    "optimizationMetrics": {...}
  },
  "metadata": {
    "executionTime": 2847,
    "region": "us-east-1",
    "cost": 0.0033
  }
}
```

#### **Async Job Management**
```http
POST /v1/jobs                    # Create async job
GET  /v1/jobs/{id}              # Get job status
GET  /v1/jobs/{id}/result       # Get job result
DELETE /v1/jobs/{id}            # Cancel job
```

**Job Creation:**
```json
{
  "domain": "manufacturing",
  "operation": "workflow.optimizeProduction",
  "payload": {...},
  "options": {
    "priority": "high",
    "timeout": 300000,
    "notifications": ["webhook", "email"]
  }
}
```

#### **Tool Discovery**
```http
GET /v1/tools?domain=manufacturing&query=optimization
GET /v1/tools/{tool_id}/schema
```

**Response:**
```json
{
  "tools": [
    {
      "id": "solver.optimizeSchedule",
      "name": "Production Schedule Optimizer",
      "domain": "manufacturing",
      "description": "AI-powered production scheduling optimization",
      "capabilities": ["constraint_solving", "cost_optimization"],
      "inputSchema": {...},
      "outputSchema": {...}
    }
  ]
}
```

#### **Model Information**
```http
GET /v1/models?region=us-east-1
GET /v1/models/{model_id}/capabilities
```

### **2. Control Plane API (Tenant Management)**

#### **Tenant API Key Management**
```http
POST /v1/tenants/{id}/keys              # Create new API key
GET  /v1/tenants/{id}/keys              # List API keys
PUT  /v1/tenants/{id}/keys/{key_id}     # Update API key
DELETE /v1/tenants/{id}/keys/{key_id}   # Revoke API key
```

#### **Tenant Policies & Guardrails**
```http
PUT /v1/tenants/{id}/policies            # Update tenant policies
GET /v1/tenants/{id}/policies            # Get tenant policies
PUT /v1/tenants/{id}/quotas              # Update resource quotas
GET /v1/tenants/{id}/quotas              # Get current usage
```

**Policy Configuration:**
```json
{
  "security": {
    "dataLocality": ["us-east-1", "us-west-2"],
    "encryptionLevel": "AES-256",
    "auditLogging": true
  },
  "performance": {
    "maxConcurrentRequests": 100,
    "rateLimit": {
      "requestsPerMinute": 1000,
      "burstSize": 100
    }
  },
  "cost": {
    "monthlyBudget": 5000,
    "costSafeMode": false,
    "autoThrottling": true
  }
}
```

#### **Tenant Profiles & Configuration**
```http
PUT /v1/tenants/{id}/profiles            # Update inference profiles
GET /v1/tenants/{id}/profiles            # Get current profiles
PUT /v1/tenants/{id}/domains             # Configure domain access
```

### **3. Observability API**

#### **Metrics & Performance**
```http
GET /v1/metrics?tenant={id}&period=1h
GET /v1/metrics/performance?domain=manufacturing
GET /v1/metrics/costs?tenant={id}&period=24h
```

#### **Health & Status**
```http
GET /v1/health                           # Overall system health
GET /v1/health/domains                  # Domain-specific health
GET /v1/health/regions                  # Regional health status
```

#### **Audit & Compliance**
```http
GET /v1/audit/events?tenant={id}&period=24h
GET /v1/audit/events?action=invoke&tool=solver.optimizeSchedule
```

## 📚 **SDK Usage Examples**

### **TypeScript SDK**

#### **Basic Setup**
```typescript
import { DcisionAI } from '@dcisionai/sdk';

const client = new DcisionAI({
  baseUrl: process.env.DCISIONAI_API_URL!,
  auth: { 
    oidc: { token: await getIdToken() } 
  },
  tenantId: "acme-manufacturing",
  options: {
    timeout: 30000,
    retries: 3,
    tracing: true
  }
});
```

#### **Tool Invocation**
```typescript
// Simple tool invocation
const result = await client.invoke({
  domain: "manufacturing",
  tool: "solver.optimizeSchedule",
  payload: {
    plantId: "NJ-01",
    horizonDays: 7
  }
});

// Async job with streaming
const job = await client.createJob({
  domain: "manufacturing",
  operation: "workflow.optimizeProduction",
  payload: { /* large dataset */ },
  options: { stream: true }
});

// Monitor job progress
for await (const update of job.stream()) {
  console.log(`Progress: ${update.progress}%`);
  if (update.status === 'completed') {
    const finalResult = await job.getResult();
    console.log('Final result:', finalResult);
  }
}
```

#### **Error Handling**
```typescript
try {
  const result = await client.invoke({
    domain: "manufacturing",
    tool: "solver.optimizeSchedule",
    payload: { plantId: "NJ-01" }
  });
} catch (error) {
  if (error instanceof DcisionAIError) {
    switch (error.code) {
      case 'RATE_LIMITED':
        await delay(1000); // Wait and retry
        break;
      case 'QUOTA_EXCEEDED':
        console.error('Monthly quota exceeded');
        break;
      case 'TOOL_UNAVAILABLE':
        console.error('Tool temporarily unavailable');
        break;
    }
  }
}
```

### **Python SDK**

#### **Basic Setup**
```python
from dcisionai import DcisionAI

client = DcisionAI(
    base_url=os.environ["DCISIONAI_API_URL"],
    auth={"oidc": {"token": get_id_token()}},
    tenant_id="acme-manufacturing",
    options={
        "timeout": 30000,
        "retries": 3,
        "tracing": True
    }
)
```

#### **Tool Invocation**
```python
# Simple tool invocation
result = await client.invoke(
    domain="manufacturing",
    tool="solver.optimizeSchedule",
    payload={
        "plantId": "NJ-01",
        "horizonDays": 7
    }
)

# Async job with streaming
job = await client.create_job(
    domain="manufacturing",
    operation="workflow.optimizeProduction",
    payload={},  # large dataset
    options={"stream": True}
)

# Monitor job progress
async for update in job.stream():
    print(f"Progress: {update.progress}%")
    if update.status == "completed":
        final_result = await job.get_result()
        print("Final result:", final_result)
```

## 🔒 **Security & Compliance**

### **Data Locality**
- **Enforced**: API automatically routes requests to configured regions
- **Configurable**: Per-tenant data locality policies
- **Auditable**: All cross-region data movements logged

### **Encryption**
- **At Rest**: AES-256 encryption with per-tenant KMS keys
- **In Transit**: TLS 1.3 for all communications
- **Key Rotation**: Automatic KMS key rotation every 90 days

### **Access Control**
- **Tenant Isolation**: Complete data and process separation
- **Role-Based Access**: Fine-grained permissions per tool/domain
- **API Key Scoping**: Limited API key permissions per use case

### **Audit & Compliance**
- **Immutable Logs**: All API calls logged with S3 object lock
- **Compliance Ready**: SOX, GDPR, ISO 27001 compliant logging
- **Real-time Monitoring**: Security events trigger immediate alerts

## 📊 **Rate Limiting & Quotas**

### **Default Limits**
```json
{
  "perTenant": {
    "requestsPerMinute": 1000,
    "requestsPerHour": 50000,
    "requestsPerDay": 1000000,
    "concurrentRequests": 100
  },
  "perTool": {
    "requestsPerMinute": 100,
    "timeout": 300000
  }
}
```

### **Quota Management**
- **Automatic Throttling**: Requests throttled when quotas exceeded
- **Cost Safe Mode**: Force local region only when budget exceeded
- **Graceful Degradation**: Return cached results when possible

## 🚀 **Performance & Reliability**

### **SLA Commitments**
- **Response Time**: P95 < 2 seconds for tool invocation
- **Availability**: 99.9% uptime SLA
- **Throughput**: 1000+ concurrent requests per tenant

### **Optimization Features**
- **Intelligent Routing**: Automatic region selection based on load/cost
- **Caching**: Multi-level caching for repeated requests
- **Connection Pooling**: Optimized connection management

### **Error Handling**
- **Retry Logic**: Automatic retries with exponential backoff
- **Circuit Breaker**: Prevents cascade failures
- **Fallback Strategies**: Graceful degradation when tools unavailable

## 📋 **API Versioning & Deprecation**

### **Versioning Strategy**
- **Major Versions**: Breaking changes require new major version
- **Minor Versions**: New features added to existing major version
- **Deprecation Policy**: 12-month notice for breaking changes

### **Current Versions**
- **v1**: Current stable API (recommended for production)
- **v1-beta**: Beta features (use with caution)
- **v0**: Legacy API (deprecated, migration required)

## 🔧 **SDK Installation & Setup**

### **TypeScript/Node.js**
```bash
npm install @dcisionai/sdk
# or
yarn add @dcisionai/sdk
```

### **Python**
```bash
pip install dcisionai-sdk
# or
poetry add dcisionai-sdk
```

### **Environment Variables**
```bash
# Required
DCISIONAI_API_URL=https://api.dcisionai.com/v1
DCISIONAI_TENANT_ID=your-tenant-id

# Authentication (choose one)
DCISIONAI_OIDC_TOKEN=your-oidc-token
DCISIONAI_API_KEY=your-api-key
DCISIONAI_JWT_TOKEN=your-jwt-token
```

## 📞 **Support & Resources**

### **Documentation**
- **API Reference**: This document
- **SDK Guides**: Language-specific integration guides
- **Examples**: Complete working examples for common use cases
- **Tutorials**: Step-by-step integration tutorials

### **Support Channels**
- **Developer Portal**: https://developers.dcisionai.com
- **API Status**: https://status.dcisionai.com
- **Support Email**: api-support@dcisionai.com
- **Community**: https://community.dcisionai.com

### **Getting Help**
- **Quick Start**: 5-minute setup guide
- **Integration Support**: Dedicated support for enterprise customers
- **Training**: On-site and virtual training sessions

---

**Last Updated**: September 2, 2025  
**API Version**: v1.0.0  
**SDK Version**: 1.0.0  
**Status**: Production Ready ✅
