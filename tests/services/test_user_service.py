import pytest
from unittest.mock import MagicMock, patch, call
import json
import sys
import os
import importlib.util

# Construct the absolute path to the user_service.py file
user_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'user_service.py'))

# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("user_service_module", user_service_path)
user_service_module = importlib.util.module_from_spec(spec)
sys.modules["user_service_module"] = user_service_module
spec.loader.exec_module(user_service_module)

# Fixture to mock github_services functions
@pytest.fixture
def mock_github_services():
    with patch('user_service_module.get_file') as mock_get_file, \
         patch('user_service_module.create_or_update_file') as mock_create_or_update_file, \
         patch('user_service_module.get_folder_contents') as mock_get_folder_contents:
        yield mock_get_file, mock_create_or_update_file, mock_get_folder_contents

def test_user_service_module_exists():
    assert True

# Test get_user_by_id
def test_get_user_by_id_success(mock_github_services):
    mock_get_file, _, _ = mock_github_services
    user_id = "U1"
    expected_meta = {"user_id": user_id, "name": "Test User", "username": "testuser"}
    mock_get_file.return_value = (json.dumps(expected_meta), "sha", None)

    user_data, error = user_service_module.get_user_by_id(user_id)

    mock_get_file.assert_called_once_with(f"data/users/{user_id}/meta.json")
    assert user_data == expected_meta
    assert error is None

def test_get_user_by_id_not_found(mock_github_services):
    mock_get_file, _, _ = mock_github_services
    user_id = "U_NON_EXISTENT"
    mock_get_file.return_value = (None, None, {"error": True, "message": "File not found"})

    user_data, error = user_service_module.get_user_by_id(user_id)

    assert user_data is None
    assert "File not found" in error["error"]

# Test update_user_profile
def test_update_user_profile_success(mock_github_services):
    mock_get_file, mock_create_or_update_file, mock_get_folder_contents = mock_github_services
    user_id = "U1"
    current_meta = {"user_id": user_id, "name": "Old Name", "username": "oldusername", "bio": "Old bio"}
    
    # Mock get_file for current meta.json and index.json
    mock_get_file.side_effect = [
        (json.dumps(current_meta), "meta_sha", None), # For current user meta
        ('{"U1": {"name": "Old Name", "username": "oldusername"}}', "index_sha", None) # For users index
    ]
    
    # Mock get_folder_contents for username uniqueness check
    mock_get_folder_contents.return_value = {"success": True, "data": []}, None # No other users

    mock_create_or_update_file.return_value = {} # Simulate success

    new_name = "New Name"
    new_username = "newusername"
    new_bio = "New bio"

    success, error = user_service_module.update_user_profile(user_id, new_name, new_username, new_bio)

    assert success is True
    assert error is None
    assert mock_create_or_update_file.call_count == 2 # Once for meta.json, once for index.json

def test_update_user_profile_username_taken(mock_github_services):
    mock_get_file, mock_create_or_update_file, mock_get_folder_contents = mock_github_services
    user_id = "U1"
    current_meta = {"user_id": user_id, "name": "Old Name", "username": "oldusername", "bio": "Old bio"}
    
    mock_get_file.side_effect = [
        (json.dumps(current_meta), "meta_sha", None), # For current user meta
        (json.dumps({"user_id": "U2", "username": "takenusername"}), "other_meta_sha", None) # For other user meta
    ]
    
    mock_get_folder_contents.return_value = {
        "success": True,
        "data": [
            {'name': 'U2', 'type': 'dir'}
        ]
    }, None

    new_name = "New Name"
    new_username = "takenusername" # This username is taken
    new_bio = "New bio"

    success, error = user_service_module.update_user_profile(user_id, new_name, new_username, new_bio)

    assert success is False
    assert "Username already taken." in error["error"]
    mock_create_or_update_file.assert_not_called()

# Test get_user_submissions
def test_get_user_submissions_success(mock_github_services):
    mock_get_file, _, mock_get_folder_contents = mock_github_services
    user_id = "U1"
    
    mock_get_folder_contents.return_value = {
        "success": True,
        "data": [
            {'name': 'S1.json', 'type': 'file', 'path': 'data/users/U1/submissions/S1.json'},
            {'name': 'S2.json', 'type': 'file', 'path': 'data/users/U1/submissions/S2.json'},
        ]
    }, None

    mock_get_file.side_effect = [
        (json.dumps({"submission_id": "S1", "status": "accepted"}), "sha1", None),
        (json.dumps({"submission_id": "S2", "status": "wrong_answer"}), "sha2", None),
    ]

    submissions, error = user_service_module.get_user_submissions(user_id)

    assert error is None
    assert len(submissions) == 2
    assert submissions[0]["submission_id"] == "S1"
    assert submissions[1]["submission_id"] == "S2"

def test_get_user_submissions_no_submissions_folder(mock_github_services):
    mock_get_file, _, mock_get_folder_contents = mock_github_services
    user_id = "U_NO_SUBMISSIONS"
    
    mock_get_folder_contents.return_value = {"success": False, "error": "Path not found"}, None # Simulate folder not found

    submissions, error = user_service_module.get_user_submissions(user_id)

    assert error is None # Should return empty list, not error
    assert submissions == []

# Test get_solved_problems
def test_get_solved_problems_success(mock_github_services):
    mock_get_file, _, mock_get_folder_contents = mock_github_services
    user_id = "U1"
    
    mock_get_folder_contents.return_value = {
        "success": True,
        "data": [
            {'name': 'S1.json', 'type': 'file', 'path': 'data/users/U1/submissions/S1.json'},
            {'name': 'S2.json', 'type': 'file', 'path': 'data/users/U1/submissions/S2.json'},
            {'name': 'S3.json', 'type': 'file', 'path': 'data/users/U1/submissions/S3.json'},
        ]
    }, None

    mock_get_file.side_effect = [
        (json.dumps({"submission_id": "S1", "problem_id": "P1", "status": "accepted"}), "sha1", None),
        (json.dumps({"submission_id": "S2", "problem_id": "P2", "status": "wrong_answer"}), "sha2", None),
        (json.dumps({"submission_id": "S3", "problem_id": "P1", "status": "accepted"}), "sha3", None),
    ]

    solved_problems, error = user_service_module.get_solved_problems(user_id)

    assert error is None
    assert sorted(solved_problems) == sorted(["P1"]) # Only P1 should be solved
