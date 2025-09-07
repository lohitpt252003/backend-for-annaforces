import pytest
from unittest.mock import MagicMock, patch, call
import json
import time
import sys
import os
import importlib.util

# Construct the absolute path to the submission_service.py file
submission_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'submission_service.py'))

# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("submission_service_module", submission_service_path)
submission_service_module = importlib.util.module_from_spec(spec)
sys.modules["submission_service_module"] = submission_service_module
spec.loader.exec_module(submission_service_module)

# Fixture to mock judge_service.grade_submission
@pytest.fixture
def mock_grade_submission():
    with patch('submission_service_module.grade_submission') as mock_gs:
        yield mock_gs

# Fixture to mock github_services functions
@pytest.fixture
def mock_github_services():
    with patch('submission_service_module.get_file') as mock_get_file, \
         patch('submission_service_module.add_file') as mock_add_file, \
         patch('submission_service_module.update_file') as mock_update_file, \
         patch('submission_service_module.create_or_update_file') as mock_create_or_update_file:
        yield mock_get_file, mock_add_file, mock_update_file, mock_create_or_update_file

def test_submission_service_module_exists():
    assert True

def test_handle_new_submission_success(mock_grade_submission, mock_github_services):
    mock_get_file, mock_add_file, mock_update_file, mock_create_or_update_file = mock_github_services

    problem_id = "P1"
    user_id = "U1"
    language = "python"
    code = "print('hello')"

    # Mock grade_submission to return a successful result
    mock_grade_submission.return_value = {
        "overall_status": "accepted",
        "test_results": [{"test_case_number": 1, "status": "passed"}]
    }

    # Mock get_file for global_submissions_meta.json
    mock_get_file.return_value = ('{"number_of_submissions": 0}', 'sha_meta', None)

    # Mock create_or_update_file and add_file to simulate success
    mock_create_or_update_file.return_value = {}
    mock_add_file.return_value = {}

    # Mock time.strftime
    with patch('time.strftime', return_value="2023-10-27T10:00:00Z"):
        result = submission_service_module.handle_new_submission(problem_id, user_id, language, code)

        mock_grade_submission.assert_called_once_with(code, language, problem_id)
        mock_get_file.assert_called_once_with(f"{submission_service_module.GITHUB_SUBMISSIONS_BASE_PATH}/meta.json")
        
        # Verify calls to create_or_update_file and add_file
        assert mock_create_or_update_file.call_count == 3 # submission_meta, code_file, global_submissions_meta
        assert mock_add_file.call_count == 2 # problem_submission, user_submission

        assert result["message"] == "Submission successful"
        assert result["submission_id"] == "S1"
        assert result["status"] == "accepted"

def test_handle_new_submission_judge_server_error(mock_grade_submission, mock_github_services):
    mock_get_file, mock_add_file, mock_update_file, mock_create_or_update_file = mock_github_services

    problem_id = "P1"
    user_id = "U1"
    language = "python"
    code = "print('hello')"

    # Mock grade_submission to return a judge server error
    mock_grade_submission.return_value = {
        "overall_status": "error",
        "message": "Code execution server is not running. Please contact the admin."
    }

    result = submission_service_module.handle_new_submission(problem_id, user_id, language, code)

    mock_grade_submission.assert_called_once_with(code, language, problem_id)
    mock_get_file.assert_not_called() # Should not proceed to file operations
    assert "error" in result
    assert "Code execution service is not available" in result["error"]

def test_handle_new_submission_get_global_meta_error(mock_grade_submission, mock_github_services):
    mock_get_file, mock_add_file, mock_update_file, mock_create_or_update_file = mock_github_services

    problem_id = "P1"
    user_id = "U1"
    language = "python"
    code = "print('hello')"

    mock_grade_submission.return_value = {"overall_status": "accepted", "test_results": []}
    mock_get_file.return_value = (None, None, {"error": True, "message": "File not found"}) # Simulate error

    result = submission_service_module.handle_new_submission(problem_id, user_id, language, code)

    mock_grade_submission.assert_called_once()
    mock_get_file.assert_called_once()
    assert "error" in result
    assert "Failed to get global submissions metadata" in result["error"]

# Add more tests for other error scenarios (e.g., json decode error, github file operation errors)
