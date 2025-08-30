from flask import Blueprint, request, jsonify
import json
from services.github_services import get_folder_contents, get_file
from services.firebase_service import verify_user
from config.github_config import GITHUB_USERS_BASE_PATH
from utils.jwt_token import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"error": "User ID and password are required"}), 400

    is_valid, error_message = verify_user(user_id, password)

    if error_message:
        if error_message == "User not registered":
            return jsonify({"error": "You are not registered, contact admin"}), 401
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