from flask import Blueprint, request, jsonify
import sys, os
import json
from functools import wraps
from utils.jwt_token import validate_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = validate_token(token)
            if not data['valid']:
                return jsonify({'message': data['error']}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

# Step 1: Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Step 2: Import service
from services.github_services import get_file, add_file, update_file

# Step 3: Blueprint declaration
submissions_bp = Blueprint("submissions", __name__)

@submissions_bp.route('/add_submission', methods=['POST'])
@token_required
def add_submission():
    data = request.get_json()
    problem_id = data["problem_id"]
    
    # Get the last submission number
    last_submission_path = f'data/problems/{problem_id}/submissions/last_submission.txt'
    last_submission_content, _, error = get_file(last_submission_path)
    
    if error:
        # If the file doesn't exist, this is the first submission
        last_submission_number = 0
    else:
        try:
            last_submission_number = int(last_submission_content.strip())
        except ValueError:
            return jsonify({"message": "Invalid content in last_submission.txt"}), 500
            
    new_submission_number = last_submission_number + 1
    
    # Create the new submission file
    submission_file_path = f'data/problems/{problem_id}/submissions/{new_submission_number}.json'
    submission_content = json.dumps(data, indent=2)
    commit_message = f"Added submission {new_submission_number} for problem {problem_id}"
    add_file(submission_file_path, submission_content, commit_message)
    
    # Update the last submission number
    update_file(last_submission_path, str(new_submission_number), f"Updated last submission number for problem {problem_id}")
    
    return jsonify({"message": "Submission added successfully"}), 200

@submissions_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user_submissions(user_id):
    all_submissions = []
    problem_list_content, _, error = get_file('data/problem_list.json')
    if error:
        return jsonify({"message": "Could not retrieve problem list"}), 500
        
    problem_list = json.loads(problem_list_content)
    
    for problem in problem_list:
        problem_id = problem['id']
        last_submission_path = f'data/problems/{problem_id}/submissions/last_submission.txt'
        last_submission_content, _, error = get_file(last_submission_path)
        
        if error:
            continue
            
        try:
            last_submission_number = int(last_submission_content.strip())
        except ValueError:
            continue
            
        for i in range(1, last_submission_number + 1):
            submission_file_path = f'data/problems/{problem_id}/submissions/{i}.json'
            submission_content, _, file_error = get_file(submission_file_path)
            
            if file_error:
                continue
                
            try:
                submission = json.loads(submission_content)
                if submission.get('user_id') == user_id:
                    all_submissions.append(submission)
            except json.JSONDecodeError:
                continue
                
    return jsonify(all_submissions), 200