#!/usr/bin/env python3
"""
DcisionAI Platform - Enhanced Inference Manager
===============================================

Phase 2: Cross-region inference optimization with AWS Bedrock.
Handles intelligent region selection, quota management, and performance monitoring.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import boto3
import yaml
from pathlib import Path

@dataclass
class InferenceRequest:
    """Represents an inference request with metadata."""
    request_id: str
    domain: str
    request_type: str
    payload: Dict[str, Any]
    user_location: Optional[str] = None
    priority: str = "normal"
    timeout: int = 300
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class InferenceResult:
    """Represents the result of an inference operation."""
    request_id: str
    success: bool
    data: Any
    region_used: str
    execution_time: float
    cost: float
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class RegionMetrics:
    """Metrics for a specific AWS region."""
    region: str
    current_load: float  # 0.0 to 1.0
    latency_ms: float
    quota_usage: float  # 0.0 to 1.0
    error_rate: float
    cost_per_token: float
    last_updated: datetime
    health_status: str  # "healthy", "degraded", "unhealthy"

class InferenceManager:
    """
    Enhanced inference manager for cross-region optimization.
    
    Features:
    - Intelligent region selection
    - Quota management and monitoring
    - Performance optimization
    - Cost tracking
    - Health monitoring
    """
    
    def __init__(self, config_path: str = "shared/config/inference_profiles.yaml"):
        """Initialize the inference manager with configuration."""
        self.logger = logging.getLogger("inference_manager")
        self.logger.setLevel(logging.INFO)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize AWS clients
        self.bedrock_client = boto3.client('bedrock', region_name='us-east-1')
        self.cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
        
        # Initialize state
        self.region_metrics: Dict[str, RegionMetrics] = {}
        self.request_history: List[InferenceRequest] = []
        self.performance_cache: Dict[str, Any] = {}
        
        # Background task management
        self._background_tasks: List[asyncio.Task] = []
        self._running = True
        
        # Start background tasks
        self._start_background_tasks()
        
        self.logger.info("✅ Enhanced Inference Manager initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load inference configuration from YAML file."""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                self.logger.info(f"✅ Loaded inference configuration from {config_path}")
                return config
            else:
                self.logger.warning(f"⚠️ Configuration file not found: {config_path}")
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file loading fails."""
        return {
            "inference_profiles": {
                "manufacturing": {
                    "regions": ["us-east-1", "us-west-2"],
                    "max_throughput": 1000
                },
                "finance": {
                    "regions": ["us-east-1", "us-west-2"],
                    "max_throughput": 500
                },
                "pharma": {
                    "regions": ["us-east-1", "eu-west-1"],
                    "max_throughput": 750
                }
            },
            "global_settings": {
                "default_timeout": 300,
                "max_retries": 3
            }
        }
    
    def _start_background_tasks(self):
        """Start background tasks for monitoring and optimization."""
        try:
            # Create background tasks
            self._background_tasks = [
                asyncio.create_task(self._update_region_metrics()),
                asyncio.create_task(self._cleanup_old_requests()),
                asyncio.create_task(self._update_performance_cache())
            ]
            self.logger.info("✅ Background tasks started successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to start background tasks: {e}")
            raise
    
    async def _update_region_metrics(self):
        """Update region metrics every minute."""
        while self._running:
            try:
                await self._refresh_region_metrics()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                self.logger.error(f"❌ Error updating region metrics: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _refresh_region_metrics(self):
        """Refresh metrics for all regions."""
        try:
            for domain, profile in self.config.get("inference_profiles", {}).items():
                for region in profile.get("regions", []):
                    metrics = await self._get_region_metrics(region, domain)
                    self.region_metrics[region] = metrics
        except Exception as e:
            self.logger.error(f"❌ Failed to refresh region metrics: {e}")
    
    async def _get_region_metrics(self, region: str, domain: str) -> RegionMetrics:
        """Get current metrics for a specific region."""
        try:
            # Get CloudWatch metrics for the region
            current_load = await self._get_region_load(region, domain)
            latency = await self._get_region_latency(region)
            quota_usage = await self._get_quota_usage(region, domain)
            error_rate = await self._get_error_rate(region, domain)
            cost_per_token = await self._get_cost_per_token(region, domain)
            
            # Determine health status
            health_status = self._determine_health_status(
                current_load, latency, quota_usage, error_rate
            )
            
            return RegionMetrics(
                region=region,
                current_load=current_load,
                latency_ms=latency,
                quota_usage=quota_usage,
                error_rate=error_rate,
                cost_per_token=cost_per_token,
                last_updated=datetime.now(),
                health_status=health_status
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get metrics for region {region}: {e}")
            # Return degraded metrics
            return RegionMetrics(
                region=region,
                current_load=0.5,
                latency_ms=5000,
                quota_usage=0.5,
                error_rate=0.1,
                cost_per_token=0.001,
                last_updated=datetime.now(),
                health_status="degraded"
            )
    
    async def _get_region_load(self, region: str, domain: str) -> float:
        """Get current load for a region (0.0 to 1.0)."""
        try:
            # Query CloudWatch for current request count vs capacity
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace="AWS/Bedrock",
                MetricName="RequestCount",
                Dimensions=[
                    {"Name": "Region", "Value": region},
                    {"Name": "Domain", "Value": domain}
                ],
                StartTime=datetime.now() - timedelta(minutes=5),
                EndTime=datetime.now(),
                Period=300,
                Statistics=["Sum"]
            )
            
            if response["Datapoints"]:
                current_requests = response["Datapoints"][0]["Sum"]
                max_capacity = self.config["inference_profiles"][domain]["max_throughput"]
                return min(current_requests / max_capacity, 1.0)
            
            return 0.5  # Default to 50% if no data
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not get load for region {region}: {e}")
            return 0.5
    
    async def _get_region_latency(self, region: str) -> float:
        """Get current latency for a region in milliseconds."""
        try:
            # Query CloudWatch for latency metrics
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace="AWS/Bedrock",
                MetricName="ResponseTime",
                Dimensions=[{"Name": "Region", "Value": region}],
                StartTime=datetime.now() - timedelta(minutes=5),
                EndTime=datetime.now(),
                Period=300,
                Statistics=["Average"]
            )
            
            if response["Datapoints"]:
                return response["Datapoints"][0]["Average"]
            
            return 1000.0  # Default to 1 second
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not get latency for region {region}: {e}")
            return 1000.0
    
    async def _get_quota_usage(self, region: str, domain: str) -> float:
        """Get current quota usage for a region (0.0 to 1.0)."""
        try:
            # Query CloudWatch for quota usage
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace="AWS/Bedrock",
                MetricName="QuotaUsage",
                Dimensions=[
                    {"Name": "Region", "Value": region},
                    {"Name": "Domain", "Value": domain}
                ],
                StartTime=datetime.now() - timedelta(minutes=5),
                EndTime=datetime.now(),
                Period=300,
                Statistics=["Maximum"]
            )
            
            if response["Datapoints"]:
                return response["Datapoints"][0]["Maximum"] / 100.0  # Convert percentage
            
            return 0.5  # Default to 50%
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not get quota usage for region {region}: {e}")
            return 0.5
    
    async def _get_error_rate(self, region: str, domain: str) -> float:
        """Get current error rate for a region (0.0 to 1.0)."""
        try:
            # Query CloudWatch for error rate
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace="AWS/Bedrock",
                MetricName="ErrorRate",
                Dimensions=[
                    {"Name": "Region", "Value": region},
                    {"Name": "Domain", "Value": domain}
                ],
                StartTime=datetime.now() - timedelta(minutes=5),
                EndTime=datetime.now(),
                Period=300,
                Statistics=["Average"]
            )
            
            if response["Datapoints"]:
                return response["Datapoints"][0]["Average"] / 100.0  # Convert percentage
            
            return 0.01  # Default to 1%
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not get error rate for region {region}: {e}")
            return 0.01
    
    async def _get_cost_per_token(self, region: str, domain: str) -> float:
        """Get current cost per token for a region."""
        # This would typically query AWS Cost Explorer or similar
        # For now, return estimated costs based on region
        cost_map = {
            "us-east-1": 0.0008,
            "us-west-2": 0.0008,
            "eu-west-1": 0.0009,
            "ap-southeast-1": 0.0010
        }
        return cost_map.get(region, 0.0010)
    
    def _determine_health_status(self, load: float, latency: float, 
                                quota: float, error_rate: float) -> str:
        """Determine health status based on metrics."""
        if error_rate > 0.1 or quota > 0.9 or latency > 10000:
            return "unhealthy"
        elif error_rate > 0.05 or quota > 0.8 or latency > 5000:
            return "degraded"
        else:
            return "healthy"
    
    def select_optimal_region(self, request: InferenceRequest) -> str:
        """
        Select the optimal region for an inference request.
        
        Selection criteria:
        1. Health status (healthy > degraded > unhealthy)
        2. Current load (lower is better)
        3. Latency (lower is better)
        4. Quota availability (lower usage is better)
        5. Cost optimization
        6. Geographic proximity (if user location provided)
        """
        domain = request.domain
        profile = self.config["inference_profiles"].get(domain, {})
        available_regions = profile.get("regions", ["us-east-1"])
        
        if not available_regions:
            self.logger.warning(f"⚠️ No regions available for domain {domain}")
            return "us-east-1"  # Fallback
        
        # Filter regions by health status - ensure proper access to region_metrics
        healthy_regions = []
        degraded_regions = []
        
        for region in available_regions:
            if region in self.region_metrics:
                metrics = self.region_metrics[region]
                if hasattr(metrics, 'health_status'):
                    if metrics.health_status == "healthy":
                        healthy_regions.append(region)
                    elif metrics.health_status == "degraded":
                        degraded_regions.append(region)
                else:
                    # If metrics don't have health_status, treat as degraded
                    degraded_regions.append(region)
            else:
                # If region not in metrics, treat as degraded
                degraded_regions.append(region)
        
        # Prioritize healthy regions
        candidate_regions = healthy_regions + degraded_regions
        
        if not candidate_regions:
            self.logger.warning(f"⚠️ No healthy regions available for domain {domain}")
            return available_regions[0]  # Use first available as fallback
        
        # Score each region
        region_scores = []
        for region in candidate_regions:
            metrics = self.region_metrics.get(region)
            if not metrics:
                continue
            
            # Ensure metrics has required attributes
            if not hasattr(metrics, 'current_load') or not hasattr(metrics, 'latency_ms'):
                continue
            
            # Calculate score (lower is better)
            score = (
                metrics.current_load * 0.3 +      # 30% weight
                (metrics.latency_ms / 10000) * 0.3 +  # 30% weight
                metrics.quota_usage * 0.2 +       # 20% weight
                metrics.cost_per_token * 1000 * 0.1 +  # 10% weight
                metrics.error_rate * 0.1          # 10% weight
            )
            
            # Geographic proximity bonus (if user location provided)
            if request.user_location:
                proximity_bonus = self._calculate_proximity_bonus(region, request.user_location)
                score -= proximity_bonus
            
            region_scores.append((region, score))
        
        # Sort by score and return best region
        if region_scores:
            region_scores.sort(key=lambda x: x[1])
            optimal_region = region_scores[0][0]
            
            self.logger.info(f"🎯 Selected region {optimal_region} for {domain} request "
                           f"(score: {region_scores[0][1]:.4f})")
            
            return optimal_region
        else:
            # Fallback if no valid regions found
            self.logger.warning(f"⚠️ No valid regions found for {domain}, using fallback")
            return available_regions[0]
    
    def _calculate_proximity_bonus(self, region: str, user_location: str) -> float:
        """Calculate proximity bonus for region selection."""
        # Simple proximity mapping - in production, use proper geolocation
        proximity_map = {
            "us-east-1": {"us": 0.1, "eu": 0.05, "ap": 0.0},
            "us-west-2": {"us": 0.1, "eu": 0.05, "ap": 0.05},
            "eu-west-1": {"us": 0.05, "eu": 0.1, "ap": 0.05},
            "ap-southeast-1": {"us": 0.0, "eu": 0.05, "ap": 0.1}
        }
        
        # Determine user continent (simplified)
        if user_location.lower() in ["us", "usa", "united states", "canada"]:
            continent = "us"
        elif user_location.lower() in ["eu", "europe", "uk", "germany", "france"]:
            continent = "eu"
        elif user_location.lower() in ["ap", "asia", "japan", "singapore", "australia"]:
            continent = "ap"
        else:
            continent = "us"  # Default
        
        return proximity_map.get(region, {}).get(continent, 0.0)
    
    async def execute_inference(self, request: InferenceRequest) -> InferenceResult:
        """
        Execute inference with optimal region selection and monitoring.
        """
        start_time = time.time()
        
        try:
            # Select optimal region
            optimal_region = self.select_optimal_region(request)
            
            # Execute inference in selected region
            result = await self._execute_in_region(request, optimal_region)
            
            # Calculate execution time and cost
            execution_time = time.time() - start_time
            cost = self._calculate_request_cost(request, optimal_region, execution_time)
            
            # Create result object
            inference_result = InferenceResult(
                request_id=request.request_id,
                success=result.get("success", False),
                data=result.get("data"),
                region_used=optimal_region,
                execution_time=execution_time,
                cost=cost,
                metadata={
                    "domain": request.domain,
                    "request_type": request.request_type,
                    "user_location": request.user_location,
                    "priority": request.priority
                }
            )
            
            # Log success
            self.logger.info(f"✅ Inference completed in {optimal_region} "
                           f"({execution_time:.2f}s, ${cost:.4f})")
            
            return inference_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Inference failed: {e}")
            
            return InferenceResult(
                request_id=request.request_id,
                success=False,
                data=None,
                region_used="unknown",
                execution_time=execution_time,
                cost=0.0,
                metadata={"error": str(e)}
            )
    
    async def _execute_in_region(self, request: InferenceRequest, region: str) -> Dict[str, Any]:
        """Execute inference in a specific region."""
        # This would integrate with the actual inference service
        # For now, simulate the execution
        
        # Simulate region-specific processing time
        region_latency = self.region_metrics.get(region, {}).latency_ms or 1000
        await asyncio.sleep(region_latency / 1000)  # Convert to seconds
        
        # Simulate successful inference
        return {
            "success": True,
            "data": f"Inference result for {request.domain} in {region}",
            "region": region
        }
    
    def _calculate_request_cost(self, request: InferenceRequest, region: str, 
                               execution_time: float) -> float:
        """Calculate the cost of a request."""
        base_cost = self.region_metrics.get(region, {}).cost_per_token or 0.001
        
        # Estimate token count based on request size
        payload_size = len(str(request.payload))
        estimated_tokens = payload_size // 4  # Rough estimate
        
        # Add execution time cost
        time_cost = execution_time * 0.0001  # $0.0001 per second
        
        return (base_cost * estimated_tokens) + time_cost
    
    async def _cleanup_old_requests(self):
        """Clean up old request history."""
        while self._running:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.request_history = [
                    req for req in self.request_history 
                    if req.created_at > cutoff_time
                ]
                await asyncio.sleep(3600)  # Clean up every hour
            except Exception as e:
                self.logger.error(f"❌ Error cleaning up requests: {e}")
                await asyncio.sleep(3600)
    
    async def _update_performance_cache(self):
        """Update performance cache with recent metrics."""
        while self._running:
            try:
                # Update cache with recent performance data
                self.performance_cache = {
                    "last_updated": datetime.now().isoformat(),
                    "total_requests": len(self.request_history),
                    "region_health": {
                        region: metrics.health_status 
                        for region, metrics in self.region_metrics.items()
                    },
                    "average_latency": self._calculate_average_latency(),
                    "total_cost": self._calculate_total_cost()
                }
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                self.logger.error(f"❌ Error updating performance cache: {e}")
                await asyncio.sleep(300)
    
    def _calculate_average_latency(self) -> float:
        """Calculate average latency across all regions."""
        latencies = [m.latency_ms for m in self.region_metrics.values() if m.latency_ms]
        return sum(latencies) / len(latencies) if latencies else 0.0
    
    def _calculate_total_cost(self) -> float:
        """Calculate total cost from recent requests."""
        # This would typically query a cost database
        # For now, return estimated cost
        return len(self.request_history) * 0.01  # $0.01 per request estimate
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of current performance metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "region_metrics": {
                region: {
                    "health": metrics.health_status,
                    "load": metrics.current_load,
                    "latency_ms": metrics.latency_ms,
                    "quota_usage": metrics.quota_usage,
                    "error_rate": metrics.error_rate
                }
                for region, metrics in self.region_metrics.items()
            },
            "performance_cache": self.performance_cache,
            "total_requests": len(self.request_history),
            "config": {
                "domains": list(self.config["inference_profiles"].keys()),
                "total_regions": sum(len(p["regions"]) for p in self.config["inference_profiles"].values())
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the inference manager."""
        try:
            # Check if all regions have recent metrics
            stale_threshold = datetime.now() - timedelta(minutes=10)
            stale_regions = [
                region for region, metrics in self.region_metrics.items()
                if metrics.last_updated < stale_threshold
            ]
            
            # Check overall health
            unhealthy_regions = [
                region for region, metrics in self.region_metrics.items()
                if metrics.health_status == "unhealthy"
            ]
            
            health_status = "healthy"
            if unhealthy_regions:
                health_status = "degraded"
            if stale_regions:
                health_status = "degraded"
            
            return {
                "status": health_status,
                "timestamp": datetime.now().isoformat(),
                "total_regions": len(self.region_metrics),
                "healthy_regions": len([r for r in self.region_metrics.values() if r.health_status == "healthy"]),
                "degraded_regions": len([r for r in self.region_metrics.values() if r.health_status == "degraded"]),
                "unhealthy_regions": len([r for r in self.region_metrics.values() if r.health_status == "unhealthy"]),
                "stale_regions": stale_regions,
                "unhealthy_regions_list": unhealthy_regions
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources and stop background tasks."""
        try:
            self.logger.info("🔄 Stopping background tasks...")
            self._running = False
            
            # Cancel all background tasks
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self.logger.info("✅ Inference Manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            if hasattr(self, '_running') and self._running:
                self.logger.warning("⚠️ Inference Manager destroyed without cleanup")
        except:
            pass
