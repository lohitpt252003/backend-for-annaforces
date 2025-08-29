import base64
from flask import Blueprint, jsonify, request
import sys
import os
import json
import time


from services.github_services import get_file, get_folder_contents, create_or_update_file
from services.submission_service import handle_new_submission
from services.problem_service import add_problem as add_problem_service
from config.github_config import GITHUB_PROBLEMS_BASE_PATH, GITHUB_USERS_BASE_PATH

# Blueprint declaration
problems_bp = Blueprint("problems", __name__)

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
def get_problems():
    file_path = f"{GITHUB_PROBLEMS_BASE_PATH}/index.json"
    content, _, error = get_file(file_path)

    if error:
        return jsonify({"error": error["message"]}), 500

    try:
        return jsonify(json.loads(content)), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON"}), 500

@problems_bp.route('/<problem_id>', methods=['GET'])
def get_problem_by_id(problem_id):
    problem_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}"
    meta_path = f"{problem_path}/meta.json"
    problem_md_path = f"{problem_path}/problem.md"

    meta_content, _, meta_error = get_file(meta_path)
    if meta_error:
        return jsonify({"error": meta_error["message"]}), 500

    problem_md_content, _, problem_md_error = get_file(problem_md_path)
    if problem_md_error:
        return jsonify({"error": problem_md_error["message"]}), 500

    try:
        meta_data = json.loads(meta_content)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode meta.json"}), 500

    response_data = {
        "meta": meta_data,
        "problem_statement": problem_md_content
    }

    return jsonify(response_data), 200

@problems_bp.route('/<problem_id>/submit', methods=['POST'])
def submit_problem(problem_id):
    data = request.get_json()
    user_id = data.get('user_id')
    language = data.get('language')
    code = data.get('code')
    is_base64_encoded = data.get('is_base64_encoded', False)

    if is_base64_encoded:
        try:
            code = base64.b64decode(code).decode('utf-8')
        except (UnicodeDecodeError, base64.binascii.Error):
            return jsonify({"error": "Invalid base64 encoded code"}), 400

    if not all([user_id, language, code]):
        return jsonify({"error": "Missing user_id, language, or code in request body"}), 400

    result = handle_new_submission(problem_id, user_id, language, code)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500
    
    # Update user and problem meta data
    user_meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    problem_meta_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/meta.json"

    update_meta_submissions(user_meta_path)
    update_meta_submissions(problem_meta_path)
    
    return jsonify(result), 200

@problems_bp.route('/<problem_id>/submissions', methods=['GET'])
def get_problem_submissions(problem_id):
    submissions_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/submissions"
    
    folder_contents = get_folder_contents(submissions_path)

    if not folder_contents.get("success"):
        return jsonify({"error": folder_contents.get("error", "Failed to get submissions")}), 500

    submissions = []
    for file_path, content in folder_contents["data"].items():
        if file_path.endswith(".json"):
            try:
                submissions.append(json.loads(content))
            except json.JSONDecodeError:
                print(f"Error decoding JSON for {file_path}")
                continue

    return jsonify(submissions), 200

@problems_bp.route('/add', methods=['POST'])
def add_problem():
    problem_data = request.get_json()
    result = add_problem_service(problem_data)

    if "error" in result:
        error_message = result["error"]
        if "Missing required field" in error_message or \
           "Testcases must be" in error_message or \
           "is missing 'input' or 'output'" in error_message or \
           "has empty 'input' or 'output'" in error_message or \
           "cannot be empty" in error_message or \
           "Missing required section in problem.md" in error_message:
            return jsonify({"error": error_message}), 400
        print(f'problems_api.py {error_message}')
        return jsonify({"error": error_message}), 500

    return jsonify(result), 201
