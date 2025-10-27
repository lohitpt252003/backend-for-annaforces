import time
import os
import json
import re
import requests
from dotenv import load_dotenv
import subprocess

load_dotenv()

from extensions import mongo
from services.github_services import get_file, get_folder_contents
from services import problem_service

SIZE = 50

def get_testcases(problem_id):
    print(f"--- Starting get_testcases for problem_id: {problem_id} ---")
    testcases = []
    
    match = re.match(r'^(C\d+)([A-Z]+)$', problem_id)
    if not match:
        print(f"Invalid problem ID format for get_testcases: {problem_id}")
        return []
    contest_id = match.group(1)
    problem_letter = match.group(2)

    testcases_path = f'data/contests/{contest_id}/problems/{problem_letter}/testcases'
    
    print(f"[Get Testcases] Fetching test cases from: {testcases_path}")
    contents_response, error = get_folder_contents(testcases_path)
    print(f"[Get Testcases] Contents response: {contents_response}")

    if error or not contents_response.get('success'):
        error_message = error['message'] if error else contents_response.get('error', 'Unknown error')
        print(f"Error fetching test cases for problem {problem_id}: {error_message}")
        return []

    contents_list = contents_response.get('data', [])
    
    file_download_urls = {}
    for item in contents_list:
        if item['type'] == 'file' and item['name'].endswith('.in'):
            file_download_urls[item['path']] = item['download_url']

    print(f"[Get Testcases] File download URLs: {file_download_urls}")

    if not file_download_urls:
        return []

    print()
    print(SIZE * '=' + " EXTRACTING TESTCASES " + SIZE * '=')
    for file_path, download_url in file_download_urls.items():
        input_content_resp = requests.get(download_url)

        if input_content_resp.status_code == 200:
            print(f"[Get Testcases] Fetched content for {file_path}: {input_content_resp.text}")
            testcases.append({
                'stdin': input_content_resp.text,
                'path': file_path
            })
        else:
            print(f"Warning: Failed to fetch content for test case {file_path}")

    print(testcases)
    print(SIZE * '=' + " DONE WITH EXTRACTING TESTCASES " + SIZE * '=')
    print()

    return testcases

def _execute_testcase(code, language, stdin, time_limit_s, memory_limit_mb):
    url = os.getenv('EXECUTE_API_SERVER_URL')
    payload = {
        "language": language,
        "code": code,
        "stdin": stdin,
        "timelimit": str(time_limit_s),
        "memorylimit": str(memory_limit_mb)
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        print(f"Error calling execution server: {e}")
        return None, {"overall_status": "error", "message": "Code execution server is not running. Please contact the admin."}

import subprocess

def grade_submission(submission_id, code, language, problem_id):
    """
    Grades a submission by running it against all test cases for a given problem.
    This function returns a list of results for each test case.
    """
    all_test_results = []
    try:
        print("GRADING A SUBMISSION NOW")
        
        match = re.match(r'^(C\d+)([A-Z]+)$', problem_id)
        if not match:
            print(f"Invalid problem ID format for get_testcases: {problem_id}")
            return []
        contest_id = match.group(1)
        problem_letter = match.group(2)

    
        # Get problem metadata for time and memory limits from GitHub
        problem_meta_path = f'data/contests/{contest_id}/problems/{problem_letter}/meta.json'
        problem_meta_content, _, problem_meta_error = get_file(problem_meta_path)

        if problem_meta_error:
            return {"overall_status": "error", "message": f"Failed to get problem metadata: {problem_meta_error['message']}"}

        try:
            problem_meta_data = json.loads(problem_meta_content)
            time_limit_ms = int(problem_meta_data.get("timeLimit", 2000)) # Default to 2000ms
            memory_limit_mb = int(problem_meta_data.get("memoryLimit", 256)) # Default to 256MB
        except json.JSONDecodeError:
            return {"overall_status": "error", "message": "Failed to decode problem meta.json"}

        # Convert time limit from milliseconds to seconds for the judge service
        time_limit_s = max(1, time_limit_ms // 1000) # Ensure at least 1 second

        print("[Grade Submission] Calling get_testcases...")
        testcases = get_testcases(problem_id)
        
        print(f"[Grade Submission] Test cases: {testcases}")

        if not testcases:
            return {"overall_status": "error", "message": "No test cases found for this problem."}

        # Get validator path from GitHub
        validator_path = f'data/contests/{contest_id}/problems/{problem_letter}/validator.py'
        validator_content, _, validator_error = get_file(validator_path)
        if validator_error:
            return {"overall_status": "error", "message": f"Failed to get validator.py: {validator_error['message']}"}


        
        for i, testcase in enumerate(testcases):
            mongo.db.submissions_queue.update_one(
                {"_id": submission_id},
                {"$set": {"status": f"running test case {i + 1}"}}
            )
            print(SIZE * '=' + f' Running testcase {i + 1}! ' + '=' * SIZE)
            stdin = testcase.get('stdin', '') # Assuming 'stdin' field in testcase from GitHub
            
            result, error = _execute_testcase(code, language, stdin, time_limit_s, memory_limit_mb)
            if error:
                all_test_results.append(error)
                continue

            print(result)

            stdout = result.get('stdout', '')
            stderr = result.get('stderr', '')
            err = result.get('err', '')
            timetaken = result.get('timetaken', 0)
            memorytaken = result.get('memorytaken', 0)

            test_status = "passed"
            message = "Test case passed"

            # print("BEFORE err")
            if err:
                if "Compilation Error" in err:
                    test_status = "compilation_error"
                    message = f"Compilation Error: {stderr}"
                elif "Time Limit Exceeded" in err:
                    test_status = "time_limit_exceeded"
                    message = "Time Limit Exceeded"
                elif "Memory Limit Exceeded" in err:
                    test_status = "memory_limit_exceeded"
                    message = "Memory Limit Exceeded"
                else:
                    test_status = "runtime_error"
                    message = f"Runtime Error: {stderr}"
            else:
                # print("NOW NO ERR")
                # Validate the output using the validation service
                validation_url = os.getenv("VALIDATOR_API_URL")
                validation_payload = {
                    "validator_language": "python",
                    "validator_code": validator_content,
                    "user_output": stdout,
                    "test_input": stdin
                }
                headers = {'Content-Type': 'application/json'}
                
                try:
                    validation_response = requests.post(validation_url, data=json.dumps(validation_payload), headers=headers, timeout=30)
                    validation_response.raise_for_status()
                    validation_result = validation_response.json()
                    
                    verdict = validation_result.get("stdout", "").strip()
                    print(f"The verdict is {verdict}")
                    if verdict != "Accepted":
                        test_status = "wrong_answer"
                        message = "Output mismatch"
                        
                except requests.exceptions.RequestException as e:
                    test_status = "runtime_error"
                    message = f"Validator service error: {e}"
            
            print(f"[Grade Submission] Determined test_status: {test_status}")
            result["status"] = test_status
            result["message"] = message
            result["stdin"] = stdin
            print(f"[Grade Submission] Appending result: {result}")
            all_test_results.append(result)
        
        return all_test_results

    except Exception as e:
        print(f"[Grade Submission] An unexpected error occurred: {e}")
        return {"overall_status": "error", "message": f"An unexpected error occurred during grading: {e}"}