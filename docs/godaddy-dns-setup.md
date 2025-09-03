# 🌐 GoDaddy DNS Configuration Guide for DcisionAI Platform

## 📋 **Current Status: Phase 2 Complete, Phase 3 Ready**

✅ **API Gateway deployed** and working on AWS  
✅ **Lambda functions running** with real backend logic  
✅ **All endpoints responding** with real data  
🎯 **Next: Custom domains and SSL certificates**  

## 🎯 **Phase 3 Goals**

This guide will help you configure custom domains for your DcisionAI Platform:
- **api.dcisionai.com** → Production API Gateway
- **dev-api.dcisionai.com** → Development API Gateway
- **staging-api.dcisionai.com** → Staging API Gateway
- **docs.dcisionai.com** → API Documentation
- **dashboard.dcisionai.com** → Admin Dashboard

## 🚀 **What We've Built So Far**

### **Current Working Infrastructure:**
- **API Gateway**: `https://2dtpy57vn2.execute-api.us-east-1.amazonaws.com/production`
- **Lambda Functions**: Real backend logic for all endpoints
- **DynamoDB Tables**: Ready for authentication and multi-tenancy
- **IAM Roles**: Proper permissions and security

### **Working Endpoints:**
- **GET** `/api/v1/health` → System health status
- **GET** `/api/v1/tools` → Tool catalog (4 real tools)
- **POST** `/api/v1/invoke` → Tool execution simulation

## 🌐 **Domain Strategy for Phase 3**

```
dcisionai.com (main domain)
├── api.dcisionai.com → Production API Gateway
├── dev-api.dcisionai.com → Development API Gateway  
├── staging-api.dcisionai.com → Staging API Gateway
├── docs.dcisionai.com → API Documentation
├── dashboard.dcisionai.com → Admin Dashboard
├── portal.dcisionai.com → User Portal
├── developers.dcisionai.com → Developer Portal
├── sdk.dcisionai.com → SDK Downloads
└── mcp.dcisionai.com → Keep existing (MCP Server)
```

## 📋 **Required DNS Records**

### **CNAME Records**
Add the following CNAME records pointing to your AWS API Gateway regional endpoint:

| Subdomain | Points To | Purpose |
|-----------|-----------|---------|
| api | `2dtpy57vn2.execute-api.us-east-1.amazonaws.com` | Production API Gateway |
| dev-api | `2dtpy57vn2.execute-api.us-east-1.amazonaws.com` | Development API Gateway  
| staging-api | `2dtpy57vn2.execute-api.us-east-1.amazonaws.com` | Staging API Gateway |
| docs | `2dtpy57vn2.execute-api.us-east-1.amazonaws.com` | Documentation |
| dashboard | `2dtpy57vn2.execute-api.us-east-1.amazonaws.com` | Admin Dashboard |
| portal | `2dtpy57vn2.execute-api.us-east-1.amazonaws.com` | User Portal |
| developers | `2dtpy57vn2.execute-api.us-east-1.amazonaws.com` | Developer Portal |
| sdk | `2dtpy57vn2.execute-api.us-east-1.amazonaws.com` | SDK Downloads |

## 🔧 **How to Add Records in GoDaddy**

### **Adding CNAME Records:**
1. In DNS Management, click **ADD** under **Records**
2. Select **CNAME** from the Type dropdown
3. Enter the Name (e.g., `api`)
4. Enter the Value: `2dtpy57vn2.execute-api.us-east-1.amazonaws.com`
5. Set TTL to **1 Hour**
6. Click **Save**

### **Adding TXT Records:**
1. In DNS Management, click **ADD** under **Records**
2. Select **TXT** from the Type dropdown
3. Enter the Name (e.g., `_acm-validation.api`)
4. Enter the Value (from AWS)
5. Set TTL to **1 Hour**
6. Click **Save**

## ⏱️ **Timeline for DNS Propagation**

- **CNAME Records**: 1-24 hours for full propagation
- **TXT Records**: 1-48 hours for full propagation
- **SSL Certificate**: 24-72 hours for validation

## 🧪 **Testing Your DNS Configuration**

### **Test CNAME Records:**
```bash
# Test production API
nslookup api.dcisionai.com

# Test development API
nslookup dev-api.dcisionai.com

# Test staging API
nslookup staging-api.dcisionai.com
```

### **Test SSL Certificate:**
```bash
# Test HTTPS endpoints
curl -I https://api.dcisionai.com/health
curl -I https://dev-api.dcisionai.com/health
curl -I https://staging-api.dcisionai.com/health
```

## 🚨 **Important Notes**

1. **Don't delete existing records** unless you're sure they're not needed
2. **Keep the mcp subdomain** pointing to `ghs.googlehosted.com` if it's still in use
3. **Wait for propagation** before testing endpoints
4. **SSL certificate validation** happens automatically once TXT records are in place
5. **All subdomains** will initially point to the same API Gateway endpoint

## 🔗 **Useful Resources**

- [GoDaddy DNS Management Help](https://www.godaddy.com/help/manage-dns-records-680)
- [AWS Certificate Manager Documentation](https://docs.aws.amazon.com/acm/)
- [DNS Propagation Checker](https://www.whatsmydns.net/)

## 📞 **Support**

If you encounter issues:
1. Check DNS propagation using online tools
2. Verify AWS CloudFormation stack status
3. Check SSL certificate validation in AWS Console
4. Contact AWS Support if needed

## 🎯 **Next Steps After DNS Setup**

### **Phase 3A: Authentication & Security**
- Implement API key validation
- Add admin key functionality
- Set up JWT token system
- Test security features

### **Phase 3B: Custom Domain Integration**
- Update API Gateway with custom domains
- Configure SSL certificates
- Test custom domain endpoints
- Update documentation

### **Phase 3C: Production Hardening**
- Add WAF and security rules
- Implement rate limiting
- Set up monitoring and alerting
- Performance optimization

---

**🎯 Goal**: All subdomains should resolve to your AWS API Gateway and have valid SSL certificates within 72 hours of deployment.

**📅 Timeline**: Phase 3 completion expected in 2-3 weeks after DNS setup.
