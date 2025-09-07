import pytest
from unittest.mock import MagicMock, patch, call
import json
import re
import sys
import os
import importlib.util

# Construct the absolute path to the problem_service.py file
problem_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'problem_service.py'))

# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("problem_service_module", problem_service_path)
problem_service_module = importlib.util.module_from_spec(spec)
sys.modules["problem_service_module"] = problem_service_module
spec.loader.exec_module(problem_service_module)

# Fixture to mock github_services functions
@pytest.fixture
def mock_github_services():
    with patch('problem_service_module.get_file') as mock_get_file, \
         patch('problem_service_module.create_or_update_file') as mock_create_or_update_file, \
         patch('problem_service_module.add_file') as mock_add_file: # Add add_file mock
        yield mock_get_file, mock_create_or_update_file, mock_add_file

def test_problem_service_module_exists():
    assert True

# Test _validate_problem_md
@patch('re.search')
def test_validate_problem_md_success(mock_re_search):
    mock_re_search.return_value = True # Simulate all sections found
    description = "Problem 1: Title\n## Description\n## Input\n## Output\n## Constraints\n## Example1\n### Input\n### Output\n## Explanation"
    error = problem_service_module._validate_problem_md(description)
    assert error is None
    assert mock_re_search.call_count == 9 # Called for each required section

@patch('re.search')
def test_validate_problem_md_missing_section(mock_re_search):
    mock_re_search.side_effect = [True, True, False, True, True, True, True, True, True] # Simulate missing 'Input'
    description = "Problem 1: Title\n## Description\n## Output\n## Constraints\n## Example1\n### Input\n### Output\n## Explanation"
    error = problem_service_module._validate_problem_md(description)
    assert "Missing required section in problem.md: ## Input" in error

# Test _validate_problem_data
def test_validate_problem_data_success():
    problem_data = {
        "title": "Test Problem",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "Easy",
        "tags": ["Array"],
        "authors": ["Test Author"],
        "description": "Problem 1: Title\n## Description\n## Input\n## Output\n## Constraints\n## Example1\n### Input\n### Output\n## Explanation",
        "testcases": [{"input": "1", "output": "2"}]
    }
    with patch('problem_service_module._validate_problem_md', return_value=None):
        error = problem_service_module._validate_problem_data(problem_data)
        assert error is None

def test_validate_problem_data_missing_field():
    problem_data = {
        "title": "Test Problem",
        # "time_limit": 1000, # Missing
        "memory_limit": 256,
        "difficulty": "Easy",
        "tags": ["Array"],
        "authors": ["Test Author"],
        "description": "...",
        "testcases": [{"input": "1", "output": "2"}]
    }
    error = problem_service_module._validate_problem_data(problem_data)
    assert "Missing required field: time_limit" in error

def test_validate_problem_data_empty_testcases():
    problem_data = {
        "title": "Test Problem",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "Easy",
        "tags": ["Array"],
        "authors": ["Test Author"],
        "description": "...",
        "testcases": [] # Empty
    }
    error = problem_service_module._validate_problem_data(problem_data)
    assert "Testcases must be a non-empty list." in error

# Test add_problem
def test_add_problem_success(mock_github_services):
    mock_get_file, mock_create_or_update_file, _ = mock_github_services
    
    # Mock _validate_problem_data to pass
    with patch('problem_service_module._validate_problem_data', return_value=None):
        # Mock get_file for index.json
        mock_get_file.return_value = ('{}', 'sha123', None) # Empty index.json initially

        # Mock create_or_update_file for all file operations
        mock_create_or_update_file.return_value = {} # Simulate success

        problem_data = {
            "title": "New Problem",
            "time_limit": 1000,
            "memory_limit": 256,
            "difficulty": "Medium",
            "tags": ["DP"],
            "authors": ["New Author"],
            "description": "Problem 1: Title\n## Description\n## Input\n## Output\n## Constraints\n## Example1\n### Input\n### Output\n## Explanation",
            "testcases": [{"input": "in1", "output": "out1"}]
        }

        result = problem_service_module.add_problem(problem_data)

        assert "message" in result
        assert "Problem added successfully" in result["message"]
        assert "problem_id" in result
        assert result["problem_id"] == "P1" # Assuming it's the first problem

        # Verify calls to github_services
        assert mock_get_file.call_count == 2 # Once for index.json, once for get_file in create_or_update_file
        assert mock_create_or_update_file.call_count == 5 # meta.json, problem.md, 1.in, 1.out, .gitkeep, index.json

def test_add_problem_validation_failure(mock_github_services):
    mock_get_file, mock_create_or_update_file, _ = mock_github_services
    
    # Mock _validate_problem_data to fail
    with patch('problem_service_module._validate_problem_data', return_value="Validation Error"):
        problem_data = {} # Invalid data
        result = problem_service_module.add_problem(problem_data)
        assert "error" in result
        assert "Validation Error" in result["error"]
        mock_get_file.assert_not_called() # Should not proceed to GitHub operations

def test_add_problem_get_index_failure(mock_github_services):
    mock_get_file, mock_create_or_update_file, _ = mock_github_services
    
    with patch('problem_service_module._validate_problem_data', return_value=None):
        mock_get_file.return_value = (None, None, {"error": True, "message": "Failed to fetch index"}) # Simulate get_file error
        problem_data = {
            "title": "New Problem", "time_limit": 1000, "memory_limit": 256, "difficulty": "Medium",
            "tags": ["DP"], "authors": ["New Author"], "description": "...", "testcases": [{"input": "in1", "output": "out1"}]
        }
        result = problem_service_module.add_problem(problem_data)
        assert "error" in result
        assert "Failed to get problems index" in result["error"]
        mock_create_or_update_file.assert_not_called() # Should not proceed to create files
