import time
import uuid
import json
import threading
from bson.objectid import ObjectId
from extensions import mongo
from services.judge_service import grade_submission
from services.github_services import get_file, add_file
from config.github_config import GITHUB_SUBMISSIONS_BASE_PATH

def handle_new_submission(problem_id, username, language, code):
    print(f"Submission received for Problem ID: {problem_id}, Username: {username}")

    submission_data = {
        "problem_id": problem_id,
        "username": username,
        "language": language,
        "code": code,
        "status": "in_queue",
        "created_at": time.time()
    }

    result = mongo.db.submissions_queue.insert_one(submission_data)
    submission_id = str(result.inserted_id)

    return {
        "submission_id": submission_id,
        "status": "in_queue",
        "message": "Submission received and is waiting to be graded."
    }

def worker():
    while True:
        submission = mongo.db.submissions_queue.find_one_and_update(
            {"status": "in_queue"},
            {"$set": {"status": "grading"}}
        )

        if submission:
            print(f"Grading submission: {submission['_id']}")
            
            grading_results = grade_submission(
                submission['_id'],
                submission['code'], 
                submission['language'], 
                submission['problem_id']
            )

            if isinstance(grading_results, dict) and grading_results.get("overall_status") == "error":
                final_status = "error"
                test_results = []
            else:
                test_results = grading_results
                verdicts = [result["status"] for result in test_results if "status" in result]
                final_status = "accepted"
                if "compilation_error" in verdicts:
                    final_status = "compilation_error"
                elif "runtime_error" in verdicts:
                    final_status = "runtime_error"
                elif "time_limit_exceeded" in verdicts:
                    final_status = "time_limit_exceeded"
                elif "memory_limit_exceeded" in verdicts:
                    final_status = "memory_limit_exceeded"
                elif "wrong_answer" in verdicts:
                    final_status = "wrong_answer"

            submission_id_str = str(submission['_id'])
            
            # Create submission files in GitHub
            submission_path = f"{GITHUB_SUBMISSIONS_BASE_PATH}/{submission_id_str}"
            
            # Create meta.json
            meta_data = {
                "submission_id": submission_id_str,
                "problem_id": submission['problem_id'],
                "username": submission['username'],
                "language": submission['language'],
                "status": final_status,
                "timestamp": submission['created_at'],
                "test_results": test_results
            }
            add_file(f"{submission_path}/meta.json", json.dumps(meta_data, indent=4), f"Create submission {submission_id_str} meta.json")

            # Create code file
            file_extension = {"python": "py", "c": "c", "c++": "cpp"}.get(submission['language'], "txt")
            add_file(f"{submission_path}/code.{file_extension}", submission['code'], f"Create submission {submission_id_str} code file")

            # Insert into submissions collection
            mongo.db.submissions.insert_one(meta_data)

            # Remove from queue
            mongo.db.submissions_queue.delete_one({"_id": submission["_id"]})
            
            print(f"Finished grading submission: {submission['_id']}")

        time.sleep(5) # Poll every 5 seconds

def get_submissions_queue():
    queue = []
    for submission in mongo.db.submissions_queue.find():
        submission['_id'] = str(submission['_id'])
        queue.append(submission)
    return queue

def init_app(app):
    threading.Thread(target=worker, daemon=True).start()
