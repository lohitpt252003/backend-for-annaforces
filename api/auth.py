from flask import Blueprint, jsonify
from services.github_services import get_file
import json

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Fetches user information from a JSON file in the GitHub repository.
    """
    file_path = f"data/users/{user_id}/user.json"
    content, _, error = get_file(file_path)

    if error:
        return jsonify({"error": error["message"]}), 404

    try:
        user_data = json.loads(content)
        
        # Extract only the required fields
        filtered_data = {
            "name": user_data.get("name"),
            "username": user_data.get("username"),
            "user_id": user_data.get("user_id")
        }
        
        return jsonify(filtered_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode user data."}), 500