import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
import base64
import os
import time
import sys
import importlib.util

# Construct the absolute path to the github_services.py file
github_services_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend-for-annaforces', 'services', 'github_services.py'))

# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("github_services_module", github_services_path)
github_services_module = importlib.util.module_from_spec(spec)
sys.modules["github_services_module"] = github_services_module
spec.loader.exec_module(github_services_module)

# Fixture to mock environment variables for GitHub config
@pytest.fixture
def mock_github_env():
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO": "test_repo",
            "GITHUB_OWNER": "test_owner"
        }.get(key)
        yield

# Fixture to mock requests.get and requests.put
@pytest.fixture
def mock_requests():
    with patch('requests.get') as mock_get, \
         patch('requests.put') as mock_put:
        yield mock_get, mock_put

# Fixture to mock os.path functions and os.listdir
@pytest.fixture
def mock_os_paths():
    with patch('os.path.exists') as mock_exists, \
         patch('os.path.isfile') as mock_isfile, \
         patch('os.path.isdir') as mock_isdir, \
         patch('os.listdir') as mock_listdir, \
         patch('os.path.abspath') as mock_abspath, \
         patch('os.path.join') as mock_join:

        # Default mocks for path functions
        mock_exists.return_value = False
        mock_isfile.return_value = False
        mock_isdir.return_value = False
        mock_abspath.side_effect = lambda x: x # Return path as is for simplicity
        mock_join.side_effect = os.path.join # Use real join for simplicity

        yield mock_exists, mock_isfile, mock_isdir, mock_listdir, mock_abspath, mock_join



# Test for get_github_config
def test_get_github_config_success(mock_github_env):
    token, repo, owner, error = github_services_module.get_github_config()
    assert token == "test_token"
    assert repo == "test_repo"
    assert owner == "test_owner"
    assert error is None

def test_get_github_config_missing_env_var():
    with patch('os.getenv', side_effect=lambda key: None):
        token, repo, owner, error = github_services_module.get_github_config()
        assert token is None
        assert repo is None
        assert owner is None
        assert error["error"] is True
        assert "Missing required environment variables" in error["message"]

# Test for get_file (local file system)
def test_get_file_local_success(mock_os_paths):
    mock_exists, mock_isfile, _, _, _, _ = mock_os_paths
    mock_exists.return_value = True
    mock_isfile.return_value = True
    
    mock_file_content = "local file content"
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as mocked_file_open:
        content, sha, error = github_services_module.get_file("data/test.txt")
        assert content == mock_file_content
        assert sha == "local_sha"
        assert error is None
        mocked_file_open.assert_called_once()

def test_get_file_local_read_error(mock_os_paths):
    mock_exists, mock_isfile, _, _, _, _ = mock_os_paths
    mock_exists.return_value = True
    mock_isfile.return_value = True
    
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        content, sha, error = github_services_module.get_file("data/test.txt")
        assert content is None
        assert sha is None
        assert error["error"] is True
        assert "Error reading local file" in error["message"]

# Test for get_file (GitHub API)
def test_get_file_github_success(mock_github_env, mock_requests, mock_os_paths):
    mock_get, _ = mock_requests
    mock_exists, mock_isfile, _, _, _, _ = mock_os_paths # Ensure local path doesn't exist
    mock_exists.return_value = False
    mock_isfile.return_value = False

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "content": base64.b64encode(b"github file content").decode('utf-8'),
        "sha": "github_sha123"
    }
    mock_get.return_value = mock_response

    content, sha, error = github_services_module.get_file("path/to/github_file.txt")

    mock_get.assert_called_once()
    assert content == "github file content"
    assert sha == "github_sha123"
    assert error is None

def test_get_file_github_not_found(mock_github_env, mock_requests, mock_os_paths):
    mock_get, _ = mock_requests
    mock_exists, mock_isfile, _, _, _, _ = mock_os_paths
    mock_exists.return_value = False
    mock_isfile.return_value = False

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_get.return_value = mock_response

    content, sha, error = github_services_module.get_file("non_existent_file.txt")

    mock_get.assert_called_once()
    assert content is None
    assert sha is None
    assert error["error"] is True
    assert "File not found" in error["message"]

# Test for add_file
def test_add_file_success(mock_github_env, mock_requests):
    _, mock_put = mock_requests
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"content": {"name": "new_file.txt"}}
    mock_put.return_value = mock_response

    result = github_services_module.add_file("new_file.txt", "some data")

    mock_put.assert_called_once()
    assert result == {"content": {"name": "new_file.txt"}}

def test_add_file_failure_after_retries(mock_github_env, mock_requests):
    _, mock_put = mock_requests
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_put.return_value = mock_response

    with patch('time.sleep', return_value=None): # Prevent actual sleep during test
        result = github_services_module.add_file("failed_file.txt", "data", retries=3)
        mock_put.call_count == 3 # Should retry 3 times
        assert result["error"] is True
        assert "Failed to add file" in result["message"]

# Add tests for update_file, create_or_update_file, get_folder_contents
# These will follow similar patterns of mocking requests and os functions.
