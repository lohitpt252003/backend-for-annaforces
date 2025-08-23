from flask import Blueprint, jsonify, request
import sys
import os
import json
import time

from utils.jwt_token import validate_token
from services.github_services import get_file, get_folder_contents
from config.github_config import GITHUB_PROBLEMS_BASE_PATH, GITHUB_PROBLEMS_SUBMISSIONS_BASE_PATH
from services.judge_service import grade_submission
from services.submission_service import add_submission, get_problem_submissions

# Blueprint declaration
problems_bp = Blueprint("problems", __name__)

@problems_bp.route('/', methods=['GET'])
def get_problems():
    content, _, error = get_file('data/problem_list.json')
    if error:
        return jsonify({"error": error["message"]}), 404
    try:
        problems_json = json.loads(content)
        return jsonify(problems_json)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode problem list data."}), 500

@problems_bp.route('/<problem_id>', methods=['GET'])
def get_problem_by_id(problem_id):
    file_path = f'{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/problem.json'
    content, _, error = get_file(file_path)
    if error:
        return jsonify({"error": error["message"]}), 404
    try:
        problem_json = json.loads(content)
        return jsonify(problem_json)
    except json.JSONDecodeError:
        return jsonify({"error": f"Failed to decode problem data for problem id {problem_id}."}), 500

@problems_bp.route('/<id>/submit', methods=['POST'])
def submit_problem(id):
    """
    Handles a code submission for a specific problem by a user.
    """
    data = request.get_json()
    if not data or 'code' not in data or 'language' not in data:
        return jsonify({"error": "Missing required fields: code and language"}), 400

    code = data['code']
    language = data['language']
    problem_id = id
    user_id = data['user_id']

    result = grade_submission(code, language, problem_id)
    
    add = add_submission(problem_id, user_id, result)

    return jsonify(result)

@problems_bp.route('/<id>/submissions', methods=['GET'])
def get_problem_submissions(id):
    """
    Fetches all submissions for a specific problem.
    """
    submissions = get_problem_submissions(id)

    return jsonify(submissions)    