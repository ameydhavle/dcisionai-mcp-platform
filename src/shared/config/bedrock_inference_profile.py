"""
AWS Bedrock Inference Profile Management
Creates and manages inference profiles for mathematical reasoning models
"""

import logging
import boto3
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BedrockInferenceProfileManager:
    """Manages Bedrock inference profiles for mathematical reasoning models"""
    
    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        self.bedrock_client = boto3.client('bedrock', region_name=aws_region)
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region)
        
        # Math-optimized models in order of preference
        self.math_models = [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",  # Best for complex math reasoning
            "anthropic.claude-3-5-sonnet-20240620-v1:0",  # Excellent optimization modeling
            "anthropic.claude-3-opus-20240229-v1:0",      # Superior mathematical reasoning
            "anthropic.claude-3-sonnet-20240229-v1:0",    # Strong optimization capabilities
        ]
        
        self.inference_profile_name = "dcisionai-math-reasoning-profile"
        self.inference_profile_arn = None
    
    async def ensure_inference_profile(self) -> str:
        """Get the best available mathematical reasoning model"""
        try:
            # Get available models
            available_models = await self._get_available_models()
            
            # Find the best available math model
            selected_model = None
            for model in self.math_models:
                if model in available_models:
                    selected_model = model
                    break
            
            if not selected_model:
                # Try to find any Claude model
                claude_models = [m for m in available_models if 'claude' in m.lower()]
                if claude_models:
                    selected_model = claude_models[0]
                else:
                    raise Exception("No suitable mathematical reasoning models available")
            
            self.inference_profile_arn = selected_model
            logger.info(f"Selected mathematical reasoning model: {selected_model}")
            return selected_model
            
        except Exception as e:
            logger.error(f"Failed to select mathematical reasoning model: {e}")
            raise
    
    async def _get_existing_profile(self) -> Optional[str]:
        """Check if inference profile already exists"""
        try:
            response = self.bedrock_client.list_inference_profiles()
            
            for profile in response.get('inferenceProfileSummaries', []):
                if profile['inferenceProfileName'] == self.inference_profile_name:
                    return profile['inferenceProfileArn']
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to list existing profiles: {e}")
            return None
    
    async def _create_inference_profile(self) -> Optional[str]:
        """Create new inference profile for mathematical reasoning"""
        try:
            # Get available models
            available_models = await self._get_available_models()
            
            # Find the best available math model
            selected_model = None
            for model in self.math_models:
                if model in available_models:
                    selected_model = model
                    break
            
            if not selected_model:
                raise Exception("No suitable mathematical reasoning models available")
            
            logger.info(f"Creating inference profile with model: {selected_model}")
            
            # Get the full model ARN
            model_arn = f"arn:aws:bedrock:{self.aws_region}::foundation-model/{selected_model}"
            
            # Create inference profile
            response = self.bedrock_client.create_inference_profile(
                inferenceProfileName=self.inference_profile_name,
                description="DcisionAI inference profile optimized for mathematical reasoning and optimization problems",
                modelSource={
                    'copyFrom': model_arn
                },
                tags=[
                    {
                        'key': 'Purpose',
                        'value': 'MathematicalReasoning'
                    },
                    {
                        'key': 'Application',
                        'value': 'DcisionAI'
                    },
                    {
                        'key': 'OptimizedFor',
                        'value': 'OptimizationProblems'
                    }
                ]
            )
            
            profile_arn = response['inferenceProfileArn']
            
            # Wait for profile to be active
            await self._wait_for_profile_active(profile_arn)
            
            return profile_arn
            
        except Exception as e:
            logger.error(f"Failed to create inference profile: {e}")
            return None
    
    async def _get_available_models(self) -> list:
        """Get list of available foundation models"""
        try:
            response = self.bedrock_client.list_foundation_models(
                byOutputModality='TEXT'
            )
            
            return [model['modelId'] for model in response['modelSummaries']]
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def _wait_for_profile_active(self, profile_arn: str, max_wait_time: int = 300):
        """Wait for inference profile to become active"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = self.bedrock_client.get_inference_profile(
                    inferenceProfileIdentifier=profile_arn
                )
                
                status = response['status']
                logger.info(f"Inference profile status: {status}")
                
                if status == 'ACTIVE':
                    return True
                elif status == 'FAILED':
                    raise Exception(f"Inference profile creation failed: {response.get('failureMessage', 'Unknown error')}")
                
                # Wait before checking again
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error checking profile status: {e}")
                time.sleep(10)
        
        raise Exception(f"Inference profile did not become active within {max_wait_time} seconds")
    
    async def invoke_model(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.1) -> str:
        """Invoke the selected mathematical reasoning model"""
        if not self.inference_profile_arn:
            raise Exception("Mathematical reasoning model not initialized")
        
        try:
            model_id = self.inference_profile_arn
            
            # Prepare request body based on model type
            if "anthropic" in model_id.lower():
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": temperature,
                    "top_p": 0.9
                }
            elif "meta.llama" in model_id.lower():
                body = {
                    "prompt": prompt,
                    "max_gen_len": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9
                }
            elif "amazon.titan" in model_id.lower():
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": temperature,
                        "topP": 0.9
                    }
                }
            else:
                # Generic format
                body = {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            
            # Invoke model
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response based on model type
            response_body = json.loads(response['body'].read())
            
            if "anthropic" in model_id.lower():
                return response_body['content'][0]['text']
            elif "meta.llama" in model_id.lower():
                return response_body['generation']
            elif "amazon.titan" in model_id.lower():
                return response_body['results'][0]['outputText']
            else:
                # Try common response formats
                return (response_body.get('completion') or 
                       response_body.get('text') or 
                       response_body.get('generated_text') or 
                       str(response_body))
            
        except Exception as e:
            logger.error(f"Mathematical reasoning model invocation failed: {e}")
            raise
    
    async def get_profile_info(self) -> Dict[str, Any]:
        """Get information about the selected mathematical reasoning model"""
        if not self.inference_profile_arn:
            return {"status": "not_initialized"}
        
        try:
            # Since we're using the model directly, return model info
            return {
                "profile_name": f"Mathematical Reasoning Model",
                "profile_arn": self.inference_profile_arn,
                "status": "ACTIVE",
                "model_source": {"model_id": self.inference_profile_arn},
                "description": "Best available model for mathematical reasoning and optimization"
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"status": "error", "error": str(e)}


# Global instance for reuse across tools
_inference_profile_manager = None

async def get_inference_profile_manager(aws_region: str = "us-east-1") -> BedrockInferenceProfileManager:
    """Get or create global inference profile manager"""
    global _inference_profile_manager
    
    if _inference_profile_manager is None:
        _inference_profile_manager = BedrockInferenceProfileManager(aws_region)
        await _inference_profile_manager.ensure_inference_profile()
    
    return _inference_profile_manager