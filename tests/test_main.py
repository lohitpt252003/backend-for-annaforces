import pytest
import sys
import os
import importlib.util

# Add the parent directory of backend-for-annaforces to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend-for-annaforces')))

# Dynamically load the "all tests" files from subdirectories
def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Paths to the test_all.py files
api_test_all_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'api', 'test_all.py'))
services_test_all_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'services', 'test_all.py'))
utils_test_all_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils', 'test_all.py'))

# Load each test_all module
api_tests = load_module_from_path("api_tests", api_test_all_path)
services_tests = load_module_from_path("services_tests", services_test_all_path)
utils_tests = load_module_from_path("utils_tests", utils_test_all_path)

# You can add a simple test here to confirm this file is being run
def test_all_backend_tests_loaded():
    assert True

# You can also explicitly call functions from the imported modules if needed,
# but pytest will discover tests automatically if they follow naming conventions.
# For example:
# def test_run_all_api_tests():
#     # This would typically be handled by pytest discovery,
#     # but if you wanted to explicitly run them, you could.
#     pass
