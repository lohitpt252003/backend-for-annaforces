import json
from services.github_services import get_file, create_or_update_file
from config.github_config import GITHUB_USERS_BASE_PATH

def get_user_by_id(user_id):
    meta_path = f"{GITHUB_USERS_BASE_PATH}/{user_id}/meta.json"
    meta_content, _, meta_error = get_file(meta_path)

    if meta_error:
        return None, {"error": meta_error["message"]}

    try:
        meta_data = json.loads(meta_content)
        return meta_data, None
    except json.JSONDecodeError:
        return None, {"error": "Failed to decode meta.json"}
