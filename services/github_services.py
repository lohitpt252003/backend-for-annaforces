import base64
import requests
import json
import os
import time
from dotenv import load_dotenv
import queue
import threading

load_dotenv()

# --- GitHub Configuration ---
def get_github_config():
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    owner = os.getenv("GITHUB_OWNER")

    if not all([token, repo, owner]):
        return None, None, None, {
            "error": True,
            "message": "Missing required environment variables: GITHUB_TOKEN, GITHUB_REPO, GITHUB_OWNER"
        }

    return token, repo, owner, None

GITHUB_TOKEN, GITHUB_REPO, GITHUB_OWNER, config_error = get_github_config()
if config_error:
    print(f"Configuration Error: {config_error['message']}")
    exit(1)

API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# --- In-Memory Queue for Write Operations ---
write_queue = queue.Queue()

def _worker():
    while True:
        try:
            func, args, kwargs = write_queue.get()
            func(*args, **kwargs)
            write_queue.task_done()
        except Exception as e:
            print(f"Error in worker thread: {e}")

# Start the worker thread
worker_thread = threading.Thread(target=_worker, daemon=True)
worker_thread.start()

# --- Read Operations (Direct Execution) ---
def get_file(filename_path):
    if not filename_path:
        return None, None, {"error": True, "message": "filename_path cannot be empty"}

    url = f"{API_BASE}/{filename_path}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=60)

        if response.status_code == 200:
            resp_json = response.json()
            sha = resp_json['sha']

            if resp_json.get('content'):
                try:
                    content = base64.b64decode(resp_json['content']).decode('utf-8')
                except UnicodeDecodeError:
                    content = base64.b64decode(resp_json['content'])
            else:
                download_url = resp_json.get('download_url')
                if not download_url:
                    return None, None, {"error": True, "message": "File is large but no download_url found"}
                
                download_response = requests.get(download_url, timeout=60)
                if download_response.status_code == 200:
                    content = download_response.text
                else:
                    return None, None, {"error": True, "message": f"Failed to download large file: {download_response.status_code} - {download_response.text}"}

            return content, sha, None
        elif response.status_code == 404:
            return None, None, {"error": True, "message": f"File not found: {filename_path}"}
        else:
            return None, None, {"error": True, "message": f"Error getting file: {response.status_code} - {response.text}"}

    except requests.exceptions.RequestException as e:
        return None, None, {"error": True, "message": f"Request failed: {e}"}

def get_folder_contents(path):
    url = f"{API_BASE}/{path}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=60)
        if response.status_code == 200:
            contents = response.json()
            if isinstance(contents, list):
                return {"success": True, "data": contents}, None
            else:
                return {"success": False, "error": "Path is not a folder or is a file"}, None
        else:
            return {"success": False, "error": f"GitHub API Error: {response.status_code}, {response.text}"}, None
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {e}"}, None

# --- Internal Write Operations (Executed by Worker) ---
def _execute_add_file(filename_path, data, commit_message, retries=3):
    url = f"{API_BASE}/{filename_path}"
    message = commit_message or f"Add {filename_path}"
    payload = {
        "message": message,
        "content": base64.b64encode(str(data).encode('utf-8')).decode('ascii')
    }

    for attempt in range(retries):
        try:
            response = requests.put(url, headers=HEADERS, data=json.dumps(payload), timeout=30)
            if response.status_code in [200, 201]:
                print(f"Successfully added file: {filename_path}")
                return
            elif response.status_code == 422:
                print(f"Validation error adding file {filename_path}: {response.text}")
                return
            elif response.status_code == 409:
                 print(f"Conflict - file may already exist: {filename_path}")
                 return
            else:
                print(f"Error adding file {filename_path} (attempt {attempt + 1}/{retries}): {response.status_code} - {response.text}")
                time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {filename_path} (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(2 ** attempt)
    print(f"Failed to add file {filename_path} after {retries} retries.")

def _execute_update_file(filename_path, data, commit_message, retries=3):
    url = f"{API_BASE}/{filename_path}"
    message = commit_message or f"Update {filename_path}"

    content, sha, error = get_file(filename_path)
    if error:
        print(f"Cannot update file - file not found or inaccessible: {error['message']}")
        return

    payload = {
        "message": message,
        "content": base64.b64encode(str(data).encode('utf-8')).decode('ascii'),
        "sha": sha
    }
    
    for attempt in range(retries):
        try:
            response = requests.put(url, headers=HEADERS, data=json.dumps(payload), timeout=30)
            if response.status_code in [200, 201]:
                print(f"Successfully updated file: {filename_path}")
                return
            elif response.status_code == 409: # SHA conflict
                print(f"SHA conflict for {filename_path}. Retrying...")
                new_content, new_sha, new_error = get_file(filename_path)
                if new_error:
                    print(f"SHA conflict and unable to retrieve updated SHA for {filename_path}")
                    time.sleep(2 ** attempt)
                    continue
                payload["sha"] = new_sha
                # We need to re-read the content and apply changes if necessary.
                # This simple queue doesn't handle that. For now, we just retry with the new SHA.
                time.sleep(2 ** attempt)
                continue
            else:
                print(f"Error updating file {filename_path} (attempt {attempt + 1}/{retries}): {response.status_code} - {response.text}")
                time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {filename_path} (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(2 ** attempt)
    print(f"Failed to update file {filename_path} after {retries} retries.")


# --- Public Write Functions (Add to Queue) ---
def add_file(filename_path, data, commit_message=None):
    if not filename_path or data is None:
        return {"error": True, "message": "filename_path and data cannot be empty"}
    write_queue.put((_execute_add_file, (filename_path, data, commit_message), {}))
    return {"success": True, "message": "Add operation queued."}

def update_file(filename_path, data, commit_message=None):
    if not filename_path or data is None:
        return {"error": True, "message": "filename_path and data cannot be empty"}
    write_queue.put((_execute_update_file, (filename_path, data, commit_message), {}))
    return {"success": True, "message": "Update operation queued."}

def create_or_update_file(filename_path, data, commit_message=None):
    # This function needs to decide whether to add or update.
    # To avoid a race condition, we'll optimistically try to update,
    # and if it fails because the file doesn't exist, we'll queue an add.
    # A more robust solution might involve a specific "create_or_update" task in the worker.
    
    # For simplicity, we will read first, then queue the appropriate action.
    # This is not perfectly race-proof but is better than nothing.
    _content, _sha, error = get_file(filename_path)
    if error and "not found" in error["message"].lower():
        print(f"Queueing ADD for {filename_path}")
        add_file(filename_path, data, commit_message)
    elif not error:
        print(f"Queueing UPDATE for {filename_path}")
        update_file(filename_path, data, commit_message)
    else:
        # Some other error occurred during the read
        print(f"Could not determine whether to add or update file {filename_path}: {error['message']}")
        return {"error": True, "message": f"Could not queue operation: {error['message']}"}
        
    return {"success": True, "message": "Create/Update operation queued."}


if __name__ == '__main__':
    # Example Usage
    print("Queueing file creation...")
    create_or_update_file("test_queue.txt", "Hello from the queue!", "Test: Queueing")
    
    print("Waiting for queue to process...")
    write_queue.join() # Wait for all items to be processed
    print("Queue processing finished.")

    print("\nReading file content:")
    content, _, _ = get_file("test_queue.txt")
    print(content)