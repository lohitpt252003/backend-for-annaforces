import os, time, json
import sys
from flask import jsonify

from services.github_services import get_file, add_file, update_file

def add_submission_to_user(user_id, problem_id, result):
    verdict = result.get('overall_status', 'other')
    verdict = verdict.lower()
    content = json.dumps(
        {
            'timestamp' : str(int(time.time())),
            'result' : result
        }
    )

    # Changed path to include 'users'
    last_submission_path = f'data/users/{user_id}/{problem_id}/{verdict}/last_submission.txt'
    submission_content, submission_sha, error = get_file(last_submission_path)
    submission_no = 1
    if error and "not found" in error.get("message", "").lower(): # File not found
        add_file(last_submission_path, "1", f'added last_submission.txt')
    elif submission_content is not None: # File found
        # Ensure submission_content is a string before converting to int
        if isinstance(submission_content, bytes):
            submission_content = submission_content.decode('utf-8') # Decode bytes to string

        try:
            submission_no = int(submission_content) + 1
        except ValueError:
            print(f"Error: Content of {last_submission_path} is not a valid integer: '{submission_content}'")
            # Reset submission_no to 1 if content is invalid, or handle as appropriate
            submission_no = 1
        update_file(last_submission_path, str(submission_no), f'updated last_submission.txt')
    else: # Other error
        print(f"Error getting file {last_submission_path}: {error}")
        return # Or handle the error appropriately

    # Changed path to include 'users'
    filename_path = f'data/users/{user_id}/{problem_id}/{verdict}/{submission_no}.json'
    add_file(filename_path, content, f'submitted for {problem_id}')
    pass

def add_submission_to_problem(user_id, problem_id, result):
    verdict = result.get('overall_status', 'other')
    verdict = verdict.lower()
    content = json.dumps(
        {
            'timestamp' : str(int(time.time())),
            'result' : result
        }
    )

    # Changed path to include 'problems'
    last_submission_path = f'data/problems/{problem_id}/{user_id}/{verdict}/last_submission.txt'
    submission_content, submission_sha, error = get_file(last_submission_path)
    submission_no = 1
    if error and "not found" in error.get("message", "").lower(): # File not found
        add_file(last_submission_path, "1", f'added last_submission.txt')
    elif submission_content is not None: # File found
        # Ensure submission_content is a string before converting to int
        if isinstance(submission_content, bytes):
            submission_content = submission_content.decode('utf-8') # Decode bytes to string

        try:
            submission_no = int(submission_content) + 1
        except ValueError:
            print(f"Error: Content of {last_submission_path} is not a valid integer: '{submission_content}'")
            # Reset submission_no to 1 if content is invalid, or handle as appropriate
            submission_no = 1
        update_file(last_submission_path, str(submission_no), f'updated last_submission.txt')
    else: # Other error
        print(f"Error getting file {last_submission_path}: {error}")
        return # Or handle the error appropriately

    # Changed path to include 'problems'
    filename_path = f'data/problems/{problem_id}/{user_id}/{verdict}/{submission_no}.json'
    add_file(filename_path, content, f'submitted by {user_id}')
    pass

def update_problem_stats(user_id, problem_id, result):
    pass

def update_user_stats(user_id, problem_id, result):
    pass


def add_submission(problem_id, user_id, result):
    add_submission_to_user(user_id, problem_id, result)
    add_submission_to_problem(user_id, problem_id, result)
    pass