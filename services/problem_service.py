import json
import re
from services.github_services import get_file, create_or_update_file, add_file
from services import contest_service
from datetime import datetime
import pytz
# from config.github_config import GITHUB_PROBLEMS_BASE_PATH
from extensions import mongo

def _validate_problem_md(description):
    """
    Validates the problem.md description.
    """
    required_sections = [
        r"# Problem \d+: .*",
        r"## Description",
        r"## Input",
        r"## Output",
        r"## Constraints",
        r"## Example1",
        r"### Input",
        r"### Output",
        r"## Explanation"
    ]

    for section in required_sections:
        if not re.search(section, description, re.MULTILINE):
            return f"Missing required section in problem.md: {section}"

    return None

def _validate_problem_data(problem_data):
    """
    Validates the problem data.
    """
    required_fields = ["title", "time_limit", "memory_limit", "difficulty", "tags", "authors", "description", "testcases"]
    for field in required_fields:
        if field not in problem_data:
            return f"Missing required field: {field}"

    if not isinstance(problem_data["testcases"], list) or not problem_data["testcases"]:
        return "Testcases must be a non-empty list."

    for i, testcase in enumerate(problem_data["testcases"]):
        if "input" not in testcase or "output" not in testcase:
            return f"Testcase {i+1} is missing 'input' or 'output'."
        if not testcase["input"] or not testcase["output"]:
            return f"Testcase {i+1} has empty 'input' or 'output'."

    if not problem_data["description"]:
        return "Problem description (problem.md) cannot be empty."

    md_error = _validate_problem_md(problem_data["description"])
    if md_error:
        return md_error

    return None


def get_all_problems_metadata():
    try:
        problems_cursor = mongo.db.problems.find({}, {'_id': 0})
        problems_list = list(problems_cursor)
        return problems_list, None
    except Exception as e:
        return None, {"message": str(e)}

def get_problem_full_details(problem_id):
    try:
        # Extract contest_id and problem_letter from problem_id (e.g., C1A -> C1, A)
        match = re.match(r"(C\d+)([A-Z]+)", problem_id)
        if not match:
            return None, {"message": "Invalid problem ID format"}
        
        contest_id = match.group(1)
        problem_letter = match.group(2)

        # Check if contest has started
        contest_data, contest_error = contest_service.get_contest_details(contest_id)
        if contest_error:
            print(f"Error fetching contest details: {contest_error}")
            return None, {"message": f"Contest {contest_id} not found for problem {problem_id}"}

        start_time_str = contest_data.get('startTime')
        if start_time_str:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
            current_time = datetime.now(pytz.UTC)
            print(f"Contest ID: {contest_id}, Start Time: {start_time}, Current Time: {current_time}")
            if current_time < start_time:
                print(f"Contest {contest_id} has not started yet.")
                return None, {"message": "Contest has not started yet", "error_type": "contest_not_started"}

        base_path = f"data/contests/{contest_id}/problems/{problem_letter}"

        # Fetch meta.json
        meta_file_path = f"{base_path}/meta.json"
        meta_content, _, error = get_file(meta_file_path)
        if error:
            return None, {"message": f"Problem meta.json not found for {problem_id}"}
        meta_data = json.loads(meta_content)

        # Fetch problem.md (problem statement)
        problem_md_path = f"{base_path}/problem.md"
        problem_statement, _, error = get_file(problem_md_path)
        if error:
            problem_statement = "No problem statement available."

        # Fetch samples.json
        samples_json_path = f"{base_path}/samples.json"
        samples_content, _, error = get_file(samples_json_path)
        samples_data = []
        if not error:
            samples_data = json.loads(samples_content)

        # Check for PDF statement
        pdf_statement_path = f"{base_path}/statement.pdf"
        pdf_statement_exists, _, _ = get_file(pdf_statement_path)
        has_pdf_statement = pdf_statement_exists is not None

        full_problem_details = {
            "meta": meta_data,
            "problem_statement": problem_statement,
            "samples_data": samples_data,
            "has_pdf_statement": has_pdf_statement,
        }

        return full_problem_details, None
    except Exception as e:
        return None, {"message": str(e)}

def get_problem_by_id(problem_id):
    try:
        problem = mongo.db.problems.find_one({'id': problem_id}, {'_id': 0})
        if problem:
            return problem, None
        return None, {"message": "Problem not found"}
    except Exception as e:
        return None, {"message": str(e)}
