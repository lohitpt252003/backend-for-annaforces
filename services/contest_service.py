import json
from datetime import datetime
from services.github_services import get_file, create_or_update_file, get_folder_contents
from services.user_service import update_user_contests_status, get_user_by_id
from config.github_config import GITHUB_CONTESTS_BASE_PATH, GITHUB_CONTEST_PARTICIPANTS_FILE, GITHUB_CONTEST_LEADERBOARD_FILE

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

    # Update user's meta.json to record contest participation
    user_update_success, user_update_error = update_user_contests_status(user_id, contest_id)
    if user_update_error:
        print(f"Warning: Failed to update user {user_id} meta.json for contest {contest_id}: {user_update_error['error']}")

    return True, None

def get_contest_leaderboard(contest_id):
    leaderboard_path = f"{GITHUB_CONTESTS_BASE_PATH}/{contest_id}/{GITHUB_CONTEST_LEADERBOARD_FILE}"
    content, _, error = get_file(leaderboard_path)

    if error:
        if "not found" in error.get("message", "").lower():
            return {"last_updated": None, "standings": []}, None
        return None, {"error": error["message"]}

    try:
        leaderboard_data = json.loads(content)
        
        for standing in leaderboard_data.get("standings", []):
            user_id = standing.get("user_id")
            if user_id:
                user_meta, user_error = get_user_by_id(user_id)
                if not user_error and user_meta:
                    standing["username"] = user_meta.get("username", "")
        
        return leaderboard_data, None
    except json.JSONDecodeError:
        return None, {"error": "Failed to decode leaderboard.json"}

def update_contest_leaderboard(contest_id, user_id, problem_id, submission_status, submission_time, time_taken, penalty):
    leaderboard_path = f"{GITHUB_CONTESTS_BASE_PATH}/{contest_id}/{GITHUB_CONTEST_LEADERBOARD_FILE}"
    content, sha, error = get_file(leaderboard_path)

    leaderboard_data = {"last_updated": None, "standings": []}
    if not error:
        try:
            leaderboard_data = json.loads(content)
        except json.JSONDecodeError:
            pass # Will overwrite with empty if invalid JSON

    standings = leaderboard_data.get("standings", [])
    participant_standing = None
    for entry in standings:
        if entry.get("user_id") == user_id:
            participant_standing = entry
            break

    if not participant_standing:
        participant_standing = {
            "user_id": user_id,
            "total_score": 0,
            "total_penalty": 0,
            "problems": {}
        }
        standings.append(participant_standing)

    # Update problem-specific data
    problem_entry = participant_standing["problems"].setdefault(problem_id, {
        "status": "not_attempted",
        "score": 0,
        "attempts": 0,
        "time_taken": "00:00:00" # Store as string for simplicity, can be converted to timedelta
    })

    problem_entry["attempts"] += 1

    if submission_status == "accepted":
        # Only update if not already solved or if this submission is better (e.g., fewer attempts, less time)
        if problem_entry["status"] != "solved":
            problem_entry["status"] = "solved"
            problem_entry["score"] = 1 # Award 1 point for solving a problem
            problem_entry["time_taken"] = time_taken # This should be the time from contest start to submission
            participant_standing["total_score"] += 1 # Add 1 point to total score
            # Convert time_taken (HH:MM:SS) to seconds for penalty accumulation
            h, m, s = map(int, time_taken.split(':'))
            time_in_seconds = h * 3600 + m * 60 + s
            participant_standing["total_penalty"] += time_in_seconds # Accumulate time as penalty
        # If already solved, and new submission is also accepted, we might update time/attempts if better
        # For now, we'll keep the first accepted time/score.
    elif problem_entry["status"] != "solved": # Only update status if not already solved
        problem_entry["status"] = "not_solved"

    leaderboard_data["last_updated"] = datetime.now().isoformat()
    leaderboard_data["standings"] = standings

    update_result = create_or_update_file(
        leaderboard_path,
        json.dumps(leaderboard_data, indent=2),
        f"[AUTO] Update leaderboard for contest {contest_id} by user {user_id} for problem {problem_id}"
    )

    if "error" in update_result:
        print(f"Error updating leaderboard for {contest_id}: {update_result['message']}")
        return False, {"error": update_result["message"]}

    return True, None