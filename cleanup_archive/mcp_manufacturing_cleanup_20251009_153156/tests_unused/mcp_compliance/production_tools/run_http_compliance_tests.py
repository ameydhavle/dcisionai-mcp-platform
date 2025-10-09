#!/usr/bin/env python3
"""
HTTP MCP Compliance Test Runner
===============================

Simple test runner for HTTP-based MCP compliance testing.
Tests the DcisionAI FastMCP server on port 8000.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main test function."""
    print("🚀 HTTP MCP Compliance Testing - DcisionAI Platform")
    print("=" * 60)
    
    # Import our HTTP tester
    try:
        from http_mcp_compliance_tester import HTTPMCPComplianceTester
    except ImportError as e:
        print(f"❌ Failed to import HTTP tester: {e}")
        sys.exit(1)
    
    # Test configuration
    server_url = "http://localhost:8000/mcp"
    output_dir = Path("compliance_reports")
    
    print(f"📡 Server URL: {server_url}")
    print(f"📁 Output Directory: {output_dir}")
    print("=" * 60)
    
    try:
        # Initialize tester
        tester = HTTPMCPComplianceTester(
            server_url=server_url,
            timeout=30,
            max_retries=3
        )
        
        print("🧪 Running HTTP MCP Compliance Tests...")
        print()
        
        # Run tests
        results = await tester.run_compliance_tests()
        
        if results["success"]:
            print("\n" + "=" * 60)
            print("📊 TEST RESULTS SUMMARY")
            print("=" * 60)
            
            # Print individual test results
            for result in results["test_results"]:
                status_icon = "✅" if result.status == "PASS" else "❌"
                print(f"{status_icon} {result.test_name}: {result.status} (Score: {result.score:.1%})")
                if result.error_message:
                    print(f"   Error: {result.error_message}")
            
            print("\n" + "=" * 60)
            print("🏆 COMPLIANCE CERTIFICATION")
            print("=" * 60)
            
            overall_score = results["overall_score"]
            certification_status = results["certification_status"]
            
            print(f"📈 Overall Score: {overall_score:.1%}")
            print(f"🏆 Status: {certification_status}")
            print(f"📊 Tests Passed: {results['passed_tests']}/{results['total_tests']}")
            
            # Determine result
            if certification_status == "COMPLIANT":
                print("\n🎉 MCP COMPLIANCE: PASSED!")
                print("✅ DcisionAI Platform is fully MCP protocol compliant")
                exit_code = 0
            elif certification_status == "PARTIALLY_COMPLIANT":
                print("\n⚠️  MCP COMPLIANCE: PARTIAL")
                print("⚠️  DcisionAI Platform has some compliance issues")
                exit_code = 1
            else:
                print("\n❌ MCP COMPLIANCE: FAILED")
                print("❌ DcisionAI Platform is not MCP protocol compliant")
                exit_code = 1
            
            # Save detailed results
            output_dir.mkdir(exist_ok=True)
            results_file = output_dir / "http_compliance_results.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n📄 Detailed results saved to: {results_file}")
            
            # Exit with appropriate code
            sys.exit(exit_code)
            
        else:
            print(f"\n❌ Testing failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
