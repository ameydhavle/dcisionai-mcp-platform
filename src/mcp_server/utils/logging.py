"""
MCP Server Logging Configuration
===============================

Structured logging setup for the DcisionAI MCP server.
"""

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
import structlog
from structlog.stdlib import LoggerFactory

from ..config.settings import settings


def setup_logging() -> None:
    """Setup structured logging for the MCP server."""
    
    # Configure standard library logging first
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,  # Write logs to stderr to avoid interfering with MCP protocol
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class MCPLogger:
    """MCP-specific logger with tenant context."""
    
    def __init__(self, name: str, tenant_id: Optional[str] = None):
        self.logger = get_logger(name)
        self.tenant_id = tenant_id
    
    def _add_context(self, **kwargs) -> Dict[str, Any]:
        """Add context to log entries."""
        context = kwargs.copy()
        if self.tenant_id:
            context["tenant_id"] = self.tenant_id
        context["timestamp"] = datetime.utcnow().isoformat()
        return context
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self.logger.info(message, **self._add_context(**kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self.logger.warning(message, **self._add_context(**kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self.logger.error(message, **self._add_context(**kwargs))
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self.logger.debug(message, **self._add_context(**kwargs))
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception message with context."""
        self.logger.exception(message, **self._add_context(**kwargs))


# Initialize logging
setup_logging()

# Default logger
logger = get_logger("dcisionai.mcp.server")
