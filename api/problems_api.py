import base64
from flask import Blueprint, jsonify, request
import sys
import os
import json
import time
import requests
from datetime import datetime
import pytz

from services.github_services import get_file, get_folder_contents, create_or_update_file
from services.submission_service import handle_new_submission
from services.problem_service import add_problem as add_problem_service
from services import contest_service
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
    search_term = request.args.get('search', '').lower()
    filter_difficulty = request.args.get('difficulty', '').lower()
    filter_tag = request.args.get('tag', '').lower()

    file_path = f"{GITHUB_PROBLEMS_BASE_PATH}/index.json"
    content, _, error = get_file(file_path)

    if error:
        return jsonify({"error": error["message"]}), 500

    try:
        problems_data = json.loads(content)
        all_problems_list = list(problems_data.items())

        # Apply filters
        filtered_problems = []
        for problem_id, problem_info in all_problems_list:
            # Search filter
            if search_term and not (
                search_term in problem_info.get('title', '').lower() or
                search_term in problem_id.lower()
            ):
                continue

            # Difficulty filter
            if filter_difficulty and problem_info.get('difficulty', '').lower() != filter_difficulty:
                continue

            # Tag filter
            if filter_tag and not any(tag.lower() == filter_tag for tag in problem_info.get('tags', [])):
                continue

            filtered_problems.append((problem_id, problem_info))

        total_problems = len(filtered_problems)
        
        return jsonify({
            'problems': dict(filtered_problems),
            'total_problems': total_problems
        }), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON"}), 500

@problems_bp.route('/<problem_id>', methods=['GET'])
@token_required
def get_problem_by_id(current_user, problem_id):
    problem_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}"
    meta_path = f"{problem_path}/meta.json"
    index_file_path = f"{GITHUB_PROBLEMS_BASE_PATH}/index.json"

    meta_content, _, meta_error = get_file(meta_path)
    if meta_error:
        if "not found" in meta_error["message"].lower():
            return jsonify({"error": "Problem not found"}), 404
        return jsonify({"error": meta_error["message"]}), 500

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

        # Check if problem belongs to an upcoming contest
        contest_id = meta_data.get('contest_id')
        if contest_id:
            contest_details, contest_details_error = contest_service.get_contest_details(contest_id)
            if not contest_details_error and contest_details:
                start_time = datetime.fromisoformat(contest_details['startTime'].replace('Z', '+00:00'))
                current_time = datetime.now(pytz.UTC)
            
                if current_time < start_time:
                    contest_name = contest_details.get('name', 'Unnamed Contest')
                    return jsonify({"status": "not_started", "message": f"The contest '{contest_name}' has not started yet and the problem won't be revealed now."}), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON data"}), 500

    header_path = f"{problem_path}/details/header.md"
    description_path = f"{problem_path}/details/description.md"
    input_path = f"{problem_path}/details/input.md"
    output_path = f"{problem_path}/details/output.md"
    notes_path = f"{problem_path}/details/notes.md"
    constraints_path = f"{problem_path}/details/constraints.md"
    samples_dir_path = f"{problem_path}/details/samples"

    header_content, _, header_error = get_file(header_path)
    description_content, _, description_error = get_file(description_path)
    input_content, _, input_error = get_file(input_path)
    output_content, _, output_error = get_file(output_path)
    notes_content, _, notes_error = get_file(notes_path)
    constraints_content, _, constraints_error = get_file(constraints_path)

    # Handle optional files (header.md, notes.md)
    if header_error and "not found" in header_error["message"].lower():
        header_content = ""
        header_error = None
    if notes_error and "not found" in notes_error["message"].lower():
        notes_content = ""
        notes_error = None

    # Check for errors in reading main problem files
    for err in [header_error, description_error, input_error, output_error, notes_error, constraints_error]:
        if err:
            if "not found" in err["message"].lower():
                return jsonify({"error": "Problem content not found"}), 404
            return jsonify({"error": err["message"]}), 500
    # Read samples
    samples_data = []
    samples_folder_contents, samples_folder_error = get_folder_contents(samples_dir_path)

    if samples_folder_error:
        # If samples folder not found, it might be an old problem or no samples, so proceed without samples
        if "not found" not in samples_folder_error["message"].lower():
            return jsonify({"error": samples_folder_error["message"]}), 500
    else:
        # Filter for directories (each representing a sample)
        sample_dirs = [item for item in samples_folder_contents["data"] if item['type'] == 'dir']
        
        # Sort sample directories by name (e.g., sample1, sample2)
        sample_dirs.sort(key=lambda x: int(x['name'].replace('sample', '')) if x['name'].startswith('sample') and x['name'].replace('sample', '').isdigit() else float('inf'))

        for sample_dir in sample_dirs:
            sample_input_path = f"{samples_dir_path}/{sample_dir['name']}/input.md"
            sample_output_path = f"{samples_dir_path}/{sample_dir['name']}/output.md"
            sample_description_path = f"{samples_dir_path}/{sample_dir['name']}/description.md"

            sample_input_content, _, sample_input_error = get_file(sample_input_path)
            sample_output_content, _, sample_output_error = get_file(sample_output_path)
            sample_description_content, _, sample_description_error = get_file(sample_description_path)

            # Handle errors for sample files (e.g., if a sample file is missing, treat it as empty)
            samples_data.append({
                "input": sample_input_content if not sample_input_error else "",
                "output": sample_output_content if not sample_output_error else "",
                "description": sample_description_content if not sample_description_error else ""
            })

    problem_data = {
        "meta": meta_data,
        "header_content": header_content,
        "description_content": description_content,
        "input_content": input_content,
        "output_content": output_content,
        "notes_content": notes_content,
        "constraints_content": constraints_content,
        "samples_data": samples_data,
        "has_pdf_statement": False
    }

    pdf_path = f"{problem_path}/problem.pdf"
    _, _, pdf_error = get_file(pdf_path)
    if not pdf_error:
        problem_data["has_pdf_statement"] = True

    return jsonify({"status": "started", "data": problem_data}), 200

@problems_bp.route('/<problem_id>/meta', methods=['GET'])
@token_required
def get_problem_meta_by_id(current_user, problem_id):
    problem_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}"
    meta_path = f"{problem_path}/meta.json"
    index_file_path = f"{GITHUB_PROBLEMS_BASE_PATH}/index.json"

    meta_content, _, meta_error = get_file(meta_path)
    if meta_error:
        if "not found" in meta_error["message"].lower():
            return jsonify({"error": "Problem meta not found"}), 404
        return jsonify({"error": meta_error["message"]}), 500

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

        return jsonify(meta_data), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode JSON"}), 500


@problems_bp.route('/<problem_id>/solution', methods=['GET'])
@token_required
def get_problem_solution(current_user, problem_id):
    # Check if problem belongs to a running or scheduled contest
    problem_meta_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/meta.json"
    problem_meta_content, _, problem_meta_error = get_file(problem_meta_path)

    if not problem_meta_error:
        try:
            problem_meta_data = json.loads(problem_meta_content)
            contest_id = problem_meta_data.get('contest_id')

            if contest_id:
                contest_details, contest_details_error = contest_service.get_contest_details(contest_id)

                if not contest_details_error and contest_details:
                    end_time = datetime.fromisoformat(contest_details['endTime'].replace('Z', '+00:00'))
                    current_time = datetime.now(pytz.UTC)

                    if current_time < end_time: # Contest is running or scheduled
                        return jsonify({"status": "not_available", "message": "Solutions are not available for problems in a running or scheduled contest."}), 200
        except json.JSONDecodeError:
            pass # Ignore if problem meta is invalid

    solution_base_path = f"data/solutions/{problem_id}"
    
    solution_files = {
        "python": f"{solution_base_path}/solution.py",
        "cpp": f"{solution_base_path}/solution.cpp",
        "c": f"{solution_base_path}/solution.c",
        "markdown": f"{solution_base_path}/solution.md"
    }

    solution_data = {}
    for lang, path in solution_files.items():
        content, _, error = get_file(path)
        if error and "not found" in error["message"].lower():
            solution_data[lang] = None # File not found, set to None
        elif error:
            return jsonify({"error": f"Error fetching {lang} solution: {error['message']}"}), 500
        else:
            solution_data[lang] = content

    # Check if at least one solution file was found, otherwise problem_id might be invalid
    if all(value is None for value in solution_data.values()):
        return jsonify({"error": "Solution files not found for this problem_id"}), 404

    solution_data["has_pdf_solution"] = False
    pdf_path = f"{solution_base_path}/solution.pdf"
    _, _, pdf_error = get_file(pdf_path)
    if not pdf_error:
        solution_data["has_pdf_solution"] = True

    return jsonify({"status": "available", "data": solution_data}), 200

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

    language = data.get('language')
    if language and language.lower() == 'cpp':
        language = 'c++'

    supported_languages = ["python", "c", "c++"]
    if not language or language.lower() not in supported_languages:
        return jsonify({"error": f"Unsupported language: {language}. Supported languages are {', '.join(supported_languages)}"}), 400

    # Check if problem belongs to an active contest and if user is registered
    problem_meta_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/meta.json"
    problem_meta_content, _, problem_meta_error = get_file(problem_meta_path)

    if not problem_meta_error:
        try:
            problem_meta_data = json.loads(problem_meta_content)
            contest_id = problem_meta_data.get('contest_id')

            if contest_id:
                contest_details, contest_details_error = contest_service.get_contest_details(contest_id)

                if not contest_details_error and contest_details:
                    start_time = datetime.fromisoformat(contest_details['startTime'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(contest_details['endTime'].replace('Z', '+00:00'))
                    current_time = datetime.now(pytz.UTC)

                    if start_time <= current_time <= end_time: # Contest is running
                        is_registered, reg_error = contest_service.is_user_registered(contest_id, user_id)
                        if reg_error:
                            print(f"Error checking registration for contest {contest_id}: {reg_error['error']}")
                            return jsonify({"error": "Failed to check contest registration status."}), 500
                        
                        if not is_registered:
                            return jsonify({"error": "You must be registered for this contest to submit solutions."}), 403
        except json.JSONDecodeError:
            print(f"Error decoding problem meta.json for {problem_id}")

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
    
    response, error = get_folder_contents(submissions_path)

    if not response.get("success"):
        if "404" in response.get("error", "") or "not found" in response.get("error", "").lower():
            return jsonify({'submissions': [], 'total_submissions': 0}), 200
        return jsonify({"error": response.get("error", "Failed to get submissions")}), 500

    all_submissions = []
    for item in response["data"]:
        if item['type'] == 'file' and item['name'].endswith(".json"):
            try:
                # For local files, download_url will be a local path (file:///...)
                # For GitHub files, it will be a raw URL
                if item['download_url'].startswith('file:///'):
                    # Read local file directly
                    local_file_path = item['download_url'][len('file:///'):]
                    with open(local_file_path, 'r', encoding='utf-8') as f:
                        all_submissions.append(json.loads(f.read()))
                else:
                    # Fetch from URL for GitHub files
                    file_content_resp = requests.get(item['download_url'])
                    if file_content_resp.status_code == 200:
                        all_submissions.append(json.loads(file_content_resp.text))
                    else:
                        print(f"Error fetching content for {item['path']}: HTTP {file_content_resp.status_code}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON for {item['path']}")
                continue

    # Sort submissions by timestamp in descending order (newest first)
    all_submissions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return jsonify({
        'submissions': all_submissions,
        'total_submissions': len(all_submissions)
    }), 200


@problems_bp.route('/<problem_id>/statement.pdf', methods=['GET'])
@token_required
def get_problem_statement_pdf(current_user, problem_id):
    pdf_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/problem.pdf"
    pdf_content, _, pdf_error = get_file(pdf_path)

    if pdf_error:
        if "not found" in pdf_error["message"].lower():
            return jsonify({"error": "PDF statement not found"}), 404
        return jsonify({"error": pdf_error["message"]}), 500

    # pdf_content is in bytes, encode it to base64 string to be able to jsonify it
    pdf_data_base64 = base64.b64encode(pdf_content).decode('utf-8')

    return jsonify({"pdf_data": pdf_data_base64})

@problems_bp.route('/<problem_id>/solution.pdf', methods=['GET'])
@token_required
def get_problem_solution_pdf(current_user, problem_id):
    pdf_path = f"data/solutions/{problem_id}/solution.pdf"
    pdf_content, _, pdf_error = get_file(pdf_path)

    if pdf_error:
        if "not found" in pdf_error["message"].lower():
            return jsonify({"error": "PDF solution not found"}), 404
        return jsonify({"error": pdf_error["message"]}), 500

    pdf_data_base64 = base64.b64encode(pdf_content).decode('utf-8')

    return jsonify({"pdf_data": pdf_data_base64})

