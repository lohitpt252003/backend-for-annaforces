from flask import Blueprint, jsonify, request
import json

from services.github_services import get_file
from config.github_config import GITHUB_SUBMISSIONS_BASE_PATH
from api.problems_api import token_required

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