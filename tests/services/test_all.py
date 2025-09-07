import pytest
import sys
import os
import importlib.util

sys.path.insert(0, 'E:\\NEW')

# Add the parent directory of backend-for-annaforces to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Dynamically load all individual test files from this directory
def load_module_from_path(module_name, file_path):
    # Construct the module name using the full path from E:\NEW
    relative_path = os.path.relpath(file_path, 'E:\\NEW')
    # Replace \ with . and remove .py extension
    module_name_for_import = relative_path.replace(os.sep, '.').replace('.py', '')
    
    # Use importlib.import_module to handle the import
    module = importlib.import_module(module_name_for_import)
    sys.modules[module_name] = module # Keep the original module_name for consistency
    return module


# Paths to individual test files
test_files = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_cache_service.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_contest_service.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_email_service.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_firebase_service.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_github_services.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_judge_service.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_problem_service.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_submission_service.py')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_user_service.py')),
]

# Load each test module
for i, file_path in enumerate(test_files):
    load_module_from_path(f"test_services_module_{i}", file_path)

# You can add a simple test here to confirm this file is being run
def test_services_all_tests_loaded():
    assert True