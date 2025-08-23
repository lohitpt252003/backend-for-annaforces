from flask import Blueprint, jsonify, request
import sys
import os
import json
import time


from services.github_services import get_file, get_folder_contents, add_file
from config.github_config import GITHUB_PROBLEMS_BASE_PATH

# Blueprint declaration
problems_bp = Blueprint("problems", __name__)

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
    pass

@problems_bp.route('/<problem_id>/submissions', methods=['GET'])
def get_problem_submissions(problem_id):
    pass

@problems_bp.route('/add', methods=['POST'])
def add_problem():
    pass