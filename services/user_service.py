import json
from datetime import datetime
from services.github_services import get_folder_contents, get_file
from config.github_config import GITHUB_USERS_BASE_PATH
from extensions import mongo

def get_user_by_username(username):
    """Fetches a user document from MongoDB by username."""
    user_data = mongo.db.users.find_one({"username": username})
    if not user_data:
        return None, {"error": "User not found"}
    
    # Ensure all necessary fields are present
    user_data.setdefault('attempted', {})
    user_data.setdefault('solved', {})
    user_data.setdefault('not_solved', {})
    user_data.setdefault('contests', {})
    return user_data, None

def update_user_profile(username, new_name, new_username, new_bio):
    """Updates a user's profile data in MongoDB."""
    # 1. Check for username uniqueness if it's being changed
    if new_username and new_username != username:
        if mongo.db.users.find_one({"username": new_username}):
            return False, {"error": "Username already taken."}

    # 2. Build the update document
    update_fields = {}
    if new_name is not None: update_fields['name'] = new_name
    if new_username is not None: update_fields['username'] = new_username
    if new_bio is not None: update_fields['bio'] = new_bio

    if not update_fields:
        return True, None # Nothing to update

    # 3. Perform the update in MongoDB
    result = mongo.db.users.update_one(
        {"username": username},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return False, {"error": "User not found for update."}

    # Note: The logic to update the old file-based users/index.json is now obsolete
    # and has been removed.

    return True, None

def get_user_submissions(username):
    """Retrieves a user's submission data from the GitHub DATA repository."""
    submissions = []
    user_submissions_path = f"{GITHUB_USERS_BASE_PATH}/{username}/submissions"
    
    response, error = get_folder_contents(user_submissions_path)
    if error or not response.get("success"):
        if error and "not found" in str(error).lower():
            return [], None # No submissions folder means no submissions
        return None, {"error": error or "Failed to get user submissions folder"}

    submission_files = response.get("data", [])
    for item in submission_files:
        if item['type'] == 'file' and item['name'].endswith('.json'):
            submission_file_path = f"{user_submissions_path}/{item['name']}"
            content, _, file_error = get_file(submission_file_path)
            if file_error:
                print(f"Error fetching {submission_file_path}: {file_error['message']}")
                continue
            try:
                submissions.append(json.loads(content))
            except json.JSONDecodeError:
                print(f"Error decoding JSON for {submission_file_path}")
                continue

    return submissions, None

def get_solved_problems(username):
    """Retrieves a list of unique problem IDs solved by a user."""
    submissions, error = get_user_submissions(username)
    if error:
        return None, error

    solved_problem_ids = set()
    for submission in submissions:
        if submission.get("status", "").lower() == "accepted":
            solved_problem_ids.add(submission.get("problem_id"))

    return list(solved_problem_ids), None

def update_user_problem_status(username, problem_id, new_status):
    """Updates a user's problem status fields in their MongoDB document."""
    user, error = get_user_by_username(username)
    if error:
        return False, error

    timestamp = datetime.now().isoformat()
    update_doc = {"$set": {}, "$unset": {}}

    was_solved = problem_id in user.get('solved', {})

    # Remove from old categories
    update_doc["$unset"][f'attempted.{problem_id}'] = ""
    update_doc["$unset"][f'not_solved.{problem_id}'] = ""

    # Add to new category
    if new_status == "solved":
        update_doc["$set"][f'solved.{problem_id}'] = timestamp
    elif not was_solved:
        update_doc["$set"][f'not_solved.{problem_id}'] = timestamp

    # Clean up empty $set/$unset keys
    if not update_doc["$set"]:
        del update_doc["$set"]
    if not update_doc["$unset"]:
        del update_doc["$unset"]
    
    if not update_doc:
        return True, None # No changes needed

    mongo.db.users.update_one({"username": username}, update_doc)
    return True, None

def update_user_contests_status(username, contest_id):
    """Adds a contest to a user's attended contests list in their MongoDB document."""
    timestamp = datetime.now().isoformat()
    update_doc = {
        "$set": {f"contests.{contest_id}": timestamp}
    }
    result = mongo.db.users.update_one({"username": username}, update_doc)

    if result.matched_count == 0:
        return False, {"error": "User not found for contest status update."}

    return True, None
