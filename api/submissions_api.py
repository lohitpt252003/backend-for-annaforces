from flask import Blueprint, jsonify
from services import submission_service
from extensions import mongo

submissions_bp = Blueprint('submissions_bp', __name__)

@submissions_bp.route('/queue', methods=['GET'])
def get_submissions_queue():
    queue = submission_service.get_submissions_queue()
    return jsonify(queue)

@submissions_bp.route('/<submission_id>', methods=['GET'])
def get_submission_by_id(submission_id):
    submission = mongo.db.submissions.find_one({"submission_id": submission_id}, {'_id': 0})
    if submission:
        return jsonify(submission), 200
    return jsonify({"message": "Submission not found"}), 404
