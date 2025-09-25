import os, time, json, threading

from services.github_services import get_file, add_file, update_file, create_or_update_file
from services.judge_service import grade_submission
from config.github_config import GITHUB_PROBLEMS_BASE_PATH, GITHUB_USERS_BASE_PATH, GITHUB_SUBMISSIONS_BASE_PATH

def _process_submission_in_background(new_submission_id, problem_id, user_id, language, code):
    submission_meta_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/{new_submission_id}/meta.json"

    # 1. Update status to "Running"
    content, sha, error = get_file(submission_meta_path)
    if error:
        print(f"Error getting initial meta file for {new_submission_id}: {error['message']}")
        return
    
    submission_meta_data = json.loads(content)
    submission_meta_data["status"] = "Running"
    update_file(submission_meta_path, json.dumps(submission_meta_data, indent=2), f"[AUTO] Set {new_submission_id} to Running")

    # 2. Grade the submission and update after each test case
    test_results = []
    verdicts = []
    for i, result in enumerate(grade_submission(code, language, problem_id)):
        if result.get("overall_status") == "error":
            submission_meta_data["status"] = "error"
            submission_meta_data["message"] = result.get("message")
            update_file(submission_meta_path, json.dumps(submission_meta_data, indent=2), f"[AUTO] Error for {new_submission_id}")
            return

        test_results.append(result)
        verdicts.append(result["status"])
        submission_meta_data["status"] = f"Running... (Testcase {i+1})"
        submission_meta_data["test_results"] = test_results
        update_file(submission_meta_path, json.dumps(submission_meta_data, indent=2), f"[AUTO] Update {new_submission_id} after testcase {i+1}")

    # 3. Determine final status
    overall_status = "accepted"
    if "compilation_error" in verdicts:
        overall_status = "compilation_error"
    elif "runtime_error" in verdicts:
        overall_status = "runtime_error"
    elif "time_limit_exceeded" in verdicts:
        overall_status = "time_limit_exceeded"
    elif "memory_limit_exceeded" in verdicts:
        overall_status = "memory_limit_exceeded"
    elif "wrong_answer" in verdicts:
        overall_status = "wrong_answer"

    submission_meta_data["status"] = overall_status
    update_file(submission_meta_path, json.dumps(submission_meta_data, indent=2), f"[AUTO] Final status for {new_submission_id}: {overall_status}")

    # 4. Update Problem Data
    problem_submission_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/submissions/{new_submission_id}.json"
    problem_submission_data = {
        "submission_id": new_submission_id,
        "user_id": user_id,
        "timestamp": submission_meta_data["timestamp"],
        "status": overall_status
    }
    add_file(problem_submission_path, json.dumps(problem_submission_data, indent=2), f"[AUTO] Add {new_submission_id} to {problem_id} submissions")

    # 5. Update User Data
    user_submission_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/submissions/{new_submission_id}.json"
    user_submission_data = {
        "submission_id": new_submission_id,
        "problem_id": problem_id,
        "timestamp": submission_meta_data["timestamp"],
        "status": overall_status
    }
    add_file(user_submission_path, json.dumps(user_submission_data, indent=2), f"[AUTO] Add {new_submission_id} to {user_id} submissions")

    # 6. Update global submission meta
    global_submissions_meta_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/meta.json"
    global_submissions_meta_content, _, _ = get_file(global_submissions_meta_path)
    global_submissions_meta_data = json.loads(global_submissions_meta_content)
    new_submission_id_num = int(new_submission_id[1:])
    global_submissions_meta_data["number_of_submissions"] = new_submission_id_num
    update_file(global_submissions_meta_path, json.dumps(global_submissions_meta_data, indent=2), f"[AUTO] Update global submission count to {new_submission_id_num}")


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

    # 2. Create initial submission files
    submission_dir_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/{new_submission_id}"
    submission_meta_path = f"{submission_dir_path}/meta.json"
    code_file_extension = {"python": "py", "c++": "cpp", "c": "c"}.get(language.lower(), "txt")
    code_file_path = f"{submission_dir_path}/code.{code_file_extension}"

    submission_meta_data = {
        "submission_id": new_submission_id,
        "user_id": user_id,
        "problem_id": problem_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "Queued",
        "language": language,
        "test_results": []
    }

    create_or_update_file(submission_meta_path, json.dumps(submission_meta_data, indent=2), commit_message=f"[AUTO] Add {new_submission_id} meta")
    create_or_update_file(code_file_path, code, commit_message=f"[AUTO] Add {new_submission_id} code")

    # 3. Start background thread for judging
    thread = threading.Thread(target=_process_submission_in_background, args=(new_submission_id, problem_id, user_id, language, code))
    thread.start()

    return {"message": "Submission received and is being processed.", "submission_id": new_submission_id}
