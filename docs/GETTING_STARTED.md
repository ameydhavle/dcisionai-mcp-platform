# 🚀 Getting Started with DcisionAI Platform

## 🎯 **Welcome to DcisionAI!**

**DcisionAI** is a cutting-edge AI agent platform that combines the power of the **Model Context Protocol (MCP)** with enterprise-grade commercial services. Our **Dual-Track Strategy** serves both developers and enterprises.

## 🏗️ **Choose Your Track**

### **🚂 Track 1: MCP Ecosystem (Open Source)**
**For developers, researchers, and ecosystem partners**

**What you get:**
- Free MCP server download
- Open source code and documentation
- Community support and forums
- Standards-based integration

**Best for:**
- Learning MCP protocol
- Building custom tools
- Research and experimentation
- Community contribution

### **🚗 Track 2: Commercial Platform (Enterprise)**
**For businesses, CIOs, and enterprise users**

**What you get:**
- Production-ready API gateway
- Multi-tenant infrastructure
- Enterprise security and compliance
- Professional support and SLAs

**Best for:**
- Production deployments
- Enterprise integration
- Business applications
- Commercial use cases

## 🚀 **Quick Start Options**

### **Option A: Try MCP Server (Free)**
**Perfect for developers and researchers**

1. **Download MCP Server**
   ```bash
   git clone https://github.com/dcisionai/mcp-server
   cd mcp-server
   pip install -r requirements.txt
   ```

2. **Run the Server**
   ```bash
   python mcp_server.py
   ```

3. **Test with MCP Client**
   ```bash
   # Use any MCP-compatible client
   curl http://localhost:8000/api/v1/tools
   ```

4. **Read Documentation**
   - Visit: https://mcp-docs.dcisionai.com
   - Join: Discord community
   - Explore: GitHub examples

### **Option B: Try Commercial API (Free Tier)**
**Perfect for businesses and developers**

1. **Get API Key**
   - Visit: https://portal.dcisionai.com
   - Sign up for free account
   - Generate API key

2. **Test the API**
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.dcisionai.com/api/v1/health
   ```

3. **Explore SDKs**
   ```bash
   # Python SDK
   pip install dcisionai-sdk
   
   # JavaScript SDK
   npm install @dcisionai/sdk
   ```

4. **Read API Docs**
   - Visit: https://docs.dcisionai.com
   - Interactive examples
   - Code samples

## 🔧 **Development Setup**

### **Prerequisites**
- **Python 3.11+** (for MCP server)
- **Node.js 18+** (for JavaScript SDK)
- **Git** (for source code)
- **AWS CLI** (for infrastructure)

### **Local Development Environment**

1. **Clone Repository**
   ```bash
   git clone https://github.com/dcisionai/dcisionai-mcp-platform
   cd dcisionai-mcp-platform
   ```

2. **Setup Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   ```

### **Docker Setup**

1. **Build Image**
   ```bash
   docker build -t dcisionai-platform .
   ```

2. **Run Container**
   ```bash
   docker run -p 8000:8000 dcisionai-platform
   ```

## 🌐 **Platform Access**

### **MCP Track (Open Source)**
- **Server**: https://mcp.dcisionai.com
- **Documentation**: https://mcp-docs.dcisionai.com
- **Status**: https://mcp-status.dcisionai.com
- **GitHub**: https://github.com/dcisionai

### **Commercial Track (Enterprise)**
- **API Gateway**: https://api.dcisionai.com
- **SDK Downloads**: https://sdk.dcisionai.com
- **Customer Portal**: https://portal.dcisionai.com
- **API Documentation**: https://docs.dcisionai.com

### **Shared Services**
- **Authentication**: https://auth.dcisionai.com
- **Monitoring**: https://monitoring.dcisionai.com
- **Service Status**: https://status.dcisionai.com

## 📚 **Learning Paths**

### **For MCP Developers**
1. **Start with MCP Protocol**
   - Read MCP specification
   - Understand tool concepts
   - Build simple tools

2. **Explore DcisionAI Server**
   - Download and run server
   - Test with MCP clients
   - Customize for your needs

3. **Contribute to Community**
   - Share tools and examples
   - Report issues and improvements
   - Help other developers

### **For Enterprise Developers**
1. **Understand the Platform**
   - Read platform overview
   - Explore API documentation
   - Try free tier features

2. **Integration Planning**
   - Identify use cases
   - Plan authentication strategy
   - Design multi-tenant architecture

3. **Production Deployment**
   - Set up monitoring
   - Implement security measures
   - Plan scaling strategy

### **For DevOps Engineers**
1. **Infrastructure Setup**
   - Review CloudFormation templates
   - Understand multi-tenant isolation
   - Plan monitoring and alerting

2. **Security Configuration**
   - Configure IAM roles
   - Set up VPC and security groups
   - Implement WAF rules

3. **Monitoring & Operations**
   - Set up CloudWatch dashboards
   - Configure alerting
   - Plan disaster recovery

## 🧪 **Testing & Validation**

### **MCP Compliance Testing**
```bash
# Run MCP compliance tests
cd tests/mcp_compliance
python run_mcp_compliance_tests.py

# Test with real MCP client
python test_real_mcp.py
```

### **API Testing**
```bash
# Test authentication
curl -X POST https://api.dcisionai.com/api/v1/auth/validate-key \
     -H "Content-Type: application/json" \
     -d '{"api_key": "YOUR_API_KEY"}'

# Test endpoints
curl https://api.dcisionai.com/api/v1/health
curl https://api.dcisionai.com/api/v1/tools
```

### **Load Testing**
```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f load_tests/api_load_test.py
```

## 🔐 **Security & Compliance**

### **Authentication Methods**
- **API Keys**: Simple key-based authentication
- **JWT Tokens**: Secure token-based authentication
- **OAuth 2.0**: Industry-standard OAuth flow
- **Admin Keys**: Elevated permissions for administrators

### **Multi-Tenant Security**
- **Complete Isolation**: No data sharing between tenants
- **Role-Based Access**: Fine-grained permissions
- **Audit Logging**: Comprehensive activity tracking
- **Encryption**: AES-256 at rest, TLS 1.3 in transit

### **Compliance Features**
- **SOC 2 Ready**: Security and availability controls
- **GDPR Compliant**: Data protection and privacy
- **Industry Standards**: HIPAA, PCI-DSS ready
- **Regular Audits**: Security assessments and penetration testing

## 📊 **Monitoring & Observability**

### **Platform Metrics**
- **API Performance**: Response times and throughput
- **Error Rates**: Success/failure ratios
- **Resource Usage**: CPU, memory, and storage
- **User Activity**: API calls and feature usage

### **Business Metrics**
- **Tenant Growth**: New customer acquisition
- **Usage Patterns**: Feature adoption rates
- **Revenue Metrics**: Subscription and usage billing
- **Customer Satisfaction**: Support tickets and feedback

### **Alerting & Notifications**
- **Performance Alerts**: Response time thresholds
- **Error Alerts**: Error rate spikes
- **Security Alerts**: Suspicious activity detection
- **Business Alerts**: Usage and revenue milestones

## 🚨 **Troubleshooting**

### **Common Issues**

#### **MCP Server Issues**
```bash
# Check server status
curl http://localhost:8000/api/v1/health

# Check logs
tail -f logs/mcp_server.log

# Verify configuration
python -c "from config import settings; print(settings)"
```

#### **API Authentication Issues**
```bash
# Validate API key
curl -X POST https://api.dcisionai.com/api/v1/auth/validate-key \
     -H "Content-Type: application/json" \
     -d '{"api_key": "YOUR_API_KEY"}'

# Check key permissions
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.dcisionai.com/api/v1/auth/me
```

#### **Infrastructure Issues**
```bash
# Check CloudFormation status
aws cloudformation describe-stacks --stack-name dcisionai-platform

# Check service health
curl https://status.dcisionai.com

# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics --namespace AWS/ApiGateway
```

### **Getting Help**

#### **Community Support**
- **Discord**: Join developer community
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides and examples
- **Forums**: Community discussions and Q&A

#### **Enterprise Support**
- **Support Portal**: https://portal.dcisionai.com
- **Email Support**: support@dcisionai.com
- **Phone Support**: +1 (555) 123-4567
- **Professional Services**: Custom development and integration

## 🔄 **Next Steps**

### **Immediate Actions**
1. **Choose your track** (MCP or Commercial)
2. **Set up development environment**
3. **Try basic examples**
4. **Join community channels**

### **Short Term (1-2 weeks)**
1. **Build first integration**
2. **Test with real data**
3. **Explore advanced features**
4. **Plan production deployment**

### **Medium Term (1-3 months)**
1. **Production deployment**
2. **Performance optimization**
3. **Security hardening**
4. **Team training and adoption**

### **Long Term (3-12 months)**
1. **Scale infrastructure**
2. **Advanced features**
3. **Partner integrations**
4. **Market expansion**

## 📞 **Support & Resources**

### **Documentation**
- **Platform Overview**: [PLATFORM_OVERVIEW.md](PLATFORM_OVERVIEW.md)
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)
- **Architecture Guide**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

### **Community**
- **GitHub**: https://github.com/dcisionai
- **Discord**: Join our developer community
- **Blog**: https://blog.dcisionai.com
- **Newsletter**: Subscribe for updates

### **Enterprise**
- **Sales**: sales@dcisionai.com
- **Support**: support@dcisionai.com
- **Partnerships**: partnerships@dcisionai.com
- **Training**: training@dcisionai.com

---

**🎯 Ready to get started? Choose your track and begin building the future of AI agents!**

**Need help? Our team is here to support your journey every step of the way.**
