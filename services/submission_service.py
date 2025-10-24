import time
import uuid
from extensions import mongo

def handle_new_submission(problem_id, username, language, code):
    print(f"Submission received for Problem ID: {problem_id}, Username: {username}")

    submission_id = str(uuid.uuid4())

    submission_doc = {
        "submission_id": submission_id, # Use submission_id for unique identifier
        "problem_id": problem_id,
        "username": username,
        "language": language,
        "code": code,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "Queued"
    }

    try:
        mongo.db.submissions_queue.insert_one(submission_doc)
        return {"problem_id": problem_id, "username": username, "message": "Submission received and queued.", "submission_id": submission_id}
    except Exception as e:
        return {"error": f"Failed to queue submission: {str(e)}"}

def init_app(app):
    pass # No initialization needed for this minimal version