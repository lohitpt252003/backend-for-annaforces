from flask import Blueprint, request, jsonify
import sys, os
import json

# Step 1: Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Step 2: Import service
from services.github_services import get_file, add_file, update_file

# Step 3: Blueprint declaration
problems_bp = Blueprint("problems", __name__)

# Step 4: Flask route function
@problems_bp.route('/', methods=['GET'])
def get_problems():
    file_obj = get_file('data/problem_list.json')[0]
    if not file_obj:
        return jsonify({
            "message": f"file data/problem_list.json not found"
        })
    problems_json = json.loads(file_obj)
    return problems_json

@problems_bp.route('/<id>', methods=['GET'])
def get_problem(id):
    file_obj = get_file(f'data/problems/{id}/problem.json')[0]
    if not file_obj:
        return jsonify({
            "message": f"Problem with id {id} not found"
        })
    problem_json = json.loads(file_obj)
    return problem_json

# New API endpoint to get all submissions for a particular problem ID from GitHub
@problems_bp.route('/<int:problem_id>/submissions', methods=['GET'])
def get_all_submissions_for_problem(problem_id):
    """
    Retrieves all submission files for a given problem ID from GitHub.
    Iterates from 1.json up to last_submission.json.
    """
    print("FUNC IS CALLED")
    submissions_data = []
    last_submission_path = f'data/problems/{problem_id}/submissions/last_submission.txt'
    last_submission_content, _, error = get_file(last_submission_path)

    if error:
        # Handle case where last_submission.txt is not found or error occurs
        return jsonify({"message": f"Could not retrieve last_submission.txt: {error.get('message', 'Unknown error')}"}), 404

    try:
        last_submission_number = int(last_submission_content.strip())
    except ValueError:
        return jsonify({"message": "Invalid content in last_submission.txt"}), 500

    for i in range(1, last_submission_number + 1):
        submission_file_path = f'data/problems/{problem_id}/submissions/{i}.json'
        submission_content, _, file_error = get_file(submission_file_path)
        # print(submission_content)
        # print(get_file(submission_file_path))

        # if file_error:
        #     print(f"Warning: Could not retrieve {submission_file_path}: {file_error.get('message', 'Unknown error')}")
        #     continue # Skip this file and try the next one

        try:
            submission = json.loads(submission_content)
            submissions_data.append(submission)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not decode JSON from {submission_file_path}: {e}")
            submissions_data.append({
                "id": f"error-{i}",
                "problem_id": problem_id,
                "status": "Error: Invalid JSON",
                "message": f"Could not decode JSON from file: {submission_file_path}. Error: {e}"
            })
            continue # Continue to the next file

    return jsonify(submissions_data), 200


@problems_bp.route('/add_problem', methods=['POST'])
def add_problem():
    pass
    # data = request.get_json()
    # id = data["id"]
    # file_path = f'data/problems/{id}/problem.json'
    # file_content = json.dumps(data, indent=2)
    # commit_message = f"Added problem {id}"
    # add_file(file_path, file_content, commit_message, 1)
    # return {"message": "Problem added"}

@problems_bp.route('/update_problem', methods=['POST'])
def update_problem():
    pass
    # data = request.get_json()
    # id = data["id"]
    # file_path = f'data/problems/{id}/problem.json'
    # file_content = json.dumps(data, indent=2)
    # commit_message = f"Updated problem {id}"
    # update_file(file_path, file_content, commit_message, 1)
    # return {"message": "Problem updated"}