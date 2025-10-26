# Services

This directory contains various service modules used in the `backend-for-annaforces` application. Each service encapsulates specific business logic and interacts with external resources like GitHub or Firebase.

## Modules:

- `__init__.py`: Initializes the services package.

- `cache_service.py`: (Empty) This file is currently empty and does not contain any caching logic.

- `contest_service.py`:
  - **Description**: Manages contest data, including fetching details, checking registration, and handling leaderboard. Now fetches contest data directly from MongoDB.
  - **Key Functions**:
    - `get_all_contests_metadata()`: Retrieves metadata for all contests from MongoDB.
    - `get_contest_details(contest_id)`: Retrieves full details for a contest from MongoDB, including calculated `status_info` (Upcoming, Running, Over).
    - `get_contest_meta_from_mongo(contest_id)`: Retrieves only metadata for a contest from MongoDB.
    - `get_contest_status(contest_data)`: Calculates the current status of a contest based on its `startTime` and `endTime`.
    - `is_user_registered(contest_id, user_id)`: Checks if a user is registered for a contest.
    - `register_user_for_contest(contest_id, user_id)`: Registers a user for a contest.
  - **Dependencies**: `json`, `datetime`, `pytz`, `services.github_services`, `config.github_config`, `extensions.mongo`.

- `firebase_service.py`:
  - **Description**: Handles integration with Google Firebase Firestore for user management.
  - **Key Functions**:
    - `get_user(user_id)`: Fetches user data from Firestore.
    - `add_user(user_id, password)`: Adds a new user with a hashed password.
    - `verify_user(user_id, password)`: Verifies a user's password against the stored hash.
  - **Dependencies**: `firebase_admin`, `argon2`, `dotenv`, `json`, `os`.

- `github_services.py`:
  - **Description**: Provides an interface for interacting with the GitHub API to manage files. Includes an in-memory queue for write operations and a caching layer for read operations. Supports fetching files larger than 1MB.
  - **Key Functions**:
    - `get_file(filename_path, force_refresh=False)`: Fetches the content and SHA of a file, with optional cache bypass.
    - `add_file(filename_path, data, commit_message)`: Queues an operation to add a new file.
    - `update_file(filename_path, data, commit_message)`: Queues an operation to update an existing file.
    - `create_or_update_file(filename_path, data, commit_message)`: Queues an operation to add or update a file.
    - `get_folder_contents(path)`: Lists the contents of a folder.
    - `invalidate_cache(path=None)`: Invalidates specific or all cache entries.
  - **Dependencies**: `requests`, `json`, `os`, `base64`, `time`, `dotenv`, `queue`, `threading`.

- `judge_service.py`:
  - **Description**: Manages the automated judging of code submissions. Accepts a `submission_id` for live status updates. Calls executor service for code execution and verdict validation.
  - **Key Functions**:
    - `get_testcases(problem_id)`: Fetches all test cases for a given problem.
    - `grade_submission(submission_id, code, language, problem_id)`: Grades a submission and provides live status updates.
  - **Dependencies**: `os`, `json`, `requests`, `services.github_services`, `extensions.mongo`.

- `problem_service.py`:
  - **Description**: Handles the creation and management of programming problems. Validates problem data and orchestrates storage on GitHub. Now includes contest start time checks.
  - **Key Functions**:
    - `_validate_problem_md(description)`: Validates `problem.md` structure.
    - `_validate_problem_data(problem_data)`: Validates overall problem data.
    - `add_problem(problem_data)`: Adds a new problem.
    - `get_all_problems_metadata()`: Retrieves metadata for all problems.
    - `get_problem_full_details(problem_id)`: Retrieves full details for a problem, including contest start time check.
    - `get_problem_by_id(problem_id)`: Retrieves problem details from MongoDB.
  - **Dependencies**: `json`, `re`, `services.github_services`, `services.contest_service`, `datetime`, `pytz`, `extensions.mongo`.

- `submission_service.py`:
  - **Description**: Manages the lifecycle of user code submissions using a persistent, MongoDB-based queue. Includes functions for adding submissions to the queue, processing them by a background worker, and retrieving queue contents.
  - **Key Functions**:
    - `handle_new_submission(problem_id, username, language, code)`: Adds a new submission to the MongoDB queue.
    - `get_submissions_queue()`: Retrieves all submissions currently in the processing queue.
    - `worker()`: The background worker function that processes submissions from the queue.
    - `init_app(app)`: Initializes the background worker thread.
  - **Dependencies**: `os`, `time`, `json`, `threading`, `pymongo`, `dotenv`, `services.github_services`, `services.judge_service`, `services.user_service`, `services.contest_service`, `config.github_config`, `extensions.mongo`.

- `user_service.py`:
  - **Description**: Provides functionalities for retrieving user-specific data and submission history. Handles updating user's problem status.
  - **Key Functions**:
    - `get_user_by_id(user_id)`: Fetches a user's metadata.
    - `get_user_submissions(user_id)`: Retrieves all submissions made by a specific user.
  - **Dependencies**: `json`, `services.github_services`, `config.github_config`.

- `__pycache__`: Directory containing compiled Python files.

## Recent Bug Fixes and Enhancements

-   **Contest Service:**
    -   Implemented `get_contest_status` to calculate and return contest status (Upcoming, Running, Over).
    -   Updated `get_contest_details` to include `status_info` in the returned contest data.
    -   Added `get_contest_meta_from_mongo` to fetch only contest metadata from MongoDB.
    -   Fixed `time data does not match format` error by updating `strptime` format to include microseconds.
    -   Fixed `NameError: name 'pytz' is not defined` by importing `pytz`.
    -   Ensured `meta.json` is force-refreshed to bypass caching when fetching contest details.

-   **Problem Service:**
    -   Added logic to `get_problem_full_details` to check contest start time and return "Contest has not started yet" if applicable.

-   **Submission Service:**
    -   Added `get_submissions_queue()` function to retrieve submissions from the queue.

-   **GitHub Service:**
    -   Implemented a caching layer for read operations (`get_file`, `get_folder_contents`) to improve performance.

-   **General Bug Fixes:**
    -   Resolved `NameError: name 'mongo' is not defined` in `problems_api.py` and `submissions_api.py` by importing `mongo`.
