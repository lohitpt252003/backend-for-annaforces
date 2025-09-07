import pytest
from unittest.mock import MagicMock, patch, call
import json
import os
import sys
import importlib.util

# Construct the absolute path to the judge_service.py file
judge_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'judge_service.py'))

# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("judge_service_module", judge_service_path)
judge_service_module = importlib.util.module_from_spec(spec)
sys.modules["judge_service_module"] = judge_service_module
spec.loader.exec_module(judge_service_module)

# Fixture to mock environment variables
@pytest.fixture
def mock_env_vars():
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            "JUDGE_API_SERVER_URL": "http://mock-judge-server.com",
            # Add other env vars if needed by judge_service
        }.get(key, default)
        yield

# Fixture to mock github_services functions
@pytest.fixture
def mock_github_services():
    with patch('judge_service_module.get_file') as mock_get_file, \
         patch('judge_service_module.get_folder_contents') as mock_get_folder_contents:
        yield mock_get_file, mock_get_folder_contents

# Fixture to mock requests
@pytest.fixture
def mock_requests():
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield mock_get, mock_post

def test_judge_service_module_exists():
    assert True

# Test for get_testcases
def test_get_testcases_success(mock_github_services, mock_requests, mock_env_vars):
    mock_get_file, mock_get_folder_contents = mock_github_services
    mock_get_req, _ = mock_requests

    problem_id = "P1"
    
    # Mock get_folder_contents to return input/output files
    mock_get_folder_contents.return_value = {
        'success': True,
        'data': [
            {'name': '1.in', 'type': 'file', 'path': 'data/problems/P1/testcases/1.in', 'download_url': 'http://mock.com/1.in'},
            {'name': '1.out', 'type': 'file', 'path': 'data/problems/P1/testcases/1.out', 'download_url': 'http://mock.com/1.out'},
            {'name': '2.in', 'type': 'file', 'path': 'data/problems/P1/testcases/2.in', 'download_url': 'http://mock.com/2.in'},
            {'name': '2.out', 'type': 'file', 'path': 'data/problems/P1/testcases/2.out', 'download_url': 'http://mock.com/2.out'},
        ]
    }

    # Mock requests.get for downloading test case content
    mock_input_resp1 = MagicMock(status_code=200, text="input1")
    mock_output_resp1 = MagicMock(status_code=200, text="output1")

    mock_input_resp2 = MagicMock(status_code=200, text="input2")
    mock_output_resp2 = MagicMock(status_code=200, text="output2")

    mock_get_req.side_effect = [
        mock_input_resp1, mock_output_resp1,
        mock_input_resp2, mock_output_resp2
    ]

    testcases = judge_service_module.get_testcases(problem_id)

    assert len(testcases) == 2
    assert testcases[0]['stdin'] == "input1"
    assert testcases[0]['stdout'] == "output1"
    assert testcases[1]['stdin'] == "input2"
    assert testcases[1]['stdout'] == "output2"
    mock_get_folder_contents.assert_called_once()
    assert mock_get_req.call_count == 4

def test_get_testcases_no_testcases_found(mock_github_services, mock_requests, mock_env_vars):
    mock_get_file, mock_get_folder_contents = mock_github_services
    mock_get_folder_contents.return_value = {'success': True, 'data': []} # No test cases

    testcases = judge_service_module.get_testcases("P_NO_TESTCASES")
    assert testcases == []
    mock_get_folder_contents.assert_called_once()

# Test for grade_submission
def test_grade_submission_accepted(mock_github_services, mock_requests, mock_env_vars):
    mock_get_file, mock_get_folder_contents = mock_github_services
    mock_get_req, mock_post_req = mock_requests

    problem_id = "P_ACCEPTED"
    code = "print('Hello')"
    language = "python"

    # Mock problem meta.json
    mock_get_file.return_value = (json.dumps({"timeLimit": 1000, "memoryLimit": 128}), "sha", None)

    # Mock get_testcases (called internally by grade_submission)
    mock_get_folder_contents.return_value = {
        'success': True,
        'data': [
            {'name': '1.in', 'type': 'file', 'path': 'data/problems/P_ACCEPTED/testcases/1.in', 'download_url': 'http://mock.com/1.in'},
            {'name': '1.out', 'type': 'file', 'path': 'data/problems/P_ACCEPTED/testcases/1.out', 'download_url': 'http://mock.com/1.out'},
        ]
    }
    mock_input_resp = MagicMock(status_code=200, text="input_data")
    mock_output_resp = MagicMock(status_code=200, text="expected_output")
    mock_get_req.side_effect = [mock_input_resp, mock_output_resp]

    # Mock judge server response for a successful run
    mock_judge_resp = MagicMock()
    mock_judge_resp.status_code = 200
    mock_judge_resp.json.return_value = {
        "stdout": "expected_output",
        "stderr": "",
        "err": "",
        "timetaken": 50,
        "memorytaken": 10
    }
    mock_post_req.return_value = mock_judge_resp

    result = judge_service_module.grade_submission(code, language, problem_id)

    assert result["overall_status"] == "accepted"
    assert len(result["test_results"]) == 1
    assert result["test_results"][0]["status"] == "passed"
    mock_get_file.assert_called_once()
    mock_get_folder_contents.assert_called_once()
    mock_post_req.assert_called_once()

def test_grade_submission_wrong_answer(mock_github_services, mock_requests, mock_env_vars):
    mock_get_file, mock_get_folder_contents = mock_github_services
    mock_get_req, mock_post_req = mock_requests

    problem_id = "P_WA"
    code = "print('Wrong output')"
    language = "python"

    # Mock problem meta.json
    mock_get_file.return_value = (json.dumps({"timeLimit": 1000, "memoryLimit": 128}), "sha", None)

    # Mock get_testcases
    mock_get_folder_contents.return_value = {
        'success': True,
        'data': [
            {'name': '1.in', 'type': 'file', 'path': 'data/problems/P_WA/testcases/1.in', 'download_url': 'http://mock.com/1.in'},
            {'name': '1.out', 'type': 'file', 'path': 'data/problems/P_WA/testcases/1.out', 'download_url': 'http://mock.com/1.out'},
        ]
    }
    mock_input_resp = MagicMock(status_code=200, text="input_data")
    mock_output_resp = MagicMock(status_code=200, text="correct_output")
    mock_get_req.side_effect = [mock_input_resp, mock_output_resp]

    # Mock judge server response for wrong answer
    mock_judge_resp = MagicMock()
    mock_judge_resp.status_code = 200
    mock_judge_resp.json.return_value = {
        "stdout": "incorrect_output",
        "stderr": "",
        "err": "",
        "timetaken": 50,
        "memorytaken": 10
    }
    mock_post_req.return_value = mock_judge_resp

    result = judge_service_module.grade_submission(code, language, problem_id)

    assert result["overall_status"] == "wrong_answer"
    assert result["test_results"][0]["status"] == "wrong_answer"

def test_grade_submission_compilation_error(mock_github_services, mock_requests, mock_env_vars):
    mock_get_file, mock_get_folder_contents = mock_github_services
    mock_get_req, mock_post_req = mock_requests

    problem_id = "P_CE"
    code = "invalid code"
    language = "python"

    # Mock problem meta.json
    mock_get_file.return_value = (json.dumps({"timeLimit": 1000, "memoryLimit": 128}), "sha", None)

    # Mock get_testcases
    mock_get_folder_contents.return_value = {
        'success': True,
        'data': [
            {'name': '1.in', 'type': 'file', 'path': 'data/problems/P_CE/testcases/1.in', 'download_url': 'http://mock.com/1.in'},
            {'name': '1.out', 'type': 'file', 'path': 'data/problems/P_CE/testcases/1.out', 'download_url': 'http://mock.com/1.out'},
        ]
    }
    mock_input_resp = MagicMock(status_code=200, text="input_data")
    mock_output_resp = MagicMock(status_code=200, text="expected_output")
    mock_get_req.side_effect = [mock_input_resp, mock_output_resp]

    # Mock judge server response for compilation error
    mock_judge_resp = MagicMock()
    mock_judge_resp.status_code = 200
    mock_judge_resp.json.return_value = {
        "stdout": "",
        "stderr": "Syntax Error",
        "err": "Compilation Error",
        "timetaken": 0,
        "memorytaken": 0
    }
    mock_post_req.return_value = mock_judge_resp

    result = judge_service_module.grade_submission(code, language, problem_id)

    assert result["overall_status"] == "compilation_error"
    assert result["test_results"][0]["status"] == "compilation_error"

# Add tests for other error types (TLE, MLE, RTE) and edge cases (no meta.json, judge server down)
