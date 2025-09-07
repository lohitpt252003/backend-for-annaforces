import pytest
import requests
import os
import sys

# Add the parent directory of backend-for-annaforces to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend-for-annaforces')))

# Define the base URL for the backend API
# This should be configured to point to your running backend server
# For local development, it might be "http://127.0.0.1:5000" or "http://localhost:5000"
# You might want to get this from an environment variable or a config file
BASE_URL = os.getenv("BACKEND_API_BASE_URL", "http://127.0.0.1:5000")

# Fixture to ensure the backend server is running
@pytest.fixture(scope="module")
def live_server_url():
    # In a real scenario, you would start the Flask server here
    # or ensure it's running before tests execute.
    # For this exercise, we assume the server is already running as per user's instruction.
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print(f"Backend server is reachable at {BASE_URL}")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Backend server not running or unreachable at {BASE_URL}: {e}")
    return BASE_URL

# Test for GET /api/problems/
def test_get_problems_returns_list(live_server_url):
    response = requests.get(f"{live_server_url}/api/problems/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test for POST /api/problems/add (requires authentication and specific data)
# This is a placeholder and will likely fail without proper authentication setup
def test_add_problem_requires_auth(live_server_url):
    new_problem_data = {
        "problem_id": "P999",
        "title": "Test Problem",
        "difficulty": "Easy",
        "tags": ["Test", "API"],
        "description": "This is a test problem description."
    }
    response = requests.post(f"{live_server_url}/api/problems/add", json=new_problem_data)
    # Expecting 401 Unauthorized or 403 Forbidden without proper auth
    assert response.status_code in [401, 403]

# Test for GET /api/problems/<problem_id>
def test_get_problem_by_id_not_found(live_server_url):
    response = requests.get(f"{live_server_url}/api/problems/NON_EXISTENT_ID")
    assert response.status_code == 404
    assert "Problem not found" in response.json().get("message", "")

# Add more tests for other endpoints (update, delete, submissions, solution)
# These will require more complex setup (e.g., adding a problem first, authentication)
# and will be added incrementally.