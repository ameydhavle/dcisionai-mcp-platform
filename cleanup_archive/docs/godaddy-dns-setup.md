# 🌐 GoDaddy DNS Setup for DcisionAI Platform

## 🎯 **Enhanced Domain Strategy Overview**

This guide covers the complete DNS setup for our **Dual-Track Architecture**:

### **Track 1: MCP Server (Engine) - Open Ecosystem**
- `mcp.dcisionai.com` → MCP Protocol Server
- `mcp-api.dcisionai.com` → MCP-specific API endpoints
- `mcp-docs.dcisionai.com` → MCP Protocol documentation
- `mcp-status.dcisionai.com` → MCP service status

### **Track 2: Commercial API/SDK (Car) - Enterprise Business**
- `api.dcisionai.com` → Main commercial API gateway
- `sdk.dcisionai.com` → SDK downloads and documentation
- `portal.dcisionai.com` → Customer portal and billing
- `docs.dcisionai.com` → API documentation and guides

### **Shared Infrastructure & Services**
- `auth.dcisionai.com` → Centralized authentication service
- `monitoring.dcisionai.com` → System health and metrics
- `status.dcisionai.com` → Overall service status page

## 📋 **Current Status: Phase 2 Complete, Phase 3 Ready**

✅ **Working API Gateway**: `https://abc123.execute-api.us-east-1.amazonaws.com/prod/`  
✅ **Working Endpoints**: `/`, `/health`, `/protected`, `/admin`, `/tenant/{id}`  
✅ **Authentication System**: API keys, admin keys, multi-tenant isolation  
✅ **DynamoDB Integration**: API keys, admin keys, tenants tables  

## 🔧 **Phase 3A: Domain Setup (Current Priority)**

### **Step 1: GoDaddy DNS Configuration**

#### **Primary Domains (A Records)**
```
dcisionai.com          → AWS Load Balancer IP
www.dcisionai.com      → AWS Load Balancer IP
```

#### **MCP Track Subdomains (CNAME Records)**
```
mcp.dcisionai.com      → mcp-api-gateway.dcisionai.com
mcp-api.dcisionai.com  → api-gateway.dcisionai.com
mcp-docs.dcisionai.com → docs-bucket.dcisionai.com
mcp-status.dcisionai.com → status-page.dcisionai.com
```

#### **Commercial Track Subdomains (CNAME Records)**
```
api.dcisionai.com      → api-gateway.dcisionai.com
sdk.dcisionai.com      → sdk-bucket.dcisionai.com
portal.dcisionai.com   → customer-portal.dcisionai.com
docs.dcisionai.com     → api-docs.dcisionai.com
```

#### **Shared Service Subdomains (CNAME Records)**
```
auth.dcisionai.com     → auth-service.dcisionai.com
monitoring.dcisionai.com → monitoring.dcisionai.com
status.dcisionai.com   → status-page.dcisionai.com
```

### **Step 2: AWS Resource Mapping**

#### **API Gateway Endpoints**
```
api-gateway.dcisionai.com      → Regional API Gateway
mcp-api-gateway.dcisionai.com → MCP-specific API Gateway
```

#### **Static Content (S3 + CloudFront)**
```
docs-bucket.dcisionai.com     → S3 + CloudFront for MCP docs
sdk-bucket.dcisionai.com      → S3 + CloudFront for SDK downloads
api-docs.dcisionai.com        → S3 + CloudFront for API documentation
status-page.dcisionai.com     → S3 + CloudFront for status pages
```

#### **Application Services**
```
customer-portal.dcisionai.com → Customer portal application
auth-service.dcisionai.com    → Authentication service
monitoring.dcisionai.com      → Monitoring dashboard
```

## 🚀 **Phase 3B: SSL Certificate Setup**

### **Wildcard Certificate Request**
```
*.dcisionai.com
dcisionai.com
```

### **SSL Termination Points**
- **API Gateway**: SSL termination for API endpoints
- **CloudFront**: SSL termination for static content
- **Load Balancer**: SSL termination for application services

## 🔄 **Phase 3C: Service Deployment**

### **Week 1: MCP Track Deployment**
1. Deploy MCP server to `mcp.dcisionai.com`
2. Configure MCP protocol endpoints
3. Set up MCP documentation at `mcp-docs.dcisionai.com`
4. Deploy MCP status page at `mcp-status.dcisionai.com`

### **Week 2: Commercial Track Deployment**
1. Deploy main API to `api.dcisionai.com`
2. Set up SDK distribution at `sdk.dcisionai.com`
3. Deploy customer portal at `portal.dcisionai.com`
4. Configure API documentation at `docs.dcisionai.com`

### **Week 3: Shared Services**
1. Deploy authentication service at `auth.dcisionai.com`
2. Set up monitoring dashboard at `monitoring.dcisionai.com`
3. Deploy status page at `status.dcisionai.com`

## 📊 **DNS Record Configuration**

### **GoDaddy DNS Manager Setup**

#### **A Records (Root Domains)**
```
Type: A
Name: @ (or leave blank for root)
Value: [AWS Load Balancer IP]
TTL: 300 (5 minutes)
```

#### **CNAME Records (Subdomains)**
```
Type: CNAME
Name: mcp
Value: mcp-api-gateway.dcisionai.com
TTL: 300

Type: CNAME
Name: api
Value: api-gateway.dcisionai.com
TTL: 300

Type: CNAME
Name: sdk
Value: sdk-bucket.dcisionai.com
TTL: 300

Type: CNAME
Name: portal
Value: customer-portal.dcisionai.com
TTL: 300

Type: CNAME
Name: docs
Value: api-docs.dcisionai.com
TTL: 300

Type: CNAME
Name: auth
Value: auth-service.dcisionai.com
TTL: 300

Type: CNAME
Name: monitoring
Value: monitoring.dcisionai.com
TTL: 300

Type: CNAME
Name: status
Value: status-page.dcisionai.com
TTL: 300
```

## 🔒 **Security Considerations**

### **DNS Security**
- Enable DNSSEC if available
- Use short TTL values for quick updates
- Monitor DNS propagation

### **SSL Security**
- Use strong cipher suites
- Enable HSTS headers
- Regular certificate renewal monitoring

### **Access Control**
- MCP track: Public access with rate limiting
- Commercial track: Enterprise authentication required
- Shared services: Role-based access control

## 📈 **Monitoring & Maintenance**

### **DNS Health Checks**
- Monitor DNS resolution for all subdomains
- Track SSL certificate expiration
- Monitor domain propagation

### **Performance Monitoring**
- Track response times for each subdomain
- Monitor SSL handshake performance
- Track CDN performance for static content

## 🎯 **Success Criteria**

### **Phase 3A Complete When:**
- ✅ All subdomains resolve correctly
- ✅ SSL certificates are active
- ✅ Basic routing is functional
- ✅ DNS propagation is complete

### **Phase 3B Complete When:**
- ✅ MCP server is accessible at mcp.dcisionai.com
- ✅ Commercial API is accessible at api.dcisionai.com
- ✅ All documentation sites are live
- ✅ Customer portal is functional

### **Phase 3C Complete When:**
- ✅ All services are deployed and accessible
- ✅ Monitoring and alerting are active
- ✅ Performance optimization is complete
- ✅ Security hardening is implemented

## 🔄 **Next Steps After DNS Setup**

1. **SSL Certificate Validation** - Verify all certificates are active
2. **DNS Propagation Testing** - Test all subdomains globally
3. **Service Deployment** - Deploy applications to each subdomain
4. **Performance Testing** - Validate response times and SSL performance
5. **Security Testing** - Verify access controls and security measures

---

*This enhanced domain strategy transforms our platform into a professional, enterprise-ready solution that clearly communicates our dual-track approach to both developers and enterprise customers.*
