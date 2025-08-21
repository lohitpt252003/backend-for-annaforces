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

print(get_testcases(1))

def grade_submission(code, language, problem_id):
    """
    Grades a submission by running it against all test cases for a given problem.
    """
    testcases = get_testcases(problem_id)
    
    if not testcases:
        return {"overall_status": "error", "message": "No test cases found for this problem."}

    results = []
    overall_status = "accepted" # Assume accepted until a test case fails

    extension = 'py'
    if language.lower() == 'python': extension = 'py'
    elif language.lower() == 'c': extension = 'c'
    elif language.lower() == 'c++': extension = 'cpp'
    

    for i, testcase in enumerate(testcases):
        print(f'Running {i + 1} testcase!')
        stdin = testcase.get('stdin', '')
        expected_stdout = testcase.get('stdout', '')
        result = execute_code(language, code, testcase.get('stdin'))
        print(result)
        # Run the code in a container
        # Assuming run_code_in_container returns stdout, stderr, exit_code, execution_time, memory_usage
        # stdout, stderr, exit_code, execution_time, memory_usage = run_code_in_container(code, language, stdin)

        test_status = "passed"
        message = "Test case passed"

        # if exit_code != 0:
        #     test_status = "runtime_error"
        #     message = f"Runtime Error: {stderr}"
        #     overall_status = "wrong_answer" # A runtime error means wrong answer overall
        # elif stdout.strip() != expected_stdout.strip():
        #     test_status = "wrong_answer"
        #     message = "Output mismatch"
        #     overall_status = "wrong_answer" # If any test case fails, overall status is wrong answer

        # results.append({
        #     "test_case_number": i + 1,
        #     "status": test_status,
        #     "message": message,
        #     "execution_time": execution_time,
        #     "memory_usage": memory_usage,
        #     "actual_output": stdout,
        #     "expected_output": expected_stdout
        # })
        
        if test_status != "passed":
            overall_status = "wrong_answer" # If any test case fails, overall status is wrong answer

    return {
        "overall_status": overall_status,
        "test_results": results
    }



code = 'print(int(input()) + int(input()))'
g = grade_submission(code, 'python', 1)
print(g)