#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Platform - Customer Showcase Runner
==============================================================

Simple script to run the customer showcase demonstration.
This script handles setup, execution, and provides a user-friendly interface.

Usage:
    python3 run_customer_showcase.py [--quick] [--verbose] [--scenarios N]

Options:
    --quick      Run only 2 scenarios for quick demonstration (default: all 4)
    --verbose    Enable verbose logging output
    --scenarios  Number of scenarios to run (1-4, default: 4)

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

def print_banner():
    """Print the customer showcase banner."""
    print("=" * 80)
    print("🚀 DcisionAI MANUFACTURING MCP PLATFORM - CUSTOMER SHOWCASE")
    print("=" * 80)
    print("🎯 Demonstrating 18-Agent Swarm Architecture")
    print("🌐 Real AWS Bedrock Integration (NO MOCK RESPONSES)")
    print("🏭 Complete Manufacturing Optimization Workflow")
    print("=" * 80)
    print()

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if we're in the right directory
    if not Path("test_customer_showcase_e2e.py").exists():
        print("❌ Customer showcase test file not found")
        print("   Please run this script from the platform root directory")
        return False
    print("✅ Customer showcase test file found")
    
    # Check AWS credentials
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            print("⚠️ AWS credentials not found")
            print("   Please configure AWS credentials using 'aws configure'")
            return False
        print("✅ AWS credentials configured")
    except ImportError:
        print("❌ boto3 not installed")
        print("   Please install: pip install boto3")
        return False
    
    # Check required directories
    required_dirs = [
        "domains/manufacturing/mcp_server",
        "tests"
    ]
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Required directory not found: {dir_path}")
            return False
    print("✅ Required directories found")
    
    print("✅ All prerequisites met!")
    return True

def run_showcase(quick_mode=False, verbose=False, num_scenarios=4):
    """Run the customer showcase."""
    print(f"\n🚀 Starting customer showcase...")
    print(f"📊 Mode: {'Quick (2 scenarios)' if quick_mode else f'Full ({num_scenarios} scenarios)'}")
    print(f"📝 Verbose: {'Enabled' if verbose else 'Disabled'}")
    print()
    
    # Prepare command
    cmd = [sys.executable, "test_customer_showcase_e2e.py"]
    
    # Add environment variables for configuration
    env = os.environ.copy()
    if quick_mode:
        env["SHOWCASE_QUICK_MODE"] = "true"
    if verbose:
        env["SHOWCASE_VERBOSE"] = "true"
    env["SHOWCASE_NUM_SCENARIOS"] = str(num_scenarios)
    
    # Run the showcase
    start_time = time.time()
    try:
        print("⏳ Running customer showcase (this may take 10-20 minutes)...")
        print("   You can press Ctrl+C to stop at any time")
        print()
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n🎉 Customer showcase completed successfully!")
            print(f"⏱️ Total execution time: {execution_time:.2f} seconds")
            return True
        else:
            print(f"\n❌ Customer showcase failed with exit code {result.returncode}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n👋 Customer showcase interrupted by user")
        print(f"⏱️ Execution time: {time.time() - start_time:.2f} seconds")
        return False
    except Exception as e:
        print(f"\n💥 Customer showcase failed: {e}")
        return False

def show_results():
    """Show the generated results."""
    print("\n📄 Generated Reports:")
    
    # Look for the most recent report file
    report_files = list(Path(".").glob("customer_showcase_report_*.json"))
    if report_files:
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        print(f"   📊 Detailed Report: {latest_report}")
        print(f"   📅 Generated: {datetime.fromtimestamp(latest_report.stat().st_mtime)}")
    else:
        print("   ⚠️ No report files found")
    
    # Look for any other generated files
    other_files = list(Path(".").glob("*customer*"))
    if other_files:
        print(f"   📁 Other files: {', '.join(f.name for f in other_files)}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run the DcisionAI Manufacturing MCP Platform Customer Showcase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_customer_showcase.py                    # Run full showcase (4 scenarios)
  python3 run_customer_showcase.py --quick           # Run quick showcase (2 scenarios)
  python3 run_customer_showcase.py --verbose         # Run with verbose output
  python3 run_customer_showcase.py --scenarios 2     # Run only 2 scenarios
        """
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick showcase with only 2 scenarios (default: all 4)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output"
    )
    
    parser.add_argument(
        "--scenarios",
        type=int,
        choices=range(1, 5),
        default=4,
        help="Number of scenarios to run (1-4, default: 4)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Confirm before running
    if args.quick:
        num_scenarios = 2
    else:
        num_scenarios = args.scenarios
    
    print(f"\n📋 Showcase Configuration:")
    print(f"   Scenarios: {num_scenarios}")
    print(f"   Verbose: {'Yes' if args.verbose else 'No'}")
    print(f"   Estimated time: {num_scenarios * 3}-{num_scenarios * 5} minutes")
    
    response = input("\n🚀 Ready to start the customer showcase? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("👋 Customer showcase cancelled")
        sys.exit(0)
    
    # Run the showcase
    success = run_showcase(
        quick_mode=args.quick,
        verbose=args.verbose,
        num_scenarios=num_scenarios
    )
    
    # Show results
    show_results()
    
    # Final message
    if success:
        print("\n🎉 Customer showcase completed successfully!")
        print("📊 Check the generated report files for detailed results")
        print("📞 Contact sales@dcisionai.com for next steps")
    else:
        print("\n⚠️ Customer showcase completed with issues")
        print("📞 Contact support@dcisionai.com for assistance")
    
    print("\n📚 For more information, see CUSTOMER_SHOWCASE_GUIDE.md")
    print("=" * 80)

if __name__ == "__main__":
    main()
