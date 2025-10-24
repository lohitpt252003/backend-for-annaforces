import json
from datetime import datetime
from services.github_services import get_file, create_or_update_file, get_folder_contents
from config.github_config import GITHUB_CONTESTS_BASE_PATH, GITHUB_CONTEST_PARTICIPANTS_FILE

def get_all_contests_metadata():
    index_path = f"{GITHUB_CONTESTS_BASE_PATH}/index.json"
    content, _, error = get_file(index_path)

    if error:
        return None, {"error": error["message"]}

    try:
        contests_data = json.loads(content)
        # If contests_data is a list, return it directly
        if isinstance(contests_data, list):
            return contests_data, None
        # If it's a dictionary, convert it to a list of contest objects
        elif isinstance(contests_data, dict):
            contests_list = []
            for contest_id, contest_info in contests_data.items():
                contests_list.append({"id": contest_id, **contest_info})
            return contests_list, None
        else:
            return None, {"error": "Unexpected format for contests index.json"}
    except json.JSONDecodeError:
        return None, {"error": "Failed to decode contests index.json"}

def get_contest_details(contest_id):
    contest_path = f"{GITHUB_CONTESTS_BASE_PATH}/{contest_id}"
    meta_path = f"{contest_path}/meta.json"
    description_path = f"{contest_path}/description.md"
    theory_path = f"{contest_path}/theory.md"

    meta_content, _, meta_error = get_file(meta_path)
    if meta_error:
        return None, {"error": f"Contest meta.json not found for {contest_id}"}

    description_content, _, description_error = get_file(description_path)
    if description_error:
        description_content = "No description provided."

    theory_content, _, theory_error = get_file(theory_path)
    if theory_error:
        theory_content = "No theory provided."

    try:
        meta_data = json.loads(meta_content)
        contest_data = {
            "id": contest_id,
            **meta_data,
            "contest_description": description_content,
            "contest_theory": theory_content
        }
        return contest_data, None
    except json.JSONDecodeError:
        return None, {"error": "Failed to decode contest meta.json"}

def is_user_registered(contest_id, user_id):
    participants_path = f"{GITHUB_CONTESTS_BASE_PATH}/{contest_id}/{GITHUB_CONTEST_PARTICIPANTS_FILE}"
    content, _, error = get_file(participants_path)

    if error:
        # If file not found, no one is registered
        if "not found" in error.get("message", "").lower():
            return False, None
        return False, {"error": error["message"]}

    try:
        participants_data = json.loads(content)
        for participant in participants_data.get("participants", []):
            if participant.get("user_id") == user_id:
                return True, None
        return False, None
    except json.JSONDecodeError:
        return False, {"error": "Failed to decode participants.json"}

def register_user_for_contest(contest_id, user_id):
    participants_path = f"{GITHUB_CONTESTS_BASE_PATH}/{contest_id}/{GITHUB_CONTEST_PARTICIPANTS_FILE}"
    content, sha, error = get_file(participants_path)

    participants_data = {"participants": []}
    if not error:
        try:
            participants_data = json.loads(content)
        except json.JSONDecodeError:
            pass # Will overwrite with empty if invalid JSON

    # Check if user is already registered
    for participant in participants_data.get("participants", []):
        if participant.get("user_id") == user_id:
            return False, {"error": "User already registered for this contest."}

    participants_data["participants"].append({
        "user_id": user_id,
        "registration_time": datetime.now().isoformat()
    })

    update_result = create_or_update_file(
        participants_path,
        json.dumps(participants_data, indent=2),
        f"[AUTO] Register user {user_id} for contest {contest_id}"
    )

    if "error" in update_result:
        return False, {"error": update_result["message"]}

    return True, None