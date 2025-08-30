import firebase_admin
import os
from firebase_admin import credentials, firestore
from argon2 import PasswordHasher
from dotenv import load_dotenv
import json

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

def get_user(user_id):
    """Fetches a user from the Firestore database.

    Args:
        user_id (str): The ID of the user to fetch.

    Returns:
        tuple: A tuple containing the user data (dict) and an error message (str).
               Returns (None, error_message) if there is an error.
               Returns (user_data, None) on success.
    """
    if not db:
        return None, "Database not initialized. FIREBASE_DB_JSON_PATH not set."
    doc_ref = db.collection(u'users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict(), None
    else:
        return None, None

# def add_user(user_id, password):
#     """Adds a new user to the Firestore database with a hashed password.

#     Args:
#         user_id (str): The ID of the new user.
#         password (str): The password for the new user.

#     Returns:
#         tuple: A tuple containing a success boolean and an error message (str).
#                Returns (None, error_message) if there is an error.
#                Returns (True, None) on success.
#     """
#     if not db:
#         return None, "Database not initialized. FIREBASE_DB_JSON_PATH not set."
#     # Hash the password before storing it
#     hashed_password = ph.hash(password)
#     doc_ref = db.collection(u'users').document(user_id)
#     doc_ref.set({
#         u'password': hashed_password
#     })
#     return True, None

def verify_user(user_id, password):
    """Verifies the password of an existing user.

    Args:
        user_id (str): The ID of the user to verify.
        password (str): The password to verify.

    Returns:
        tuple: A tuple containing a boolean indicating if the password is valid and an error message (str).
               Returns (None, error_message) if there is an error.
               Returns (True, None) if the password is valid.
               Returns (False, None) if the password is not valid.
    """
    if not db:
        return None, "Database not initialized. FIREBASE_DB_JSON_PATH not set."
    user_data, error = get_user(user_id)
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
