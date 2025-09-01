# Deployment Guide

This guide covers the CI/CD pipeline and deployment process for the DcisionAI MCP Server Platform.

## 🚀 CI/CD Pipeline Overview

### Workflow Triggers
- **Push to `main`**: Full CI/CD pipeline (test → build → deploy staging)
- **Push to `develop`**: Test only
- **Pull Request**: Test only
- **Release published**: Deploy to production

### Pipeline Stages

1. **Test Suite** (`test` job)
   - Python 3.11 setup
   - Dependency installation
   - Run all test suites
   - Code coverage reporting

2. **Security Scan** (`security-scan` job)
   - Bandit security analysis
   - Safety dependency check

3. **Build** (`build` job)
   - Docker image build for AMD64
   - Push to Amazon ECR
   - Tag with commit SHA and latest

4. **Deploy Staging** (`deploy-staging` job)
   - Deploy to staging environment
   - Health check validation
   - Automatic rollback on failure

5. **Deploy Production** (`deploy-production` job)
   - Deploy to production environment
   - Health check validation
   - Manual approval required

## 🔧 Setup Requirements

### GitHub Secrets
Configure these secrets in your GitHub repository settings:

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### AWS Permissions
The AWS credentials need these permissions:
- ECR: Full access
- ECS: Full access
- CloudFormation: Full access
- EC2: Read access for network interfaces
- IAM: Role creation for ECS tasks

### GitHub Environments
Create these environments in your repository:
- `staging`: For staging deployments
- `production`: For production deployments (with protection rules)

## 📋 Manual Deployment

### Local Development
```bash
# Run tests locally
python tests/test_fallback_server.py
python tests/test_intent_responses.py
python tests/test_specific_intents.py

# Start local server
python src/mcp_server_fallback.py
```

### Manual AWS Deployment
```bash
# Deploy to staging
python scripts/deployment/dcisionai_manufacturing_deploy_agentcore.py

# Deploy to production
python scripts/deployment/dcisionai_manufacturing_invoke_agentcore.py
```

### Check Deployment Status
```bash
# Check ECS service status
aws ecs describe-services \
  --cluster DcisionAI-MCP-Simple-staging \
  --services DcisionAI-MCP-Simple-Service-staging \
  --region us-east-1

# Get service URL
aws ecs list-tasks \
  --cluster DcisionAI-MCP-Simple-staging \
  --service-name DcisionAI-MCP-Simple-Service-staging \
  --region us-east-1
```

## 🔍 Monitoring and Health Checks

### Health Endpoints
- **Health Check**: `GET /health`
- **Root**: `GET /`
- **MCP Protocol**: `POST /mcp`

### CloudWatch Monitoring
- ECS service metrics
- Application logs
- Custom business metrics

### Alerts
- Service health check failures
- High error rates
- Performance degradation

## 🚨 Troubleshooting

### Common Issues

1. **Docker Build Failures**
   ```bash
   # Check Docker build locally
   docker buildx build --platform linux/amd64 -f Dockerfile.mcp -t test .
   ```

2. **ECS Deployment Failures**
   ```bash
   # Check ECS service events
   aws ecs describe-services \
     --cluster DcisionAI-MCP-Simple-staging \
     --services DcisionAI-MCP-Simple-Service-staging
   ```

3. **Health Check Failures**
   ```bash
   # Check application logs
   aws logs get-log-events \
     --log-group-name "/ecs/DcisionAI-MCP-Simple-staging" \
     --log-stream-name "latest"
   ```

### Rollback Process
```bash
# Rollback to previous version
aws ecs update-service \
  --cluster DcisionAI-MCP-Simple-staging \
  --service DcisionAI-MCP-Simple-Service-staging \
  --task-definition previous-task-definition-arn
```

## 📊 Performance Metrics

### Key Metrics
- **Response Time**: <0.15s for intent classification
- **Uptime**: 99.9% target
- **Error Rate**: <0.1% target
- **Throughput**: 1000+ requests/minute

### Monitoring Dashboard
- CloudWatch dashboard: `DcisionAI-MCP-Monitoring`
- Metrics: CPU, Memory, Network, Application

## 🔒 Security

### Network Security
- VPC isolation
- Security groups
- No direct internet access

### Application Security
- HTTPS only
- IAM roles with least privilege
- Container security scanning

### Secrets Management
- AWS Secrets Manager for sensitive data
- Environment variables for configuration
- No secrets in code

## 📈 Scaling

### Auto Scaling
- ECS service auto scaling based on CPU/Memory
- Target tracking scaling policies
- Scale out: 70% CPU utilization
- Scale in: 30% CPU utilization

### Manual Scaling
```bash
# Scale service
aws ecs update-service \
  --cluster DcisionAI-MCP-Simple-staging \
  --service DcisionAI-MCP-Simple-Service-staging \
  --desired-count 3
```

## 🎯 Best Practices

1. **Always test locally before pushing**
2. **Use feature branches for development**
3. **Review pull requests thoroughly**
4. **Monitor deployments closely**
5. **Keep dependencies updated**
6. **Document all changes**
7. **Use semantic versioning**

## 📞 Support

For deployment issues:
1. Check GitHub Actions logs
2. Review CloudWatch logs
3. Verify AWS credentials
4. Contact the development team

---

**Status**: ✅ CI/CD Pipeline Ready - Automated deployment to staging and production!
