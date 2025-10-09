#!/usr/bin/env python3
"""
AWS Bedrock Inference Profiles Setup
===================================

Set up inference profiles for all optimization agents with proper IAM permissions.
This follows AWS best practices for production deployment.
"""

import boto3
import json
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS clients
bedrock_client = boto3.client('bedrock', region_name='us-east-1')
iam_client = boto3.client('iam', region_name='us-east-1')

class InferenceProfileManager:
    """Manages inference profiles for optimization agents."""
    
    def __init__(self):
        self.profiles = {
            "intent_classification": {
                "name": "dcisionai-intent-classification",
                "description": "Intent classification for optimization problems",
                "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
                "max_tokens": 1000,
                "temperature": 0.1,
                "system_prompt": "You are an expert operations research analyst. Classify optimization problems into specific intents with high accuracy."
            },
            "data_analysis": {
                "name": "dcisionai-data-analysis", 
                "description": "Data analysis for optimization problems",
                "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
                "max_tokens": 2000,
                "temperature": 0.2,
                "system_prompt": "You are an expert data analyst. Analyze optimization problems and identify required data entities and complexity."
            },
            "model_building": {
                "name": "dcisionai-model-building",
                "description": "Mathematical model building for optimization",
                "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",  # Use Sonnet for complex model generation
                "max_tokens": 4000,
                "temperature": 0.1,
                "system_prompt": "You are an expert operations research scientist. Build realistic mathematical optimization models with proper variables and constraints."
            },
            "optimization_solution": {
                "name": "dcisionai-optimization-solution",
                "description": "Optimization solution and recommendations",
                "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
                "max_tokens": 3000,
                "temperature": 0.3,
                "system_prompt": "You are an expert optimization consultant. Provide detailed solutions and actionable recommendations."
            }
        }
    
    def create_inference_profile(self, profile_config: Dict[str, Any]) -> bool:
        """Create an inference profile for a specific agent."""
        try:
            logger.info(f"Creating inference profile: {profile_config['name']}")
            
            # Create the inference profile (not provisioned throughput)
            response = bedrock_client.create_inference_profile(
                inferenceProfileName=profile_config['name'],
                modelSource={
                    'copyFrom': f"arn:aws:bedrock:us-east-1::foundation-model/{profile_config['model_id']}"
                },
                description=profile_config['description'],
                tags=[
                    {
                        'key': 'Project',
                        'value': 'DcisionAI-Optimization'
                    },
                    {
                        'key': 'Agent',
                        'value': profile_config['name']
                    }
                ]
            )
            
            logger.info(f"✅ Created inference profile: {profile_config['name']}")
            logger.info(f"Inference Profile ARN: {response['inferenceProfileArn']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create inference profile {profile_config['name']}: {e}")
            return False
    
    def create_iam_policy(self) -> str:
        """Create IAM policy for Bedrock inference profiles."""
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": [
                        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:GetProvisionedModelThroughput",
                        "bedrock:ListProvisionedModelThroughputs"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            policy_name = "DcisionAI-Bedrock-Inference-Profile-Policy"
            
            # Create the policy
            response = iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document),
                Description="Policy for DcisionAI optimization agents to access Bedrock inference profiles"
            )
            
            policy_arn = response['Policy']['Arn']
            logger.info(f"✅ Created IAM policy: {policy_arn}")
            
            return policy_arn
            
        except iam_client.exceptions.EntityAlreadyExistsException:
            logger.info(f"Policy {policy_name} already exists")
            return f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:policy/{policy_name}"
        except Exception as e:
            logger.error(f"❌ Failed to create IAM policy: {e}")
            return None
    
    def attach_policy_to_role(self, role_name: str, policy_arn: str) -> bool:
        """Attach the Bedrock policy to a Lambda execution role."""
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            
            logger.info(f"✅ Attached policy to role: {role_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to attach policy to role {role_name}: {e}")
            return False
    
    def setup_all_profiles(self) -> bool:
        """Set up all inference profiles for optimization agents."""
        logger.info("Setting up inference profiles for all optimization agents...")
        
        # Create IAM policy first
        policy_arn = self.create_iam_policy()
        if not policy_arn:
            return False
        
        # Attach policy to Lambda role
        lambda_role = "dcisionai-streaming-lambda-role"
        if not self.attach_policy_to_role(lambda_role, policy_arn):
            logger.warning(f"Could not attach policy to {lambda_role}, continuing...")
        
        # Create inference profiles
        success_count = 0
        for agent_name, profile_config in self.profiles.items():
            if self.create_inference_profile(profile_config):
                success_count += 1
        
        logger.info(f"✅ Successfully created {success_count}/{len(self.profiles)} inference profiles")
        return success_count == len(self.profiles)
    
    def list_existing_profiles(self) -> List[Dict[str, Any]]:
        """List existing inference profiles."""
        try:
            response = bedrock_client.list_inference_profiles()
            profiles = response.get('inferenceProfileSummaries', [])
            
            logger.info(f"Found {len(profiles)} existing inference profiles:")
            for profile in profiles:
                logger.info(f"  - {profile['inferenceProfileName']}: {profile['inferenceProfileArn']}")
            
            return profiles
            
        except Exception as e:
            logger.error(f"❌ Failed to list inference profiles: {e}")
            return []
    
    def get_profile_arn(self, profile_name: str) -> str:
        """Get the ARN of a specific inference profile."""
        try:
            response = bedrock_client.get_inference_profile(
                inferenceProfileIdentifier=profile_name
            )
            return response['inferenceProfileArn']
            
        except Exception as e:
            logger.error(f"❌ Failed to get profile ARN for {profile_name}: {e}")
            return None

def main():
    """Main function to set up inference profiles."""
    logger.info("🚀 Starting AWS Bedrock Inference Profiles Setup")
    
    manager = InferenceProfileManager()
    
    # List existing profiles first
    logger.info("\n📋 Checking existing inference profiles...")
    existing_profiles = manager.list_existing_profiles()
    
    # Set up all profiles
    logger.info("\n🔧 Setting up inference profiles...")
    success = manager.setup_all_profiles()
    
    if success:
        logger.info("\n✅ All inference profiles set up successfully!")
        logger.info("\n📝 Next steps:")
        logger.info("1. Update Lambda function to use inference profile ARNs")
        logger.info("2. Test each agent with the new inference profiles")
        logger.info("3. Monitor performance and adjust model units as needed")
    else:
        logger.error("\n❌ Some inference profiles failed to set up")
        logger.info("Check the logs above for specific errors")

if __name__ == "__main__":
    main()
