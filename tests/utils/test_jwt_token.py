import unittest
from unittest.mock import MagicMock, patch
import jwt
import time
import os
import sys

# Add the parent directory (backend-for-annaforces) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Direct import of jwt_token from utils
from utils import jwt_token

class TestJwtToken(unittest.TestCase):

    @patch('os.getenv', return_value="test_secret_key")
    def setUp(self, mock_getenv):
        # This will be called before each test method
        # Re-import jwt_token to ensure the patched getenv is used
        # This is necessary because SERVER_SECRET_KEY is loaded at module level
        import importlib
        importlib.reload(jwt_token)
        pass

    def test_jwt_token_module_exists(self):
        print("\n*************************************************")
        print("*    Test Case 1: JWT token module exists     *")
        print("*************************************************")
        self.assertTrue(True)

    @patch('jwt.encode')
    @patch('time.time', return_value=1678886400) # Mock current time for predictable 'exp'
    def test_generate_token_success(self, mock_time, mock_jwt_encode):
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

        token = jwt_token.generate_token(user_id, username, name, expires_in)

        print(f"Actual Output: {token}")

        expected_payload = {
            "user_id": user_id,
            "username": username,
            "name": name,
            "exp": 1678886400 + expires_in
        }
        mock_jwt_encode.assert_called_once_with(
            expected_payload,
            "test_secret_key", # This should now be the mocked value
            algorithm="HS256"
        )
        self.assertEqual(token, expected_token)

    @patch('jwt.decode')
    def test_validate_token_valid(self, mock_jwt_decode):
        print("\n*************************************************")
        print("*    Test Case 3: Token validation (valid)      *")
        print("*************************************************")
        token = "valid_token"
        decoded_payload = {"user_id": "U1", "username": "testuser", "exp": int(time.time()) + 3600}
        mock_jwt_decode.return_value = decoded_payload

        print(f"Input: token={token}")
        print(f"Expected Output: valid=True, data={decoded_payload}")

        result = jwt_token.validate_token(token)

        print(f"Actual Output: {result}")

        mock_jwt_decode.assert_called_once_with(
            token,
            "test_secret_key", # This should now be the mocked value
            algorithms=["HS256"]
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["data"], decoded_payload)

    @patch('jwt.decode', side_effect=jwt.ExpiredSignatureError)
    def test_validate_token_expired(self, mock_jwt_decode):
        print("\n*************************************************")
        print("*    Test Case 4: Token validation (expired)    *")
        print("*************************************************")
        token = "expired_token"

        print(f"Input: token={token}")
        print(f"Expected Output: valid=False, error='Token expired'")

        result = jwt_token.validate_token(token)

        print(f"Actual Output: {result}")

        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "Token expired")

    @patch('jwt.decode', side_effect=jwt.InvalidTokenError)
    def test_validate_token_invalid(self, mock_jwt_decode):
        print("\n*************************************************")
        print("*    Test Case 5: Token validation (invalid)    *")
        print("*************************************************")
        token = "invalid_token"

        print(f"Input: token={token}")
        print(f"Expected Output: valid=False, error='Invalid token'")

        result = jwt_token.validate_token(token)

        print(f"Actual Output: {result}")

        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "Invalid token")

    @patch('os.getenv', return_value="test_secret_key")
    def test_generate_and_validate_token_e2e(self, mock_getenv):
        print("\n*************************************************")
        print("*    Test Case 6: E2E JWT Token                 *")
        print("*************************************************")
        # Re-import jwt_token to ensure the patched getenv is used for this test
        import importlib
        importlib.reload(jwt_token)

        user_id = "U_E2E"
        username = "e2e_user"
        name = "E2E Test User"
        expires_in = 1 # Token expires in 1 second for quick testing of expiry

        print(f"User ID: {user_id}, Username: {username}, Name: {name}, Expires In: {expires_in} seconds")

        # Generate a real token
        token = jwt_token.generate_token(user_id, username, name, expires_in)
        print(f"Generated Token: {token}")
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

        # Validate the token immediately (should be valid)
        result = jwt_token.validate_token(token)
        print(f"Validation Result (initial): {result}")
        self.assertTrue(result["valid"])
        self.assertEqual(result["data"]["user_id"], user_id)
        self.assertEqual(result["data"]["username"], username)
        self.assertEqual(result["data"]["name"], name)

        # Wait for the token to expire
        print(f"Waiting for {expires_in} seconds for token to expire...")
        time.sleep(expires_in + 0.1) # Add a small buffer

        # Validate the token after expiry (should be expired)
        result_expired = jwt_token.validate_token(token)
        print(f"Validation Result (after expiry): {result_expired}")
        self.assertFalse(result_expired["valid"])
        self.assertEqual(result_expired["error"], "Token expired")
        print(f"--- E2E JWT Token Test Complete ---")

if __name__ == '__main__':
    unittest.main()