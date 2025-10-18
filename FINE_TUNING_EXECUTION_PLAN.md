# 🚀 DcisionAI Fine-Tuning Execution Plan

## 📋 **Overview**

This document provides a step-by-step execution plan for fine-tuning DcisionAI models using AWS Bedrock, leveraging our comprehensive S3 training data.

---

## 🎯 **Prerequisites**

### **AWS Account Setup**
- AWS Account with Bedrock access
- Appropriate IAM permissions for model customization
- S3 buckets for training data and model outputs

### **Required Tools**
- AWS CLI configured with appropriate credentials
- Python 3.8+ with boto3
- Access to our S3 training data bucket

---

## 📊 **Step-by-Step Execution**

### **Step 1: Environment Setup** (Day 1)

**1.1 Configure AWS CLI**
```bash
# Configure AWS credentials
aws configure

# Verify Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

**1.2 Create S3 Buckets**
```bash
# Create training data bucket
aws s3 mb s3://dcisionai-training-bucket --region us-east-1

# Create models output bucket  
aws s3 mb s3://dcisionai-models-bucket --region us-east-1

# Set up bucket policies for Bedrock access
aws s3api put-bucket-policy --bucket dcisionai-training-bucket --policy file://bucket-policy.json
```

**1.3 Install Dependencies**
```bash
# Install required Python packages
pip install boto3 argparse

# Make scripts executable
chmod +x scripts/convert_training_data.py
chmod +x scripts/submit_fine_tuning_job.py
```

### **Step 2: Data Preparation** (Day 1-2)

**2.1 Convert Training Data**
```bash
# Convert S3 JSON models to Bedrock training format
python scripts/convert_training_data.py \
  --input-bucket dcisionai-slm-training-data \
  --output-bucket dcisionai-training-bucket \
  --output-dir ./training_data
```

**Expected Output**:
- `train.jsonl`: ~450 training examples
- `validation.jsonl`: ~50 validation examples  
- `metadata.json`: Dataset statistics

**2.2 Validate Training Data**
```bash
# Check training data format
head -5 training_data/train.jsonl | jq .

# Verify data quality
python scripts/validate_training_data.py --input training_data/
```

**2.3 Upload to S3**
```bash
# Upload training data to S3
aws s3 cp training_data/train.jsonl s3://dcisionai-training-bucket/training_data/
aws s3 cp training_data/validation.jsonl s3://dcisionai-training-bucket/training_data/
aws s3 cp training_data/metadata.json s3://dcisionai-training-bucket/training_data/
```

### **Step 3: Fine-Tuning Job Submission** (Day 2)

**3.1 Submit Fine-Tuning Job**
```bash
# Submit fine-tuning job to AWS Bedrock
python scripts/submit_fine_tuning_job.py \
  --region us-east-1 \
  --bucket dcisionai-training-bucket \
  --training-data training_data/train.jsonl \
  --validation-data training_data/validation.jsonl \
  --output-data custom-models/ \
  --model-name dcisionai-optimization-expert \
  --monitor
```

**Expected Timeline**: 4-8 hours for 500 examples

**3.2 Monitor Job Progress**
```bash
# Check job status
aws bedrock get-model-customization-job \
  --job-identifier arn:aws:bedrock:us-east-1:ACCOUNT:model-customization-job/JOB_ID

# List custom models
aws bedrock list-custom-models
```

### **Step 4: Model Validation** (Day 3)

**4.1 Test Custom Model**
```bash
# Test the fine-tuned model
python scripts/test_custom_model.py \
  --model-arn arn:aws:bedrock:us-east-1:ACCOUNT:custom-model/MODEL_ID \
  --test-problems test_problems.json
```

**4.2 Performance Benchmarking**
```bash
# Run comprehensive tests
python scripts/benchmark_model.py \
  --baseline-model anthropic.claude-3-haiku-20240307-v1:0 \
  --custom-model arn:aws:bedrock:us-east-1:ACCOUNT:custom-model/MODEL_ID \
  --test-suite optimization_test_suite.json
```

### **Step 5: Integration** (Day 4-5)

**5.1 Update MCP Server**
```python
# Update MCP server to use custom model
CUSTOM_MODEL_ARN = "arn:aws:bedrock:us-east-1:ACCOUNT:custom-model/MODEL_ID"

# Modify tools.py to use custom model
async def classify_intent(self, problem_description: str):
    response = await self.bedrock_client.invoke_model(
        modelId=CUSTOM_MODEL_ARN,  # Use custom model
        body=json.dumps({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": problem_description}
            ]
        })
    )
```

**5.2 Deploy to AgentCore**
```bash
# Update AgentCore deployment with custom model
cd saas-platform/deployment/
python deploy_to_agentcore.py --custom-model-arn CUSTOM_MODEL_ARN
```

**5.3 Update SaaS Platform**
```bash
# Update SaaS platform backend
cd saas-platform/backend/
# Update agentcore_client.py to use custom model
python app.py  # Test with custom model
```

---

## 📊 **Expected Results**

### **Performance Improvements**

| Metric | Before Fine-Tuning | After Fine-Tuning | Improvement |
|--------|-------------------|-------------------|-------------|
| **Accuracy** | 85-92% | 95%+ | +10% |
| **Response Time** | 2-3 seconds | 1-2 seconds | -33% |
| **Domain Coverage** | 10-15 domains | 50+ domains | +300% |
| **Mathematical Correctness** | 80-85% | 95%+ | +15% |
| **Business Logic** | 75-80% | 90%+ | +15% |

### **Cost Analysis**

**Training Costs** (One-time):
- Claude 3 Haiku Fine-tuning: ~$800 for 500 examples
- Storage: ~$50/month
- **Total**: ~$850

**Inference Costs** (Ongoing):
- Custom Model Premium: ~20% over base model
- Expected Usage: 1,000 requests/day
- **Additional Monthly Cost**: ~$200-300

**ROI Calculation**:
- **Development Time Saved**: 50% reduction in prompt engineering
- **Customer Satisfaction**: Higher success rates
- **Break-even**: 2-3 months with current usage

---

## 🔧 **Troubleshooting Guide**

### **Common Issues**

**1. Training Data Format Errors**
```bash
# Validate JSONL format
python -c "
import json
with open('training_data/train.jsonl') as f:
    for i, line in enumerate(f):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f'Error on line {i+1}: {e}')
"
```

**2. IAM Permission Issues**
```bash
# Check IAM permissions
aws iam get-role --role-name BedrockCustomModelRole
aws iam list-attached-role-policies --role-name BedrockCustomModelRole
```

**3. S3 Access Issues**
```bash
# Test S3 access
aws s3 ls s3://dcisionai-training-bucket/
aws s3 cp test.txt s3://dcisionai-training-bucket/test.txt
```

**4. Job Failure Debugging**
```bash
# Get detailed job information
aws bedrock get-model-customization-job \
  --job-identifier JOB_ARN \
  --query 'failureMessage'
```

### **Monitoring Commands**

```bash
# Monitor job progress
watch -n 60 'aws bedrock get-model-customization-job --job-identifier JOB_ARN --query "status"'

# Check training metrics
aws bedrock get-model-customization-job \
  --job-identifier JOB_ARN \
  --query 'trainingMetrics'

# List all custom models
aws bedrock list-custom-models --query 'modelSummaries[*].[modelName,modelStatus]'
```

---

## 📈 **Success Metrics**

### **Technical Metrics**
- ✅ **Accuracy**: >95% correct model formulation
- ✅ **Speed**: <2 seconds average response time
- ✅ **Coverage**: Support for 50+ optimization domains
- ✅ **Quality**: Mathematically sound formulations

### **Business Metrics**
- ✅ **Customer Satisfaction**: >90% positive feedback
- ✅ **Support Reduction**: 30% fewer optimization issues
- ✅ **Usage Growth**: 25% increase in platform usage
- ✅ **Revenue Impact**: 15% increase in conversion rates

---

## 🔄 **Continuous Improvement**

### **Data Collection**
- Collect user feedback on optimization results
- Monitor model performance metrics
- Identify new optimization domains

### **Model Updates**
- Quarterly fine-tuning with new data
- Domain-specific model variants
- Performance optimization

### **Quality Assurance**
- Automated testing pipeline
- Mathematical validation
- Business logic verification

---

## 📞 **Support and Resources**

### **AWS Bedrock Documentation**
- [Model Customization Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-supported.html)
- [Data Preparation Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html)
- [Job Submission Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-submit.html)

### **DcisionAI Resources**
- Training Data: `s3://dcisionai-slm-training-data/trainingdata/`
- Conversion Scripts: `scripts/convert_training_data.py`
- Job Submission: `scripts/submit_fine_tuning_job.py`
- Test Suite: `test_suite/optimization_validation.json`

---

*This execution plan provides a comprehensive roadmap for fine-tuning DcisionAI models using AWS Bedrock, leveraging our extensive S3 training data to create a specialized optimization expert.*
