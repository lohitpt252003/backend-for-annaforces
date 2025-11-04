from flask import Blueprint, jsonify
from services import submission_service
from extensions import mongo
from services.github_services import get_file
from config.github_config import GITHUB_SUBMISSIONS_BASE_PATH
import json

submissions_bp = Blueprint('submissions_bp', __name__)

@submissions_bp.route('/queue', methods=['GET'])
def get_submissions_queue():
    queue = submission_service.get_submissions_queue()
    return jsonify(queue)

@submissions_bp.route('/<submission_id>', methods=['GET'])
def get_submission_by_id(submission_id):
    submission_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/{submission_id}/meta.json"
    submission_content, _, error = get_file(submission_path)

    if error:
        return jsonify({"message": "Submission not found"}), 404

    try:
        submission_data = json.loads(submission_content)
        return jsonify(submission_data), 200
    except (json.JSONDecodeError, TypeError):
        return jsonify({"message": "Failed to decode submission data"}), 500
