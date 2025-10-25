import json
import re
from services.github_services import get_file, create_or_update_file, add_file
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
        problem = mongo.db.problems.find_one({'id': problem_id}, {'_id': 0})
        if problem:
            return problem, None
        return None, {"message": "Problem not found"}
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
