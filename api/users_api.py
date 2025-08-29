from flask import Blueprint, jsonify, request
import json

from services.user_service import get_user_by_id as get_user_by_id_service, get_user_submissions as get_user_submissions_service
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
def get_user_by_id(user_id):
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
