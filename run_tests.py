"""Test runner script for the distributed processing system."""
import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run the complete test suite."""
    print("🧪 Running Distributed Processing System Test Suite")
    print("=" * 60)
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Test commands to run
    test_commands = [
        {
            'name': 'Unit Tests - Master Service',
            'cmd': ['python', '-m', 'pytest', 'tests/test_master.py', '-v', '--tb=short'],
            'marker': 'unit'
        },
        {
            'name': 'Unit Tests - Slave Service', 
            'cmd': ['python', '-m', 'pytest', 'tests/test_slave.py', '-v', '--tb=short'],
            'marker': 'unit'
        },
        {
            'name': 'Integration Tests',
            'cmd': ['python', '-m', 'pytest', 'tests/test_integration.py', '-v', '--tb=short'],
            'marker': 'integration'
        },
        {
            'name': 'Performance Tests (Slow)',
            'cmd': ['python', '-m', 'pytest', 'tests/test_performance.py', '-v', '--tb=short', '-m', 'slow'],
            'marker': 'slow'
        },
        {
            'name': 'All Tests with Coverage',
            'cmd': ['python', '-m', 'pytest', 'tests/', '--cov=master_service', '--cov=slave_service', '--cov-report=html', '--cov-report=term'],
            'marker': 'coverage'
        }
    ]
    
    results = {}
    
    for test_suite in test_commands:
        print(f"\n🔍 Running: {test_suite['name']}")
        print("-" * 40)
        
        try:
            result = subprocess.run(test_suite['cmd'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 minute timeout
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            results[test_suite['name']] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ {test_suite['name']} PASSED")
            else:
                print(f"❌ {test_suite['name']} FAILED")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_suite['name']} TIMEOUT")
            results[test_suite['name']] = {
                'success': False,
                'output': '',
                'errors': 'Test suite timed out'
            }
        except Exception as e:
            print(f"💥 {test_suite['name']} ERROR: {e}")
            results[test_suite['name']] = {
                'success': False,
                'output': '',
                'errors': str(e)
            }
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("🚨 Some tests failed!")
        return 1

def run_quick_tests():
    """Run only quick unit tests."""
    print("⚡ Running Quick Tests (Unit Tests Only)")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    cmd = ['python', '-m', 'pytest', 'tests/test_master.py', 'tests/test_slave.py', '-v', '--tb=short']
    
    try:
        result = subprocess.run(cmd, timeout=60)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("⏰ Quick tests timed out")
        return 1
    except Exception as e:
        print(f"💥 Error running quick tests: {e}")
        return 1

def check_dependencies():
    """Check if all test dependencies are installed."""
    print("🔍 Checking test dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-cov', 
        'flask',
        'requests',
        'PIL'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n🚨 Missing packages: {', '.join(missing)}")
        print("Install with: python -m pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies installed!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for distributed processing system')
    parser.add_argument('--quick', action='store_true', help='Run only quick unit tests')
    parser.add_argument('--check-deps', action='store_true', help='Check test dependencies')
    
    args = parser.parse_args()
    
    if args.check_deps:
        sys.exit(0 if check_dependencies() else 1)
    elif args.quick:
        sys.exit(run_quick_tests())
    else:
        if not check_dependencies():
            sys.exit(1)
        sys.exit(run_tests())