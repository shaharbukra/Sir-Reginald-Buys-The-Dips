#!/usr/bin/env python3
"""
Test runner for all trading system tests
"""

import os
import sys
import asyncio
import importlib.util
from pathlib import Path

# Add parent directory to Python path so tests can import modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def run_test_file(test_file_path):
    """Run a single test file"""
    try:
        # Import and run the test file
        spec = importlib.util.spec_from_file_location("test_module", test_file_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # If the module has a main function, run it
        if hasattr(test_module, 'main'):
            if asyncio.iscoroutinefunction(test_module.main):
                asyncio.run(test_module.main())
            else:
                test_module.main()
        elif hasattr(test_module, '__name__') and test_module.__name__ == '__main__':
            # Module runs on import
            pass
            
        return True
    except Exception as e:
        print(f"❌ Error running {test_file_path}: {e}")
        return False

def main():
    """Run all test files in the tests directory"""
    print("🧪 Running All Trading System Tests")
    print("=" * 50)
    
    # Get the tests directory
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found")
        return
    
    print(f"📁 Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"   • {test_file.name}")
    
    print("\n🚀 Starting test execution...")
    
    # Run each test file
    successful_tests = 0
    failed_tests = 0
    
    for test_file in test_files:
        print(f"\n🔍 Running {test_file.name}...")
        if run_test_file(test_file):
            print(f"✅ {test_file.name} completed successfully")
            successful_tests += 1
        else:
            print(f"❌ {test_file.name} failed")
            failed_tests += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   ✅ Successful: {successful_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📁 Total: {len(test_files)}")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed")

if __name__ == "__main__":
    main()
