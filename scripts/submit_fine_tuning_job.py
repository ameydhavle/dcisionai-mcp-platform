#!/usr/bin/env python3
"""
Submit Fine-Tuning Job to AWS Bedrock
====================================

This script submits a fine-tuning job to AWS Bedrock for Claude 3 Haiku
using our converted training data.
"""

import boto3
import json
import time
from datetime import datetime
import argparse

class BedrockFineTuningJob:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_client = boto3.client('bedrock', region_name=region)
        
    def submit_fine_tuning_job(self, 
                             base_model_id: str,
                             custom_model_name: str,
                             training_data_s3_uri: str,
                             validation_data_s3_uri: str,
                             output_data_s3_uri: str,
                             hyperparameters: dict = None):
        """Submit a fine-tuning job to AWS Bedrock."""
        
        # Default hyperparameters
        if hyperparameters is None:
            hyperparameters = {
                "epochCount": "3",
                "batchSize": "1",
                "learningRate": "0.0001"
            }
        
        # Job configuration
        job_config = {
            "jobName": f"dcisionai-{int(time.time())}",
            "baseModelIdentifier": base_model_id,
            "customModelName": custom_model_name,
            "trainingDataConfig": {
                "s3Uri": training_data_s3_uri
            },
            "validationDataConfig": {
                "validators": [
                    {
                        "s3Uri": validation_data_s3_uri
                    }
                ]
            },
            "outputDataConfig": {
                "s3Uri": output_data_s3_uri
            },
            "hyperParameters": hyperparameters,
            "roleArn": self._get_or_create_role_arn(),
            "clientRequestToken": f"dcisionai-{int(time.time())}"
        }
        
        try:
            print(f"Submitting fine-tuning job for model: {custom_model_name}")
            print(f"Base model: {base_model_id}")
            print(f"Training data: {training_data_s3_uri}")
            print(f"Validation data: {validation_data_s3_uri}")
            print(f"Output location: {output_data_s3_uri}")
            
            response = self.bedrock_client.create_model_customization_job(**job_config)
            
            job_arn = response['jobArn']
            print(f"✅ Fine-tuning job submitted successfully!")
            print(f"Job ARN: {job_arn}")
            
            return job_arn
            
        except Exception as e:
            print(f"❌ Error submitting fine-tuning job: {e}")
            raise
    
    def _get_or_create_role_arn(self) -> str:
        """Get or create IAM role for Bedrock fine-tuning."""
        
        iam_client = boto3.client('iam')
        role_name = 'BedrockModelCustomizationRole'
        
        try:
            # Try to get existing role
            response = iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            print(f"Using existing role: {role_arn}")
            return role_arn
            
        except iam_client.exceptions.NoSuchEntityException:
            # Create new role
            print(f"Creating new IAM role: {role_name}")
            
            # Trust policy for Bedrock
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "bedrock.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            # Create role
            iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for Bedrock model customization'
            )
            
            # Attach policies
            policies = [
                'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            ]
            
            for policy_arn in policies:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            # Get role ARN
            response = iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            
            print(f"✅ Created role: {role_arn}")
            return role_arn
    
    def monitor_job(self, job_arn: str):
        """Monitor the fine-tuning job progress."""
        
        print(f"\n🔍 Monitoring job: {job_arn}")
        
        while True:
            try:
                response = self.bedrock_client.get_model_customization_job(
                    jobIdentifier=job_arn
                )
                
                status = response['status']
                print(f"Status: {status}")
                
                if status in ['Completed', 'Failed', 'Stopped']:
                    if status == 'Completed':
                        print("✅ Fine-tuning job completed successfully!")
                        custom_model_arn = response.get('customModelArn')
                        if custom_model_arn:
                            print(f"Custom model ARN: {custom_model_arn}")
                    else:
                        print(f"❌ Job {status.lower()}")
                        if 'failureMessage' in response:
                            print(f"Failure message: {response['failureMessage']}")
                    break
                
                # Wait before checking again
                time.sleep(60)
                
            except Exception as e:
                print(f"Error monitoring job: {e}")
                break
    
    def list_custom_models(self):
        """List all custom models."""
        
        try:
            response = self.bedrock_client.list_custom_models()
            
            print("\n📋 Custom Models:")
            for model in response.get('modelSummaries', []):
                print(f"- {model['modelName']} ({model['modelArn']})")
                print(f"  Status: {model['status']}")
                print(f"  Created: {model['creationTime']}")
                print()
                
        except Exception as e:
            print(f"Error listing custom models: {e}")

def main():
    parser = argparse.ArgumentParser(description='Submit fine-tuning job to AWS Bedrock')
    parser.add_argument('--base-model', 
                       default='anthropic.claude-3-haiku-20240307-v1:0',
                       help='Base model identifier')
    parser.add_argument('--custom-model-name', 
                       default='dcisionai-optimization-expert',
                       help='Name for the custom model')
    parser.add_argument('--training-data-s3', 
                       default='s3://dcisionai-training-bucket/training_data/train.jsonl',
                       help='S3 URI for training data')
    parser.add_argument('--validation-data-s3', 
                       default='s3://dcisionai-training-bucket/training_data/validation.jsonl',
                       help='S3 URI for validation data')
    parser.add_argument('--output-data-s3', 
                       default='s3://dcisionai-models-bucket/output/',
                       help='S3 URI for output data')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor job progress after submission')
    parser.add_argument('--list-models', action='store_true',
                       help='List existing custom models')
    
    args = parser.parse_args()
    
    # Initialize fine-tuning job
    fine_tuning = BedrockFineTuningJob()
    
    if args.list_models:
        fine_tuning.list_custom_models()
        return
    
    # Submit fine-tuning job
    job_arn = fine_tuning.submit_fine_tuning_job(
        base_model_id=args.base_model,
        custom_model_name=args.custom_model_name,
        training_data_s3_uri=args.training_data_s3,
        validation_data_s3_uri=args.validation_data_s3,
        output_data_s3_uri=args.output_data_s3
    )
    
    if args.monitor:
        fine_tuning.monitor_job(job_arn)
    else:
        print(f"\n💡 To monitor job progress, run:")
        print(f"aws bedrock get-model-customization-job --job-identifier {job_arn}")

if __name__ == "__main__":
    main()