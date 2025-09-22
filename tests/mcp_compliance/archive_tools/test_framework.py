#!/usr/bin/env python3
"""
Test MCP Compliance Testing Framework
====================================

Simple test script to verify the MCP compliance testing framework
can run without errors and generate basic reports.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mcp_compliance.mcp_compliance_tester import MCPComplianceTester
from tests.mcp_compliance.mcp_compliance_validator import MCPComplianceValidator


async def test_framework_basic():
    """Test basic framework functionality."""
    print("🧪 Testing MCP Compliance Testing Framework")
    print("=" * 50)
    
    try:
        # Test 1: Initialize tester
        print("1. Initializing MCP Compliance Tester...")
        tester = MCPComplianceTester(
            server_url="ws://localhost:8080/mcp",
            auth_token="test-token",
            timeout=30,
            max_retries=3
        )
        print("✅ MCP Compliance Tester initialized successfully")
        
        # Test 2: Initialize validator
        print("2. Initializing MCP Compliance Validator...")
        validator = MCPComplianceValidator()
        print("✅ MCP Compliance Validator initialized successfully")
        
        # Test 3: Check compliance requirements
        print("3. Checking compliance requirements...")
        print(f"   Total categories: {len(validator.categories)}")
        print(f"   Total requirements: {validator.total_requirements}")
        
        for category in validator.categories:
            print(f"   - {category.name}: {len(category.requirements)} requirements (weight: {category.weight})")
        
        print("✅ Compliance requirements loaded successfully")
        
        # Test 4: Generate mock test results
        print("4. Generating mock test results...")
        mock_test_results = [
            {
                "test_name": "protocol_version",
                "status": "PASS",
                "score": 1.0,
                "execution_time": 0.1,
                "details": {"version": "2025-03-26"}
            },
            {
                "test_name": "connection_management",
                "status": "PASS",
                "score": 0.9,
                "execution_time": 0.2,
                "details": {"websocket": True, "http": True}
            },
            {
                "test_name": "tool_management",
                "status": "PASS",
                "score": 0.95,
                "execution_time": 0.3,
                "details": {"tools_count": 5}
            }
        ]
        print("✅ Mock test results generated successfully")
        
        # Test 5: Validate compliance
        print("5. Validating compliance...")
        validation_report = validator.validate_compliance(mock_test_results)
        print(f"   Overall score: {validation_report.overall_score:.2%}")
        print(f"   Certification status: {validation_report.certification_status}")
        print(f"   Total requirements: {validation_report.total_requirements}")
        print(f"   Passed requirements: {validation_report.passed_requirements}")
        print(f"   Failed requirements: {validation_report.failed_requirements}")
        print("✅ Compliance validation completed successfully")
        
        # Test 6: Export reports
        print("6. Testing report export...")
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Export JSON report
        json_path = validator.export_report(
            validation_report,
            format="json",
            output_path=str(output_dir / "test_report.json")
        )
        print(f"   JSON report: {json_path}")
        
        # Export YAML report
        yaml_path = validator.export_report(
            validation_report,
            format="yaml",
            output_path=str(output_dir / "test_report.yaml")
        )
        print(f"   YAML report: {yaml_path}")
        
        # Export HTML report
        html_path = validator.export_report(
            validation_report,
            format="html",
            output_path=str(output_dir / "test_report.html")
        )
        print(f"   HTML report: {html_path}")
        
        print("✅ Report export completed successfully")
        
        # Test 7: Print recommendations
        print("7. Generating recommendations...")
        if validation_report.recommendations:
            print("   Recommendations:")
            for i, rec in enumerate(validation_report.recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("   No recommendations generated")
        print("✅ Recommendations generated successfully")
        
        print("\n" + "=" * 50)
        print("🎉 All framework tests passed successfully!")
        print(f"📁 Test reports saved to: {output_dir}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Framework test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    print("🚀 Testing MCP Compliance Testing Framework")
    print("This script tests the basic functionality without requiring a real MCP server.")
    print()
    
    try:
        # Run the async test
        result = asyncio.run(test_framework_basic())
        
        if result:
            print("\n✅ Framework test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Framework test failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
