from flask import Blueprint, jsonify, request
import json

from services.user_service import get_user_by_id as get_user_by_id_service, get_user_submissions as get_user_submissions_service, update_user_profile as update_user_profile_service, get_solved_problems as get_solved_problems_service
from services.github_services import get_file
from config.github_config import GITHUB_USERS_BASE_PATH
from api.problems_api import token_required

# Blueprint declaration
users_bp = Blueprint("users", __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    file_path = f"{GITHUB_USERS_BASE_PATH}/index.json"
    content, _, error = get_file(file_path)

    if error:
        return jsonify({"error": error["message"]}), 500

    try:
        return jsonify(json.loads(content)), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON"}), 500

@users_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user_by_id(current_user, user_id):
    # Validate user_id to prevent path traversal
    if not user_id.startswith('U') or not user_id[1:].isdigit():
        return jsonify({"error": "Invalid user ID format"}), 400

    user, error = get_user_by_id_service(user_id)

    if error:
        return jsonify({"error": error["error"]}), 500

    return jsonify(user), 200

@users_bp.route('/<user_id>/submissions', methods=['GET'])
@token_required
def get_user_submissions(current_user, user_id):
    submissions, error = get_user_submissions_service(user_id)

    if error:
        return jsonify({"error": error["error"]}), 500

    return jsonify(submissions), 200

@users_bp.route('/<user_id>/solved', methods=['GET'])
@token_required
def get_solved_problems(current_user, user_id):
    # Validate user_id to prevent path traversal
    if not user_id.startswith('U') or not user_id[1:].isdigit():
        return jsonify({"error": "Invalid user ID format"}), 400

    # Authorization: Any authenticated user can view any other user's solved problems
    # No need to check current_user["user_id"] == user_id

    solved_problems, error = get_solved_problems_service(user_id)

    if error:
        return jsonify({"error": error["error"]}), 500

    return jsonify(solved_problems), 200

@users_bp.route('/<user_id>/update-profile', methods=['PUT'])
@token_required
def update_user_profile(current_user, user_id):
    # Validate user_id to prevent path traversal
    if not user_id.startswith('U') or not user_id[1:].isdigit():
        return jsonify({"error": "Invalid user ID format"}), 400

    # Authorization: Ensure the user is updating their own profile
    if current_user["user_id"] != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.get_json()
    new_name = data.get('name')
    new_username = data.get('username')
    new_bio = data.get('bio')

    # At least one field must be provided for update
    if new_name is None and new_username is None and new_bio is None:
        return jsonify({"error": "No fields provided for update (name, username, or bio)."}), 400

    success, error = update_user_profile_service(user_id, new_name, new_username, new_bio)

    if error:
        return jsonify({"error": error["error"]}), 500

    return jsonify({"message": "Profile updated successfully"}), 200
