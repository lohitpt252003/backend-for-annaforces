import json
from services.github_services import get_file, create_or_update_file
from config.github_config import GITHUB_USERS_BASE_PATH, GITHUB_SUBMISSIONS_BASE_PATH

def get_user_by_id(user_id):
    meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    meta_content, _, meta_error = get_file(meta_path)

    if meta_error:
        return None, {"error": meta_error["message"]}

    try:
        meta_data = json.loads(meta_content)
        return meta_data, None
    except json.JSONDecodeError:
        return None, {"error": "Failed to decode meta.json"}

def get_user_submissions(user_id):
    meta_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/meta.json"
    meta_content, _, meta_error = get_file(meta_path)

    if meta_error:
        return None, {"error": meta_error["message"]}

    try:
        meta_data = json.loads(meta_content)
        num_submissions = meta_data.get("number_of_submissions")
        if num_submissions is None:
            return None, {"error": "number_of_submissions not found in meta.json"}
    except json.JSONDecodeError:
        return None, {"error": "Failed to decode meta.json"}

    submissions = []
    for i in range(1, num_submissions + 1):
        submission_file_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/S{i}/meta.json"
        content, _, error = get_file(submission_file_path)
        if error:
            print(f"Error fetching {submission_file_path}: {error['message']}")
            continue
        try:
            submission_data = json.loads(content)
            if submission_data.get("user_id") == user_id:
                submissions.append(submission_data)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for {submission_file_path}")
            continue

    return submissions, None
