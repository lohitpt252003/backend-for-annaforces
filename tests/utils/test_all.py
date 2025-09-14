import unittest
import os
import sys

def run_unittest_tests():
    print("\n" + "="*50)
    print("Running unittest tests for utils folder...")
    print("="*50)
    # Discover and run tests in the current directory (tests/utils)
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir=os.path.dirname(__file__), pattern='test_*.py')
    
    # Create a TextTestRunner to run the tests and capture output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    all_tests_successful = True

    # Run unittest tests
    if not run_unittest_tests():
        all_tests_successful = False

    if all_tests_successful:
        print("\n" + "="*50)
        print("All utils tests passed successfully! 🎉")
        print("="*50)
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("Some utils tests failed. ❌")
        print("="*50)
        sys.exit(1)