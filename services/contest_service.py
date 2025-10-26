import json
from datetime import datetime
import pytz
from services.github_services import get_file, create_or_update_file, get_folder_contents
from config.github_config import GITHUB_CONTESTS_BASE_PATH, GITHUB_CONTEST_PARTICIPANTS_FILE
from extensions import mongo

def get_all_contests_metadata():
    try:
        contests_cursor = mongo.db.contests.find({}, {'_id': 0})
        contests_list = []
        for contest in contests_cursor:
            contest_status = get_contest_status(contest)
            contest["status_info"] = contest_status
            contests_list.append(contest)
        return contests_list, None
    except Exception as e:
        return None, {"message": str(e)}

def get_contest_status(contest_data):
    start_time_str = contest_data.get('startTime')
    end_time_str = contest_data.get('endTime')

    if not start_time_str or not end_time_str:
        return {"status": "Unknown", "timeInfo": "N/A", "progress": 0}

    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
    end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
    current_time = datetime.now(pytz.UTC)

    if current_time < start_time:
        diff = start_time - current_time
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60
        return {
            "status": "Upcoming",
            "timeInfo": f"Starts in: {days}d {hours}h {minutes}m {seconds}s",
            "progress": 0
        }
    elif current_time >= start_time and current_time <= end_time:
        total_duration = (end_time - start_time).total_seconds()
        elapsed = (current_time - start_time).total_seconds()
        remaining = (end_time - current_time).total_seconds()
        progress = (elapsed / total_duration) * 100 if total_duration > 0 else 0

        days = int(remaining // (3600 * 24))
        hours = int((remaining % (3600 * 24)) // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)

        return {
            "status": "Running",
            "timeInfo": f"Ends in: {days}d {hours}h {minutes}m {seconds}s",
            "progress": progress
        }
    else:
        return {
            "status": "Over",
            "timeInfo": "",
            "progress": 100
        }

def get_contest_details(contest_id):
    try:
        contest = mongo.db.contests.find_one({'id': contest_id}, {'_id': 0})
        if contest:
            contest_status = get_contest_status(contest)
            contest["status_info"] = contest_status
            return contest, None
        return None, {"message": "Contest not found"}
    except Exception as e:
        return None, {"message": str(e)}

def get_contest_meta_from_mongo(contest_id):
    try:
        contest_meta = mongo.db.contests.find_one({'id': contest_id}, {'_id': 0, 'contest_description': 0, 'contest_theory': 0})
        if contest_meta:
            return contest_meta, None
        return None, {"message": "Contest metadata not found"}
    except Exception as e:
        return None, {"message": str(e)}

def is_user_registered(contest_id, username):
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
            if participant.get("username") == username:
                return True, None
        return False, None
    except json.JSONDecodeError:
        return False, {"error": "Failed to decode participants.json"}

def register_user_for_contest(contest_id, username):
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
        if participant.get("username") == username:
            return False, {"error": "User already registered for this contest."}

    participants_data["participants"].append({
        "username": username,
        "registration_time": datetime.now().isoformat()
    })

    update_result = create_or_update_file(
        participants_path,
        json.dumps(participants_data, indent=2),
        f"[AUTO] Register user {username} for contest {contest_id}"
    )

    if "error" in update_result:
        return False, {"error": update_result["message"]}

    return True, None