import time
import uuid
import json
from extensions import mongo
from services.judge_service import grade_submission
from services.github_services import get_file
from config.github_config import GITHUB_SUBMISSIONS_BASE_PATH

def handle_new_submission(problem_id, username, language, code):
    print(f"Submission received for Problem ID: {problem_id}, Username: {username}")

    submission_id = str(uuid.uuid4())

    # 1. Get global submission meta to generate a new submission ID (for consistency, though not used for actual ID)
    global_submissions_meta_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/meta.json"
    global_submissions_meta_content, _, global_submissions_meta_error = get_file(global_submissions_meta_path)

    if global_submissions_meta_error:
        # Handle error, but don't fail submission if meta.json is just for counting
        print(f"Warning: Failed to get global submissions metadata: {global_submissions_meta_error['message']}")

    # 2. Grade the submission directly
    grading_results = grade_submission(code, language, problem_id)

    if isinstance(grading_results, dict) and grading_results.get("overall_status") == "error":
        # Handle overall grading error
        return {"error": grading_results["message"]}

    test_results = grading_results
    verdicts = [result["status"] for result in test_results if "status" in result]

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

    # Construct the response with grading results
    response_data = {
        "submission_id": submission_id,
        "problem_id": problem_id,
        "username": username,
        "language": language,
        "status": overall_status,
        "test_results": test_results,
        "message": "Submission graded."
    }

    return response_data

def init_app(app):
    pass # No initialization needed for this minimal version