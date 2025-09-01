"""
MCP Server Metrics Collection
============================

Metrics collection and monitoring for the DcisionAI MCP server.
"""

import time
import boto3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import contextmanager

from ..config.settings import settings
from .logging import get_logger

logger = get_logger("dcisionai.mcp.metrics")


@dataclass
class MetricData:
    """Metric data structure."""
    namespace: str
    metric_name: str
    value: float
    unit: str
    dimensions: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MetricsCollector:
    """Metrics collector for MCP server."""
    
    def __init__(self):
        self.cloudwatch = None
        self.metrics_buffer: List[MetricData] = []
        self.buffer_size = 20
        self.last_flush = datetime.utcnow()
        self.flush_interval = timedelta(seconds=60)
        
        if settings.metrics_enabled:
            try:
                self.cloudwatch = boto3.client('cloudwatch', region_name=settings.aws_region)
                logger.info("CloudWatch metrics enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize CloudWatch: {e}")
    
    def add_metric(self, metric_name: str, value: float, unit: str = "Count", 
                   tenant_id: Optional[str] = None, tool_name: Optional[str] = None,
                   **dimensions) -> None:
        """Add a metric to the buffer."""
        if not settings.metrics_enabled:
            return
        
        dims = dimensions.copy()
        if tenant_id:
            dims["TenantId"] = tenant_id
        if tool_name:
            dims["ToolName"] = tool_name
        
        metric = MetricData(
            namespace=settings.cost_tracking_namespace,
            metric_name=metric_name,
            value=value,
            unit=unit,
            dimensions=dims
        )
        
        self.metrics_buffer.append(metric)
        
        # Flush if buffer is full or enough time has passed
        if (len(self.metrics_buffer) >= self.buffer_size or 
            datetime.utcnow() - self.last_flush >= self.flush_interval):
            self.flush_metrics()
    
    def flush_metrics(self) -> None:
        """Flush metrics to CloudWatch."""
        if not self.metrics_buffer or not self.cloudwatch:
            return
        
        try:
            # Group metrics by namespace
            metrics_by_namespace = {}
            for metric in self.metrics_buffer:
                if metric.namespace not in metrics_by_namespace:
                    metrics_by_namespace[metric.namespace] = []
                
                cloudwatch_metric = {
                    'MetricName': metric.metric_name,
                    'Value': metric.value,
                    'Unit': metric.unit,
                    'Timestamp': metric.timestamp,
                }
                
                if metric.dimensions:
                    cloudwatch_metric['Dimensions'] = [
                        {'Name': k, 'Value': v} for k, v in metric.dimensions.items()
                    ]
                
                metrics_by_namespace[metric.namespace].append(cloudwatch_metric)
            
            # Send metrics to CloudWatch
            for namespace, metrics in metrics_by_namespace.items():
                self.cloudwatch.put_metric_data(
                    Namespace=namespace,
                    MetricData=metrics
                )
            
            logger.debug(f"Flushed {len(self.metrics_buffer)} metrics to CloudWatch")
            self.metrics_buffer.clear()
            self.last_flush = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to flush metrics to CloudWatch: {e}")
    
    def record_request_start(self, tenant_id: str, tool_name: str) -> None:
        """Record the start of a request."""
        self.add_metric("RequestStart", 1, "Count", tenant_id, tool_name)
    
    def record_request_duration(self, tenant_id: str, tool_name: str, duration_ms: float) -> None:
        """Record request duration."""
        self.add_metric("RequestDuration", duration_ms, "Milliseconds", tenant_id, tool_name)
    
    def record_request_success(self, tenant_id: str, tool_name: str) -> None:
        """Record successful request."""
        self.add_metric("RequestSuccess", 1, "Count", tenant_id, tool_name)
    
    def record_request_failure(self, tenant_id: str, tool_name: str, error_type: str) -> None:
        """Record failed request."""
        self.add_metric("RequestFailure", 1, "Count", tenant_id, tool_name, ErrorType=error_type)
    
    def record_tool_cost(self, tenant_id: str, tool_name: str, cost: float) -> None:
        """Record tool cost."""
        self.add_metric("ToolCost", cost, "None", tenant_id, tool_name)
    
    def record_concurrent_requests(self, tenant_id: str, count: int) -> None:
        """Record concurrent request count."""
        self.add_metric("ConcurrentRequests", count, "Count", tenant_id)


@contextmanager
def track_request(metrics_collector: MetricsCollector, tenant_id: str, tool_name: str):
    """Context manager to track request metrics."""
    start_time = time.time()
    metrics_collector.record_request_start(tenant_id, tool_name)
    
    try:
        yield
        duration_ms = (time.time() - start_time) * 1000
        metrics_collector.record_request_duration(tenant_id, tool_name, duration_ms)
        metrics_collector.record_request_success(tenant_id, tool_name)
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        metrics_collector.record_request_duration(tenant_id, tool_name, duration_ms)
        metrics_collector.record_request_failure(tenant_id, tool_name, type(e).__name__)
        raise


# Global metrics collector instance
metrics_collector = MetricsCollector()
