# DcisionAI AgentCore Integration

## 🚀 **Overview**

The DcisionAI AgentCore integration provides serverless deployment of the DcisionAI MCP server on AWS Bedrock AgentCore Runtime. This enables enterprise-grade scalability, security, and performance for mathematical optimization workloads.

---

## 🏗️ **Architecture**

### **AgentCore Runtime Integration**
```
┌─────────────────────────────────────────────────────────────┐
│                Client Applications                          │
│  (Web UI, IDE, API Clients)                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Flask Backend                                │
│              (MCP Client & API Gateway)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            AWS Bedrock AgentCore Runtime                   │
│              (Serverless MCP Server)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              DcisionAI MCP Server                          │
│         (Optimization Tools & AI Reasoning)                │
└─────────────────────────────────────────────────────────────┘
```

### **Key Benefits**
- **Serverless Scaling**: Automatic scaling based on demand
- **Enterprise Security**: AWS IAM integration and VPC isolation
- **High Availability**: 99.9% uptime with AWS infrastructure
- **Cost Efficiency**: Pay only for actual usage
- **Global Deployment**: Multi-region support

---

## 🛠️ **Deployment**

### **Prerequisites**
- **AWS Account**: Active account with billing enabled
- **AWS CLI**: Latest version installed and configured
- **IAM Permissions**: BedrockAgentCoreFullAccess policy
- **Python**: 3.10 or higher

### **Step 1: Install AgentCore CLI**
```bash
# Install AgentCore starter toolkit
pip install bedrock-agentcore-starter-toolkit

# Verify installation
agentcore --version
```

### **Step 2: Configure AWS Credentials**
```bash
# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region: us-east-1
# Enter default output format: json

# Verify credentials
aws sts get-caller-identity
```

### **Step 3: Deploy to AgentCore**
```bash
# Navigate to deployment directory
cd saas-platform/deployment

# Deploy to AgentCore (non-interactive)
./deploy_to_agentcore_noninteractive.sh

# Verify deployment
agentcore list
```

### **Step 4: Test Deployment**
```bash
# Test the deployed agent
agentcore invoke '{"prompt": "Test optimization problem"}'

# Check agent status
agentcore status
```

---

## 🔧 **Configuration**

### **AgentCore Configuration**
```json
// agentcore_config.json
{
    "agent_name": "dcisionai_agentcore_production",
    "runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/mcp_server-IkOAiK3aOz",
    "entrypoint": "dcisionai_agentcore_standalone.py",
    "requirements": "requirements_standalone.txt",
    "environment": {
        "AWS_DEFAULT_REGION": "us-east-1",
        "DcisionAI_MODEL_PROVIDER": "claude",
        "DcisionAI_DEBUG": "false"
    }
}
```

### **Standalone Agent Code**
```python
# dcisionai_agentcore_standalone.py
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import logging

app = BedrockAgentCoreApp()

@app.entrypoint
async def main(payload, context):
    """Main entry point for AgentCore Runtime."""
    try:
        # Parse MCP request
        mcp_request = json.loads(payload)
        
        # Route to appropriate DcisionAI tool
        method = mcp_request.get('method', '')
        params = mcp_request.get('params', {})
        
        if method == 'tools/call':
            tool_name = params.get('name', '')
            arguments = params.get('arguments', {})
            
            # Call DcisionAI tool
            result = await call_dcisionai_tool(tool_name, arguments)
            return result
            
    except Exception as e:
        logging.error(f"AgentCore error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    app.run()
```

---

## 🔐 **Security**

### **IAM Roles and Policies**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:InvokeAgentRuntime",
                "bedrock-agentcore:ListAgents",
                "bedrock-agentcore:GetAgent"
            ],
            "Resource": "arn:aws:bedrock-agentcore:us-east-1:*:runtime/mcp_server-*"
        }
    ]
}
```

### **VPC Configuration**
```bash
# Create VPC for private deployment
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=dcisionai-vpc}]'

# Create private subnets
aws ec2 create-subnet \
    --vpc-id vpc-12345678 \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a
```

### **Security Groups**
```bash
# Create security group
aws ec2 create-security-group \
    --group-name dcisionai-agentcore-sg \
    --description "Security group for DcisionAI AgentCore" \
    --vpc-id vpc-12345678

# Allow HTTPS traffic
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
```

---

## 📊 **Monitoring and Logging**

### **CloudWatch Integration**
```python
import boto3
import logging

# Set up CloudWatch logging
cloudwatch = boto3.client('logs')
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create log group
cloudwatch.create_log_group(
    logGroupName='/aws/bedrock-agentcore/dcisionai'
)
```

### **Custom Metrics**
```python
# Send custom metrics to CloudWatch
cloudwatch.put_metric_data(
    Namespace='DcisionAI/AgentCore',
    MetricData=[
        {
            'MetricName': 'OptimizationRequests',
            'Value': 1,
            'Unit': 'Count'
        },
        {
            'MetricName': 'OptimizationDuration',
            'Value': 2.5,
            'Unit': 'Seconds'
        }
    ]
)
```

### **Health Checks**
```python
@app.ping
def health_check():
    """Custom health check for AgentCore."""
    try:
        # Check dependencies
        check_dcisionai_tools()
        check_optimization_engines()
        
        return "Healthy"
    except Exception as e:
        return "Unhealthy"
```

---

## 🚀 **Performance Optimization**

### **Caching Strategy**
```python
import redis
import json

# Set up Redis caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_optimization_result(problem_hash, result):
    """Cache optimization results."""
    redis_client.setex(
        f"optimization:{problem_hash}",
        3600,  # 1 hour TTL
        json.dumps(result)
    )

def get_cached_result(problem_hash):
    """Get cached optimization result."""
    cached = redis_client.get(f"optimization:{problem_hash}")
    if cached:
        return json.loads(cached)
    return None
```

### **Connection Pooling**
```python
import asyncio
import aiohttp

# Set up connection pool
connector = aiohttp.TCPConnector(
    limit=100,
    limit_per_host=30,
    ttl_dns_cache=300,
    use_dns_cache=True
)

async def make_async_request(url, data):
    """Make async HTTP request with connection pooling."""
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(url, json=data) as response:
            return await response.json()
```

### **Resource Optimization**
```python
# Configure resource limits
import resource

# Set memory limit
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 * 1024 * 1024, -1))  # 2GB

# Set CPU limit
resource.setrlimit(resource.RLIMIT_CPU, (300, -1))  # 5 minutes
```

---

## 🔄 **Scaling and Load Balancing**

### **Auto-scaling Configuration**
```yaml
# agentcore_scaling_config.yaml
scaling:
  min_capacity: 1
  max_capacity: 100
  target_utilization: 70
  scale_up_cooldown: 300
  scale_down_cooldown: 600

metrics:
  - metric_name: "OptimizationRequests"
    target_value: 10
  - metric_name: "ResponseTime"
    target_value: 2.0
```

### **Load Balancing**
```python
# Round-robin load balancing
import random

class LoadBalancer:
    def __init__(self, endpoints):
        self.endpoints = endpoints
        self.current = 0
    
    def get_endpoint(self):
        endpoint = self.endpoints[self.current]
        self.current = (self.current + 1) % len(self.endpoints)
        return endpoint
    
    def get_random_endpoint(self):
        return random.choice(self.endpoints)
```

---

## 🧪 **Testing**

### **Unit Tests**
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_agentcore_integration():
    """Test AgentCore integration."""
    from dcisionai_agentcore_standalone import main
    
    # Test payload
    payload = {
        "method": "tools/call",
        "params": {
            "name": "classify_intent",
            "arguments": {
                "problem_description": "Test optimization problem"
            }
        }
    }
    
    # Call main function
    result = await main(json.dumps(payload), None)
    
    # Assertions
    assert "result" in result
    assert result["status"] == "success"
```

### **Integration Tests**
```python
@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete optimization workflow."""
    # Test intent classification
    intent_result = await classify_intent("Test problem")
    assert intent_result["optimization_type"] == "linear_programming"
    
    # Test model building
    model_result = await build_model("Test problem", intent_result)
    assert "variables" in model_result
    
    # Test optimization
    opt_result = await solve_optimization("Test problem", model_result)
    assert opt_result["solver_status"] == "optimal"
```

### **Load Testing**
```python
import asyncio
import aiohttp
import time

async def load_test_agentcore():
    """Load test AgentCore deployment."""
    tasks = []
    start_time = time.time()
    
    for i in range(100):
        task = asyncio.create_task(make_request())
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"Completed 100 requests in {end_time - start_time:.2f} seconds")
    print(f"Average response time: {(end_time - start_time) / 100:.2f} seconds")
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Deployment Failures**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check AgentCore CLI
agentcore --version

# Check deployment logs
agentcore logs --tail
```

#### **Runtime Errors**
```bash
# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/bedrock-agentcore"

# Get recent log events
aws logs get-log-events \
    --log-group-name "/aws/bedrock-agentcore/dcisionai" \
    --log-stream-name "latest"
```

#### **Performance Issues**
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace "AWS/BedrockAgentCore" \
    --metric-name "Duration" \
    --start-time 2025-01-17T00:00:00Z \
    --end-time 2025-01-17T23:59:59Z \
    --period 300 \
    --statistics Average
```

### **Debug Mode**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Set debug environment variable
import os
os.environ['DcisionAI_DEBUG'] = 'true'
```

---

## 📚 **Best Practices**

### **Error Handling**
```python
@app.entrypoint
async def main(payload, context):
    """Main entry point with comprehensive error handling."""
    try:
        # Parse and validate input
        mcp_request = json.loads(payload)
        validate_request(mcp_request)
        
        # Process request
        result = await process_request(mcp_request)
        
        # Validate and return result
        validate_result(result)
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {"error": "Invalid JSON payload"}
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return {"error": f"Validation failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Internal server error"}
```

### **Resource Management**
```python
import asyncio
import contextlib

@contextlib.asynccontextmanager
async def resource_manager():
    """Context manager for resource cleanup."""
    resources = []
    try:
        # Initialize resources
        resources.append(await init_optimization_engine())
        resources.append(await init_ai_model())
        yield resources
    finally:
        # Cleanup resources
        for resource in resources:
            await resource.cleanup()
```

### **Monitoring Integration**
```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Send metrics
            send_metric("function_duration", duration, func.__name__)
            send_metric("function_success", 1, func.__name__)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            send_metric("function_duration", duration, func.__name__)
            send_metric("function_error", 1, func.__name__)
            raise
    return wrapper
```

---

## 📞 **Support**

- **AWS Documentation**: [Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- **GitHub Issues**: [Report bugs and request features](https://github.com/dcisionai/dcisionai-mcp-platform/issues)
- **Community**: [Join our Discord](https://discord.gg/dcisionai)
- **Email**: support@dcisionai.com

---

*The DcisionAI AgentCore integration provides enterprise-grade serverless deployment for mathematical optimization workloads with automatic scaling and high availability.*
