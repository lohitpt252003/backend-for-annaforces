import firebase_admin
import os
from firebase_admin import credentials, firestore, auth
from argon2 import PasswordHasher
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
load_dotenv()


# Load the JSON content of the service account key from the environment variable
cred_json_str = os.environ.get("FIREBASE_DB_CREDENTIALS")

# Initialize Firebase and PasswordHasher only if the environment variable is set
if not cred_json_str:
    db = None
    ph = None
    print("Warning: FIREBASE_DB_CREDENTIALS environment variable not set. Database functions will be disabled.")
else:
    try:
        # Parse the JSON string from the environment variable into a dictionary
        cred_dict = json.loads(cred_json_str)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        ph = PasswordHasher()
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in FIREBASE_DB_CREDENTIALS: {e}")
        db = None
        ph = None

def get_user(username):
    """Fetches a user from the Firestore database.

    Args:
        username (str): The username of the user to fetch.

    Returns:
        tuple: A tuple containing the user data (dict) and an error message (str).
               Returns (None, error_message) if there is an error.
               Returns (user_data, None) on success.
    """
    if not db:
        return None, "Database not initialized. FIREBASE_DB_JSON_PATH not set."
    
    # Query for the user by username
    users_ref = db.collection(u'users')
    query = users_ref.where(u'username', u'==', username).limit(1)
    docs = query.stream()
    
    user_doc = next(docs, None)
    
    if user_doc:
        return user_doc.to_dict(), None
    else:
        return None, None

def add_user(username, password=None, method='password', user_data=None, otp_secret=None, otp_expiry=None, is_verified=False):
    """Adds a new user to the Firestore database.

    Args:
        username (str): The username of the new user.
        password (str, optional): The password for the new user if method is 'password'. Defaults to None.
        method (str): The sign-up method ('password' or 'google'). Defaults to 'password'.
        user_data (dict, optional): Additional user data for 'google' method (e.g., email, name). Defaults to None.
        otp_secret (str, optional): The OTP secret if generated. Defaults to None.
        otp_expiry (datetime, optional): The OTP expiry time if generated. Defaults to None.

    Returns:
        tuple: A tuple containing a success boolean and an error message (str).
               Returns (None, error_message) if there is an error.
               Returns (True, None) on success.
    """
    if not db:
        return None, "Database not initialized. FIREBASE_DB_JSON_PATH not set."
    
    doc_ref = db.collection(u'users').document(username)
    
    user_doc = {
        u'username': username,
        u'method': method,
        u'is_verified': is_verified
    }

    if method == 'password':
        if not password:
            return None, "Password is required for password method."
        hashed_password = ph.hash(password)
        user_doc[u'password'] = hashed_password
        if otp_secret and otp_expiry:
            user_doc[u'otp_secret'] = otp_secret
            user_doc[u'otp_expiry'] = otp_expiry
    elif method == 'google':
        if not user_data:
            return None, "User data is required for google method."
        user_doc[u'email'] = user_data.get('email')
        user_doc[u'name'] = user_data.get('name')
        user_doc[u'picture'] = user_data.get('picture')
        user_doc[u'is_verified'] = True # Google users are verified by default
    else:
        return None, "Invalid sign-up method."

    doc_ref.set(user_doc)

    return True, None

def verify_user(username, password):
    """Verifies the password of an existing user.

    Args:
        username (str): The username of the user to verify.
        password (str): The password to verify.

    Returns:
        tuple: A tuple containing a boolean indicating if the password is valid and an error message (str).
               Returns (None, error_message) if there is an error.
               Returns (True, None) if the password is valid.
               Returns (False, None) if the password is not valid.
    """
    if not db:
        return None, "Database not initialized. FIREBASE_DB_JSON_PATH not set."
    user_data, error = get_user(username)
    if error:
        return None, error
    if user_data:
        try:
            # Verify the password against the stored hash
            ph.verify(user_data['password'], password)
            return True, None
        except Exception:
            # The password hash verification failed
            return False, None
    else:
        # User not found
        return False, "User not registered"

def verify_otp(username, otp):
    """Verifies the OTP for a given user.

    Args:
        username (str): The username of the user.
        otp (str): The OTP to verify.

    Returns:
        tuple: A tuple containing a boolean indicating success and an error message (str).
               Returns (True, None) on successful verification.
               Returns (False, error_message) on failure.
    """
    if not db:
        return False, "Database not initialized."

    user_data, error = get_user(username)
    if error:
        return False, error
    if not user_data:
        return False, "User not found."

    stored_otp = user_data.get('otp_secret')
    stored_expiry = user_data.get('otp_expiry')

    if not stored_otp or not stored_expiry:
        return False, "OTP not requested or expired."

    # Convert Firestore Timestamp to datetime object
    if datetime.now(timezone.utc) > stored_expiry:
        return False, "OTP expired."

    if stored_otp == otp:
        # Mark user as verified and clear OTP fields
        user_ref = db.collection(u'users').document(username)
        user_ref.update({
            u'is_verified': True,
            u'otp_secret': firestore.DELETE_FIELD,
            u'otp_expiry': firestore.DELETE_FIELD
        })
        return True, None
    else:
        return False, "Invalid OTP."

def verify_google_token(id_token):
    """Verifies a Google ID token using Firebase Admin SDK.

    Args:
        id_token (str): The Google ID token to verify.

    Returns:
        dict: The decoded token if valid.

    Raises:
        ValueError: If the token is invalid or verification fails.
    """
    if not firebase_admin._apps:
        raise ValueError("Firebase app not initialized.")
    try:
        decoded_token = firebase_admin.auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid Google ID token: {e}")

def get_or_create_google_user(id_token):
    """Verifies Google ID token and gets or creates a user in Firestore.

    Args:
        id_token (str): The Google ID token.

    Returns:
        tuple: A tuple containing the user data (dict) and an error message (str).
               Returns (None, error_message) if there is an error.
               Returns (user_data, None) on success.
    """
    if not db:
        return None, "Database not initialized."

    try:
        decoded_token = verify_google_token(id_token)
        email = decoded_token.get('email')
        if not email:
            return None, "Email not found in Google token."

        username = email # Using email as username

        user_data, error = get_user(username)
        if error:
            return None, error

        if user_data:
            # User exists, return their data
            return user_data, None
        else:
            # User does not exist, create a new one
            user_info = {
                'email': email,
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
            }
            success, error = add_user(username, method='google', user_data=user_info)
            if error:
                return None, error
            
            # Fetch the newly created user to return complete data
            return get_user(username)

    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"