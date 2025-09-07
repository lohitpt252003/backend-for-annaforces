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

# Test for GET /api/users/
def test_get_users_returns_list(live_server_url):
    response = requests.get(f"{live_server_url}/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test for GET /api/users/<user_id>
def test_get_user_by_id_not_found(live_server_url):
    response = requests.get(f"{live_server_url}/api/users/NON_EXISTENT_ID")
    assert response.status_code == 404
    assert "User not found" in response.json().get("message", "")

# Test for GET /api/users/<user_id>/submissions
def test_get_user_submissions_returns_list(live_server_url):
    user_id = "U1" # Assuming U1 exists
    response = requests.get(f"{live_server_url}/api/users/{user_id}/submissions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test for PUT /api/users/<user_id> (requires authentication and specific data)
# This is a placeholder and will likely fail without proper authentication and user setup
def test_update_user_profile_requires_auth(live_server_url):
    user_id = "U1" # Assuming U1 exists
    update_data = {
        "name": "Updated Name",
        "bio": "Updated bio"
    }
    response = requests.put(f"{live_server_url}/api/users/{user_id}", json=update_data)
    # Expecting 401 Unauthorized or 403 Forbidden without proper auth
    assert response.status_code in [401, 403]