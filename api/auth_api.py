from flask import Blueprint, request, jsonify
import json
from services.github_services import get_folder_contents, get_file, create_or_update_file
from services.firebase_service import verify_user, get_or_create_google_user, get_user, add_user
from config.github_config import GITHUB_USERS_BASE_PATH
from utils.jwt_token import generate_token
from services.email_service import generate_otp, send_otp_email, send_welcome_email, send_userid_reminder_email, send_password_reset_email, send_password_changed_confirmation_email
from datetime import datetime, timedelta
import secrets
from extensions import mail, mongo # Import the mail and mongo instances

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Verify credentials using Firebase
    is_valid, error_message = verify_user(username, password)
    if error_message:
        return jsonify({"error": error_message}), 500
    if not is_valid:
        return jsonify({"error": "Invalid credentials"}), 401

    # Fetch user details from MongoDB
    user_data = mongo.db.users.find_one({"username": username})
    if not user_data:
        return jsonify({"error": "User not found in database after successful verification"}), 500

    name = user_data.get('name')

    # Generate token
    token = generate_token(username, name)

    return jsonify({
        "message": "Login successful",
        "username": username,
        "name": name,
        "token": token
    }), 200

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
    username = user_data.get('username') # Using email as username for Google users
    name = user_data.get('name')

    token = generate_token(username, name)

    return jsonify({
        "message": "Google sign-in successful",
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

    # Check if username or email already exists in MongoDB
    if mongo.db.users.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 409
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

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

    user_data_temp = unverified_users.get(email)

    if not user_data_temp:
        return jsonify({"error": "Invalid email or registration session expired."}), 400

    if datetime.now() > user_data_temp['otp_expiry']:
        return jsonify({"error": "OTP expired."}), 400

    if user_data_temp.get('otp_attempts', 0) >= 3:
        del unverified_users[email]
        return jsonify({"error": "Too many incorrect OTP attempts. Please try signing up again."}), 400

    if user_data_temp['otp_secret'] != otp:
        user_data_temp['otp_attempts'] = user_data_temp.get('otp_attempts', 0) + 1
        unverified_users[email] = user_data_temp
        return jsonify({"error": "Invalid OTP."}), 400

    # OTP is correct, now create the user
    username = user_data_temp['username']
    password = user_data_temp['password']
    name = user_data_temp['name']

    # Add user to Firebase
    success, error_message = add_user(username, password)
    if error_message:
        return jsonify({"error": error_message}), 500

    # Insert user data into MongoDB
    user_document = {
        "username": username,
        "name": name,
        "email": email,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "bio": "",
        "number_of_submissions": 0
    }
    mongo.db.users.insert_one(user_document)

    # Create user folder in GitHub DATA repo
    user_folder_path = f"{GITHUB_USERS_BASE_PATH}/{username}/.gitkeep"
    commit_message = f"[AUTO] Create directory for user {username}"
    create_response = create_or_update_file(user_folder_path, "", commit_message)

    if create_response.get("error"):
        # This is a significant issue, but we won't roll back the DB entries for simplicity.
        # In a real-world app, a rollback or cleanup job would be necessary.
        print(f"Warning: Failed to create user directory in DATA repo: {create_response['message']}")

    # Send welcome email
    send_welcome_email(mail, email, name, username)

    # Clean up
    del unverified_users[email]

    return jsonify({"message": "Email verified and user registered successfully!", "username": username}), 201


@auth_bp.route('/<username>/submissions', methods=['GET'])
def get_user_submissions(username):
    user_submissions = list(mongo.db.submissions.find({"username": username}, {'_id': 0}))
    return jsonify(user_submissions), 200

@auth_bp.route('/forgot-userid', methods=['POST'])
def forgot_userid():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user_data = mongo.db.users.find_one({"email": email})

    if user_data:
        username = user_data.get('username')
        name = user_data.get('name')
        send_userid_reminder_email(mail, email, name, username)
    
    # Always return a generic message to prevent email enumeration
    return jsonify({"message": "If a user with that email exists, a reminder has been sent."}), 200

password_reset_otps = {}

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user_data = mongo.db.users.find_one({"email": email})

    if user_data:
        username = user_data.get('username')
        name = user_data.get('name')
        otp = generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=5)

        password_reset_otps[email] = {
            'username': username,
            'name': name,
            'otp_secret': otp,
            'otp_expiry': otp_expiry,
            'otp_attempts': 0
        }

        send_password_reset_email(mail, email, name, otp)
    
    # Always return a generic message to prevent email enumeration
    return jsonify({"message": "If a user with that email exists, an OTP has been sent."}), 200

@auth_bp.route('/verify-password-reset-otp', methods=['POST'])
def verify_password_reset_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')

    if not all([email, otp, new_password]):
        return jsonify({"error": "Email, OTP, and new password are required"}), 400

    reset_data = password_reset_otps.get(email)

    if not reset_data:
        return jsonify({"error": "Invalid email or password reset session expired."}), 400

    if datetime.now() > reset_data['otp_expiry']:
        del password_reset_otps[email]
        return jsonify({"error": "OTP expired."}), 400

    if reset_data.get('otp_attempts', 0) >= 3:
        del password_reset_otps[email]
        return jsonify({"error": "Too many incorrect OTP attempts. Please try requesting a new OTP."}), 400

    if reset_data['otp_secret'] != otp:
        reset_data['otp_attempts'] = reset_data.get('otp_attempts', 0) + 1
        password_reset_otps[email] = reset_data
        return jsonify({"error": "Invalid OTP."}), 400

    username = reset_data['username']
    name = reset_data['name']

    # Update password in Firebase
    success, error_message = add_user(username, new_password)
    if error_message:
        return jsonify({"error": error_message}), 500

    send_password_changed_confirmation_email(mail, email, name)

    del password_reset_otps[email]

    return jsonify({"message": "Password has been reset successfully."}), 200