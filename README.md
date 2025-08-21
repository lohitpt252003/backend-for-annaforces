# Backend for AnnaForces

This is the backend for the AnnaForces application.

## API Documentation

### Authentication API

This API is responsible for user authentication.

#### Get User Information

*   **Endpoint:** `/user/<user_id>`
*   **Method:** `GET`
*   **Description:** Fetches user information from the GitHub repository and returns it along with a JWT token for authentication.
*   **URL Parameters:**
    *   `user_id` (string, required): The ID of the user.
*   **Success Response (200):**
    *   **Content:**
        ```json
        {
            "user": {
                "name": "John Doe",
                "username": "johndoe",
                "user_id": "12345"
            },
            "token": "your.jwt.token"
        }
        ```
*   **Error Responses:**
    *   **404 Not Found:** If the user's data file is not found in the repository.
        ```json
        {
            "error": "File not found"
        }
        ```
    *   **500 Internal Server Error:** If the user's data file is not a valid JSON.
        ```json
        {
            "error": "Failed to decode user data."
        }
        ```

### Problems API

This API is responsible for fetching problem information.

#### Get All Problems

*   **Endpoint:** `/api/problems`
*   **Method:** `GET`
*   **Description:** Fetches a list of all available problems.
*   **Success Response (200):**
    *   **Content:**
        ```json
        [
            {
                "id": "problem1",
                "title": "Problem 1 Title"
            },
            {
                "id": "problem2",
                "title": "Problem 2 Title"
            }
        ]
        ```
*   **Error Responses:**
    *   **404 Not Found:** If `data/problem_list.json` is not found.
        ```json
        {
            "error": "file data/problem_list.json not found"
        }
        ```
    *   **500 Internal Server Error:** If the problem list data is not a valid JSON.
        ```json
        {
            "error": "Failed to decode problem list data."
        }
        ```

#### Get Problem by ID

*   **Endpoint:** `/api/problems/<problem_id>`
*   **Method:** `GET`
*   **Description:** Fetches the details of a specific problem.
*   **URL Parameters:**
    *   `problem_id` (string, required): The ID of the problem.
*   **Success Response (200):**
    *   **Content:**
        ```json
        {
          "authors": [
            1
          ],
          "constraints": {
            "-100 <= a <= 100": true,
            "-100 <= b <= 100": true
          },
          "description": "There is nothing to describe the problem\nAuthor has covered everything in the statment itself.",
          "id": 1,
          "input_format": "Two integers a and b",
          "language_supported": "c, cpp, py",
          "output_format": "Print a + b in single line",
          "sample_testcases": [
            {
              "explanation": "1 + 2 = 3",
              "input": "1 2",
              "output": "3"
            },
            {
              "explanation": "2 + 3 = 5",
              "input": "2 3",
              "output": "5"
            }
          ],
          "space_limit": "1MB",
          "statement": "Add the given two numbers",
          "tags": [
            "input",
            "output",
            "basic"
          ],
          "testers": [
            1
          ],
          "time_limit": "1s",
          "title": "Add"
        }
        ```
*   **Error Responses:**
    *   **404 Not Found:** If the problem with the given ID is not found.
        ```json
        {
            "error": "Problem with id <problem_id> not found"
        }
        ```
    *   **500 Internal Server Error:** If the problem data is not a valid JSON.
        ```json
        {
            "error": "Failed to decode problem data for problem id <problem_id>."
        }
        ```

### Submissions API

This API is responsible for grading code submissions.

#### Grade Submission

*   **Endpoint:** `/api/problems/<problem_id>/submit`
*   **Method:** `POST`
*   **Description:** Submits code for grading against a specific problem.
*   **Request Body:**
    ```json
    {
        "code": "#include <iostream>\nint main() {\n    int a, b;
    std::cin >> a >> b;
    std::cout << a + b;
    return 0;
}",
        "language": "c++",
        "problem_id": "1"
    }
    ```
*   **Success Response (200):**
    *   **Content:** The response will include an `overall_status` and a list of `test_results`.
    *   **`overall_status` can be one of:** `accepted`, `wrong_answer`, `time_limit_exceeded`, `memory_limit_exceeded`, `compilation_error`, `runtime_error`.
    *   **Example (Accepted):**
        ```json
        {
            "overall_status": "accepted",
            "test_results": [
                {
                    "actual_output": "2",
                    "execution_time": 0.0,
                    "expected_output": "2",
                    "memory_usage": 3.3671875,
                    "message": "Test case passed",
                    "status": "passed",
                    "test_case_number": 1
                },
                {
                    "actual_output": "4",
                    "execution_time": 0.0,
                    "expected_output": "4",
                    "memory_usage": 3.5078125,
                    "message": "Test case passed",
                    "status": "passed",
                    "test_case_number": 2
                }
            ]
        }
        ```
*   **Error Responses:**
    *   **404 Not Found:** If the problem with the given ID is not found.
        ```json
        {
            "error": "Problem with id <problem_id> not found"
        }
        ```
    *   **500 Internal Server Error:** If there is an issue with the judging process (e.g., no test cases found, compilation error).
        ```json
        {
            "overall_status": "error",
            "message": "No test cases found for this problem."
        }
        ```

#### Submission Storage

All code submissions and their results are stored directly in the configured GitHub repository. This allows for persistent storage and easy access to submission history.

**Folder Structure:**

Submissions are organized into two main categories: user-specific and problem-specific.

*   **User-Specific Submissions:**
    *   **Path:** `data/users/{user_id}/{problem_id}/{verdict}/`
    *   **Files:**
        *   `last_submission.txt`: Stores a simple integer representing the count of submissions for that specific user, problem, and verdict. This is used to generate unique filenames for each submission.
        *   `{submission_no}.json`: Contains the detailed JSON result of a specific submission. `{submission_no}` corresponds to the count from `last_submission.txt`.

*   **Problem-Specific Submissions:**
    *   **Path:** `data/problems/{problem_id}/{user_id}/{verdict}/`
    *   **Files:**
        *   `last_submission.txt`: Similar to the user-specific version, this stores the count of submissions for a given problem, user, and verdict.
        *   `{submission_no}.json`: Contains the detailed JSON result of a specific submission for that problem and user.

**Implicit Folder Creation:**

Folders within the `data/` directory (e.g., `users/`, `problems/`, `user_id/`, `problem_id/`, `verdict/`) are created automatically by the GitHub API when the first file is added to a new path. There is no need for explicit folder creation.

### Judge API

The Judge API is not a separate service but a core component of the backend responsible for executing code submissions securely. It uses a dedicated module, `judge_image_for_annaforces`, which leverages Docker to create an isolated environment for each submission.

#### How It Works

1.  **Sandboxing:** Each submission is run inside a Docker container to prevent it from accessing the host system or interfering with other submissions.
2.  **Resource Limiting:** The execution is strictly limited by time and memory constraints defined for the problem.
3.  **Supported Languages:** The judge currently supports C, C++, and Python.
4.  **Execution Process:**
    *   The user's code and the problem's test cases are copied into the container.
    *   For C and C++, the code is first compiled. If compilation fails, an error is returned.
    *   The code is then executed against each test case.
    *   The output of the code is compared with the expected output for each test case.
5.  **Results:** The judge returns detailed results for each test case, including status (passed, wrong answer, time limit exceeded, etc.), execution time, and memory usage.
