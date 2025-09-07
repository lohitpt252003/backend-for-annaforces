import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timedelta, timezone
import json
import sys
import os
import importlib.util

# Construct the absolute path to the firebase_service.py file
firebase_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend-for-annaforces', 'services', 'firebase_service.py'))

# Create a module spec from the file path
spec = importlib.util.spec_from_file_location("firebase_service_module", firebase_service_path)
firebase_service_module = importlib.util.module_from_spec(spec)
sys.modules["firebase_service_module"] = firebase_service_module
spec.loader.exec_module(firebase_service_module)

# Mock the environment variable for Firebase credentials
@patch('os.environ.get', return_value=json.dumps({'type': 'service_account'}))
# Mock firebase_admin and its submodules
@patch('firebase_admin.credentials.Certificate')
@patch('firebase_admin.initialize_app')
@patch('firebase_admin.firestore.client')
@patch('firebase_admin.auth.verify_id_token')
# Mock argon2.PasswordHasher
@patch('argon2.PasswordHasher')
def setup_firebase_mocks(
    mock_ph, mock_firestore_client,
    mock_initialize_app, mock_certificate, mock_environ_get
):
    # Re-import the module to ensure mocks are applied to the module-level variables
    # This is crucial because db and ph are initialized at import time
    # import services.firebase_service as firebase_service_module # Removed
    
    # Reset mocks for each test
    mock_ph.reset_mock()
    mock_firestore_client.reset_mock()
    mock_initialize_app.reset_mock()
    mock_certificate.reset_mock()
    mock_environ_get.reset_mock()

    # Configure mocks for db and ph
    firebase_service_module.db = MagicMock()
    firebase_service_module.ph = MagicMock()

    return firebase_service_module.db, firebase_service_module.ph

def test_firebase_service_module_exists():
    assert True

@pytest.fixture
def mock_db_and_ph():
    # This fixture will ensure mocks are set up before each test
    # and the module's db/ph are correctly mocked.
    with patch('os.environ.get', return_value=json.dumps({'type': 'service_account'})) as mock_environ_get, \
         patch('firebase_admin.credentials.Certificate') as mock_certificate, \
         patch('firebase_admin.initialize_app') as mock_initialize_app, \
         patch('firebase_admin.firestore.client') as mock_firestore_client, \
         patch('argon2.PasswordHasher') as mock_ph_class:
        
        # Mock the instances returned by the patched classes
        mock_db_instance = MagicMock()
        mock_firestore_client.return_value = mock_db_instance
        mock_ph_instance = MagicMock()
        mock_ph_class.return_value = mock_ph_instance

        # Re-import the module to ensure mocks are applied
        # import services.firebase_service as firebase_service_module # Removed
        
        # Ensure the module's db and ph are the mocked instances
        firebase_service_module.db = mock_db_instance
        firebase_service_module.ph = mock_ph_instance

        yield mock_db_instance, mock_ph_instance
        
        # Clean up after test if necessary
        del firebase_service_module.db
        del firebase_service_module.ph


def test_get_user_success(mock_db_and_ph):
    mock_db, _ = mock_db_and_ph
    user_id = "test_user_id"
    expected_user_data = {"name": "Test User", "email": "test@example.com"}

    mock_doc_ref = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = expected_user_data
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    user_data, error = firebase_service_module.get_user(user_id)

    mock_db.collection.assert_called_once_with('users')
    mock_db.collection.return_value.document.assert_called_once_with(user_id)
    mock_doc_ref.get.assert_called_once()
    assert user_data == expected_user_data
    assert error is None

def test_get_user_not_found(mock_db_and_ph):
    mock_db, _ = mock_db_and_ph
    user_id = "non_existent_user"

    mock_doc_ref = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    user_data, error = firebase_service_module.get_user(user_id)

    assert user_data is None
    assert error is None # No error, just not found

def test_add_user_password_method_success(mock_db_and_ph):
    mock_db, mock_ph = mock_db_and_ph
    user_id = "new_user_id"
    password = "secure_password"
    hashed_password = "hashed_secure_password"

    mock_ph.hash.return_value = hashed_password
    mock_doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    success, error = firebase_service_module.add_user(user_id, password=password, method='password')

    mock_ph.hash.assert_called_once_with(password)
    mock_db.collection.assert_called_once_with('users')
    mock_db.collection.return_value.document.assert_called_once_with(user_id)
    mock_doc_ref.set.assert_called_once_with({
        'method': 'password',
        'is_verified': False,
        'password': hashed_password
    })
    assert success is True
    assert error is None

def test_add_user_google_method_success(mock_db_and_ph):
    mock_db, _ = mock_db_and_ph
    user_id = "google_user_id"
    user_data = {"email": "google@example.com", "name": "Google User", "picture": "url"}

    mock_doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    success, error = firebase_service_module.add_user(user_id, method='google', user_data=user_data)

    mock_db.collection.assert_called_once_with('users')
    mock_db.collection.return_value.document.assert_called_once_with(user_id)
    mock_doc_ref.set.assert_called_once_with({
        'method': 'google',
        'is_verified': True,
        'email': user_data['email'],
        'name': user_data['name'],
        'picture': user_data['picture']
    })
    assert success is True
    assert error is None

def test_add_user_password_method_missing_password(mock_db_and_ph):
    _, _ = mock_db_and_ph # Mocks are still active but not used in this specific test path
    user_id = "user_no_password"
    
    success, error = firebase_service_module.add_user(user_id, method='password')
    
    assert success is None
    assert "Password is required for password method." in error

def test_verify_user_success(mock_db_and_ph):
    mock_db, mock_ph = mock_db_and_ph
    user_id = "existing_user"
    password = "correct_password"
    hashed_password = "hashed_correct_password"
    
    # Mock get_user to return user data
    mock_doc_ref = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"password": hashed_password}
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    mock_ph.verify.return_value = None # argon2.verify returns None on success

    success, error = firebase_service_module.verify_user(user_id, password)

    mock_ph.verify.assert_called_once_with(hashed_password, password)
    assert success is True
    assert error is None

def test_verify_user_invalid_password(mock_db_and_ph):
    mock_db, mock_ph = mock_db_and_ph
    user_id = "existing_user"
    password = "wrong_password"
    hashed_password = "hashed_correct_password"
    
    # Mock get_user to return user data
    mock_doc_ref = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"password": hashed_password}
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    mock_ph.verify.side_effect = Exception("Password verification failed") # Simulate incorrect password

    success, error = firebase_service_module.verify_user(user_id, password)

    mock_ph.verify.assert_called_once_with(hashed_password, password)
    assert success is False
    assert error is None # Error is None for invalid password, as per function's return

def test_verify_otp_success(mock_db_and_ph):
    mock_db, _ = mock_db_and_ph
    user_id = "otp_user"
    otp = "123456"
    
    # Mock user data with valid OTP and future expiry
    future_expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
    mock_user_data = {"otp_secret": otp, "otp_expiry": future_expiry, "is_verified": False}

    mock_doc_ref = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = mock_user_data
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    success, error = firebase_service_module.verify_otp(user_id, otp)

    mock_doc_ref.update.assert_called_once_with({
        'is_verified': True,
        'otp_secret': firebase_service_module.firestore.DELETE_FIELD,
        'otp_expiry': firebase_service_module.firestore.DELETE_FIELD
    })
    assert success is True
    assert error is None

def test_verify_otp_expired(mock_db_and_ph):
    mock_db, _ = mock_db_and_ph
    user_id = "otp_user"
    otp = "123456"
    
    # Mock user data with expired OTP
    past_expiry = datetime.now(timezone.utc) - timedelta(minutes=5)
    mock_user_data = {"otp_secret": otp, "otp_expiry": past_expiry, "is_verified": False}

    mock_doc_ref = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = mock_user_data
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    success, error = firebase_service_module.verify_otp(user_id, otp)

    mock_doc_ref.update.assert_not_called() # Should not update if expired
    assert success is False
    assert "OTP expired." in error

@patch('firebase_service_module.auth')
def test_verify_google_token_success(mock_auth, mock_db_and_ph):
    _, _ = mock_db_and_ph # Use fixture to ensure db/ph are mocked
    id_token = "valid_token" # This string doesn't matter as verify_id_token is mocked
    expected_decoded_token = {"uid": "google_uid", "email": "google@example.com", "name": "Test User"} # Simulate a decoded token
    mock_auth.verify_id_token.return_value = expected_decoded_token

    decoded_token = firebase_service_module.verify_google_token(id_token)

    mock_auth.verify_id_token.assert_called_once_with(id_token)
    assert decoded_token == expected_decoded_token

@patch('firebase_service_module.auth')
def test_verify_google_token_invalid(mock_auth, mock_db_and_ph):
    _, _ = mock_db_and_ph
    id_token = "invalid_token"
    mock_auth.verify_id_token.side_effect = Exception("Invalid token")

    with pytest.raises(ValueError, match="Invalid Google ID token"):
        firebase_service_module.verify_google_token(id_token)

@patch('firebase_service_module.verify_google_token')
@patch('firebase_service_module.get_user')
@patch('firebase_service_module.add_user')
def test_get_or_create_google_user_existing_user(
    mock_add_user, mock_get_user, mock_verify_google_token, mock_db_and_ph
):
    mock_db, _ = mock_db_and_ph
    id_token = "some_id_token"
    decoded_token = {"uid": "google_uid", "email": "existing@example.com"}
    existing_user_data = {"uid": "google_uid", "name": "Existing User"}

    mock_verify_google_token.return_value = decoded_token
    mock_get_user.return_value = (existing_user_data, None) # User exists

    user_data, error = firebase_service_module.get_or_create_google_user(id_token)

    mock_verify_google_token.assert_called_once_with(id_token)
    mock_get_user.assert_called_once_with("google_uid")
    mock_add_user.assert_not_called() # Should not call add_user
    assert user_data == existing_user_data
    assert error is None

@patch('firebase_service_module.verify_google_token')
@patch('firebase_service_module.get_user')
@patch('firebase_service_module.add_user')
def test_get_or_create_google_user_new_user(
    mock_add_user, mock_get_user, mock_verify_google_token, mock_db_and_ph
):
    mock_db, _ = mock_db_and_ph
    id_token = "new_id_token"
    decoded_token = {"uid": "new_google_uid", "email": "new@example.com", "name": "New User"}
    new_user_data_after_add = {"uid": "new_google_uid", "name": "New User", "method": "google"}

    mock_verify_google_token.return_value = decoded_token
    mock_get_user.side_effect = [(None, None), (new_user_data_after_add, None)] # First call: not found, Second call: found after add
    mock_add_user.return_value = (True, None)

    user_data, error = firebase_service_module.get_or_create_google_user(id_token)

    mock_verify_google_token.assert_called_once_with(id_token)
    assert mock_get_user.call_count == 2 # Called once to check existence, once to fetch after add
    mock_add_user.assert_called_once_with(
        "new_google_uid",
        method='google',
        user_data={'email': 'new@example.com', 'name': 'New User', 'picture': None}
    )
    assert user_data == new_user_data_after_add
    assert error is None
