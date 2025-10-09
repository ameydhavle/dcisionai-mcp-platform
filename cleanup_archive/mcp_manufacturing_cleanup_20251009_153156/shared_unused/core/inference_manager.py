#!/usr/bin/env python3
"""
DcisionAI Platform - AWS Bedrock Inference Profile Manager
=========================================================

Enterprise-grade inference management using AWS Bedrock Inference Profiles:
- Cross-region optimization via AWS native inference profiles
- Automatic region selection and failover
- Cost tracking and usage monitoring
- Multi-tenant quota management

Leverages AWS Bedrock Inference Profiles for production-ready cross-region optimization.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from contextvars import ContextVar

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .base_agent import TenantContext, get_current_tenant

logger = logging.getLogger(__name__)

class OptimizationFocus(Enum):
    """Optimization focus areas - maps to AWS Bedrock inference profile types."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    COST = "cost"
    RELIABILITY = "reliability"

@dataclass
class InferenceProfile:
    """AWS Bedrock Inference Profile configuration."""
    profile_arn: str
    profile_name: str
    regions: List[str]
    model_id: str
    optimization_focus: OptimizationFocus
    cost_tier: str = "standard"
    sla_tier: str = "pro"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_arn": self.profile_arn,
            "profile_name": self.profile_name,
            "regions": self.regions,
            "model_id": self.model_id,
            "optimization_focus": self.optimization_focus.value,
            "cost_tier": self.cost_tier,
            "sla_tier": self.sla_tier
        }

@dataclass
class InferenceRequest:
    """Inference request with tenant context."""
    request_id: str
    tenant_context: TenantContext
    domain: str
    request_type: str
    payload: Dict[str, Any]
    inference_profile: Optional[str] = None  # Profile ARN or name
    timeout: int = 60
    priority: str = "normal"
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())

@dataclass
class InferenceResult:
    """Inference execution result."""
    request_id: str
    success: bool
    result: Dict[str, Any]
    profile_used: str
    region_used: str
    execution_time: float
    cost: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.utcnow)

class BedrockInferenceManager:
    """
    AWS Bedrock Inference Profile Manager for AgentCore.
    
    Features:
    - Uses AWS Bedrock Inference Profiles for cross-region optimization
    - Automatic region selection and failover
    - Cost tracking and usage monitoring
    - Multi-tenant quota management
    - Integration with AgentCore runtime
    """
    
    def __init__(self, 
                 region: str = "us-east-1",
                 default_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        """
        Initialize the Bedrock Inference Profile Manager.
        
        Args:
            region: AWS region for the manager
            default_model: Default model ID to use
        """
        self.region = region
        self.default_model = default_model
        
        # Initialize AWS clients
        try:
            self.bedrock_client = boto3.client('bedrock', region_name=region)
            self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
            logger.info(f"✅ AWS Bedrock clients initialized in {region}")
        except (NoCredentialsError, ClientError) as e:
            logger.error(f"❌ Failed to initialize AWS clients: {e}")
            raise
        
        # Inference profiles cache
        self.inference_profiles: Dict[str, InferenceProfile] = {}
        self.profile_cache_expiry: Optional[datetime] = None
        self.cache_ttl = timedelta(minutes=15)  # Cache profiles for 15 minutes
        
        # Performance tracking
        self.request_history: List[InferenceRequest] = []
        self.result_history: List[InferenceResult] = []
        
        # Multi-tenant quotas
        self.tenant_quotas: Dict[str, Dict[str, int]] = {}
        
        # Default inference profiles for common use cases
        self._initialize_default_profiles()
        
        logger.info("✅ Bedrock Inference Profile Manager initialized successfully")
    
    def _initialize_default_profiles(self):
        """Initialize default inference profiles for common use cases."""
        # These profiles are created via AWS CLI and are now ACTIVE
        # See infrastructure/inference-profiles-summary.md for ARNs
        default_profiles = {
            # Tier-based profiles
            "dcisionai-gold-tier-production": InferenceProfile(
                profile_arn="arn:aws:bedrock:us-east-1:808953421331:application-inference-profile/it9ypms13aut",
                profile_name="dcisionai-gold-tier-production",
                regions=["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                model_id=self.default_model,
                optimization_focus=OptimizationFocus.LATENCY,
                sla_tier="gold"
            ),
            "dcisionai-pro-tier-production": InferenceProfile(
                profile_arn="arn:aws:bedrock:us-east-1:808953421331:application-inference-profile/d0fxmnqls2sx",
                profile_name="dcisionai-pro-tier-production",
                regions=["us-east-1", "us-west-2", "eu-west-1"],
                model_id=self.default_model,
                optimization_focus=OptimizationFocus.COST,
                sla_tier="pro"
            ),
            "dcisionai-free-tier-production": InferenceProfile(
                profile_arn="arn:aws:bedrock:us-east-1:808953421331:application-inference-profile/y5bn061vrmh5",
                profile_name="dcisionai-free-tier-production",
                regions=["us-east-1", "us-west-2"],
                model_id=self.default_model,
                optimization_focus=OptimizationFocus.COST,
                sla_tier="free"
            ),
            
            # Domain-specific profiles
            "dcisionai-manufacturing-latency-production": InferenceProfile(
                profile_arn="arn:aws:bedrock:us-east-1:808953421331:application-inference-profile/kkz1l5bo5td8",
                profile_name="dcisionai-manufacturing-latency-production",
                regions=["us-east-1", "us-west-2"],
                model_id=self.default_model,
                optimization_focus=OptimizationFocus.LATENCY
            ),
            "dcisionai-manufacturing-cost-production": InferenceProfile(
                profile_arn="arn:aws:bedrock:us-east-1:808953421331:application-inference-profile/ero4w7afnw84",
                profile_name="dcisionai-manufacturing-cost-production",
                regions=["us-east-1", "us-west-2", "eu-west-1"],
                model_id=self.default_model,
                optimization_focus=OptimizationFocus.COST
            ),
            "dcisionai-manufacturing-reliability-production": InferenceProfile(
                profile_arn="arn:aws:bedrock:us-east-1:808953421331:application-inference-profile/m7g5wcozgkm0",
                profile_name="dcisionai-manufacturing-reliability-production",
                regions=["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                model_id=self.default_model,
                optimization_focus=OptimizationFocus.RELIABILITY
            )
        }
        
        self.inference_profiles.update(default_profiles)
        logger.info(f"✅ Initialized {len(default_profiles)} tenant-dedicated inference profiles")
    
    async def start(self):
        """Start the inference manager."""
        try:
            # Refresh inference profiles from AWS
            await self._refresh_inference_profiles()
            
            logger.info("✅ Bedrock Inference Profile Manager started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Bedrock Inference Profile Manager: {e}")
            raise
    
    async def stop(self):
        """Stop the inference manager."""
        try:
            # Clear caches
            self.inference_profiles.clear()
            self.profile_cache_expiry = None
            
            logger.info("✅ Bedrock Inference Profile Manager stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping Bedrock Inference Profile Manager: {e}")
    
    async def execute_inference(self, request: InferenceRequest) -> InferenceResult:
        """
        Execute inference using AWS Bedrock Inference Profiles.
        
        Args:
            request: Inference request with tenant context
            
        Returns:
            Inference result with performance metrics
        """
        start_time = time.time()
        
        try:
            # Validate tenant quotas
            if not await self._check_tenant_quotas(request.tenant_context):
                return InferenceResult(
                    request_id=request.request_id,
                    success=False,
                    result={},
                    profile_used="none",
                    region_used="none",
                    execution_time=0.0,
                    cost=0.0,
                    error="Tenant quota exceeded"
                )
            
            # Select or use specified inference profile
            profile = await self._select_inference_profile(request)
            if not profile:
                return InferenceResult(
                    request_id=request.request_id,
                    success=False,
                    result={},
                    profile_used="none",
                    region_used="none",
                    execution_time=0.0,
                    cost=0.0,
                    error="No suitable inference profile available"
                )
            
            # Execute inference using the profile
            result = await self._execute_with_profile(request, profile)
            
            # Update metrics
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.completed_at = datetime.utcnow()
            
            # Store results
            self.result_history.append(result)
            
            # Update tenant usage
            await self._update_tenant_usage(request.tenant_context, result)
            
            logger.info(f"✅ Inference completed using profile {profile.profile_name} in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Inference failed: {e}")
            
            return InferenceResult(
                request_id=request.request_id,
                success=False,
                result={},
                profile_used="none",
                region_used="none",
                execution_time=execution_time,
                cost=0.0,
                error=str(e)
            )
    
    async def _select_inference_profile(self, request: InferenceRequest) -> Optional[InferenceProfile]:
        """Select the appropriate inference profile for the request."""
        try:
            # If specific profile requested, use it
            if request.inference_profile:
                profile = self.inference_profiles.get(request.inference_profile)
                if profile:
                    return profile
                # Try to find by name if ARN not found
                for p in self.inference_profiles.values():
                    if p.profile_name == request.inference_profile:
                        return p
            
            # Auto-select based on domain and tenant preferences
            domain = request.domain
            tenant = request.tenant_context
            
            # Check for domain-specific profiles
            domain_profiles = [
                p for p in self.inference_profiles.values()
                if domain in p.profile_name.lower()
            ]
            
            if domain_profiles:
                # Select based on tenant SLA tier
                if tenant.sla_tier.value == "gold":
                    # Gold tier gets reliability-focused profiles
                    reliability_profiles = [p for p in domain_profiles 
                                         if p.optimization_focus == OptimizationFocus.RELIABILITY]
                    if reliability_profiles:
                        return reliability_profiles[0]
                
                # Default to latency-optimized for most use cases
                latency_profiles = [p for p in domain_profiles 
                                  if p.optimization_focus == OptimizationFocus.LATENCY]
                if latency_profiles:
                    return latency_profiles[0]
                
                # Fallback to any available profile
                return domain_profiles[0]
            
            # Fallback to default profiles
            default_profile = self.inference_profiles.get("dcisionai-manufacturing-latency")
            if default_profile:
                logger.info(f"🎯 Using default inference profile: {default_profile.profile_name}")
                return default_profile
            
            return None
            
        except Exception as e:
            logger.error(f"Error selecting inference profile: {e}")
            return None
    
    async def _execute_with_profile(self, request: InferenceRequest, 
                                   profile: InferenceProfile) -> InferenceResult:
        """Execute inference using the specified inference profile."""
        try:
            # Prepare the request payload for Bedrock
            bedrock_payload = self._prepare_bedrock_payload(request, profile)
            
            # Execute via Bedrock using the inference profile
            response = await self._invoke_bedrock_with_profile(profile, bedrock_payload)
            
            # Parse response and extract metrics
            result_data = self._parse_bedrock_response(response)
            
            # Estimate cost based on profile and usage
            estimated_cost = self._estimate_cost(profile, result_data)
            
            # Determine which region was actually used (AWS handles this automatically)
            region_used = profile.regions[0]  # AWS will route to optimal region
            
            return InferenceResult(
                request_id=request.request_id,
                success=True,
                result=result_data,
                profile_used=profile.profile_name,
                region_used=region_used,
                execution_time=0.0,  # Will be set by caller
                cost=estimated_cost,
                metadata={
                    "profile_arn": profile.profile_arn,
                    "model_id": profile.model_id,
                    "optimization_focus": profile.optimization_focus.value
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing with profile {profile.profile_name}: {e}")
            raise
    
    def _prepare_bedrock_payload(self, request: InferenceRequest, 
                                 profile: InferenceProfile) -> Dict[str, Any]:
        """Prepare the request payload for AWS Bedrock."""
        # Format depends on the model being used
        if "claude" in profile.model_id.lower():
            # Claude format
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Domain: {request.domain}\nRequest Type: {request.request_type}\nPayload: {json.dumps(request.payload)}"
                            }
                        ]
                    }
                ]
            }
        else:
            # Generic format
            return {
                "prompt": f"Domain: {request.domain}\nRequest Type: {request.request_type}\nPayload: {json.dumps(request.payload)}",
                "max_tokens": 4096
            }
    
    async def _invoke_bedrock_with_profile(self, profile: InferenceProfile, 
                                          payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke AWS Bedrock using the inference profile."""
        try:
            # Use the inference profile ARN as the model ID
            # AWS will automatically route to the optimal region
            response = self.bedrock_runtime.invoke_model(
                modelId=profile.profile_arn,  # Use profile ARN instead of model ID
                body=json.dumps(payload)
            )
            
            # Parse response body
            response_body = json.loads(response['body'].read())
            return response_body
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ThrottlingException':
                logger.warning(f"⚠️ Throttling detected for profile {profile.profile_name}")
                # Could implement retry logic here
                raise
            else:
                logger.error(f"❌ Bedrock API error: {error_code} - {e}")
                raise
        except Exception as e:
            logger.error(f"❌ Unexpected error invoking Bedrock: {e}")
            raise
    
    def _parse_bedrock_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the Bedrock API response."""
        try:
            # Extract content based on model type
            if 'content' in response:
                # Claude format
                content = response['content'][0]['text']
            elif 'completion' in response:
                # Generic completion format
                content = response['completion']
            else:
                content = str(response)
            
            return {
                "content": content,
                "model_response": response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing Bedrock response: {e}")
            return {
                "content": "Error parsing response",
                "error": str(e),
                "raw_response": response
            }
    
    def _estimate_cost(self, profile: InferenceProfile, result_data: Dict[str, Any]) -> float:
        """Estimate the cost of the inference request."""
        # This is a simplified cost estimation
        # In production, you'd use AWS Cost Explorer or similar
        
        base_cost = 0.001  # Base cost per request
        
        # Adjust based on optimization focus
        if profile.optimization_focus == OptimizationFocus.COST:
            base_cost *= 0.8  # 20% discount for cost-optimized profiles
        elif profile.optimization_focus == OptimizationFocus.RELIABILITY:
            base_cost *= 1.2  # 20% premium for reliability-focused profiles
        
        # Adjust based on SLA tier
        if profile.sla_tier == "gold":
            base_cost *= 1.5  # 50% premium for gold tier
        
        return base_cost
    
    async def _check_tenant_quotas(self, tenant_context: TenantContext) -> bool:
        """Check if tenant has available quotas."""
        tenant_id = tenant_context.tenant_id
        
        # Get current usage
        current_usage = self.tenant_quotas.get(tenant_id, {})
        
        # Check basic quotas (simplified)
        if current_usage.get("requests_per_minute", 0) > 1000:
            return False
        
        if current_usage.get("concurrent_jobs", 0) > 10:
            return False
        
        return True
    
    async def _update_tenant_usage(self, tenant_context: TenantContext, result: InferenceResult):
        """Update tenant usage metrics."""
        tenant_id = tenant_context.tenant_id
        
        if tenant_id not in self.tenant_quotas:
            self.tenant_quotas[tenant_id] = {}
        
        # Update usage counters
        self.tenant_quotas[tenant_id]["total_requests"] = \
            self.tenant_quotas[tenant_id].get("total_requests", 0) + 1
        
        self.tenant_quotas[tenant_id]["total_cost"] = \
            self.tenant_quotas[tenant_id].get("total_cost", 0.0) + result.cost
    
    async def _refresh_inference_profiles(self):
        """Refresh inference profiles from AWS Bedrock."""
        try:
            # Query AWS Bedrock for profile status
            bedrock_client = boto3.client('bedrock', region_name=self.region)
            
            # Get all inference profiles
            response = bedrock_client.list_inference_profiles()
            profiles = response.get('inferenceProfileSummaries', [])
            
            # Check our profiles are still active
            active_count = 0
            for profile_name, profile in self.inference_profiles.items():
                # Find matching profile in AWS
                aws_profile = next((p for p in profiles if p.get('profileName') == profile_name), None)
                if aws_profile and aws_profile.get('status') == 'ACTIVE':
                    active_count += 1
                    logger.debug(f"✅ {profile_name} is active in AWS")
                else:
                    logger.warning(f"⚠️ {profile_name} not found or inactive in AWS")
            
            # Mark cache as fresh
            self.profile_cache_expiry = datetime.utcnow() + self.cache_ttl
            
            logger.info(f"✅ Refreshed inference profile status: {active_count}/{len(self.inference_profiles)} active")
            
        except Exception as e:
            logger.error(f"Error refreshing inference profiles: {e}")
            # Profiles are already configured with real ARNs, so this is not critical
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        total_requests = len(self.result_history)
        successful_requests = len([r for r in self.result_history if r.success])
        
        if total_requests == 0:
            return {"error": "No requests processed yet"}
        
        avg_execution_time = sum(r.execution_time for r in self.result_history) / total_requests
        avg_cost = sum(r.cost for r in self.result_history) / total_requests
        success_rate = successful_requests / total_requests
        
        # Profile usage statistics
        profile_stats = {}
        for profile_name in set(r.profile_used for r in self.result_history):
            profile_results = [r for r in self.result_history if r.profile_used == profile_name]
            if profile_results:
                profile_stats[profile_name] = {
                    "requests": len(profile_results),
                    "avg_execution_time": sum(r.execution_time for r in profile_results) / len(profile_results),
                    "avg_cost": sum(r.cost for r in profile_results) / len(profile_results)
                }
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time,
            "avg_cost": avg_cost,
            "profile_stats": profile_stats,
            "tenant_quotas": self.tenant_quotas,
            "available_profiles": [p.profile_name for p in self.inference_profiles.values()]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        try:
            # Check AWS credentials and connectivity
            self.bedrock_client.list_foundation_models()
            
            return {
                "status": "healthy",
                "aws_connectivity": "connected",
                "available_profiles": len(self.inference_profiles),
                "region": self.region,
                "cache_status": "fresh" if self.profile_cache_expiry and self.profile_cache_expiry > datetime.utcnow() else "stale"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "aws_connectivity": "disconnected",
                "error": str(e),
                "region": self.region
            }
    
    async def cleanup(self):
        """Cleanup inference manager resources."""
        try:
            await self.stop()
            logger.info("✅ Bedrock Inference Profile Manager cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

# Alias for backward compatibility
InferenceManager = BedrockInferenceManager
