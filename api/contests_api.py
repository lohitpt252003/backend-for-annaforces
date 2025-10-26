from flask import Blueprint, jsonify, request
import json
import os
from services import contest_service
from utils.jwt_token import validate_token
from functools import wraps
from datetime import datetime
import pytz

contests_bp = Blueprint('contests_bp', __name__)

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

@contests_bp.route('/', methods=['GET'])
@token_required
def get_contests(current_user):
    contests_metadata, error = contest_service.get_all_contests_metadata()
    if error:
        return jsonify(error), 404

    search_term = request.args.get('search', '').lower()
    filter_author = request.args.get('author', '').lower()

    filtered_contests = []
    for contest in contests_metadata:
        # Search filter
        if search_term and not (
            search_term in contest.get('name', '').lower() or
            search_term in contest.get('id', '').lower()
        ):
            continue

        # Author filter
        if filter_author and not any(author.lower() == filter_author for author in contest.get('authors', [])):
            continue

        filtered_contests.append(contest)

    return jsonify(filtered_contests)

@contests_bp.route('/<contest_id>', methods=['GET'])
@token_required
def get_contest(current_user, contest_id):
    contest_data, error = contest_service.get_contest_details(contest_id)
    if error:
        return jsonify(error), 404
    return jsonify(contest_data), 200

@contests_bp.route('/<contest_id>/meta', methods=['GET'])
@token_required
def get_contest_meta(current_user, contest_id):
    contest_meta, error = contest_service.get_contest_meta_from_mongo(contest_id)
    if error:
        return jsonify(error), 404
    return jsonify(contest_meta), 200

@contests_bp.route('/<contest_id>/is-registered', methods=['GET'])
@token_required
def check_contest_registration(current_user, contest_id):
    username = current_user['username']
    is_registered, error = contest_service.is_user_registered(contest_id, user_id)
    if error:
        return jsonify(error), 500
    return jsonify({"is_registered": is_registered}), 200

@contests_bp.route('/<contest_id>/register', methods=['POST'])
@token_required
def register_for_contest(current_user, contest_id):
    username = current_user['username']
    success, error = contest_service.register_user_for_contest(contest_id, username)
    if error:
        return jsonify(error), 500
    return jsonify({"message": "Successfully registered for the contest."}), 200


