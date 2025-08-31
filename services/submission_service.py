import os, time, json
import sys

from services.github_services import get_file, add_file, update_file, create_or_update_file
from services.judge_service import grade_submission
from config.github_config import GITHUB_PROBLEMS_BASE_PATH, GITHUB_USERS_BASE_PATH, GITHUB_SUBMISSIONS_BASE_PATH

def handle_new_submission(problem_id, user_id, language, code):
    # 1. Get global submission meta to generate a new submission ID
    global_submissions_meta_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/meta.json"
    global_submissions_meta_content, _, global_submissions_meta_error = get_file(global_submissions_meta_path)

    if global_submissions_meta_error:
        return {"error": f"Failed to get global submissions metadata from {global_submissions_meta_path}: {global_submissions_meta_error['message']}"}

    try:
        global_submissions_meta_data = json.loads(global_submissions_meta_content)
        new_submission_id_num = global_submissions_meta_data.get("number_of_submissions", 0) + 1
        new_submission_id = f"S{new_submission_id_num}"
    except json.JSONDecodeError:
        return {"error": "Failed to decode global submissions meta.json"}

    # 2. Create main submission files
    submission_dir_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/{new_submission_id}"
    submission_meta_path = f"{submission_dir_path}/meta.json"
    code_file_extension = {"python": "py", "c++": "cpp", "c": "c"}.get(language.lower(), "txt")
    code_file_path = f"{submission_dir_path}/code.{code_file_extension}"

    submission_meta_data = {
        "submission_id": new_submission_id,
        "user_id": user_id,
        "problem_id": problem_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "Pending",
        "language": language
    }

    # Add submission meta.json to the main submissions folder
    add_meta_result = create_or_update_file(submission_meta_path, json.dumps(submission_meta_data, indent=2), commit_message=f"[AUTO] Add {new_submission_id} meta")
    if "error" in add_meta_result:
        return {"error": f"Failed to add submission meta: {add_meta_result['message']}"}

    # Add code file to the main submissions folder
    add_code_result = create_or_update_file(code_file_path, code, commit_message=f"[AUTO] Add {new_submission_id} code")
    if "error" in add_code_result:
        return {"error": f"Failed to add submission code: {add_code_result['message']}"}

    # 3. Grade the submission
    judge_result = grade_submission(code, language, problem_id)
    if judge_result.get("overall_status") == "error":
        return {"error": judge_result.get("message", "An unknown error occurred during judging.")}

    submission_meta_data["status"] = judge_result["overall_status"]
    submission_meta_data["test_results"] = judge_result["test_results"]

    # Update main submission meta.json with judging results
    update_submission_meta_result = create_or_update_file(submission_meta_path, json.dumps(submission_meta_data, indent=2), commit_message=f"[AUTO] Update {new_submission_id} meta with judging results")
    if "error" in update_submission_meta_result:
        return {"error": f"Failed to update submission meta with judging results: {update_submission_meta_result['message']}"}

    # 4. Update Problem Data
    # Add submission reference to problem
    problem_submission_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/submissions/{new_submission_id}.json"
    problem_submission_data = {
        "submission_id": new_submission_id,
        "user_id": user_id,
        "timestamp": submission_meta_data["timestamp"],
        "status": submission_meta_data["status"]
    }
    add_problem_submission_result = add_file(problem_submission_path, json.dumps(problem_submission_data, indent=2), commit_message=f"[AUTO] Add {new_submission_id} to {problem_id} submissions")
    if "error" in add_problem_submission_result:
        # Log error but continue
        print(f"Error adding submission reference to problem: {add_problem_submission_result['message']}")


    # 5. Update User Data
    # Add submission reference to user
    user_submission_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/submissions/{new_submission_id}.json"
    user_submission_data = {
        "submission_id": new_submission_id,
        "problem_id": problem_id,
        "timestamp": submission_meta_data["timestamp"],
        "status": submission_meta_data["status"]
    }
    add_user_submission_result = add_file(user_submission_path, json.dumps(user_submission_data, indent=2), commit_message=f"[AUTO] Add {new_submission_id} to {user_id} submissions")
    if "error" in add_user_submission_result:
        # Log error but continue
        print(f"Error adding submission reference to user: {add_user_submission_result['message']}")


    # 6. Update global submission meta
    global_submissions_meta_data["number_of_submissions"] = new_submission_id_num
    update_global_meta_result = create_or_update_file(global_submissions_meta_path, json.dumps(global_submissions_meta_data, indent=2), commit_message=f"[AUTO] Update global submission count to {new_submission_id_num}")
    if "error" in update_global_meta_result:
        # Log error but continue
        print(f"Error updating global submission meta: {update_global_meta_result['message']}")


    return {"message": "Submission successful", "submission_id": new_submission_id, "status": submission_meta_data["status"]}