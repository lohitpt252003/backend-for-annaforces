import pytest
import sys
import os
import importlib.util

# Add the parent directory of backend-for-annaforces to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend-for-annaforces')))

# Dynamically load all individual test files from this directory
def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Paths to individual test files
test_files = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_helper.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_jwt_token.py')),
]

# Load each test module
for i, file_path in enumerate(test_files):
    load_module_from_path(f"test_utils_module_{i}", file_path)

# You can add a simple test here to confirm this file is being run
def test_utils_all_tests_loaded():
    assert True
