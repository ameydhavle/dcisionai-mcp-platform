#!/usr/bin/env python3
"""
DcisionAI MCP Server Main Entry Point
=====================================

Main entry point for the DcisionAI MCP server.
"""

import sys
import asyncio
import signal
from typing import Optional
import json

# Add the project root to Python path
import os
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Handle imports based on how the script is run
try:
    from .config.settings import settings
    from .utils.logging import logger, setup_logging
    from .utils.metrics import metrics_collector
    from .tenants.manager import tenant_manager
    from .tools.base import tool_registry
    from .tools.intent_tool import IntentClassificationTool
    from .protocol.handler import protocol_handler
except ImportError:
    # Fallback for direct execution
    from src.mcp_server.config.settings import settings
    from src.mcp_server.utils.logging import logger, setup_logging
    from src.mcp_server.utils.metrics import metrics_collector
    from src.mcp_server.tenants.manager import tenant_manager
    from src.mcp_server.tools.base import tool_registry
    from src.mcp_server.tools.intent_tool import IntentClassificationTool
    from src.mcp_server.protocol.handler import protocol_handler


class MCPServer:
    """Main MCP server class."""
    
    def __init__(self):
        self.running = False
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Setup logging
        setup_logging()
        self.logger = logger
    
    async def initialize(self) -> None:
        """Initialize the MCP server."""
        try:
            self.logger.info("Initializing DcisionAI MCP Server")
            
            # Register tools
            await self._register_tools()
            
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.logger.info("MCP Server initialized successfully")
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize MCP server: {e}")
            raise
    
    async def _register_tools(self) -> None:
        """Register all available tools."""
        try:
            # Register intent classification tool
            intent_tool = IntentClassificationTool()
            tool_registry.register_tool(intent_tool)
            
            self.logger.info(f"Registered {len(tool_registry.get_tool_names())} tools")
            
        except Exception as e:
            self.logger.exception(f"Failed to register tools: {e}")
            raise
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup loop."""
        while self.running:
            try:
                # Clean up expired sessions
                expired_count = await tenant_manager.cleanup_expired_sessions()
                if expired_count > 0:
                    self.logger.info(f"Cleaned up {expired_count} expired sessions")
                
                # Flush metrics
                metrics_collector.flush_metrics()
                
                # Wait for next cleanup cycle
                await asyncio.sleep(60)  # Clean up every minute
                
            except Exception as e:
                self.logger.exception(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)
    
    async def handle_stdio(self) -> None:
        """Handle MCP protocol over stdio."""
        try:
            self.logger.info("Starting MCP server (stdio mode)")
            
            while self.running:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Process the message
                response = await protocol_handler.process_message(line)
                
                # Send response if any
                if response:
                    print(response, flush=True)
                    # Also flush stderr to ensure logs are written
                    sys.stderr.flush()
            
        except Exception as e:
            self.logger.exception(f"Stdio handling error: {e}")
        finally:
            self.logger.info("MCP server (stdio mode) stopped")
    
    async def handle_http(self) -> None:
        """Handle MCP protocol over HTTP."""
        try:
            from .http_server import start_http_server
            
            host = self.settings.server_host
            port = self.settings.server_port
            
            self.logger.info(f"Starting MCP server (HTTP mode) on {host}:{port}")
            await start_http_server(host, port)
            
        except Exception as e:
            self.logger.exception(f"HTTP handling error: {e}")
            raise
    
    async def start(self, mode: str = "stdio") -> None:
        """Start the MCP server."""
        try:
            self.running = True
            
            # Initialize server
            await self.initialize()
            
            # Start server based on mode
            if mode == "stdio":
                await self.handle_stdio()
            elif mode == "http":
                await self.handle_http()
            else:
                raise ValueError(f"Unknown mode: {mode}")
                
        except Exception as e:
            self.logger.exception(f"Server start error: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Shutdown the MCP server."""
        try:
            self.logger.info("Shutting down MCP server")
            self.running = False
            
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Final metrics flush
            metrics_collector.flush_metrics()
            
            self.logger.info("MCP server shutdown complete")
            
        except Exception as e:
            self.logger.exception(f"Shutdown error: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print(f"\nReceived signal {signum}, shutting down...", file=sys.stderr)
    sys.exit(0)


async def main():
    """Main entry point."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start server
    server = MCPServer()
    
    try:
        # Determine mode from command line arguments
        mode = "stdio"
        if len(sys.argv) > 1:
            mode = sys.argv[1]
        
        await server.start(mode)
        
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())
