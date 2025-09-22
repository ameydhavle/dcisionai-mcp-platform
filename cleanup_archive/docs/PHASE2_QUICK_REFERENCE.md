# 🚀 Phase 2: Quick Reference Card

## 🎯 **What We're Deploying**
- **CloudFront Distributions** for global CDN
- **SSL Certificates** for HTTPS everywhere
- **Enhanced S3 Security** with proper policies
- **Professional Subdomains** ready for services

## 🚀 **Deployment Commands**

### **1. Deploy Phase 2**
```bash
cd infrastructure
./deploy-phase2.sh
```

### **2. Check Deployment Status**
```bash
# CloudFormation stack status
aws cloudformation describe-stacks \
  --stack-name dcisionai-enhanced-domains-phase2 \
  --query 'Stacks[0].StackStatus' \
  --output text

# Stack outputs
aws cloudformation describe-stacks \
  --stack-name dcisionai-enhanced-domains-phase2 \
  --query 'Stacks[0].Outputs' \
  --output table
```

## 🔍 **Verification Commands**

### **SSL Certificate Status**
```bash
# Check certificate status
aws acm list-certificates --region us-east-1 \
  --query 'CertificateSummaryList[?DomainName==`dcisionai.com`].{Domain:DomainName,Status:Status}' \
  --output table

# Monitor validation progress
aws acm describe-certificate \
  --certificate-arn <certificate-arn> \
  --region us-east-1
```

### **CloudFront Distributions**
```bash
# List all distributions
aws cloudfront list-distributions \
  --query 'DistributionList.Items[?Comment!=`null`].{Comment:Comment,DomainName:DomainName,Status:Status}' \
  --output table

# Check specific distribution
aws cloudfront get-distribution --id <distribution-id>
```

### **DNS Resolution**
```bash
# Test subdomain resolution
nslookup mcp.dcisionai.com
nslookup sdk.dcisionai.com
nslookup docs.dcisionai.com
nslookup status.dcisionai.com

# Check Route 53 records
aws route53 list-resource-record-sets \
  --hosted-zone-id Z0178448QST5UHZB6URE \
  --query 'ResourceRecordSets[?Type==`A`].{Name:Name,Type:Type,Records:ResourceRecords}' \
  --output table
```

## 📊 **Expected Results**

### **✅ Success Indicators:**
- **Stack Status**: `CREATE_COMPLETE` or `UPDATE_COMPLETE`
- **SSL Certificate**: `ISSUED`
- **CloudFront**: 4 active distributions
- **DNS**: All subdomains resolve to CloudFront
- **HTTPS**: All subdomains accessible via HTTPS

### **🟡 Status Progression:**
1. **Stack Creation**: `CREATE_IN_PROGRESS` → `CREATE_COMPLETE`
2. **SSL Validation**: `PENDING_VALIDATION` → `ISSUED` (10-30 min)
3. **CloudFront**: `InProgress` → `Deployed`
4. **DNS Propagation**: Global (24-48 hours)

## 🚨 **Troubleshooting**

### **Common Issues:**
```bash
# Stack failed - check events
aws cloudformation describe-stack-events \
  --stack-name dcisionai-enhanced-domains-phase2 \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].{Resource:LogicalResourceId,Reason:ResourceStatusReason}' \
  --output table

# SSL stuck - check validation
aws acm describe-certificate \
  --certificate-arn <certificate-arn> \
  --region us-east-1 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord'

# CloudFront issues - check distribution
aws cloudfront get-distribution --id <distribution-id> \
  --query 'Distribution.Status'
```

### **Quick Fixes:**
- **Stack Rollback**: Delete and redeploy
- **SSL Issues**: Check DNS validation records
- **CloudFront**: Verify S3 bucket permissions
- **DNS Issues**: Check Route 53 configuration

## 🔄 **Next Steps After Phase 2**

### **Immediate (After Deployment):**
1. ✅ Wait for SSL certificate validation
2. ✅ Test all subdomains
3. ✅ Verify HTTPS access
4. ✅ Check performance

### **Phase 3 Preparation:**
1. 🔄 Plan service architecture
2. 🔄 Prepare content for S3 buckets
3. 🔄 Design monitoring and alerts
4. 🔄 Plan security hardening

## 📱 **Quick Status Check**
```bash
# One-liner to check everything
echo "=== PHASE 2 STATUS ===" && \
echo "Stack: $(aws cloudformation describe-stacks --stack-name dcisionai-enhanced-domains-phase2 --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo 'NOT_FOUND')" && \
echo "SSL: $(aws acm list-certificates --region us-east-1 --query 'CertificateSummaryList[?DomainName==`dcisionai.com`].Status' --output text 2>/dev/null || echo 'NOT_FOUND')" && \
echo "CloudFront: $(aws cloudfront list-distributions --query 'length(DistributionList.Items[?Comment!=`null`])' --output text 2>/dev/null || echo '0') distributions"
```

---

**🚀 Ready to deploy? Run `./deploy-phase2.sh`!**
