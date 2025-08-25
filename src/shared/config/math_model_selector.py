"""
Mathematical Reasoning Model Selector
Selects the best available model for mathematical reasoning with Bedrock and Claude API fallback
"""

import logging
import boto3
import json
import asyncio
import time
from typing import Dict, Any, Optional
from config.llm_client import create_math_llm_client, UnifiedLLMClient, LLMClientError

logger = logging.getLogger(__name__)

# AWS Bedrock Request Manager following best practices
class BedrockRequestManager:
    def __init__(self, max_concurrent_requests: int = 2, requests_per_minute: int = 10):
        self.max_concurrent = max_concurrent_requests
        self.requests_per_minute = requests_per_minute
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.request_times = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a Bedrock request"""
        # Limit concurrent requests
        await self.semaphore.acquire()
        
        # Implement rate limiting
        async with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.request_times = [req_time for req_time in self.request_times if now - req_time < 60]
            
            # If we're at the rate limit, wait
            if len(self.request_times) >= self.requests_per_minute:
                wait_time = 60 - (now - self.request_times[0]) + 1
                logger.info(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                return await self.acquire()
            
            # Record this request
            self.request_times.append(now)
    
    def release(self):
        """Release the semaphore after request completion"""
        self.semaphore.release()

# Global request manager instance
_bedrock_manager = BedrockRequestManager(max_concurrent_requests=2, requests_per_minute=8)


class MathModelSelector:
    """Selects and manages the best mathematical reasoning model with Bedrock and Claude API fallback"""
    
    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        self.bedrock_client = boto3.client('bedrock', region_name=aws_region)
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region)
        
        # Initialize unified LLM client with fallback capability
        self.unified_client = create_math_llm_client(region=aws_region)
        
        # Inference Profiles for production use (better rate limits and failover)
        self.inference_profiles = [
            "us.anthropic.claude-3-5-sonnet-20240620-v1:0",  # Inference profile for Claude 3.5 Sonnet
            "us.anthropic.claude-3-sonnet-20240229-v1:0",    # Inference profile for Claude 3 Sonnet
            "us.anthropic.claude-3-haiku-20240307-v1:0",     # Inference profile for Claude 3 Haiku
        ]
        
        # Fallback to direct models if inference profiles not available
        self.direct_models = [
            "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "anthropic.claude-3-sonnet-20240229-v1:0", 
            "anthropic.claude-3-haiku-20240307-v1:0",
        ]
        
        self.selected_model = None
    
    async def get_best_math_model(self) -> str:
        """Get the best available model, preferring inference profiles for production"""
        try:
            # Get available models and inference profiles
            available_models = await self._get_available_models()
            available_profiles = await self._get_available_inference_profiles()
            
            # First, try inference profiles (better for production)
            for profile in self.inference_profiles:
                if profile in available_profiles:
                    self.selected_model = profile
                    logger.info(f"Selected inference profile: {profile}")
                    return profile
            
            # Fallback to direct models
            for model in self.direct_models:
                if model in available_models:
                    self.selected_model = model
                    logger.info(f"Selected direct model: {model}")
                    return model
            
            # Last resort: any Claude model
            claude_models = [m for m in available_models if 'claude' in m.lower()]
            if claude_models:
                self.selected_model = claude_models[0]
                logger.info(f"Using available Claude model: {claude_models[0]}")
                return claude_models[0]
            
            raise Exception("No suitable mathematical reasoning models available in this region")
            
        except Exception as e:
            logger.error(f"Failed to select mathematical reasoning model: {e}")
            raise
    
    async def _get_available_models(self) -> list:
        """Get list of available foundation models"""
        try:
            response = self.bedrock_client.list_foundation_models(
                byOutputModality='TEXT'
            )
            
            return [model['modelId'] for model in response['modelSummaries']]
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            raise
    
    async def _get_available_inference_profiles(self) -> list:
        """Get list of available inference profiles"""
        try:
            # Try to list inference profiles (this API might not be available in all regions)
            try:
                response = self.bedrock_client.list_inference_profiles()
                return [profile['inferenceProfileId'] for profile in response.get('inferenceProfileSummaries', [])]
            except Exception as e:
                logger.warning(f"Could not list inference profiles: {e}")
                # Return expected inference profile IDs based on region
                return [
                    f"{self.aws_region}.anthropic.claude-3-5-sonnet-20240620-v1:0",
                    f"{self.aws_region}.anthropic.claude-3-sonnet-20240229-v1:0",
                    f"{self.aws_region}.anthropic.claude-3-haiku-20240307-v1:0",
                ]
            
        except Exception as e:
            logger.warning(f"Failed to get inference profiles, using direct models: {e}")
            return []
    
    async def invoke_model(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.1, retry_count: int = 0) -> str:
        """Invoke mathematical reasoning model with automatic Bedrock/Claude API fallback"""
        
        # Apply AWS best practices for request management
        await _bedrock_manager.acquire()
        
        try:
            # Use unified client with automatic fallback
            result = await self.unified_client.invoke_model(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                retry_count=retry_count
            )
            
            logger.info("Mathematical reasoning model invocation successful")
            return result
            
        except LLMClientError as e:
            logger.error(f"LLM invocation failed: {e}")
            raise Exception(f"Mathematical reasoning model failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error in model invocation: {e}")
            raise Exception(f"Mathematical reasoning model error: {str(e)}")
        finally:
            # Always release the semaphore
            _bedrock_manager.release()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the selected model"""
        if not self.selected_model:
            return {"status": "not_selected"}
        
        is_inference_profile = self.selected_model.startswith(f"{self.aws_region}.")
        
        return {
            "model_id": self.selected_model,
            "status": "ACTIVE",
            "type": "inference_profile" if is_inference_profile else "direct_model",
            "description": f"Mathematical reasoning optimized {'inference profile' if is_inference_profile else 'model'}",
            "capabilities": ["mathematical_reasoning", "optimization_modeling", "problem_solving"],
            "production_optimized": is_inference_profile
        }


# Global instance for reuse across tools
_math_model_selector = None

async def get_math_model_selector(aws_region: str = "us-east-1") -> MathModelSelector:
    """Get or create global mathematical reasoning model selector"""
    global _math_model_selector
    
    if _math_model_selector is None:
        _math_model_selector = MathModelSelector(aws_region)
        await _math_model_selector.get_best_math_model()
    
    return _math_model_selector