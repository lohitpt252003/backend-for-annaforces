from flask import Blueprint, request, jsonify
import json
from services.github_services import get_folder_contents, get_file
from config.github_config import GITHUB_USERS_BASE_PATH
from utils.jwt_token import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    meta_content, _, meta_error = get_file(meta_path)

    if not meta_error:
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
                "token": token # Include the token in the response
            }), 200
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid user metadata"}), 500
    else:
        return jsonify({"error": "Invalid credentials"}), 401