#!/usr/bin/env python3
"""
Real MCP Compliance Testing CLI
===============================

Simple command-line interface for running real MCP server compliance tests.

Usage:
    python run_real_tests.py [environment] [options]
    
Examples:
    python run_real_tests.py                    # Use default environment
    python run_real_tests.py local             # Use local environment
    python run_real_tests.py dev               # Use development environment
    python run_real_tests.py prod              # Use production environment
    python run_real_tests.py --help            # Show help
    python run_real_tests.py --config          # Show current configuration
    python run_real_tests.py --test-connection # Test connection only
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mcp_compliance.run_real_mcp_tests import RealMCPComplianceTester
from tests.mcp_compliance.config import MCPComplianceConfig, load_environment_config


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Real MCP Server Compliance Testing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_real_tests.py                    # Use default environment
  python run_real_tests.py local             # Use local environment
  python run_real_tests.py dev               # Use development environment
  python run_real_tests.py prod              # Use production environment
  python run_real_tests.py --test-connection # Test connection only
  python run_real_tests.py --config          # Show current configuration
        """
    )
    
    parser.add_argument(
        "environment",
        nargs="?",
        default="default",
        help="Environment to use (default, local, dev, prod)"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration and exit"
    )
    
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test server connection only (skip full compliance testing)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Custom output directory for reports and logs"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        help="Custom timeout in seconds"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        help="Custom maximum retry attempts"
    )
    
    return parser.parse_args()


async def test_connection_only(config: MCPComplianceConfig):
    """Test only server connectivity without full compliance testing."""
    print("🔗 Testing server connection only...")
    
    try:
        tester = RealMCPComplianceTester(config)
        
        # Test connectivity
        connectivity_result = await tester._test_server_connectivity()
        
        if connectivity_result["success"]:
            print("✅ Server connection successful!")
            print(f"   WebSocket: {connectivity_result['websocket_score']:.1%}")
            print(f"   HTTP: {connectivity_result['http_score']:.1%}")
            print(f"   Resilience: {connectivity_result['resilience_score']:.1%}")
            print(f"   Overall Score: {connectivity_result['score']:.1%}")
        else:
            print("❌ Server connection failed!")
            print(f"   Error: {connectivity_result.get('error', 'Unknown error')}")
            print(f"   Score: {connectivity_result['score']:.1%}")
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    return connectivity_result["success"]


async def main():
    """Main entry point."""
    args = parse_arguments()
    
    print("🚀 Real MCP Compliance Testing CLI")
    print("="*50)
    
    try:
        # Load environment configuration
        if args.environment != "default":
            print(f"🔧 Loading environment: {args.environment}")
            load_environment_config(args.environment)
        
        # Load configuration
        config = MCPComplianceConfig()
        
        # Override config with command line arguments
        if args.output_dir:
            config.output_dir = args.output_dir
        if args.timeout:
            config.timeout = args.timeout
        if args.max_retries:
            config.max_retries = args.max_retries
        
        # Validate configuration
        if not config.validate_config():
            print("❌ Configuration validation failed. Please check your environment variables.")
            print("\nRequired environment variables:")
            print("  DCISIONAI_MCP_SERVER_URL - MCP server URL")
            print("  DCISIONAI_AUTH_TOKEN - Authentication token")
            print("  DCISIONAI_OUTPUT_DIR - Output directory for reports")
            sys.exit(1)
        
        # Show configuration if requested
        if args.config:
            print("\n📋 Current Configuration:")
            config.print_config()
            return
        
        # Test connection only if requested
        if args.test_connection:
            success = await test_connection_only(config)
            sys.exit(0 if success else 1)
        
        # Run full compliance testing
        print(f"🎯 Running full compliance tests against: {config.server_url}")
        print(f"📁 Output directory: {config.output_dir}")
        print(f"⏱️  Timeout: {config.timeout}s")
        print(f"🔄 Max retries: {config.max_retries}")
        print()
        
        # Initialize tester
        tester = RealMCPComplianceTester(config)
        
        # Run comprehensive compliance test
        results = await tester.run_comprehensive_compliance_test()
        
        if results["status"] == "COMPLETED":
            # Print summary
            tester.print_summary(results)
            
            # Exit with appropriate code
            if results["overall_status"] == "PASSED":
                print("\n🎉 Real MCP Compliance Testing PASSED!")
                sys.exit(0)
            elif results["overall_status"] == "PARTIAL":
                print("\n⚠️ Real MCP Compliance Testing PARTIAL - Some issues found")
                sys.exit(1)
            else:
                print("\n❌ Real MCP Compliance Testing FAILED")
                sys.exit(1)
        else:
            print(f"\n❌ Real MCP Compliance Testing FAILED: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
