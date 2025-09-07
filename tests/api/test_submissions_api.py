import pytest
import requests
import os
import sys

# Add the parent directory of backend-for-annaforces to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend-for-annaforces')))

BASE_URL = os.getenv("BACKEND_API_BASE_URL", "http://127.0.0.1:5000")

@pytest.fixture(scope="module")
def live_server_url():
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print(f"Backend server is reachable at {BASE_URL}")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Backend server not running or unreachable at {BASE_URL}: {e}")
    return BASE_URL

# Test for GET /api/submissions/
def test_get_submissions_returns_list(live_server_url):
    response = requests.get(f"{live_server_url}/api/submissions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test for GET /api/submissions/<submission_id>
def test_get_submission_by_id_not_found(live_server_url):
    response = requests.get(f"{live_server_url}/api/submissions/NON_EXISTENT_ID")
    assert response.status_code == 404
    assert "Submission not found" in response.json().get("message", "")

# Test for POST /api/problems/<problem_id>/submit (requires authentication and specific data)
# This is a placeholder and will likely fail without proper authentication and problem setup
def test_add_submission_requires_auth(live_server_url):
    problem_id = "P1" # Assuming P1 exists
    submission_data = {
        "language": "python",
        "code": "print('Hello World')"
    }
    response = requests.post(f"{live_server_url}/api/problems/{problem_id}/submit", json=submission_data)
    # Expecting 401 Unauthorized or 403 Forbidden without proper auth
    assert response.status_code in [401, 403]

# Test for GET /api/problems/<problem_id>/submissions
def test_get_problem_submissions_returns_list(live_server_url):
    problem_id = "P1" # Assuming P1 exists
    response = requests.get(f"{live_server_url}/api/problems/{problem_id}/submissions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)