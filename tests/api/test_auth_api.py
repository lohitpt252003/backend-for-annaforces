import pytest
import requests
import os
import uuid
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

# Test for POST /api/auth/register
def test_register_user_success(live_server_url):
    # Generate a unique username and email for each test run
    unique_id = str(uuid.uuid4())[:8]
    test_username = f"testuser_{unique_id}"
    test_email = f"test_{unique_id}@example.com"
    test_password = "password123"

    register_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password
    }
    response = requests.post(f"{live_server_url}/api/auth/register", json=register_data)
    assert response.status_code == 201
    assert "message" in response.json()
    assert "user_id" in response.json()

# Test for POST /api/auth/login
def test_login_user_success(live_server_url):
    # This test assumes a user is already registered (e.g., from a setup fixture or manual registration)
    # For a robust test, you'd register a user first, then attempt login.
    login_data = {
        "username": "existing_test_user", # Replace with a known existing user
        "password": "existing_password"   # Replace with the password for that user
    }
    response = requests.post(f"{live_server_url}/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user_id" in response.json()

def test_login_user_invalid_credentials(live_server_url):
    login_data = {
        "username": "non_existent_user",
        "password": "wrong_password"
    }
    response = requests.post(f"{live_server_url}/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "message" in response.json()
    assert "Invalid credentials" in response.json()["message"]

# Add tests for verify_otp, resend_otp, reset_password_request, reset_password_confirm
# These will require more complex state management (e.g., OTP generation, user verification status)
# and will be added incrementally.