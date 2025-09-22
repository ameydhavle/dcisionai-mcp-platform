# 📚 DcisionAI Platform - SDK Implementation Guides

## 🎯 **SDK Overview**

**The DcisionAI Platform provides enterprise-grade SDKs for TypeScript/Node.js and Python, enabling customers to integrate AI capabilities quickly and securely. These SDKs handle authentication, retries, tracing, and error handling automatically.**

## 🚀 **TypeScript/Node.js SDK**

### **Installation & Setup**

#### **1. Package Installation**
```bash
# Using npm
npm install @dcisionai/sdk

# Using yarn
yarn add @dcisionai/sdk

# Using pnpm
pnpm add @dcisionai/sdk
```

#### **2. Environment Configuration**
```bash
# Required environment variables
export DCISIONAI_API_URL="https://api.dcisionai.com/v1"
export DCISIONAI_TENANT_ID="your-tenant-id"

# Authentication (choose one)
export DCISIONAI_OIDC_TOKEN="your-oidc-token"
export DCISIONAI_API_KEY="your-api-key"
export DCISIONAI_JWT_TOKEN="your-jwt-token"
```

#### **3. Basic Client Setup**
```typescript
import { DcisionAI, DcisionAIError } from '@dcisionai/sdk';

// Initialize client with OIDC authentication
const client = new DcisionAI({
  baseUrl: process.env.DCISIONAI_API_URL!,
  auth: { 
    oidc: { token: await getIdToken() } 
  },
  tenantId: process.env.DCISIONAI_TENANT_ID!,
  options: {
    timeout: 30000,
    retries: 3,
    tracing: true,
    idempotency: true
  }
});

// Initialize client with API key authentication
const client = new DcisionAI({
  baseUrl: process.env.DCISIONAI_API_URL!,
  auth: { 
    apiKey: process.env.DCISIONAI_API_KEY! 
  },
  tenantId: process.env.DCISIONAI_TENANT_ID!,
  options: {
    timeout: 30000,
    retries: 3,
    tracing: true
  }
});
```

### **Core API Usage**

#### **1. Tool Invocation**
```typescript
// Simple tool invocation
try {
  const result = await client.invoke({
    domain: "manufacturing",
    tool: "solver.optimizeSchedule",
    payload: {
      plantId: "NJ-01",
      horizonDays: 7,
      constraints: ["capacity", "deadlines"]
    },
    options: {
      timeout: 30000,
      stream: false,
      region: "auto"
    }
  });

  console.log("Optimization result:", result.result);
  console.log("Execution time:", result.metadata.executionTime);
  console.log("Cost:", result.metadata.cost);

} catch (error) {
  if (error instanceof DcisionAIError) {
    switch (error.code) {
      case 'RATE_LIMITED':
        console.error('Rate limit exceeded, retrying...');
        await delay(1000);
        break;
      case 'QUOTA_EXCEEDED':
        console.error('Monthly quota exceeded');
        break;
      case 'TOOL_UNAVAILABLE':
        console.error('Tool temporarily unavailable');
        break;
      case 'AUTHENTICATION_FAILED':
        console.error('Authentication failed, check credentials');
        break;
      default:
        console.error('Unexpected error:', error.message);
    }
  }
}

// Tool invocation with streaming
try {
  const stream = await client.invoke({
    domain: "manufacturing",
    tool: "workflow.optimizeProduction",
    payload: { plantId: "NJ-01" },
    options: { stream: true }
  });

  for await (const chunk of stream) {
    if (chunk.type === 'progress') {
      console.log(`Progress: ${chunk.data.progress}%`);
    } else if (chunk.type === 'result') {
      console.log('Final result:', chunk.data);
    }
  }

} catch (error) {
  console.error('Streaming invocation failed:', error);
}
```

#### **2. Async Job Management**
```typescript
// Create async job
try {
  const job = await client.createJob({
    domain: "manufacturing",
    operation: "workflow.optimizeProduction",
    payload: {
      plantId: "NJ-01",
      productionData: largeDataset,
      optimizationParams: optimizationConfig
    },
    options: {
      priority: "high",
      timeout: 300000, // 5 minutes
      notifications: ["webhook", "email"],
      webhookUrl: "https://your-webhook.com/callback"
    }
  });

  console.log("Job created:", job.id);
  console.log("Status:", job.status);

} catch (error) {
  console.error('Job creation failed:', error);
}

// Monitor job progress
try {
  const jobId = "job-12345";
  
  // Get job status
  const status = await client.getJobStatus(jobId);
  console.log("Job status:", status);

  // Stream job updates
  const updates = await client.streamJobUpdates(jobId);
  for await (const update of updates) {
    console.log(`Update: ${update.type} - ${update.data}`);
    
    if (update.type === 'completed') {
      const result = await client.getJobResult(jobId);
      console.log('Job result:', result);
      break;
    }
  }

} catch (error) {
  console.error('Job monitoring failed:', error);
}

// Cancel job
try {
  await client.cancelJob(jobId);
  console.log("Job cancelled successfully");

} catch (error) {
  console.error('Job cancellation failed:', error);
}
```

#### **3. Tool Discovery & Metadata**
```typescript
// Discover available tools
try {
  const tools = await client.discoverTools({
    domain: "manufacturing",
    query: "optimization"
  });

  console.log("Available tools:");
  tools.forEach(tool => {
    console.log(`- ${tool.name}: ${tool.description}`);
    console.log(`  Capabilities: ${tool.capabilities.join(', ')}`);
  });

} catch (error) {
  console.error('Tool discovery failed:', error);
}

// Get tool schema
try {
  const toolId = "solver.optimizeSchedule";
  const schema = await client.getToolSchema(toolId);
  
  console.log("Input schema:", schema.inputSchema);
  console.log("Output schema:", schema.outputSchema);
  console.log("Examples:", schema.examples);

} catch (error) {
  console.error('Schema retrieval failed:', error);
}
```

#### **4. Tenant Management**
```typescript
// Get tenant policies
try {
  const policies = await client.getTenantPolicies();
  
  console.log("Data locality:", policies.dataProtection.dataLocality);
  console.log("Rate limits:", policies.rateLimiting);
  console.log("Cost budget:", policies.cost.monthlyBudget);

} catch (error) {
  console.error('Policy retrieval failed:', error);
}

// Update tenant policies
try {
  const updatedPolicies = await client.updateTenantPolicies({
    dataProtection: {
      dataLocality: ["us-east-1", "us-west-2"],
      encryptionLevel: "AES-256"
    },
    rateLimiting: {
      requestsPerMinute: 2000,
      burstSize: 200
    }
  });

  console.log("Policies updated successfully");

} catch (error) {
  console.error('Policy update failed:', error);
}

// Get tenant quotas and usage
try {
  const quotas = await client.getTenantQuotas();
  
  console.log("Current usage:", quotas.currentUsage);
  console.log("Limits:", quotas.limits);
  console.log("Remaining:", quotas.remaining);

} catch (error) {
  console.error('Quota retrieval failed:', error);
}
```

### **Advanced Features**

#### **1. Error Handling & Retries**
```typescript
import { DcisionAI, DcisionAIError, RetryStrategy } from '@dcisionai/sdk';

// Custom retry strategy
const customRetryStrategy: RetryStrategy = {
  maxRetries: 5,
  baseDelay: 1000,
  maxDelay: 30000,
  backoffMultiplier: 2,
  retryableErrors: ['RATE_LIMITED', 'SERVICE_UNAVAILABLE', 'TIMEOUT'],
  onRetry: (error, attempt, delay) => {
    console.log(`Retry attempt ${attempt} after ${delay}ms due to: ${error.message}`);
  }
};

const client = new DcisionAI({
  baseUrl: process.env.DCISIONAI_API_URL!,
  auth: { apiKey: process.env.DCISIONAI_API_KEY! },
  tenantId: process.env.DCISIONAI_TENANT_ID!,
  options: {
    retryStrategy: customRetryStrategy,
    timeout: 60000
  }
});

// Error handling with custom logic
try {
  const result = await client.invoke({
    domain: "manufacturing",
    tool: "solver.optimizeSchedule",
    payload: { plantId: "NJ-01" }
  });

} catch (error) {
  if (error instanceof DcisionAIError) {
    // Handle specific error types
    switch (error.code) {
      case 'RATE_LIMITED':
        await handleRateLimit(error);
        break;
      case 'QUOTA_EXCEEDED':
        await handleQuotaExceeded(error);
        break;
      case 'AUTHENTICATION_FAILED':
        await handleAuthFailure(error);
        break;
      case 'VALIDATION_ERROR':
        await handleValidationError(error);
        break;
      default:
        await handleUnexpectedError(error);
    }
  } else {
    // Handle unexpected errors
    console.error('Unexpected error:', error);
  }
}

async function handleRateLimit(error: DcisionAIError) {
  const retryAfter = error.headers?.['retry-after'];
  if (retryAfter) {
    const delay = parseInt(retryAfter) * 1000;
    console.log(`Rate limited, waiting ${delay}ms`);
    await new Promise(resolve => setTimeout(resolve, delay));
  }
}

async function handleQuotaExceeded(error: DcisionAIError) {
  console.error('Monthly quota exceeded');
  // Notify administrators or switch to cost-safe mode
}
```

#### **2. Idempotency & Deduplication**
```typescript
import { v4 as uuidv4 } from 'uuid';

// Generate idempotency key
const idempotencyKey = uuidv4();

try {
  const result = await client.invoke({
    domain: "manufacturing",
    tool: "solver.optimizeSchedule",
    payload: { plantId: "NJ-01" },
    idempotencyKey: idempotencyKey
  });

  console.log("Request processed with idempotency key:", idempotencyKey);

} catch (error) {
  if (error instanceof DcisionAIError && error.code === 'DUPLICATE_REQUEST') {
    console.log("Request already processed, retrieving result...");
    // Handle duplicate request
  }
}
```

#### **3. Tracing & Observability**
```typescript
import { trace, context } from '@opentelemetry/api';

// Create trace span
const tracer = trace.getTracer('dcisionai-client');

async function optimizeProduction() {
  const span = tracer.startSpan('optimize-production');
  
  try {
    const result = await client.invoke({
      domain: "manufacturing",
      tool: "solver.optimizeSchedule",
      payload: { plantId: "NJ-01" },
      traceId: span.spanContext().traceId
    });

    span.setAttributes({
      'dcisionai.domain': 'manufacturing',
      'dcisionai.tool': 'solver.optimizeSchedule',
      'dcisionai.execution_time': result.metadata.executionTime,
      'dcisionai.cost': result.metadata.cost
    });

    return result;

  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: SpanStatusCode.ERROR });
    throw error;
  } finally {
    span.end();
  }
}
```

#### **4. Batch Operations**
```typescript
// Batch tool invocations
async function batchOptimize(plantIds: string[]) {
  const batchSize = 10;
  const results = [];

  for (let i = 0; i < plantIds.length; i += batchSize) {
    const batch = plantIds.slice(i, i + batchSize);
    
    const batchPromises = batch.map(plantId =>
      client.invoke({
        domain: "manufacturing",
        tool: "solver.optimizeSchedule",
        payload: { plantId },
        options: { timeout: 30000 }
      })
    );

    const batchResults = await Promise.allSettled(batchPromises);
    
    batchResults.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        results.push({
          plantId: batch[index],
          status: 'success',
          result: result.value
        });
      } else {
        results.push({
          plantId: batch[index],
          status: 'error',
          error: result.reason.message
        });
      }
    });

    // Rate limiting between batches
    if (i + batchSize < plantIds.length) {
      await delay(1000);
    }
  }

  return results;
}
```

## 🐍 **Python SDK**

### **Installation & Setup**

#### **1. Package Installation**
```bash
# Using pip
pip install dcisionai-sdk

# Using poetry
poetry add dcisionai-sdk

# Using conda
conda install -c conda-forge dcisionai-sdk
```

#### **2. Environment Configuration**
```bash
# Required environment variables
export DCISIONAI_API_URL="https://api.dcisionai.com/v1"
export DCISIONAI_TENANT_ID="your-tenant-id"

# Authentication (choose one)
export DCISIONAI_OIDC_TOKEN="your-oidc-token"
export DCISIONAI_API_KEY="your-api-key"
export DCISIONAI_JWT_TOKEN="your-jwt-token"
```

#### **3. Basic Client Setup**
```python
import os
import asyncio
from dcisionai import DcisionAI, DcisionAIError
from dcisionai.auth import OIDCAuth, APIKeyAuth

# Initialize client with OIDC authentication
async def create_oidc_client():
    client = DcisionAI(
        base_url=os.environ["DCISIONAI_API_URL"],
        auth=OIDCAuth(token=await get_id_token()),
        tenant_id=os.environ["DCISIONAI_TENANT_ID"],
        options={
            "timeout": 30000,
            "retries": 3,
            "tracing": True,
            "idempotency": True
        }
    )
    return client

# Initialize client with API key authentication
async def create_api_key_client():
    client = DcisionAI(
        base_url=os.environ["DCISIONAI_API_URL"],
        auth=APIKeyAuth(api_key=os.environ["DCISIONAI_API_KEY"]),
        tenant_id=os.environ["DCISIONAI_TENANT_ID"],
        options={
            "timeout": 30000,
            "retries": 3,
            "tracing": True
        }
    )
    return client

# Usage
async def main():
    client = await create_api_key_client()
    # Use client...
```

### **Core API Usage**

#### **1. Tool Invocation**
```python
import asyncio
from dcisionai import DcisionAIError

async def invoke_tool():
    try:
        result = await client.invoke(
            domain="manufacturing",
            tool="solver.optimizeSchedule",
            payload={
                "plantId": "NJ-01",
                "horizonDays": 7,
                "constraints": ["capacity", "deadlines"]
            },
            options={
                "timeout": 30000,
                "stream": False,
                "region": "auto"
            }
        )

        print(f"Optimization result: {result.result}")
        print(f"Execution time: {result.metadata.execution_time}")
        print(f"Cost: {result.metadata.cost}")

    except DcisionAIError as error:
        if error.code == 'RATE_LIMITED':
            print("Rate limit exceeded, retrying...")
            await asyncio.sleep(1)
        elif error.code == 'QUOTA_EXCEEDED':
            print("Monthly quota exceeded")
        elif error.code == 'TOOL_UNAVAILABLE':
            print("Tool temporarily unavailable")
        elif error.code == 'AUTHENTICATION_FAILED':
            print("Authentication failed, check credentials")
        else:
            print(f"Unexpected error: {error.message}")

# Streaming tool invocation
async def invoke_tool_streaming():
    try:
        stream = await client.invoke(
            domain="manufacturing",
            tool="workflow.optimizeProduction",
            payload={"plantId": "NJ-01"},
            options={"stream": True}
        )

        async for chunk in stream:
            if chunk.type == 'progress':
                print(f"Progress: {chunk.data.progress}%")
            elif chunk.type == 'result':
                print(f"Final result: {chunk.data}")

    except DcisionAIError as error:
        print(f"Streaming invocation failed: {error}")
```

#### **2. Async Job Management**
```python
import uuid

async def create_job():
    try:
        job = await client.create_job(
            domain="manufacturing",
            operation="workflow.optimizeProduction",
            payload={
                "plantId": "NJ-01",
                "productionData": large_dataset,
                "optimizationParams": optimization_config
            },
            options={
                "priority": "high",
                "timeout": 300000,  # 5 minutes
                "notifications": ["webhook", "email"],
                "webhook_url": "https://your-webhook.com/callback"
            }
        )

        print(f"Job created: {job.id}")
        print(f"Status: {job.status}")

    except DcisionAIError as error:
        print(f"Job creation failed: {error}")

async def monitor_job(job_id: str):
    try:
        # Get job status
        status = await client.get_job_status(job_id)
        print(f"Job status: {status}")

        # Stream job updates
        updates = await client.stream_job_updates(job_id)
        async for update in updates:
            print(f"Update: {update.type} - {update.data}")
            
            if update.type == 'completed':
                result = await client.get_job_result(job_id)
                print(f"Job result: {result}")
                break

    except DcisionAIError as error:
        print(f"Job monitoring failed: {error}")

async def cancel_job(job_id: str):
    try:
        await client.cancel_job(job_id)
        print("Job cancelled successfully")

    except DcisionAIError as error:
        print(f"Job cancellation failed: {error}")
```

#### **3. Tool Discovery & Metadata**
```python
async def discover_tools():
    try:
        tools = await client.discover_tools(
            domain="manufacturing",
            query="optimization"
        )

        print("Available tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
            print(f"  Capabilities: {', '.join(tool.capabilities)}")

    except DcisionAIError as error:
        print(f"Tool discovery failed: {error}")

async def get_tool_schema(tool_id: str):
    try:
        schema = await client.get_tool_schema(tool_id)
        
        print(f"Input schema: {schema.input_schema}")
        print(f"Output schema: {schema.output_schema}")
        print(f"Examples: {schema.examples}")

    except DcisionAIError as error:
        print(f"Schema retrieval failed: {error}")
```

### **Advanced Features**

#### **1. Error Handling & Retries**
```python
from dcisionai.retry import RetryStrategy

# Custom retry strategy
custom_retry_strategy = RetryStrategy(
    max_retries=5,
    base_delay=1.0,
    max_delay=30.0,
    backoff_multiplier=2.0,
    retryable_errors=['RATE_LIMITED', 'SERVICE_UNAVAILABLE', 'TIMEOUT'],
    on_retry=lambda error, attempt, delay: print(f"Retry attempt {attempt} after {delay}s due to: {error.message}")
)

client = DcisionAI(
    base_url=os.environ["DCISIONAI_API_URL"],
    auth=APIKeyAuth(api_key=os.environ["DCISIONAI_API_KEY"]),
    tenant_id=os.environ["DCISIONAI_TENANT_ID"],
    options={
        "retry_strategy": custom_retry_strategy,
        "timeout": 60000
    }
)

# Error handling with custom logic
async def handle_errors():
    try:
        result = await client.invoke(
            domain="manufacturing",
            tool="solver.optimizeSchedule",
            payload={"plantId": "NJ-01"}
        )

    except DcisionAIError as error:
        # Handle specific error types
        if error.code == 'RATE_LIMITED':
            await handle_rate_limit(error)
        elif error.code == 'QUOTA_EXCEEDED':
            await handle_quota_exceeded(error)
        elif error.code == 'AUTHENTICATION_FAILED':
            await handle_auth_failure(error)
        elif error.code == 'VALIDATION_ERROR':
            await handle_validation_error(error)
        else:
            await handle_unexpected_error(error)

async def handle_rate_limit(error):
    retry_after = error.headers.get('retry-after')
    if retry_after:
        delay = int(retry_after)
        print(f"Rate limited, waiting {delay}s")
        await asyncio.sleep(delay)

async def handle_quota_exceeded(error):
    print("Monthly quota exceeded")
    # Notify administrators or switch to cost-safe mode
```

#### **2. Idempotency & Deduplication**
```python
import uuid

async def invoke_with_idempotency():
    # Generate idempotency key
    idempotency_key = str(uuid.uuid4())

    try:
        result = await client.invoke(
            domain="manufacturing",
            tool="solver.optimizeSchedule",
            payload={"plantId": "NJ-01"},
            idempotency_key=idempotency_key
        )

        print(f"Request processed with idempotency key: {idempotency_key}")

    except DcisionAIError as error:
        if error.code == 'DUPLICATE_REQUEST':
            print("Request already processed, retrieving result...")
            # Handle duplicate request
```

#### **3. Tracing & Observability**
```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Create trace span
tracer = trace.get_tracer(__name__)

async def optimize_production():
    with tracer.start_as_current_span("optimize-production") as span:
        try:
            result = await client.invoke(
                domain="manufacturing",
                tool="solver.optimizeSchedule",
                payload={"plantId": "NJ-01"},
                trace_id=span.get_span_context().trace_id
            )

            span.set_attributes({
                "dcisionai.domain": "manufacturing",
                "dcisionai.tool": "solver.optimizeSchedule",
                "dcisionai.execution_time": result.metadata.execution_time,
                "dcisionai.cost": result.metadata.cost
            })

            return result

        except Exception as error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR))
            raise
```

#### **4. Batch Operations**
```python
async def batch_optimize(plant_ids: list):
    batch_size = 10
    results = []

    for i in range(0, len(plant_ids), batch_size):
        batch = plant_ids[i:i + batch_size]
        
        batch_tasks = [
            client.invoke(
                domain="manufacturing",
                tool="solver.optimizeSchedule",
                payload={"plantId": plant_id},
                options={"timeout": 30000}
            )
            for plant_id in batch
        ]

        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        for j, result in enumerate(batch_results):
            plant_id = batch[j]
            if isinstance(result, Exception):
                results.append({
                    "plantId": plant_id,
                    "status": "error",
                    "error": str(result)
                })
            else:
                results.append({
                    "plantId": plant_id,
                    "status": "success",
                    "result": result
                })

        # Rate limiting between batches
        if i + batch_size < len(plant_ids):
            await asyncio.sleep(1)

    return results
```

## 🔧 **SDK Configuration Options**

### **Client Options**
```typescript
// TypeScript
const clientOptions = {
  timeout: 30000,           // Request timeout in milliseconds
  retries: 3,               // Number of retry attempts
  tracing: true,            // Enable OpenTelemetry tracing
  idempotency: true,        // Enable idempotency keys
  userAgent: "MyApp/1.0",   // Custom user agent
  headers: {                // Custom headers
    "X-Custom-Header": "value"
  }
};

// Python
client_options = {
    "timeout": 30000,           # Request timeout in milliseconds
    "retries": 3,               # Number of retry attempts
    "tracing": True,            # Enable OpenTelemetry tracing
    "idempotency": True,        # Enable idempotency keys
    "user_agent": "MyApp/1.0", # Custom user agent
    "headers": {                # Custom headers
        "X-Custom-Header": "value"
    }
}
```

### **Retry Strategy Configuration**
```typescript
// TypeScript
const retryStrategy = {
  maxRetries: 5,
  baseDelay: 1000,
  maxDelay: 30000,
  backoffMultiplier: 2,
  retryableErrors: ['RATE_LIMITED', 'SERVICE_UNAVAILABLE'],
  onRetry: (error, attempt, delay) => {
    console.log(`Retry ${attempt} after ${delay}ms`);
  }
};

// Python
retry_strategy = RetryStrategy(
    max_retries=5,
    base_delay=1.0,
    max_delay=30.0,
    backoff_multiplier=2.0,
    retryable_errors=['RATE_LIMITED', 'SERVICE_UNAVAILABLE'],
    on_retry=lambda error, attempt, delay: print(f"Retry {attempt} after {delay}s")
)
```

## 📊 **Performance & Monitoring**

### **Performance Metrics**
```typescript
// TypeScript
import { performance } from 'perf_hooks';

const startTime = performance.now();
const result = await client.invoke({
  domain: "manufacturing",
  tool: "solver.optimizeSchedule",
  payload: { plantId: "NJ-01" }
});
const endTime = performance.now();

console.log(`Request took ${endTime - startTime} milliseconds`);
console.log(`Platform execution time: ${result.metadata.executionTime} milliseconds`);
```

```python
# Python
import time

start_time = time.time()
result = await client.invoke(
    domain="manufacturing",
    tool="solver.optimizeSchedule",
    payload={"plantId": "NJ-01"}
)
end_time = time.time()

print(f"Request took {(end_time - start_time) * 1000:.2f} milliseconds")
print(f"Platform execution time: {result.metadata.execution_time} milliseconds")
```

### **Health Checks**
```typescript
// TypeScript
try {
  const health = await client.getHealth();
  console.log("Platform health:", health.status);
  console.log("Component health:", health.components);
} catch (error) {
  console.error("Health check failed:", error);
}
```

```python
# Python
try:
    health = await client.get_health()
    print(f"Platform health: {health.status}")
    print(f"Component health: {health.components}")
except Exception as error:
    print(f"Health check failed: {error}")
```

## 🚀 **Best Practices**

### **1. Error Handling**
- Always wrap SDK calls in try-catch blocks
- Handle specific error types appropriately
- Implement retry logic for transient failures
- Log errors with sufficient context

### **2. Performance Optimization**
- Use streaming for large datasets
- Implement batch processing for multiple requests
- Set appropriate timeouts based on operation complexity
- Monitor and optimize request patterns

### **3. Security**
- Store API keys securely (use environment variables)
- Rotate API keys regularly
- Use OIDC/SAML for enterprise applications
- Implement proper access controls

### **4. Monitoring & Observability**
- Enable tracing for production applications
- Monitor API usage and costs
- Set up alerts for quota limits and errors
- Track performance metrics

## 📞 **Support & Resources**

### **Getting Help**
- **Documentation**: https://docs.dcisionai.com
- **API Reference**: https://api.dcisionai.com/docs
- **Community**: https://community.dcisionai.com
- **Support**: api-support@dcisionai.com

### **SDK Updates**
- **TypeScript**: `npm update @dcisionai/sdk`
- **Python**: `pip install --upgrade dcisionai-sdk`

### **Examples Repository**
- **GitHub**: https://github.com/dcisionai/sdk-examples
- **Code Samples**: Complete working examples for all use cases
- **Integration Guides**: Step-by-step tutorials for common scenarios

---

**Last Updated**: September 2, 2025  
**SDK Version**: 1.0.0  
**Supported Languages**: TypeScript/Node.js, Python  
**Status**: Production Ready ✅
