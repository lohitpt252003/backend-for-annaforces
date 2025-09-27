from flask import Blueprint, jsonify, request
import json

from services.github_services import get_file
from config.github_config import GITHUB_SUBMISSIONS_BASE_PATH
from api.problems_api import token_required
from datetime import datetime
import pytz
from services import contest_service
from config.github_config import GITHUB_PROBLEMS_BASE_PATH

# Blueprint declaration
submissions_bp = Blueprint("submissions", __name__)

@submissions_bp.route('/<submission_id>', methods=['GET'])
@token_required
def get_submission_by_id(current_user, submission_id):
    # Validate submission_id to prevent path traversal
    if not submission_id.startswith('S') or not submission_id[1:].isdigit():
        return jsonify({"error": "Invalid submission ID format"}), 400

    submission_meta_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/{submission_id}/meta.json"
    
    meta_content, _, meta_error = get_file(submission_meta_path)

    if meta_error:
        if "not found" in meta_error["message"].lower():
            return jsonify({"error": "Submission not found"}), 404
        return jsonify({"error": meta_error["message"]}), 500

    try:
        submission_data = json.loads(meta_content)

        problem_id = submission_data.get("problem_id")
        submission_user_id = submission_data.get("user_id")

        if problem_id:
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
                                if current_user['user_id'] != submission_user_id:
                                    return jsonify({"error": "You are not allowed to see the submission of the other user during the contest."}), 403
                except json.JSONDecodeError:
                    pass # Ignore if problem meta is invalid
        
        language = submission_data.get('language')
        if not language:
            return jsonify({"error": "Language not found in submission metadata"}), 500

        language_extensions = {
            "python": "py",
            "c": "c",
            "c++": "cpp"
        }
        extension = language_extensions.get(language.lower())

        if not extension:
            return jsonify({"error": f"Unsupported language: {language}"}), 500

        code_file_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/{submission_id}/code.{extension}"
        code_content, _, code_error = get_file(code_file_path)

        if code_error:
            return jsonify({"error": code_error["message"]}), 500

        submission_data['code'] = code_content
        submission_data['language'] = language

        return jsonify(submission_data), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode submission metadata"}), 500