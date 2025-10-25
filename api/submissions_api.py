from flask import Blueprint, jsonify
from services import submission_service

submissions_bp = Blueprint('submissions_bp', __name__)

@submissions_bp.route('/queue', methods=['GET'])
def get_submissions_queue():
    queue = submission_service.get_submissions_queue()
    return jsonify(queue)
