import json
from services import github_services

CONTESTS_DATA_PATH = "data/contests"

def get_all_contests_metadata():
    index_file_path = f"{CONTESTS_DATA_PATH}/index.json"
    content, _, error = github_services.get_file(index_file_path)
    if error:
        return None, error
    try:
        return json.loads(content), None
    except json.JSONDecodeError:
        return None, {"error": True, "message": "Invalid JSON in contests index"}

def get_contest_details(contest_id):
    contest_dir_path = f"{CONTESTS_DATA_PATH}/{contest_id}"
    
    meta_file_path = f"{contest_dir_path}/meta.json"
    contest_md_file_path = f"{contest_dir_path}/contest.md"
    theory_md_file_path = f"{contest_dir_path}/theory.md"

    # Fetch meta.json
    meta_content, _, meta_error = github_services.get_file(meta_file_path)
    if meta_error:
        return None, meta_error
    try:
        contest_data = json.loads(meta_content)
    except json.JSONDecodeError:
        return None, {"error": True, "message": "Invalid JSON in contest metadata"}

    # Fetch contest.md
    contest_description, _, contest_desc_error = github_services.get_file(contest_md_file_path)
    if contest_desc_error and "not found" not in contest_desc_error["message"].lower():
        return None, contest_desc_error
    contest_data['contest_description'] = contest_description if contest_description else ""

    # Fetch theory.md
    contest_theory, _, contest_theory_error = github_services.get_file(theory_md_file_path)
    if contest_theory_error and "not found" not in contest_theory_error["message"].lower():
        return None, contest_theory_error
    contest_data['contest_theory'] = contest_theory if contest_theory else ""

    return contest_data, None
