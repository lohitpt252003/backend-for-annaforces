import json
import re
from services.github_services import get_file, create_or_update_file, add_file
from config.github_config import GITHUB_PROBLEMS_BASE_PATH



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

def add_problem(problem_data):
    # 1. Validate problem data
    error = _validate_problem_data(problem_data)
    print(_validate_problem_data(problem_data))
    if error:
        return {"error": error}

    # 2. Get index.json to determine new problem ID
    index_path = f"{GITHUB_PROBLEMS_BASE_PATH}/index.json"
    index_content, _, index_error = get_file(index_path)
    print('problems_service.py index_path ', index_path)

    if index_error:
        return {"error": f"Failed to get problems index: {index_error['message']}"}

    try:
        index_data = json.loads(index_content)
        if not index_data:
            new_problem_id_num = 1
        else:
            problem_ids = [int(k.replace('P', '')) for k in index_data.keys()]
            new_problem_id_num = max(problem_ids) + 1
        new_problem_id = f"P{new_problem_id_num}"
    except (json.JSONDecodeError, ValueError):
        return {"error": "Failed to decode problems index.json or parse problem IDs"}

    # 3. Create problem directory and files
    problem_dir_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{new_problem_id}"

    # Create meta.json
    meta_data = {
        "id": new_problem_id,
        "title": problem_data["title"],
        "timeLimit": problem_data["time_limit"],
        "memoryLimit": problem_data["memory_limit"],
        "number_of_submissions": 0
    }
    meta_path = f"{problem_dir_path}/meta.json"
    add_meta_result = create_or_update_file(meta_path, json.dumps(meta_data, indent=2), f"Add meta.json for {new_problem_id}")
    if "error" in add_meta_result:
        return {"error": f"Failed to add meta.json: {add_meta_result['message']}"}

    # Create problem.md
    problem_md_path = f"{problem_dir_path}/problem.md"
    add_problem_md_result = create_or_update_file(problem_md_path, problem_data["description"], f"Add problem.md for {new_problem_id}")
    if "error" in add_problem_md_result:
        return {"error": f"Failed to add problem.md: {add_problem_md_result['message']}"}

    # Create testcases
    testcases_dir_path = f"{problem_dir_path}/testcases"
    for i, testcase in enumerate(problem_data["testcases"]):
        input_path = f"{testcases_dir_path}/{i+1}.in"
        output_path = f"{testcases_dir_path}/{i+1}.out"
        add_input_result = create_or_update_file(input_path, testcase["input"], f"Add testcase {i+1}.in for {new_problem_id}")
        if "error" in add_input_result:
            return {"error": f"Failed to add testcase input: {add_input_result['message']}"}
        add_output_result = create_or_update_file(output_path, testcase["output"], f"Add testcase {i+1}.out for {new_problem_id}")
        if "error" in add_output_result:
            return {"error": f"Failed to add testcase output: {add_output_result['message']}"}

    # Create submissions directory
    submissions_dir_path = f"{problem_dir_path}/submissions"
    gitkeep_path = f"{submissions_dir_path}/.gitkeep"
    add_gitkeep_result = create_or_update_file(gitkeep_path, "", f"Create submissions directory for {new_problem_id}")
    if "error" in add_gitkeep_result:
        return {"error": f"Failed to create submissions directory: {add_gitkeep_result['message']}"}

    # 4. Update index.json
    index_data[new_problem_id] = {
        "title": problem_data["title"],
        "difficulty": problem_data["difficulty"],
        "tags": problem_data["tags"],
        "authors": problem_data["authors"]
    }
    update_index_result = create_or_update_file(index_path, json.dumps(index_data, indent=2), f"Add {new_problem_id} to index.json")
    if "error" in update_index_result:
        return {"error": f"Failed to update index.json: {update_index_result['message']}"}

    return {"message": "Problem added successfully", "problem_id": new_problem_id}
