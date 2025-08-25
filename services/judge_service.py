import sys
import os
import json
import tempfile
import shutil

from services.github_services import get_file, get_folder_contents
from judge_image_for_annaforces.good_one import execute_code


SIZE = 50

def get_testcases(problem_id):
    testcases = []
    testcases_path = f'data/problems/{problem_id}/testcases'
    
    contents = get_folder_contents(testcases_path)

    if not contents['success']:
        print(f"Error fetching test cases for problem {problem_id}: {contents['error']}")
        return []

    testcase_files = contents['data']
    
    # Find the highest test case number from the .in files
    max_test_case = 0
    for filename in testcase_files:
        if filename.endswith('.in'):
            try:
                num = int(os.path.splitext(os.path.basename(filename))[0])
                if num > max_test_case:
                    max_test_case = num
            except ValueError:
                continue

    if max_test_case == 0:
        return []

    print()
    print(SIZE * '=' + " EXTRACTING TESTCASES " + SIZE * '=')
    for i in range(1, max_test_case + 1):
        input_filename = f'{testcases_path}/{i}.in'
        output_filename = f'{testcases_path}/{i}.out'

        if input_filename in testcase_files and output_filename in testcase_files:
            testcases.append({
                'stdin': testcase_files[input_filename],
                'stdout': testcase_files[output_filename].strip()
            })
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
    testcases = get_testcases(problem_id)
    
    if not testcases:
        return {"overall_status": "error", "message": "No test cases found for this problem."}

    results = []
    verdicts = []

    for i, testcase in enumerate(testcases):
        print(SIZE * '=' + f' Running testcase {i + 1}! ' + '=' * SIZE)
        stdin = testcase.get('stdin', '')
        expected_stdout = testcase.get('stdout', '')
        
        result = execute_code(language, code, testcase.get('stdin'))
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
            "actual_output": stdout,
            "expected_output": expected_stdout
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
