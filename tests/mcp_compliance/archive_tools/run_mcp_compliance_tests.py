#!/usr/bin/env python3
"""
MCP Compliance Test Runner
==========================

Main test runner for MCP protocol compliance testing.
Orchestrates the complete testing and validation process.

This script:
1. Runs comprehensive MCP compliance tests
2. Validates compliance requirements
3. Generates detailed compliance reports
4. Exports reports in multiple formats
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mcp_compliance.mcp_compliance_tester import MCPComplianceTester
from tests.mcp_compliance.mcp_compliance_validator import MCPComplianceValidator

logger = logging.getLogger(__name__)


class MCPComplianceTestRunner:
    """
    Main test runner for MCP protocol compliance testing.
    
    Orchestrates the complete testing and validation process,
    ensuring DcisionAI Platform meets all MCP protocol requirements.
    """
    
    def __init__(
        self,
        server_url: str,
        auth_token: Optional[str] = None,
        output_dir: str = "compliance_reports",
        export_formats: Optional[list] = None
    ):
        """
        Initialize MCP compliance test runner.
        
        Args:
            server_url: MCP server URL to test
            auth_token: Authentication token for the server
            output_dir: Directory for output reports
            export_formats: List of export formats (json, yaml, html)
        """
        self.server_url = server_url
        self.auth_token = auth_token
        self.output_dir = Path(output_dir)
        self.export_formats = export_formats or ["json", "yaml", "html"]
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.tester = MCPComplianceTester(
            server_url=server_url,
            auth_token=auth_token,
            timeout=30,
            max_retries=3
        )
        
        self.validator = MCPComplianceValidator()
        
        logger.info(f"🚀 MCP Compliance Test Runner initialized")
        logger.info(f"📡 Server URL: {server_url}")
        logger.info(f"📁 Output Directory: {self.output_dir}")
        logger.info(f"📤 Export Formats: {', '.join(self.export_formats)}")
    
    def _setup_logging(self) -> None:
        """Setup comprehensive logging for the test runner."""
        # Create logs directory
        logs_dir = self.output_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Setup file logging
        log_file = logs_dir / f"mcp_compliance_test_{int(time.time())}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger.info(f"📝 Logging to: {log_file}")
    
    async def run_complete_compliance_test(self) -> Dict[str, Any]:
        """
        Run complete MCP compliance testing and validation.
        
        Returns:
            Dictionary containing test results and validation report
        """
        logger.info("🚀 Starting Complete MCP Compliance Testing")
        
        start_time = time.time()
        
        try:
            # Step 1: Run MCP compliance tests
            logger.info("🔍 Step 1: Running MCP Compliance Tests")
            test_report = await self.tester.run_full_compliance_test()
            
            # Step 2: Validate compliance requirements
            logger.info("🔍 Step 2: Validating Compliance Requirements")
            validation_report = self.validator.validate_compliance(
                [asdict(result) for result in test_report.test_results]
            )
            
            # Step 3: Export reports
            logger.info("🔍 Step 3: Exporting Compliance Reports")
            export_results = await self._export_reports(validation_report)
            
            # Step 4: Generate summary
            logger.info("🔍 Step 4: Generating Test Summary")
            summary = self._generate_summary(test_report, validation_report, export_results)
            
            # Calculate total execution time
            total_time = time.time() - start_time
            
            logger.info(f"✅ Complete MCP Compliance Testing completed in {total_time:.2f}s")
            logger.info(f"📊 Final Compliance Score: {validation_report.overall_score:.2%}")
            logger.info(f"🏆 Certification Status: {validation_report.certification_status}")
            
            return {
                "test_report": test_report,
                "validation_report": validation_report,
                "export_results": export_results,
                "summary": summary,
                "execution_time": total_time,
                "status": "COMPLETED"
            }
            
        except Exception as e:
            logger.error(f"❌ MCP Compliance Testing failed: {e}")
            return {
                "error": str(e),
                "execution_time": time.time() - start_time,
                "status": "FAILED"
            }
    
    async def _export_reports(self, validation_report) -> Dict[str, str]:
        """Export compliance reports in multiple formats."""
        logger.info("📤 Exporting compliance reports")
        
        export_results = {}
        timestamp = int(time.time())
        
        for format_type in self.export_formats:
            try:
                filename = f"mcp_compliance_report_{timestamp}.{format_type}"
                output_path = self.output_dir / filename
                
                exported_path = self.validator.export_report(
                    validation_report,
                    format=format_type,
                    output_path=str(output_path)
                )
                
                export_results[format_type] = exported_path
                logger.info(f"✅ Exported {format_type.upper()} report: {exported_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to export {format_type.upper()} report: {e}")
                export_results[format_type] = f"ERROR: {str(e)}"
        
        return export_results
    
    def _generate_summary(self, test_report, validation_report, export_results) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        summary = {
            "test_summary": {
                "total_tests": test_report.total_tests,
                "passed_tests": test_report.passed_tests,
                "failed_tests": test_report.failed_tests,
                "skipped_tests": test_report.skipped_tests,
                "test_success_rate": (test_report.passed_tests / test_report.total_tests * 100) if test_report.total_tests > 0 else 0
            },
            "compliance_summary": {
                "overall_score": validation_report.overall_score,
                "compliance_percentage": validation_report.compliance_percentage,
                "certification_status": validation_report.certification_status,
                "total_requirements": validation_report.total_requirements,
                "passed_requirements": validation_report.passed_requirements,
                "failed_requirements": validation_report.failed_requirements,
                "category_scores": {
                    cat.name: cat.category_score for cat in validation_report.categories
                }
            },
            "export_summary": {
                "formats_exported": list(export_results.keys()),
                "export_paths": export_results,
                "output_directory": str(self.output_dir)
            },
            "recommendations": validation_report.recommendations,
            "next_review_date": validation_report.next_review_date.isoformat() if validation_report.next_review_date else None
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]) -> None:
        """Print formatted test summary to console."""
        print("\n" + "="*80)
        print("🏆 MCP COMPLIANCE TESTING SUMMARY")
        print("="*80)
        
        # Test Summary
        test_summary = summary["test_summary"]
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total Tests: {test_summary['total_tests']}")
        print(f"   Passed: {test_summary['passed_tests']} ✅")
        print(f"   Failed: {test_summary['failed_tests']} ❌")
        print(f"   Skipped: {test_summary['skipped_tests']} ⚠️")
        print(f"   Success Rate: {test_summary['test_success_rate']:.1f}%")
        
        # Compliance Summary
        compliance_summary = summary["compliance_summary"]
        print(f"\n🔒 COMPLIANCE SUMMARY:")
        print(f"   Overall Score: {compliance_summary['overall_score']:.1%}")
        print(f"   Compliance: {compliance_summary['compliance_percentage']:.1f}%")
        print(f"   Status: {compliance_summary['certification_status']}")
        print(f"   Requirements: {compliance_summary['passed_requirements']}/{compliance_summary['total_requirements']} passed")
        
        # Category Scores
        print(f"\n📋 CATEGORY SCORES:")
        for category, score in compliance_summary['category_scores'].items():
            status_icon = "✅" if score >= 0.8 else "❌" if score < 0.6 else "⚠️"
            print(f"   {category}: {score:.1%} {status_icon}")
        
        # Export Summary
        export_summary = summary["export_summary"]
        print(f"\n📤 EXPORT SUMMARY:")
        print(f"   Output Directory: {export_summary['output_directory']}")
        print(f"   Formats Exported: {', '.join(export_summary['formats_exported'])}")
        
        # Recommendations
        if summary["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(summary["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        # Next Review
        if summary["next_review_date"]:
            print(f"\n📅 Next Review Date: {summary['next_review_date']}")
        
        print("\n" + "="*80)


async def main():
    """Main entry point for MCP compliance testing."""
    # Configuration
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    auth_token = os.getenv("MCP_AUTH_TOKEN")
    output_dir = os.getenv("COMPLIANCE_OUTPUT_DIR", "compliance_reports")
    export_formats = os.getenv("EXPORT_FORMATS", "json,yaml,html").split(",")
    
    print("🚀 DcisionAI Platform - MCP Protocol Compliance Testing")
    print("="*60)
    print(f"Server URL: {server_url}")
    print(f"Output Directory: {output_dir}")
    print(f"Export Formats: {', '.join(export_formats)}")
    print("="*60)
    
    try:
        # Initialize test runner
        runner = MCPComplianceTestRunner(
            server_url=server_url,
            auth_token=auth_token,
            output_dir=output_dir,
            export_formats=export_formats
        )
        
        # Run complete compliance test
        results = await runner.run_complete_compliance_test()
        
        if results["status"] == "COMPLETED":
            # Print summary
            runner.print_summary(results["summary"])
            
            # Save summary to file
            summary_file = Path(output_dir) / "test_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(results["summary"], f, indent=2, default=str)
            
            print(f"\n📄 Detailed summary saved to: {summary_file}")
            
            # Exit with appropriate code
            if results["validation_report"].certification_status == "COMPLIANT":
                print("\n🎉 MCP Compliance Testing PASSED - Server is COMPLIANT!")
                sys.exit(0)
            else:
                print(f"\n⚠️ MCP Compliance Testing completed with status: {results['validation_report'].certification_status}")
                sys.exit(1)
        else:
            print(f"\n❌ MCP Compliance Testing FAILED: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
