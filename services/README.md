# Services

This directory contains various service modules used in the `backend-for-annaforces` application. Each service encapsulates specific business logic and interacts with external resources like GitHub or Firebase.

## Modules:

- `__init__.py`: Initializes the services package.

- `cache_service.py`: (Empty) This file is currently empty and does not contain any caching logic.

- `contest_service.py`: (Empty) This file is currently empty and does not contain any contest-related functionalities.

- `firebase_service.py`:
  - **Description**: Handles integration with Google Firebase Firestore for user management.
  - **Key Functions**:
    - `get_user(user_id)`: Fetches user data from Firestore.
    - `add_user(user_id, password)`: Adds a new user with a hashed password.
    - `verify_user(user_id, password)`: Verifies a user's password against the stored hash.
  - **Dependencies**: `firebase_admin`, `argon2`, `dotenv`, `json`, `os`.

- `github_services.py`:
  - **Description**: Provides an interface for interacting with the GitHub API to manage files and directories within a specified repository. It now supports fetching files larger than 1MB by using the `download_url` provided by the GitHub API.
  - **Key Functions**:
    - `get_github_config()`: Retrieves GitHub authentication details from environment variables.
    - `get_file(filename_path)`: Fetches the content and SHA of a file, handling large files transparently.
    - `add_file(filename_path, data, commit_message)`: Adds a new file to the repository.
    - `update_file(filename_path, data, commit_message)`: Updates an existing file.
    - `create_or_update_file(filename_path, data, commit_message)`: Adds a file if it doesn't exist, otherwise updates it.
    - `get_folder_contents(path)`: Lists the contents of a folder in the repository.
  - **Dependencies**: `requests`, `json`, `os`, `base64`, `time`, `dotenv`.

- `judge_service.py`:
  - **Description**: Manages the automated judging process for code submissions. It retrieves test cases from GitHub and sends the code to an external code execution server for judging. It then determines the submission's verdict based on the results from the execution server.
  - **Key Functions**:
    - `get_testcases(problem_id)`: Fetches input and output test cases for a given problem from GitHub.
    - `grade_submission(code, language, problem_id)`: Sends the provided code to an external server for execution against all test cases and returns detailed results, including status (e.g., accepted, wrong answer, time limit exceeded). If the execution server is not running, it returns an error message.
  - **Dependencies**: `os`, `json`, `requests`, `services.github_services`.

- `problem_service.py`:
  - **Description**: Handles the creation and management of programming problems. It validates problem data and orchestrates the storage of problem-related files on GitHub.
  - **Key Functions**:
    - `_validate_problem_md(description)`: Validates the structure and content of the `problem.md` description.
    - `_validate_problem_data(problem_data)`: Validates the overall problem data, including required fields and test case format.
    - `add_problem(problem_data)`: Adds a new problem, creating `meta.json`, `problem.md`, test case files, and updating the global problem index on GitHub.
  - **Dependencies**: `json`, `re`, `services.github_services`, `config.github_config`.

- `submission_service.py`:
  - **Description**: Manages the lifecycle of user code submissions, from creation to grading and recording.
  - **Key Functions**:
    - `handle_new_submission(problem_id, user_id, language, code)`: Processes a new submission, generates a submission ID, stores code and metadata, triggers grading, and updates relevant problem and user records.
  - **Dependencies**: `os`, `time`, `json`, `sys`, `services.github_services`, `services.judge_service`, `config.github_config`.

- `user_service.py`:
  - **Description**: Provides functionalities for retrieving user-specific data and submission history.
  - **Key Functions**:
    - `get_user_by_id(user_id)`: Fetches a user's metadata.
    - `get_user_submissions(user_id)`: Retrieves all submissions made by a specific user.
  - **Dependencies**: `json`, `services.github_services`, `config.github_config`.

- `__pycache__`: Directory containing compiled Python files.

## Recent Bug Fixes

- **`github_services.py`:**
  - Fixed an issue where files larger than 1MB could not be fetched from GitHub. The service now uses the `download_url` for large files.
- **`judge_service.py`:**
  - Fixed a bug related to tuple indexing when fetching test cases.
- **`submission_service.py`:**
  - Fixed an issue where the service was not returning detailed test results.
  - Fixed a bug that caused the service to crash if there was an error adding a submission to the database.
  - Corrected a syntax error that prevented the service from returning any value.
  - Standardized the language parameter for C++ submissions to "c++".