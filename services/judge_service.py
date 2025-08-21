import sys
import os
import json
import tempfile
import shutil

from services.github_services import get_file
from judge_image_for_annaforces.good_one import execute_code

def get_testcases(problem_id):
    testcases = []
    # Path to the file containing the number of test cases
    num_testcases_file_path = f'data/problems/{problem_id}/testcases/no.txt'
    
    # Get the content of no.txt
    number_of_testcases_str, _, error = get_file(num_testcases_file_path)
    
    if error:
        print(f"Error fetching number of test cases for problem {problem_id}: {error.get('message')}")
        return [] # Return empty list if we can't get the number of test cases

    try:
        number_of_testcases = int(number_of_testcases_str.strip())
    except (ValueError, TypeError):
        print(f"Error: Could not parse number of test cases from {num_testcases_file_path}. Content: {number_of_testcases_str}")
        return []

    for i in range(1, number_of_testcases + 1):
        input_file_path = f'data/problems/{problem_id}/testcases/{i}.in'
        output_file_path = f'data/problems/{problem_id}/testcases/{i}.out'
        
        stdin_content, _, stdin_error = get_file(input_file_path)
        stdout_content, _, stdout_error = get_file(output_file_path)
        
        if stdin_error:
            print(f"Error fetching input for test case {i} of problem {problem_id}: {stdin_error.get('message')}")
            continue # Skip this test case if input is not found
        if stdout_error:
            print(f"Error fetching output for test case {i} of problem {problem_id}: {stdout_error.get('message')}")
            continue # Skip this test case if output is not found

        testcases.append(
            {
                'stdin' : stdin_content,
                'stdout' : stdout_content.strip()
            }
        )
    
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
        print(f'Running {i + 1} testcase!')
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
                message = "Compilation Error"
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
