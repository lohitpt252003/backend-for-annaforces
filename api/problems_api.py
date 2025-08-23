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
    problem_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}"
    meta_path = f"{problem_path}/meta.json"

    meta_content, _, meta_error = get_file(meta_path)
    if meta_error:
        return jsonify({"error": meta_error["message"]}), 500

    try:
        meta_data = json.loads(meta_content)
        num_submissions = meta_data.get("number_of_submissions")
        if num_submissions is None:
            return jsonify({"error": "number_of_submissions not found in meta.json"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode meta.json"}), 500

    submissions = []
    for i in range(1, num_submissions + 1):
        submission_file_path = f"{problem_path}/submissions/S{i}.json"
        content, _, error = get_file(submission_file_path)
        if error:
            print(f"Error fetching {submission_file_path}: {error['message']}")
            continue
        try:
            submissions.append(json.loads(content))
        except json.JSONDecodeError:
            print(f"Error decoding JSON for {submission_file_path}")
            continue

    return jsonify(submissions), 200

@problems_bp.route('/add', methods=['POST'])
def add_problem():
    pass