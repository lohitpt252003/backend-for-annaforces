from flask import Blueprint, jsonify, request
from services import user_service
from utils.jwt_token import validate_token
from functools import wraps

users_bp = Blueprint('users', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        result = validate_token(token)
        if not result['valid']:
            return jsonify({'message': result['error']}), 401

        current_user = result['data']
        return f(current_user, *args, **kwargs)
    return decorated

@users_bp.route('/<username>', methods=['GET'])
@token_required
def get_user(current_user, username):
    user, error = user_service.get_user_by_username(username)
    if error:
        return jsonify(error), 404
    return jsonify(user), 200

@users_bp.route('/<username>/update-profile', methods=['PUT'])
@token_required
def update_profile(current_user, username):
    data = request.get_json()
    name = data.get('name')
    new_username = data.get('username')
    bio = data.get('bio')

    if current_user['username'] != username:
        return jsonify({'message': 'You are not authorized to update this profile'}), 403

    result, error = user_service.update_user_profile(username, name, new_username, bio)
    if error:
        return jsonify(error), 500
    return jsonify(result), 200
