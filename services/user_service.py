import json
from datetime import datetime
from services.github_services import get_file, create_or_update_file, get_folder_contents
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

def update_user_profile(user_id, new_name, new_username, new_bio):
    # 1. Fetch current user meta.json
    meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    meta_content, meta_sha, meta_error = get_file(meta_path)

    if meta_error:
        return False, {"error": f"Could not fetch user metadata: {meta_error['message']}"}

    try:
        current_meta_data = json.loads(meta_content)
    except json.JSONDecodeError:
        return False, {"error": "Failed to decode current user metadata."}

    # 2. Check for username uniqueness if it's being changed
    if new_username and new_username != current_meta_data.get('username'):
        response, error = get_folder_contents(GITHUB_USERS_BASE_PATH)
        if error:
            return False, {"error": "Could not retrieve users list to check username uniqueness."}

        users_folders = response.get("data", [])
        for item in users_folders:
            if item['type'] == 'dir' and item['name'].startswith('U') and item['name'] != user_id:
                other_user_meta_path = f"{GITHUB_USERS_BASE_PATH}/{item['name']}/meta.json"
                other_meta_content, _, other_meta_error = get_file(other_user_meta_path)
                if not other_meta_error and other_meta_content:
                    try:
                        other_meta_data = json.loads(other_meta_content)
                        if other_meta_data.get('username') == new_username:
                            return False, {"error": "Username already taken."}
                    except json.JSONDecodeError:
                        continue # Skip invalid meta.json files

    # 3. Update meta.json
    updated_meta_data = current_meta_data.copy()
    if new_name is not None: updated_meta_data['name'] = new_name
    if new_username is not None: updated_meta_data['username'] = new_username
    if new_bio is not None: updated_meta_data['bio'] = new_bio

    update_meta_result = create_or_update_file(
        meta_path,
        json.dumps(updated_meta_data, indent=2),
        f"[AUTO] Update profile for {user_id}"
    )
    if "error" in update_meta_result:
        return False, {"error": f"Failed to update user metadata: {update_meta_result['message']}"}

    # 4. Update users/index.json if name or username changed
    index_path = f"{GITHUB_USERS_BASE_PATH}/index.json"
    index_content, index_sha, index_error = get_file(index_path)

    if index_error:
        print(f"Warning: Could not retrieve users index for update: {index_error['message']}")
        return True, None # Non-critical error, proceed

    try:
        users_index = json.loads(index_content)
    except json.JSONDecodeError:
        print("Warning: Failed to decode users index.json for update.")
        return True, None # Non-critical error, proceed

    index_updated = False
    if users_index.get(user_id):
        if new_username is not None and users_index[user_id].get('username') != new_username:
            users_index[user_id]['username'] = new_username
            index_updated = True
        if new_name is not None and users_index[user_id].get('name') != new_name:
            users_index[user_id]['name'] = new_name
            index_updated = True
    
    if index_updated:
        update_index_result = create_or_update_file(
            index_path,
            json.dumps(users_index, indent=2),
            f"[AUTO] Update index for user {user_id}"
        )
        if "error" in update_index_result:
            print(f"Warning: Failed to update users/index.json: {update_index_result['message']}")

    return True, None

def get_user_by_id(user_id):
    meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    meta_content, _, meta_error = get_file(meta_path)

    if meta_error:
        return None, {"error": meta_error["message"]}

    try:
        meta_data = json.loads(meta_content)
        # Initialize new fields if they don't exist
        meta_data.setdefault('attempted', {})
        meta_data.setdefault('solved', {})
        meta_data.setdefault('not_solved', {})
        return meta_data, None
    except json.JSONDecodeError:
        return None, {"error": "Failed to decode meta.json"}

def get_user_submissions(user_id):
    submissions = []
    
    user_submissions_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/submissions"
    
    # Get all submission files for this specific user
    response, error = get_folder_contents(user_submissions_path)
    print(f"[DEBUG] get_folder_contents response for user submissions: {response}")
    if not response.get("success"):
        # If the folder doesn't exist, it means no submissions for this user
        if "not found" in response.get("error", "").lower():
            return [], None
        return None, {"error": response.get("error", "Failed to get user submissions folder contents")}

    submission_files = response.get("data")
    print(f"[DEBUG] submission_files for user {user_id}: {submission_files}")

    for item in submission_files:
        if item['type'] == 'file' and item['name'].endswith('.json'):
            submission_file_path = f"{user_submissions_path}/{item['name']}"
            print(f"[DEBUG] submission_file_path: {submission_file_path}")
            content, _, error = get_file(submission_file_path)
            if error:
                print(f"Error fetching {submission_file_path}: {error['message']}")
                continue
            try:
                submission_data = json.loads(content)
                print(f"[DEBUG] submission_data: {submission_data}")
                submissions.append(submission_data)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for {submission_file_path}")
                continue

    return submissions, None

def get_solved_problems(user_id):
    submissions, error = get_user_submissions(user_id)
    if error:
        return None, error

    solved_problem_ids = set()
    for submission in submissions:
        if submission.get("status") and submission.get("status").lower() == "accepted":
            solved_problem_ids.add(submission.get("problem_id"))

    return list(solved_problem_ids), None

def update_user_problem_status(user_id, problem_id, new_status):
    meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    meta_content, meta_sha, meta_error = get_file(meta_path)

    if meta_error:
        print(f"Error fetching user meta.json for {user_id}: {meta_error['message']}")
        return False, {"error": f"Could not fetch user metadata: {meta_error['message']}"}

    try:
        meta_data = json.loads(meta_content)
    except json.JSONDecodeError:
        print(f"Error decoding user meta.json for {user_id}")
        return False, {"error": "Failed to decode user metadata."}

    # Ensure the fields exist and are dictionaries
    meta_data.setdefault('attempted', {})
    meta_data.setdefault('solved', {})
    meta_data.setdefault('not_solved', {})

    # Check if the problem was already solved
    was_solved = problem_id in meta_data['solved']

    # Remove problem_id from attempted and not_solved if it exists there
    # This ensures it's only in one category at a time, unless it's already solved.
    meta_data['attempted'].pop(problem_id, None)
    meta_data['not_solved'].pop(problem_id, None)

    # Add problem_id to the appropriate category with current timestamp
    timestamp = datetime.now().isoformat()

    if new_status == "solved":
        meta_data['solved'][problem_id] = timestamp
    elif not was_solved: # Only update if it wasn't already solved
        meta_data['not_solved'][problem_id] = timestamp
    
    # The 'attempted' status is implicitly covered by being in either 'solved' or 'not_solved'.
    # We don't need a separate explicit 'attempted' list for this logic.

    update_meta_result = create_or_update_file(
        meta_path,
        json.dumps(meta_data, indent=2),
        f"[AUTO] Update problem status for user {user_id} and problem {problem_id}"
    )

    if "error" in update_meta_result:
        print(f"Error updating user problem status for {user_id}: {update_meta_result['message']}")
        return False, {"error": f"Failed to update user problem status: {update_meta_result['message']}"}

    return True, None
