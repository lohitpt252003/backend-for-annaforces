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

# Create a session and set default headers
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Cache-Control": "no-cache" # Explicitly disable caching
})

HEADERS = session.headers # Keep HEADERS for compatibility if needed elsewhere

# --- In-Memory Queue for Write Operations ---
write_queue = queue.Queue()
MAX_RETRIES = 5

def _worker():
    while True:
        try:
            func, args, kwargs, retries = write_queue.get()
            print(f"[GitHub Worker] Processing item from queue: {func.__name__}")
            success = func(*args, **kwargs)
            if not success and retries < MAX_RETRIES:
                retry_delay = 2 ** retries
                print(f"Operation failed. Retrying in {retry_delay} seconds... (Attempt {retries + 1}/{MAX_RETRIES})")
                time.sleep(retry_delay)
                write_queue.put((func, args, kwargs, retries + 1))
            elif not success:
                print(f"Operation failed after {MAX_RETRIES} retries. Giving up.")
            write_queue.task_done()
        except Exception as e:
            print(f"Error in worker thread: {e}")

# Start the worker thread
worker_thread = threading.Thread(target=_worker, daemon=True)
worker_thread.start()

# --- Caching Layer ---
file_cache = {}
folder_cache = {}

def invalidate_cache(path=None):
    global file_cache, folder_cache
    if path:
        # Invalidate specific file or folder entries
        file_cache.pop(path, None)
        # Invalidate any folder that contains this path
        for key in list(folder_cache.keys()):
            if path.startswith(key):
                folder_cache.pop(key, None)
    else:
        # Invalidate all cache
        file_cache = {}
        folder_cache = {}

# --- Read Operations (Direct Execution) ---
def get_file(filename_path, force_refresh=False):
    if not filename_path:
        return None, None, {"error": True, "message": "filename_path cannot be empty"}

    # Check cache first, unless force_refresh is True
    if not force_refresh and filename_path in file_cache:
        return file_cache[filename_path]["content"], file_cache[filename_path]["sha"], None

    url = f"{API_BASE}/{filename_path}"

    try:
        response = session.get(url, timeout=60)

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

            # Cache the result
            file_cache[filename_path] = {"content": content, "sha": sha}
            return content, sha, None
        elif response.status_code == 404:
            return None, None, {"error": True, "message": f"File not found: {filename_path}"}
        else:
            return None, None, {"error": True, "message": f"Error getting file: {response.status_code} - {response.text}"}

    except requests.exceptions.RequestException as e:
        return None, None, {"error": True, "message": f"Request failed: {e}"}

def get_folder_contents(path):
    # Check cache first
    if path in folder_cache:
        return folder_cache[path], None

    url = f"{API_BASE}/{path}"
    try:
        response = session.get(url, timeout=60)
        if response.status_code == 200:
            contents = response.json()
            if isinstance(contents, list):
                # Cache the result
                folder_cache[path] = {"success": True, "data": contents}
                return {"success": True, "data": contents}, None
            else:
                return {"success": False, "error": "Path is not a folder or is a file"}, None
        else:
            return {"success": False, "error": f"GitHub API Error: {response.status_code}, {response.text}"}, None
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {e}"}, None

# --- Internal Write Operations (Executed by Worker) ---
def _execute_add_file(filename_path, data, commit_message):
    url = f"{API_BASE}/{filename_path}"
    message = commit_message or f"Add {filename_path}"
    payload = {
        "message": message,
        "content": base64.b64encode(str(data).encode('utf-8')).decode('ascii')
    }

    try:
        response = session.put(url, data=json.dumps(payload), timeout=30)
        if response.status_code in [200, 201]:
            print(f"Successfully added file: {filename_path}")
            invalidate_cache(filename_path)
            return True
        else:
            print(f"Error adding file {filename_path}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {filename_path}: {e}")
        return False

def _execute_update_file(filename_path, data, commit_message):
    url = f"{API_BASE}/{filename_path}"
    message = commit_message or f"Update {filename_path}"

    content, sha, error = get_file(filename_path)
    if error:
        print(f"Cannot update file - file not found or inaccessible: {error['message']}")
        return False

    payload = {
        "message": message,
        "content": base64.b64encode(str(data).encode('utf-8')).decode('ascii'),
        "sha": sha
    }
    
    try:
        response = session.put(url, data=json.dumps(payload), timeout=30)
        if response.status_code in [200, 201]:
            print(f"Successfully updated file: {filename_path}")
            invalidate_cache(filename_path)
            return True
        elif response.status_code == 409: # SHA conflict
            print(f"SHA conflict for {filename_path}. The operation will be retried by the worker.")
            return False # Let the worker re-queue this
        else:
            print(f"Error updating file {filename_path}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {filename_path}: {e}")
        return False


# --- Public Write Functions (Add to Queue) ---
def add_file(filename_path, data, commit_message=None):
    if not filename_path or data is None:
        return {"error": True, "message": "filename_path and data cannot be empty"}
    write_queue.put((_execute_add_file, (filename_path, data, commit_message), {}, 0))
    return {"success": True, "message": "Add operation queued."}

def update_file(filename_path, data, commit_message=None):
    if not filename_path or data is None:
        return {"error": True, "message": "filename_path and data cannot be empty"}
    write_queue.put((_execute_update_file, (filename_path, data, commit_message), {}, 0))
    return {"success": True, "message": "Update operation queued."}

def create_or_update_file(filename_path, data, commit_message=None):
    _content, _sha, error = get_file(filename_path, force_refresh=True)
    if error and "not found" in error["message"].lower():
        print(f"Queueing ADD for {filename_path}")
        add_file(filename_path, data, commit_message)
    elif not error:
        print(f"Queueing UPDATE for {filename_path}")
        update_file(filename_path, data, commit_message)
    else:
        print(f"Could not determine whether to add or update file {filename_path}: {error['message']}")
        return {"error": True, "message": f"Could not queue operation: {error['message']}"}
        
    return {"success": True, "message": "Create/Update operation queued."}


if __name__ == '__main__':
    # Example Usage
    print("Queueing file creation...")
    create_or_update_file("test_queue.txt", "Hello from the resilient queue!", "Test: Resilient Queueing")
    
    print("Waiting for queue to process...")
    write_queue.join() # Wait for all items to be processed
    print("Queue processing finished.")

    print("\nReading file content:")
    content, _, _ = get_file("test_queue.txt")
    print(content)
