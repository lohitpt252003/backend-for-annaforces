import pytest
from unittest.mock import MagicMock, patch
import jwt
import time
import os
import sys
import importlib.util

# Construct the absolute path to the jwt_token.py file relative to this test file
test_dir = os.path.dirname(os.path.abspath(__file__))
jwt_token_path = os.path.abspath(os.path.join(test_dir, '..', '..', 'utils', 'jwt_token.py'))

# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("jwt_token_module", jwt_token_path)
jwt_token_module = importlib.util.module_from_spec(spec)
sys.modules["jwt_token_module"] = jwt_token_module
spec.loader.exec_module(jwt_token_module)

# Fixture to mock environment variables for SERVER_SECRET_KEY
@pytest.fixture
def mock_secret_key():
    # Patch the SERVER_SECRET_KEY directly in the module
    with patch('jwt_token_module.SERVER_SECRET_KEY', "test_secret_key"):
        yield

def test_jwt_token_module_exists():
    print("\n*************************************************")
    print("*    Test Case 1: JWT token module exists     *")
    print("*************************************************")
    assert True

@patch('jwt.encode')
@patch('time.time', return_value=1678886400) # Mock current time for predictable 'exp'
def test_generate_token_success(mock_time, mock_jwt_encode, mock_secret_key):
    print("\n*************************************************")
    print("*    Test Case 2: Successful token generation   *")
    print("*************************************************")
    user_id = "U1"
    username = "testuser"
    name = "Test User"
    expires_in = 3600 # 1 hour
    expected_token = "mocked_jwt_token"

    print(f"Input: user_id={user_id}, username={username}, name={name}, expires_in={expires_in}")
    print(f"Expected Output: {expected_token}")

    mock_jwt_encode.return_value = expected_token

    token = jwt_token_module.generate_token(user_id, username, name, expires_in)

    print(f"Actual Output: {token}")

    expected_payload = {
        "user_id": user_id,
        "username": username,
        "name": name,
        "exp": 1678886400 + expires_in
    }
    mock_jwt_encode.assert_called_once_with(
        expected_payload,
        "test_secret_key",
        algorithm="HS256"
    )
    assert token == expected_token

@patch('jwt.decode')
def test_validate_token_valid(mock_jwt_decode, mock_secret_key):
    print("\n*************************************************")
    print("*    Test Case 3: Token validation (valid)      *")
    print("*************************************************")
    token = "valid_token"
    decoded_payload = {"user_id": "U1", "username": "testuser", "exp": int(time.time()) + 3600}
    mock_jwt_decode.return_value = decoded_payload

    print(f"Input: token={token}")
    print(f"Expected Output: valid=True, data={decoded_payload}")

    result = jwt_token_module.validate_token(token)

    print(f"Actual Output: {result}")

    mock_jwt_decode.assert_called_once_with(
        token,
        "test_secret_key",
        algorithms=["HS256"]
    )
    assert result["valid"] is True
    assert result["data"] == decoded_payload

@patch('jwt.decode', side_effect=jwt.ExpiredSignatureError)
def test_validate_token_expired(mock_jwt_decode, mock_secret_key):
    print("\n*************************************************")
    print("*    Test Case 4: Token validation (expired)    *")
    print("*************************************************")
    token = "expired_token"

    print(f"Input: token={token}")
    print(f"Expected Output: valid=False, error='Token expired'")

    result = jwt_token_module.validate_token(token)

    print(f"Actual Output: {result}")

    assert result["valid"] is False
    assert result["error"] == "Token expired"

@patch('jwt.decode', side_effect=jwt.InvalidTokenError)
def test_validate_token_invalid(mock_jwt_decode, mock_secret_key):
    print("\n*************************************************")
    print("*    Test Case 5: Token validation (invalid)    *")
    print("*************************************************")
    token = "invalid_token"

    print(f"Input: token={token}")
    print(f"Expected Output: valid=False, error='Invalid token'")

    result = jwt_token_module.validate_token(token)

    print(f"Actual Output: {result}")

    assert result["valid"] is False
    assert result["error"] == "Invalid token"

def test_generate_and_validate_token_e2e(mock_secret_key):
    print("\n*************************************************")
    print("*    Test Case 6: E2E JWT Token                 *")
    print("*************************************************")
    user_id = "U_E2E"
    username = "e2e_user"
    name = "E2E Test User"
    expires_in = 1 # Token expires in 1 second for quick testing of expiry

    print(f"User ID: {user_id}, Username: {username}, Name: {name}, Expires In: {expires_in} seconds")

    # Generate a real token
    token = jwt_token_module.generate_token(user_id, username, name, expires_in)
    print(f"Generated Token: {token}")
    assert isinstance(token, str)
    assert len(token) > 0

    # Validate the token immediately (should be valid)
    result = jwt_token_module.validate_token(token)
    print(f"Validation Result (initial): {result}")
    assert result["valid"] is True
    assert result["data"]["user_id"] == user_id
    assert result["data"]["username"] == username
    assert result["data"]["name"] == name

    # Wait for the token to expire
    print(f"Waiting for {expires_in} seconds for token to expire...")
    time.sleep(expires_in + 0.1) # Add a small buffer

    # Validate the token after expiry (should be expired)
    result_expired = jwt_token_module.validate_token(token)
    print(f"Validation Result (after expiry): {result_expired}")
    assert result_expired["valid"] is False
    assert result_expired["error"] == "Token expired"
    print(f"--- E2E JWT Token Test Complete ---")