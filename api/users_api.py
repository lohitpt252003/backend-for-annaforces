from flask import Blueprint, jsonify, request
import json

from services.user_service import get_user_by_id as get_user_by_id_service, get_user_submissions as get_user_submissions_service, update_user_profile as update_user_profile_service, get_solved_problems as get_solved_problems_service
from services import contest_service
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

    # Sort submissions by timestamp in descending order (newest first)
    submissions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return jsonify({
        'submissions': submissions,
        'total_submissions': len(submissions)
    }), 200

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

@users_bp.route('/<user_id>/username', methods=['GET'])
@token_required
def get_username_by_id(current_user, user_id):
    # Validate user_id to prevent path traversal
    if not user_id.startswith('U') or not user_id[1:].isdigit():
        return jsonify({"error": "Invalid user ID format"}), 400

    user, error = get_user_by_id_service(user_id)

    if error:
        return jsonify({"error": error["error"]}), 500

    if user and "username" in user:
        return jsonify({"username": user["username"]}), 200
    else:
        return jsonify({"error": "Username not found for the given user ID"}), 404

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

@users_bp.route('/<user_id>/problem-status', methods=['GET'])
@token_required
def get_user_problem_status(current_user, user_id):
    # Validate user_id to prevent path traversal
    if not user_id.startswith('U') or not user_id[1:].isdigit():
        return jsonify({"error": "Invalid user ID format"}), 400

    # Authorization: Any authenticated user can view any other user's problem status

    user_meta, error = get_user_by_id_service(user_id)

    if error:
        return jsonify({"error": error["error"]}), 500

    problem_statuses = {}
    # Combine all problems from solved, not_solved, and attempted
    all_problem_ids = set()
    all_problem_ids.update(user_meta.get('solved', {}).keys())
    all_problem_ids.update(user_meta.get('not_solved', {}).keys())
    all_problem_ids.update(user_meta.get('attempted', {}).keys())

    for problem_id in all_problem_ids:
        if problem_id in user_meta.get('solved', {}):
            problem_statuses[problem_id] = "solved"
        elif problem_id in user_meta.get('not_solved', {}):
            problem_statuses[problem_id] = "not_solved"
        else:
            problem_statuses[problem_id] = "not_attempted" # Should not happen if logic is correct, but as a fallback

    return jsonify(problem_statuses), 200

@users_bp.route('/<user_id>/contests', methods=['GET'])
@token_required
def get_user_contests(current_user, user_id):
    # Validate user_id to prevent path traversal
    if not user_id.startswith('U') or not user_id[1:].isdigit():
        return jsonify({"error": "Invalid user ID format"}), 400

    # Authorization: Any authenticated user can view any other user's contest participation

    contests_participated = []
    all_contests, error = contest_service.get_all_contests_metadata()

    if error:
        return jsonify({"error": error["error"]}), 500

    for contest in all_contests:
        is_registered, reg_error = contest_service.is_user_registered(contest['id'], user_id)
        if reg_error:
            print(f"Error checking registration for contest {contest['id']}: {reg_error['error']}")
            continue
        if is_registered:
            contests_participated.append(contest['id'])

    return jsonify(contests_participated), 200
