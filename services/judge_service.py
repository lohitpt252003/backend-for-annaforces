import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from services.github_services import get_file, get_folder_contents
from config.github_config import GITHUB_PROBLEMS_BASE_PATH

SIZE = 50

def get_testcases(problem_id):
    testcases = []
    testcases_path = f'{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/testcases'
    
    contents_response, error = get_folder_contents(testcases_path)

    if error or not contents_response.get('success'):
        error_message = error['message'] if error else contents_response.get('error', 'Unknown error')
        print(f"Error fetching test cases for problem {problem_id}: {error_message}")
        return []

    contents_list = contents_response.get('data', [])
    
    file_download_urls = {}
    for item in contents_list:
        if item['type'] == 'file':
            file_download_urls[item['path']] = item['download_url']

    max_test_case = 0
    for filename_path in file_download_urls.keys():
        if filename_path.endswith('.in'):
            try:
                base_filename = os.path.basename(filename_path)
                num = int(os.path.splitext(base_filename)[0])
                if num > max_test_case:
                    max_test_case = num
            except ValueError:
                continue

    if max_test_case == 0:
        return []

    print()
    print(SIZE * '=' + " EXTRACTING TESTCASES " + SIZE * '=')
    for i in range(1, max_test_case + 1):
        input_file_full_path = f'{testcases_path}/{i}.in'
        output_file_full_path = f'{testcases_path}/{i}.out'

        if input_file_full_path in file_download_urls and output_file_full_path in file_download_urls:
            input_content_resp = requests.get(file_download_urls[input_file_full_path])
            output_content_resp = requests.get(file_download_urls[output_file_full_path])

            if input_content_resp.status_code == 200 and output_content_resp.status_code == 200:
                testcases.append({
                    'stdin': input_content_resp.text,
                    'stdout': output_content_resp.text.strip()
                })
            else:
                print(f"Warning: Failed to fetch content for test case {i}")
        else:
            print(f"Warning: Missing input or output file for test case {i}")

    print(testcases)
    print(SIZE * '=' + " DONE WITH EXTRACTING TESTCASES " + SIZE * '=')
    print()

    return testcases

def grade_submission(code, language, problem_id):
    """
    Grades a submission by running it against all test cases for a given problem.
    """

    # Get problem metadata for time and memory limits
    problem_meta_path = f"{GITHUB_PROBLEMS_BASE_PATH}/{problem_id}/meta.json"
    problem_meta_content, _, problem_meta_error = get_file(problem_meta_path)

    if problem_meta_error:
        return {"overall_status": "error", "message": f"Failed to get problem metadata: {problem_meta_error['message']}"}

    try:
        problem_meta_data = json.loads(problem_meta_content)
        time_limit_ms = problem_meta_data.get("timeLimit", 2000) # Default to 2000ms
        memory_limit_mb = problem_meta_data.get("memoryLimit", 256) # Default to 256MB
    except json.JSONDecodeError:
        return {"overall_status": "error", "message": "Failed to decode problem meta.json"}

    # Convert time limit from milliseconds to seconds for the judge service
    time_limit_s = max(1, time_limit_ms // 1000) # Ensure at least 1 second

    
    testcases = get_testcases(problem_id)
    
    if not testcases:
        return {"overall_status": "error", "message": "No test cases found for this problem."}

    results = []
    verdicts = []

    for i, testcase in enumerate(testcases):
        print(SIZE * '=' + f' Running testcase {i + 1}! ' + '=' * SIZE)
        stdin = testcase.get('stdin', '')
        expected_stdout = testcase.get('stdout', '')
        
        url = os.getenv('JUDGE_API_SERVER_URL')
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
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling execution server: {e}")
            return {"overall_status": "error", "message": "Code execution server is not running. Please contact the admin."}
        
        print(result)

        stdout = result.get('stdout', '')
        stderr = result.get('stderr', '')
        err = result.get('err', '')
        timetaken = result.get('timetaken', 0)
        memorytaken = result.get('memorytaken', 0)

        test_status = "passed"
        message = "Test case passed"

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
                message = f"Runtime Error: {err}"
        elif stdout.strip() != expected_stdout.strip():
            test_status = "wrong_answer"
            message = "Output mismatch"
        print()
        verdicts.append(test_status)

        results.append({
            "test_case_number": i + 1,
            "status": test_status,
            "message": message,
            "execution_time": timetaken,
            "memory_usage": memorytaken,
            "actual_output": stdout.strip(),
            "expected_output": expected_stdout,
            "input": stdin
        })

    # Determine overall status based on the verdicts
    overall_status = "accepted"
    if "compilation_error" in verdicts:
        overall_status = "compilation_error"
    elif "runtime_error" in verdicts:
        overall_status = "runtime_error"
    elif "time_limit_exceeded" in verdicts:
        overall_status = "time_limit_exceeded"
    elif "memory_limit_exceeded" in verdicts:
        overall_status = "memory_limit_exceeded"
    elif "wrong_answer" in verdicts:
        overall_status = "wrong_answer"

    return {
        "overall_status": overall_status,
        "test_results": results
    }