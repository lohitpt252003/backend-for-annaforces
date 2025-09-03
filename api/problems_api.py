import base64
from flask import Blueprint, jsonify, request
import sys
import os
import json
import time
import requests


from services.github_services import get_file, get_folder_contents, create_or_update_file
from services.submission_service import handle_new_submission
from services.problem_service import add_problem as add_problem_service
from config.github_config import GITHUB_PROBLEMS_BASE_PATH, GITHUB_USERS_BASE_PATH
from utils.jwt_token import validate_token
from functools import wraps

# Blueprint declaration
problems_bp = Blueprint("problems", __name__)

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

def update_meta_submissions(meta_path):
    content, _, error = get_file(meta_path)
    
    if error:
        # If file not found, create it
        if "not found" in error.get("message", "").lower():
            meta_data = {"number_of_submissions": 1}
            create_or_update_file(meta_path, json.dumps(meta_data, indent=4), commit_message=f"[AUTO] Create meta file for {meta_path}")
        return

    try:
        meta_data = json.loads(content)
        meta_data["number_of_submissions"] = meta_data.get("number_of_submissions", 0) + 1
        create_or_update_file(meta_path, json.dumps(meta_data, indent=4), commit_message=f"[AUTO] Update submission count for {meta_path}")
    except json.JSONDecodeError:
        # Handle case where file is empty or has invalid json
        meta_data = {"number_of_submissions": 1}
        create_or_update_file(meta_path, json.dumps(meta_data, indent=4), commit_message=f"[AUTO] Create meta file for {meta_path}")

@problems_bp.route('/', methods=['GET'])
@token_required
def get_problems(current_user):
    file_path = f"{GITHUB_PROBLEMS_BASE_PATH}/index.json"
    content, _, error = get_file(file_path)

    if error:
        return jsonify({"error": error["message"]}), 500

    try:
        return jsonify(json.loads(content)), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON"}), 500

@problems_bp.route('/<problem_id>', methods=['GET'])
@token_required
def get_problem_by_id(current_user, problem_id):
    problem_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}"
    meta_path = f"{problem_path}/meta.json"
    problem_md_path = f"{problem_path}/problem.md"
    index_file_path = f"{GITHUB_PROBLEMS_BASE_PATH}/index.json"

    meta_content, _, meta_error = get_file(meta_path)
    if meta_error:
        if "not found" in meta_error["message"].lower():
            return jsonify({"error": "Problem not found"}), 404
        return jsonify({"error": meta_error["message"]}), 500

    problem_md_content, _, problem_md_error = get_file(problem_md_path)
    if problem_md_error:
        return jsonify({"error": problem_md_error["message"]}), 500

    index_content, _, index_error = get_file(index_file_path)
    if index_error:
        return jsonify({"error": index_error["message"]}), 500

    try:
        meta_data = json.loads(meta_content)
        problem_index = json.loads(index_content)

        problem_info_from_index = problem_index.get(problem_id, {})
        meta_data['tags'] = problem_info_from_index.get('tags', [])
        meta_data['authors'] = problem_info_from_index.get('authors', [])
        meta_data['difficulty'] = problem_info_from_index.get('difficulty')
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON data"}), 500

    response_data = {
        "meta": meta_data,
        "problem_statement": problem_md_content
    }

    return jsonify(response_data), 200

@problems_bp.route('/<problem_id>/solution', methods=['GET'])
@token_required
def get_problem_solution(current_user, problem_id):
    solution_base_path = f"data/solutions/{problem_id}"
    
    solution_files = {
        "python": f"{solution_base_path}/solution.py",
        "cpp": f"{solution_base_path}/solution.cpp",
        "c": f"{solution_base_path}/solution.c",
        "markdown": f"{solution_base_path}/solution.md"
    }

    response_data = {}
    for lang, path in solution_files.items():
        content, _, error = get_file(path)
        if error and "not found" in error["message"].lower():
            response_data[lang] = None # File not found, set to None
        elif error:
            return jsonify({"error": f"Error fetching {lang} solution: {error['message']}"}), 500
        else:
            response_data[lang] = content

    # Check if at least one solution file was found, otherwise problem_id might be invalid
    if all(value is None for value in response_data.values()):
        return jsonify({"error": "Solution files not found for this problem_id"}), 404

    return jsonify(response_data), 200

@problems_bp.route('/<problem_id>/submit', methods=['POST'])
@token_required
def submit_problem(current_user, problem_id):
    data = request.get_json()
    user_id = current_user['user_id']
    language = data.get('language')
    code = data.get('code')
    is_base64_encoded = data.get('is_base64_encoded', False)

    if is_base64_encoded:
        try:
            code = base64.b64decode(code).decode('utf-8')
        except (UnicodeDecodeError, base64.binascii.Error):
            return jsonify({"error": "Invalid base64 encoded code"}), 400

    if not all([language, code]):
        return jsonify({"error": "Missing language or code in request body"}), 400

    result = handle_new_submission(problem_id, user_id, language, code)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500
    
    user_meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    problem_meta_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/meta.json"

    update_meta_submissions(user_meta_path)
    update_meta_submissions(problem_meta_path)
    
    return jsonify(result), 200

@problems_bp.route('/<problem_id>/submissions', methods=['GET'])
@token_required
def get_problem_submissions(current_user, problem_id):
    submissions_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/submissions"
    
    folder_contents_response = get_folder_contents(submissions_path)

    if not folder_contents_response.get("success"):
        return jsonify({"error": folder_contents_response.get("error", "Failed to get submissions")}), 500

    submissions = []
    for item in folder_contents_response["data"]:
        if item['type'] == 'file' and item['name'].endswith(".json"):
            try:
                file_content_resp = requests.get(item['download_url'])
                if file_content_resp.status_code == 200:
                    submissions.append(json.loads(file_content_resp.text))
                else:
                    print(f"Error fetching content for {item['path']}: HTTP {file_content_resp.status_code}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON for {item['path']}")
                continue

    return jsonify(submissions), 200

# @problems_bp.route('/add', methods=['POST'])
# def add_problem():
#     problem_data = request.get_json()
#     result = add_problem_service(problem_data)

#     if "error" in result:
#         error_message = result["error"]
#         if "Missing required field" in error_message or \
#            "Testcases must be" in error_message or \
#            "is missing 'input' or 'output'" in error_message or \
#            "has empty 'input' or 'output'" in error_message or \
#            "cannot be empty" in error_message or \
#            "Missing required section in problem.md" in error_message:
#             return jsonify({"error": error_message}), 400
#         print(f'problems_api.py {error_message}')
#         return jsonify({"error": error_message}), 500

#     return jsonify(result), 201