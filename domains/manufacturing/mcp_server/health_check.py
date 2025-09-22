#!/usr/bin/env python3
"""
Production Health Check and Monitoring for DcisionAI Manufacturing MCP Server

This module provides comprehensive health checks and monitoring for the production deployment.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """Health status for a component."""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    timestamp: datetime
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class SystemMetrics:
    """System performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

class ProductionHealthChecker:
    """Production health checker for the MCP server."""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = SystemMetrics()
        self.health_history: List[HealthStatus] = []
        
        # Initialize AWS clients
        try:
            self.bedrock_client = boto3.client('bedrock', region_name='us-east-1')
            self.aws_available = True
        except NoCredentialsError:
            logger.warning("AWS credentials not available for health checks")
            self.aws_available = False
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self.start_time
    
    def get_memory_usage(self) -> float:
        """Get memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent()
        except ImportError:
            return 0.0
    
    async def check_aws_bedrock_health(self) -> HealthStatus:
        """Check AWS Bedrock service health."""
        start_time = time.time()
        
        try:
            if not self.aws_available:
                return HealthStatus(
                    component="aws_bedrock",
                    status="unhealthy",
                    message="AWS credentials not available",
                    timestamp=datetime.now(),
                    response_time_ms=None
                )
            
            # Test Bedrock service availability
            response = self.bedrock_client.list_foundation_models()
            
            response_time = (time.time() - start_time) * 1000
            
            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return HealthStatus(
                    component="aws_bedrock",
                    status="healthy",
                    message="AWS Bedrock service is available",
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    details={
                        "models_available": len(response.get('modelSummaries', [])),
                        "region": "us-east-1"
                    }
                )
            else:
                return HealthStatus(
                    component="aws_bedrock",
                    status="degraded",
                    message="AWS Bedrock service responded with non-200 status",
                    timestamp=datetime.now(),
                    response_time_ms=response_time
                )
                
        except ClientError as e:
            response_time = (time.time() - start_time) * 1000
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            return HealthStatus(
                component="aws_bedrock",
                status="unhealthy",
                message=f"AWS Bedrock error: {error_code}",
                timestamp=datetime.now(),
                response_time_ms=response_time,
                details={"error_code": error_code}
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                component="aws_bedrock",
                status="unhealthy",
                message=f"Unexpected error: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    async def check_inference_profiles_health(self) -> HealthStatus:
        """Check inference profiles health."""
        start_time = time.time()
        
        try:
            if not self.aws_available:
                return HealthStatus(
                    component="inference_profiles",
                    status="unhealthy",
                    message="AWS credentials not available",
                    timestamp=datetime.now(),
                    response_time_ms=None
                )
            
            # Test inference profile availability
            response = self.bedrock_client.get_inference_profile(
                inferenceProfileId="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return HealthStatus(
                    component="inference_profiles",
                    status="healthy",
                    message="Inference profiles are available",
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    details={
                        "profile_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                        "status": response.get('status', 'unknown')
                    }
                )
            else:
                return HealthStatus(
                    component="inference_profiles",
                    status="degraded",
                    message="Inference profiles responded with non-200 status",
                    timestamp=datetime.now(),
                    response_time_ms=response_time
                )
                
        except ClientError as e:
            response_time = (time.time() - start_time) * 1000
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            return HealthStatus(
                component="inference_profiles",
                status="unhealthy",
                message=f"Inference profiles error: {error_code}",
                timestamp=datetime.now(),
                response_time_ms=response_time,
                details={"error_code": error_code}
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                component="inference_profiles",
                status="unhealthy",
                message=f"Unexpected error: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    async def check_swarm_health(self) -> HealthStatus:
        """Check swarm architecture health."""
        start_time = time.time()
        
        try:
            # Import swarm components
            from manufacturing_intent_swarm import ManufacturingIntentSwarm
            from manufacturing_data_swarm import ManufacturingDataSwarm
            from manufacturing_model_swarm import ManufacturingModelSwarm
            from manufacturing_solver_swarm import ManufacturingSolverSwarm
            
            # Initialize swarms
            intent_swarm = ManufacturingIntentSwarm()
            data_swarm = ManufacturingDataSwarm()
            model_swarm = ManufacturingModelSwarm()
            solver_swarm = ManufacturingSolverSwarm()
            
            response_time = (time.time() - start_time) * 1000
            
            # Check if all swarms are initialized
            total_agents = (
                len(intent_swarm.agents) +
                len(data_swarm.agents) +
                len(model_swarm.agents) +
                len(solver_swarm.agents)
            )
            
            if total_agents == 18:  # Expected total agents
                return HealthStatus(
                    component="swarm_architecture",
                    status="healthy",
                    message="All swarms initialized successfully",
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    details={
                        "intent_agents": len(intent_swarm.agents),
                        "data_agents": len(data_swarm.agents),
                        "model_agents": len(model_swarm.agents),
                        "solver_agents": len(solver_swarm.agents),
                        "total_agents": total_agents
                    }
                )
            else:
                return HealthStatus(
                    component="swarm_architecture",
                    status="degraded",
                    message=f"Expected 18 agents, found {total_agents}",
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    details={
                        "intent_agents": len(intent_swarm.agents),
                        "data_agents": len(data_swarm.agents),
                        "model_agents": len(model_swarm.agents),
                        "solver_agents": len(solver_swarm.agents),
                        "total_agents": total_agents
                    }
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                component="swarm_architecture",
                status="unhealthy",
                message=f"Swarm initialization failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    async def check_system_resources(self) -> HealthStatus:
        """Check system resource usage."""
        start_time = time.time()
        
        try:
            memory_usage = self.get_memory_usage()
            cpu_usage = self.get_cpu_usage()
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine health status based on resource usage
            if memory_usage > 3000 or cpu_usage > 80:  # 3GB memory or 80% CPU
                status = "degraded"
                message = f"High resource usage: {memory_usage:.1f}MB memory, {cpu_usage:.1f}% CPU"
            elif memory_usage > 2000 or cpu_usage > 60:  # 2GB memory or 60% CPU
                status = "healthy"
                message = f"Moderate resource usage: {memory_usage:.1f}MB memory, {cpu_usage:.1f}% CPU"
            else:
                status = "healthy"
                message = f"Low resource usage: {memory_usage:.1f}MB memory, {cpu_usage:.1f}% CPU"
            
            return HealthStatus(
                component="system_resources",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=response_time,
                details={
                    "memory_usage_mb": memory_usage,
                    "cpu_usage_percent": cpu_usage,
                    "uptime_seconds": self.get_uptime()
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                component="system_resources",
                status="unhealthy",
                message=f"Resource check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check for all components."""
        logger.info("Running comprehensive health check...")
        
        # Run all health checks in parallel
        health_checks = [
            self.check_aws_bedrock_health(),
            self.check_inference_profiles_health(),
            self.check_swarm_health(),
            self.check_system_resources()
        ]
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Process results
        health_statuses = []
        overall_status = "healthy"
        
        for result in results:
            if isinstance(result, Exception):
                health_statuses.append(HealthStatus(
                    component="unknown",
                    status="unhealthy",
                    message=f"Health check failed: {str(result)}",
                    timestamp=datetime.now()
                ))
                overall_status = "unhealthy"
            else:
                health_statuses.append(result)
                if result.status == "unhealthy":
                    overall_status = "unhealthy"
                elif result.status == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"
        
        # Update metrics
        self.metrics.uptime_seconds = self.get_uptime()
        self.metrics.memory_usage_mb = self.get_memory_usage()
        self.metrics.cpu_usage_percent = self.get_cpu_usage()
        
        # Store health history
        self.health_history.extend(health_statuses)
        if len(self.health_history) > 100:  # Keep last 100 health checks
            self.health_history = self.health_history[-100:]
        
        # Prepare response
        response = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self.metrics.uptime_seconds,
            "components": [asdict(status) for status in health_statuses],
            "metrics": asdict(self.metrics),
            "version": "2.0.0",
            "environment": "production"
        }
        
        logger.info(f"Health check completed: {overall_status}")
        return response
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for monitoring dashboards."""
        if not self.health_history:
            return {"status": "unknown", "message": "No health checks performed yet"}
        
        # Get latest health status for each component
        latest_statuses = {}
        for status in reversed(self.health_history):
            if status.component not in latest_statuses:
                latest_statuses[status.component] = status
        
        # Determine overall status
        overall_status = "healthy"
        for status in latest_statuses.values():
            if status.status == "unhealthy":
                overall_status = "unhealthy"
                break
            elif status.status == "degraded" and overall_status == "healthy":
                overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {comp: asdict(status) for comp, status in latest_statuses.items()},
            "uptime_seconds": self.get_uptime(),
            "total_health_checks": len(self.health_history)
        }

# Global health checker instance
health_checker = ProductionHealthChecker()
