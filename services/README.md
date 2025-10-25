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
  - **Description**: Manages the automated judging of code submissions. It accepts a `submission_id` to provide live status updates during the grading process. For each test case, it calls the executor service to run the code and then calls the executor's `/api/validate` endpoint to get a verdict.
  - **Key Functions**:
    - `get_testcases(problem_id)`: Fetches all test cases for a given problem.
    - `grade_submission(submission_id, code, language, problem_id)`: Grades a submission and provides live status updates.
  - **Dependencies**: `os`, `json`, `requests`, `services.github_services`, `extensions.mongo`.

- `problem_service.py`:
  - **Description**: Handles the creation and management of programming problems. It validates problem data and orchestrates the storage of problem-related files on GitHub.
  - **Key Functions**:
    - `_validate_problem_md(description)`: Validates the structure and content of the `problem.md` description.
    - `_validate_problem_data(problem_data)`: Validates the overall problem data, including required fields and test case format.
    - `add_problem(problem_data)`: Adds a new problem (with ID format `C<contest_id><problem_letter>`), creating `meta.json`, `problem.md`, test case files, and updating the global problem index on GitHub.
  - **Dependencies**: `json`, `re`, `services.github_services`, `config.github_config`.

- `submission_service.py`:
  - **Description**: Manages the lifecycle of user code submissions using a persistent, MongoDB-based queue. The `handle_new_submission` function adds new submissions to the queue. A background worker, started by `init_app`, continuously polls this queue, picks up new submissions, and passes them to the `judge_service` for grading, including the `submission_id` for live status updates.
  - **Key Functions**:
    - `handle_new_submission(problem_id, username, language, code)`: Adds a new submission to the MongoDB queue.
    - `worker()`: The background worker function that processes submissions from the queue.
    - `init_app(app)`: Initializes the background worker thread.
  - **Dependencies**: `os`, `time`, `json`, `threading`, `pymongo`, `dotenv`, `services.github_services`, `services.judge_service`, `services.user_service`, `services.contest_service`, `config.github_config`, `extensions.mongo`.

- `user_service.py`:
  - **Description**: Provides functionalities for retrieving user-specific data and submission history. It also handles updating the user's problem status after a submission is graded, and includes a fix for a `WriteError` that occurred during this process.
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