#!/usr/bin/env python3
"""
DcisionAI MCP Platform - Test Runner
====================================

Run all tests for the DcisionAI Manufacturing MCP Platform.

Usage:
    python tests/run_all_tests.py [--unit] [--integration] [--workflow] [--all]

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests_in_directory(directory: str, test_type: str):
    """Run all tests in a specific directory"""
    print(f"\n🧪 Running {test_type} tests in {directory}...")
    print("=" * 60)
    
    test_dir = Path(directory)
    if not test_dir.exists():
        print(f"❌ Test directory {directory} not found")
        return False
    
    test_files = list(test_dir.glob("test_*.py"))
    if not test_files:
        print(f"⚠️ No test files found in {directory}")
        return True
    
    success_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file.name}...")
        try:
            result = subprocess.run([sys.executable, str(test_file)], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {test_file.name} - PASSED")
                success_count += 1
            else:
                print(f"❌ {test_file.name} - FAILED")
                print(f"Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file.name} - TIMEOUT")
        except Exception as e:
            print(f"💥 {test_file.name} - ERROR: {e}")
    
    print(f"\n📊 {test_type} Test Results: {success_count}/{total_count} passed")
    return success_count == total_count

def main():
    parser = argparse.ArgumentParser(description="Run DcisionAI MCP Platform tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--workflow", action="store_true", help="Run workflow tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    print("🚀 DcisionAI MCP Platform - Test Runner")
    print("=" * 60)
    
    # If no specific test type is specified, run all
    if not any([args.unit, args.integration, args.workflow, args.all]):
        args.all = True
    
    all_passed = True
    
    if args.unit or args.all:
        all_passed &= run_tests_in_directory("tests/unit", "Unit")
    
    if args.integration or args.all:
        all_passed &= run_tests_in_directory("tests/integration", "Integration")
    
    if args.workflow or args.all:
        all_passed &= run_tests_in_directory("tests/workflow", "Workflow")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
