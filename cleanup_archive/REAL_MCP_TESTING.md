# 🚀 Real MCP Server Compliance Testing

This guide covers how to run comprehensive compliance tests against **real** MCP servers, including the DcisionAI MCP server and other production environments.

## 📋 Overview

The Real MCP Compliance Testing framework provides:

- **Live server connectivity testing** against actual MCP servers
- **Real protocol validation** with production infrastructure
- **Performance benchmarking** with real-world conditions
- **Comprehensive compliance reporting** for enterprise validation
- **Environment-specific configurations** for different deployment stages

## 🏗️ Architecture

```
Real MCP Compliance Testing
├── RealMCPComplianceTester     # Main testing orchestrator
├── MCPComplianceTester         # Core testing logic
├── MCPComplianceValidator      # Compliance validation
├── Environment Configurations   # Pre-configured environments
└── CLI Interface               # Easy command-line usage
```

## 🚀 Quick Start

### 1. **Basic Connection Test**
```bash
# Test connection to default server
python tests/mcp_compliance/run_real_tests.py --test-connection

# Test connection to specific environment
python tests/mcp_compliance/run_real_tests.py local --test-connection
```

### 2. **Full Compliance Testing**
```bash
# Run full compliance tests against local server
python tests/mcp_compliance/run_real_tests.py local

# Run against development environment
python tests/mcp_compliance/run_real_tests.py dev

# Run against production environment
python tests/mcp_compliance/run_real_tests.py prod
```

### 3. **Integration with Main Test Runner**
```bash
# Run real MCP tests with main test suite
python tests/run_all_tests.py --real-mcp

# Run all tests including real MCP
python tests/run_all_tests.py --all
```

## 🌍 Available Environments

### **Local Development**
```bash
python tests/mcp_compliance/run_real_tests.py local
```
- **URL**: `ws://localhost:8080/mcp`
- **Auth**: None required
- **Features**: Basic MCP protocol, development tools
- **Use Case**: Local development and testing

### **Development Environment**
```bash
python tests/mcp_compliance/run_real_tests.py dev
```
- **URL**: `wss://dev-mcp.dcisionai.com/mcp`
- **Auth**: Required (set `DCISIONAI_DEV_AUTH_TOKEN`)
- **Features**: Basic security, rate limiting, health checks
- **Use Case**: Development team testing

### **Staging Environment**
```bash
python tests/mcp_compliance/run_real_tests.py staging
```
- **URL**: `wss://staging-mcp.dcisionai.com/mcp`
- **Auth**: Required (set `DCISIONAI_STAGING_AUTH_TOKEN`)
- **Features**: Production-like features, circuit breaker, audit logging
- **Use Case**: Pre-production validation

### **Production Environment**
```bash
python tests/mcp_compliance/run_real_tests.py prod
```
- **URL**: `wss://mcp.dcisionai.com/mcp`
- **Auth**: Required (set `DCISIONAI_PROD_AUTH_TOKEN`)
- **Features**: Full enterprise features, advanced security
- **Use Case**: Production compliance validation

### **Enterprise Environment**
```bash
python tests/mcp_compliance/run_real_tests.py enterprise
```
- **URL**: `wss://enterprise-mcp.dcisionai.com/mcp`
- **Auth**: Required (set `DCISIONAI_ENTERPRISE_AUTH_TOKEN`)
- **Features**: Advanced compliance, maximum security
- **Use Case**: Enterprise compliance certification

## ⚙️ Configuration

### **Environment Variables**

#### **Required for All Environments**
```bash
# Server URL (auto-configured for environments)
export MCP_SERVER_URL="wss://your-server.com/mcp"

# Authentication token
export MCP_AUTH_TOKEN="your-auth-token"

# Output directory for reports
export COMPLIANCE_OUTPUT_DIR="compliance_reports"
```

#### **Environment-Specific Tokens**
```bash
# Development
export DCISIONAI_DEV_AUTH_TOKEN="dev-token"

# Staging
export DCISIONAI_STAGING_AUTH_TOKEN="staging-token"

# Production
export DCISIONAI_PROD_AUTH_TOKEN="prod-token"

# Enterprise
export DCISIONAI_ENTERPRISE_AUTH_TOKEN="enterprise-token"
```

#### **Test Configuration**
```bash
# Timeout settings
export MCP_TIMEOUT="60"              # Connection timeout in seconds
export MCP_MAX_RETRIES="5"           # Maximum retry attempts
export TEST_TIMEOUT="900"            # Test execution timeout
export PARALLEL_TESTS="10"           # Parallel test execution

# Output and reporting
export EXPORT_FORMATS="json,yaml,html"  # Report formats
export RUN_REAL_TESTS="true"            # Enable real server testing
```

### **Custom Configuration**
```bash
# Override configuration at runtime
python tests/mcp_compliance/run_real_tests.py prod \
  --timeout 120 \
  --max-retries 7 \
  --output-dir custom_reports
```

## 🧪 Test Categories

### **1. Server Connectivity**
- **WebSocket Connection**: Basic connection establishment
- **HTTP Connection**: HTTP/2 support validation
- **Connection Resilience**: Reconnection and stability testing
- **Performance Metrics**: Connection time and response time

### **2. Protocol Compliance**
- **MCP Protocol Version**: Latest protocol support
- **Message Format**: JSON-RPC 2.0 compliance
- **Parameter Validation**: Request/response validation
- **Error Handling**: Standard error codes and messages

### **3. Tools and Resources**
- **Tool Management**: Tool listing and execution
- **Resource Management**: CRUD operations for resources
- **Prompt Management**: Prompt creation and execution
- **Schema Validation**: Tool and resource schemas

### **4. Security and Authentication**
- **Authentication**: API key, OAuth, JWT validation
- **Security Features**: TLS, encryption, audit logging
- **Rate Limiting**: Request throttling and limits
- **Access Control**: Permission and authorization

### **5. Performance and Resilience**
- **Error Handling**: Standard error codes and recovery
- **Circuit Breaker**: Failure isolation and recovery
- **Health Checks**: Server health monitoring
- **Performance Metrics**: Response times and throughput

## 📊 Test Results

### **Success Criteria**
- **PASSED**: 80%+ success rate, 80%+ weighted score
- **PARTIAL**: 60%+ success rate, 60%+ weighted score
- **FAILED**: Below 60% success rate or weighted score

### **Scoring System**
```yaml
Weights:
  Connectivity: 20%
  Protocol: 25%
  Tools: 25%
  Security: 20%
  Performance: 10%
```

### **Output Formats**
- **JSON**: Machine-readable test results
- **YAML**: Human-readable test results
- **HTML**: Visual compliance report
- **Console**: Real-time test progress

## 🔍 Troubleshooting

### **Common Issues**

#### **Connection Failed**
```bash
❌ Server connectivity failed: Connection refused
```
**Solutions:**
- Check server URL and port
- Verify server is running
- Check firewall settings
- Validate network connectivity

#### **Authentication Failed**
```bash
❌ Authentication failed: Invalid token
```
**Solutions:**
- Verify auth token is correct
- Check token expiration
- Ensure proper environment variables
- Validate token permissions

#### **Timeout Errors**
```bash
⏰ Test execution timeout
```
**Solutions:**
- Increase timeout values
- Check server performance
- Reduce parallel test count
- Optimize test execution

#### **Protocol Errors**
```bash
❌ Protocol compliance failed: Invalid message format
```
**Solutions:**
- Verify MCP protocol version
- Check message structure
- Validate JSON-RPC compliance
- Review server implementation

### **Debug Mode**
```bash
# Enable verbose logging
python tests/mcp_compliance/run_real_tests.py prod --verbose

# Test connection only
python tests/mcp_compliance/run_real_tests.py prod --test-connection

# Show configuration
python tests/mcp_compliance/run_real_tests.py prod --config
```

### **Log Files**
```bash
# Logs are saved to:
compliance_reports/{environment}/logs/real_mcp_compliance_{timestamp}.log

# Reports are saved to:
compliance_reports/{environment}/real_mcp_compliance_report_{timestamp}.json
```

## 🚀 Advanced Usage

### **Custom Environment Configuration**
```python
# Create custom environment in environments.py
CUSTOM_ENV = MCPEnvironment(
    name="Custom Server",
    description="Custom MCP server configuration",
    server_url="wss://custom-server.com/mcp",
    auth_token="custom-token",
    timeout=45,
    max_retries=5,
    # ... other settings
)
```

### **Integration with CI/CD**
```yaml
# GitHub Actions example
- name: Run MCP Compliance Tests
  run: |
    python tests/mcp_compliance/run_real_tests.py staging
  env:
    DCISIONAI_STAGING_AUTH_TOKEN: ${{ secrets.STAGING_TOKEN }}
    COMPLIANCE_OUTPUT_DIR: compliance_reports/staging
```

### **Automated Testing Scripts**
```bash
#!/bin/bash
# Run compliance tests for all environments
for env in local dev staging prod; do
    echo "Testing environment: $env"
    python tests/mcp_compliance/run_real_tests.py $env
    
    if [ $? -eq 0 ]; then
        echo "✅ $env tests passed"
    else
        echo "❌ $env tests failed"
        exit 1
    fi
done
```

## 📚 API Reference

### **RealMCPComplianceTester**
```python
tester = RealMCPComplianceTester(config)

# Run comprehensive testing
results = await tester.run_comprehensive_compliance_test()

# Test specific areas
connectivity = await tester._test_server_connectivity()
protocol = await tester._test_protocol_compliance()
tools = await tester._test_tools_and_resources()
security = await tester._test_security_and_auth()
performance = await tester._test_performance_and_resilience()
```

### **Environment Configuration**
```python
from tests.mcp_compliance.environments import get_environment

# Get environment config
env = get_environment("prod")
config = get_environment_config("prod")

# Validate environment
is_valid = validate_environment("prod")

# List available environments
envs = list_environments()
```

## 🔗 Related Documentation

- [MCP Protocol Compliance](./MCP_PROTOCOL_COMPLIANCE.md) - Protocol compliance framework
- [Compliance Testing Framework](./README.md) - Core testing infrastructure
- [Environment Configuration](./environments.py) - Environment definitions
- [Configuration Management](./config.py) - Configuration handling

## 💡 Best Practices

### **Before Running Tests**
1. **Verify server availability** and network connectivity
2. **Set proper authentication tokens** for secure environments
3. **Check resource availability** for parallel test execution
4. **Review environment configuration** for accuracy

### **During Test Execution**
1. **Monitor real-time progress** with console output
2. **Check log files** for detailed error information
3. **Validate test results** against expected outcomes
4. **Document any failures** for investigation

### **After Test Completion**
1. **Review comprehensive reports** for compliance status
2. **Analyze performance metrics** for optimization opportunities
3. **Address any failures** before production deployment
4. **Archive test results** for compliance documentation

## 🆘 Support

### **Getting Help**
- **Documentation**: Review this guide and related docs
- **Logs**: Check log files for detailed error information
- **Configuration**: Verify environment and server settings
- **Community**: Reach out to the development team

### **Reporting Issues**
When reporting issues, include:
- Environment name and configuration
- Complete error messages and logs
- Test command and parameters
- Server status and configuration
- Expected vs. actual behavior

---

**Ready to test your MCP server?** Start with a connection test:

```bash
python tests/mcp_compliance/run_real_tests.py --test-connection
```

Then run full compliance testing:

```bash
python tests/mcp_compliance/run_real_tests.py prod
```
