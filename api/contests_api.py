from flask import Blueprint, jsonify, request
import json
import os
from services import contest_service
from utils.jwt_token import validate_token
from functools import wraps

contests_api = Blueprint('contests_api', __name__)

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

@contests_api.route('/', methods=['GET'])
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

@contests_api.route('/<contest_id>', methods=['GET'])
@token_required
def get_contest(current_user, contest_id):
    contest_data, error = contest_service.get_contest_details(contest_id)
    if error:
        return jsonify(error), 404
    return jsonify(contest_data)
