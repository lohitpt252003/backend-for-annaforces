from flask import Blueprint, jsonify, request
from services.user_service import (
    get_user_by_username as get_user_by_username_service,
    get_user_submissions as get_user_submissions_service,
    update_user_profile as update_user_profile_service,
    get_solved_problems as get_solved_problems_service
)
from extensions import mongo
from api.problems_api import token_required

users_bp = Blueprint("users", __name__)

@users_bp.route('/', methods=['GET'])
@token_required
def get_users(current_user):
    # Fetch all users from MongoDB, projecting only necessary fields
    users_cursor = mongo.db.users.find({}, {'_id': 0, 'username': 1, 'name': 1})
    users_list = list(users_cursor)
    return jsonify(users_list), 200

@users_bp.route('/<username>', methods=['GET'])
@token_required
def get_user_by_username(current_user, username):
    user, error = get_user_by_username_service(username)
    if error:
        return jsonify({"error": error["error"]}), 404
    
    # Don't return sensitive fields like email or password hash
    user.pop('_id', None)
    user.pop('email', None)
    return jsonify(user), 200

@users_bp.route('/<username>/submissions', methods=['GET'])
@token_required
def get_user_submissions(current_user, username):
    submissions, error = get_user_submissions_service(username)
    if error:
        return jsonify({"error": error["error"]}), 500

    submissions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return jsonify({
        'submissions': submissions,
        'total_submissions': len(submissions)
    }), 200

@users_bp.route('/<username>/solved', methods=['GET'])
@token_required
def get_solved_problems(current_user, username):
    solved_problems, error = get_solved_problems_service(username)
    if error:
        return jsonify({"error": error["error"]}), 500
    return jsonify(solved_problems), 200

@users_bp.route('/<username>/update-profile', methods=['PUT'])
@token_required
def update_user_profile(current_user, username):
    # Authorization: Ensure the user is updating their own profile
    if current_user['username'] != username:
        return jsonify({"error": "Unauthorized to update this profile"}), 403

    data = request.get_json()
    new_name = data.get('name')
    new_username = data.get('username')
    new_bio = data.get('bio')

    if new_name is None and new_username is None and new_bio is None:
        return jsonify({"error": "No fields provided for update."}), 400

    success, error = update_user_profile_service(username, new_name, new_username, new_bio)
    if not success:
        return jsonify({"error": error["error"]}), 500

    return jsonify({"message": "Profile updated successfully"}), 200

@users_bp.route('/<username>/problem-status', methods=['GET'])
@token_required
def get_user_problem_status(current_user, username):
    user_data, error = get_user_by_username_service(username)
    if error:
        return jsonify({"error": error["error"]}), 404

    problem_statuses = {}
    all_problem_ids = set()
    all_problem_ids.update(user_data.get('solved', {}).keys())
    all_problem_ids.update(user_data.get('not_solved', {}).keys())
    all_problem_ids.update(user_data.get('attempted', {}).keys())

    for problem_id in all_problem_ids:
        if problem_id in user_data.get('solved', {}):
            problem_statuses[problem_id] = "solved"
        elif problem_id in user_data.get('not_solved', {}):
            problem_statuses[problem_id] = "not_solved"
        else:
            problem_statuses[problem_id] = "not_attempted"

    return jsonify(problem_statuses), 200
