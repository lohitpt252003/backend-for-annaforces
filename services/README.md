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
  - **Description**: Provides an interface for interacting with the GitHub API to manage files. To handle concurrency, it now includes an in-memory queue for all write operations (`add`, `update`), ensuring that file modifications are executed sequentially by a background worker thread. It also supports fetching files larger than 1MB by using the `download_url` provided by the GitHub API.
  - **Key Functions**:
    - `get_file(filename_path)`: Fetches the content and SHA of a file.
    - `add_file(filename_path, data, commit_message)`: Queues an operation to add a new file.
    - `update_file(filename_path, data, commit_message)`: Queues an operation to update an existing file.
    - `create_or_update_file(filename_path, data, commit_message)`: Queues an operation to add or update a file.
    - `get_folder_contents(path)`: Lists the contents of a folder.
  - **Dependencies**: `requests`, `json`, `os`, `base64`, `time`, `dotenv`, `queue`, `threading`.

- `judge_service.py`:
  - **Description**: Manages the automated judging of code submissions. To support live feedback, the `grade_submission` function is now a generator that executes test cases one by one and yields the result of each, allowing for incremental status updates.
  - **Key Functions**:
    - `get_testcases(problem_id)`: Fetches all test cases for a given problem.
    - `grade_submission(code, language, problem_id)`: A generator function that runs code against each test case and yields the result.
  - **Dependencies**: `os`, `json`, `requests`, `services.github_services`.

- `problem_service.py`:
  - **Description**: Handles the creation and management of programming problems. It validates problem data and orchestrates the storage of problem-related files on GitHub.
  - **Key Functions**:
    - `_validate_problem_md(description)`: Validates the structure and content of the `problem.md` description.
    - `_validate_problem_data(problem_data)`: Validates the overall problem data, including required fields and test case format.
    - `add_problem(problem_data)`: Adds a new problem, creating `meta.json`, `problem.md`, test case files, and updating the global problem index on GitHub.
  - **Dependencies**: `json`, `re`, `services.github_services`, `config.github_config`.

- `submission_service.py`:
  - **Description**: Manages the lifecycle of user code submissions using an asynchronous, live-updating approach. It immediately queues a submission for processing and returns a submission ID. A background thread then handles the judging process. After each test case, it updates the status in the main submission file as well as the reference files in the user and problem directories, ensuring live data consistency.
  - **Key Functions**:
    - `handle_new_submission(problem_id, user_id, language, code)`: Creates initial submission files, queues the submission for judging in a background thread, and returns an immediate response.
  - **Dependencies**: `os`, `time`, `json`, `threading`, `services.github_services`, `services.judge_service`, `config.github_config`.

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