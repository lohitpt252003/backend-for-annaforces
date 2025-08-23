import os, time, json
import sys


from services.github_services import get_file, add_file, update_file, get_folder_contents
from config.github_config import GITHUB_PROBLEMS_SUBMISSIONS_BASE_PATH

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
    last_submission_path = f'data/users/{user_id}/{problem_id}/submissions/{verdict}/last_submission.txt'
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
    filename_path = f'data/users/{user_id}/{problem_id}/submissions/{verdict}/{submission_no}.json'
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
    last_submission_path = f'data/problems/{problem_id}/submissions/{user_id}/{verdict}/last_submission.txt'
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
    filename_path = f'data/problems/{problem_id}/submissions/{user_id}/{verdict}/{submission_no}.json'
    add_file(filename_path, content, f'submitted by {user_id}')
    pass

def update_problem_stats(user_id, problem_id, result):
    pass

def update_user_stats(user_id, problem_id, result):
    pass

def get_problem_submissions(problem_id):
    path = f'{GITHUB_PROBLEMS_SUBMISSIONS_BASE_PATH}/{problem_id}/submissions'
    contents = get_folder_contents(path)
    print(path)
    print(contents)

    if not contents['success']:
        return {"error": contents['error']}

    submissions = []
    for file_path, file_content in contents['data'].items():
        try:
            # Extract user_id, verdict, and submission_no from the path
            parts = file_path.split('/')
            if len(parts) > 5:
                user_id = parts[3]
                verdict = parts[4]
                submission_no = parts[5].split('.')[0]

                submission_data = json.loads(file_content)
                submissions.append({
                    "user_id": user_id,
                    "problem_id": problem_id,
                    "verdict": verdict,
                    "submission_no": submission_no,
                    "submission_data": submission_data
                })
        except (json.JSONDecodeError, IndexError):
            # Ignore files that are not valid JSON or don't match the expected path structure
            continue

    return submissions


def add_submission(problem_id, user_id, result):
    add_submission_to_user(user_id, problem_id, result)
    add_submission_to_problem(user_id, problem_id, result)
    pass

if __name__ == '__main__':
    print(get_problem_submissions(1))
    