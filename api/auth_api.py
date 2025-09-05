from flask import Blueprint, request, jsonify
import json
from services.github_services import get_folder_contents, get_file, create_or_update_file
from services.firebase_service import verify_user, get_or_create_google_user, get_user, add_user, verify_otp as firebase_verify_otp
from config.github_config import GITHUB_USERS_BASE_PATH
from utils.jwt_token import generate_token
from services.email_service import generate_otp, send_otp_email, send_welcome_email, send_userid_reminder_email
from datetime import datetime, timedelta
from extensions import mail # Import the mail instance

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"error": "User ID and password are required"}), 400

    user_data, error_message = get_user(user_id)
    if error_message:
        return jsonify({"error": error_message}), 500
    if not user_data:
        return jsonify({"error": "User not found. Please sign up or contact the admin."}), 401

    

    is_valid, error_message = verify_user(user_id, password)

    if error_message:
        return jsonify({"error": error_message}), 500

    if not is_valid:
        return jsonify({"error": "Invalid credentials"}), 401

    # If verification is successful, proceed to get user metadata and generate token
    meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    meta_content, _, meta_error = get_file(meta_path)

    if meta_error:
        # This case should ideally not happen if verify_user passed, but as a fallback
        return jsonify({"error": "User metadata not found after successful verification"}), 500

    try:
        meta_data = json.loads(meta_content)
        returned_user_id = meta_data.get('id')
        username = meta_data.get('username')
        name = meta_data.get('name')

        # Generate token
        token = generate_token(returned_user_id, username, name)

        return jsonify({
            "message": "Login successful",
            "user_id": returned_user_id,
            "username": username,
            "name": name,
            "token": token
        }), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid user metadata"}), 500

@auth_bp.route('/google-signin', methods=['POST'])
def google_signin():
    data = request.get_json()
    id_token = data.get('id_token')

    if not id_token:
        return jsonify({"error": "ID token is required"}), 400

    user_data, error = get_or_create_google_user(id_token)

    if error:
        return jsonify({"error": error}), 401

    # Generate JWT for the user
    # Assuming user_data contains 'uid', 'email', 'name' from Google profile
    user_id = user_data.get('uid')
    username = user_data.get('email') # Using email as username for Google users
    name = user_data.get('name')

    token = generate_token(user_id, username, name)

    return jsonify({
        "message": "Google sign-in successful",
        "user_id": user_id,
        "username": username,
        "name": name,
        "token": token
    }), 200

unverified_users = {}

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    email = data.get('email')

    if not all([username, password, name, email]):
        return jsonify({"error": "All fields (username, password, name, email) are required"}), 400

    # Check if username already exists
    try:
        users_folders, error = get_folder_contents(GITHUB_USERS_BASE_PATH)
        if error:
            return jsonify({"error": "Could not retrieve users list to check for existing username."}), 500

        for item in users_folders:
            if item['type'] == 'dir':
                meta_path = f"{GITHUB_USERS_BASE_PATH}/{item['name']}/meta.json"
                meta_content, _, meta_error = get_file(meta_path)
                if not meta_error and meta_content:
                    meta_data = json.loads(meta_content)
                    if meta_data.get('username') == username:
                        return jsonify({"error": "Username already exists"}), 409
    except Exception as e:
        return jsonify({"error": f"Error checking for existing username: {str(e)}"}), 500

    # Generate and send OTP
    otp = generate_otp()
    otp_expiry = datetime.now() + timedelta(minutes=5)
    email_sent, email_error = send_otp_email(mail, email, otp)

    if not email_sent:
        return jsonify({"error": f"Failed to send OTP email: {email_error}"}), 500

    # Store user data temporarily
    unverified_users[email] = {
        'username': username,
        'password': password,
        'name': name,
        'otp_secret': otp,
        'otp_expiry': otp_expiry,
        'otp_attempts': 0
    }

    return jsonify({"message": "OTP has been sent to your email. Please verify to complete registration."}), 200

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    user_data = unverified_users.get(email)

    if not user_data:
        return jsonify({"error": "Invalid email or registration session expired."}), 400

    if datetime.now() > user_data['otp_expiry']:
        return jsonify({"error": "OTP expired."}), 400

    if user_data.get('otp_attempts', 0) >= 3:
        return jsonify({"error": "Too many incorrect OTP attempts. Please try signing up again."}), 400

    if user_data['otp_secret'] != otp:
        user_data['otp_attempts'] = user_data.get('otp_attempts', 0) + 1
        return jsonify({"error": "Invalid OTP."}), 400

    # OTP is correct, now create the user
    username = user_data['username']
    password = user_data['password']
    name = user_data['name']

    # Auto-generate user_id
    try:
        users_folders, error = get_folder_contents(GITHUB_USERS_BASE_PATH)
        if error:
            return jsonify({"error": "Could not retrieve users list to generate new user ID."}), 500

        max_id = 0
        for item in users_folders:
            if item['type'] == 'dir' and item['name'].startswith('U'):
                try:
                    user_id_num = int(item['name'][1:])
                    if user_id_num > max_id:
                        max_id = user_id_num
                except ValueError:
                    continue
        
        new_user_id = f"U{max_id + 1}"
        user_id = new_user_id

    except Exception as e:
        return jsonify({"error": f"Error generating new user ID: {str(e)}"}), 500

    # Add user to Firebase (already verified)
    success, error_message = add_user(user_id, password=password, method='password', is_verified=True)
    if error_message:
        return jsonify({"error": error_message}), 500

    # Create meta.json for the new user in GitHub
    user_meta_data = {
        "id": user_id,
        "username": username,
        "name": name,
        "email": email,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "bio": "",
        "number_of_submissions": 0
    }
    meta_file_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    
    commit_message = f"[AUTO] Add new user {user_id}"
    create_response = create_or_update_file(meta_file_path, json.dumps(user_meta_data, indent=2), commit_message)

    if create_response.get("error"):
        # If file creation fails, consider rolling back user creation in Firebase
        return jsonify({"error": f"Failed to create user metadata file: {create_response['message']}"}), 500

    # Update users/index.json
    try:
        index_path = f"{GITHUB_USERS_BASE_PATH}/index.json"
        index_content, index_sha, index_error = get_file(index_path)

        if index_error and "not found" not in index_error.get("message", "").lower():
            return jsonify({"error": f"Could not retrieve users index: {index_error['message']}"}), 500

        if index_content:
            users_index = json.loads(index_content)
        else:
            users_index = {}

        users_index[user_id] = {
            "username": username,
            "name": name
        }

        index_commit_message = f"[AUTO] Add user {user_id} to index"
        update_response = create_or_update_file(index_path, json.dumps(users_index, indent=2), index_commit_message)

        if update_response.get("error"):
            # This is a non-critical error, so we can just log it and proceed
            print(f"Warning: Failed to update users/index.json: {update_response['message']}")

    except Exception as e:
        print(f"Warning: An exception occurred while updating users/index.json: {str(e)}")

    # Send welcome email
    send_welcome_email(mail, email, name, username, user_id)

    # Clean up
    del unverified_users[email]

    return jsonify({"message": "Email verified and user registered successfully!", "user_id": user_id}), 201