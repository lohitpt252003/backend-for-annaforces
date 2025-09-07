import pytest
import sys
import os
import importlib.util

# Add the parent directory of backend-for-annaforces to sys.path
# This is needed for the dynamic loading of modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend-for-annaforces')))

# Dynamically load all individual test files from this directory
# This bypasses the Python package naming conventions for the backend-for-annaforces folder
def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Paths to individual test files
test_files = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_auth_api.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_problems_api.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_submissions_api.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_users_api.py')),
]

# Load each test module
for i, file_path in enumerate(test_files):
    load_module_from_path(f"test_api_module_{i}", file_path)

# You can add a simple test here to confirm this file is being run
def test_api_all_tests_loaded():
    assert True
