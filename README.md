# Annaforces Backend

This is the backend for Annaforces, a competitive programming platform.

## Services

### GitHub Service

This service provides a Python interface for interacting with the GitHub API, specifically for file and folder manipulation within a repository. It handles authentication, file retrieval, creation, updates, and folder content listing.

#### Configuration

The service requires the following environment variables to be set:

- `GITHUB_TOKEN`: A personal access token with repository access.
- `GITHUB_REPO`: The name of the repository.
- `GITHUB_OWNER`: The owner of the repository.

These variables are loaded using `python-dotenv`.

#### Functions

- `get_github_config()`: Retrieves the GitHub configuration from environment variables.
- `get_file(filename_path)`: Retrieves the content and SHA of a file from the repository.
- `add_file(filename_path, data, commit_message=None, retries=3)`: Adds a new file to the repository.
- `update_file(filename_path, data, commit_message=None, retries=3)`: Updates an existing file in the repository.
- `create_or_update_file(filename_path, data, commit_message=None)`: Creates a new file or updates an existing one.
- `get_folder_contents(path)`: Retrieves the contents of all files in a folder.

### Submission Service

This service manages submissions for problems in the coding platform. It interacts with the GitHub repository to store and retrieve submission data.

#### Functions

- `add_submission_to_user(user_id, problem_id, result)`: Adds a submission record to the user's data in the repository.
- `add_submission_to_problem(user_id, problem_id, result)`: Adds a submission record to the problem's data in the repository.
- `get_problem_submissions(problem_id)`: Retrieves all submissions for a specific problem.
- `add_submission(problem_id, user_id, result)`: A wrapper function that calls `add_submission_to_user` and `add_submission_to_problem`.

## Data Models

The data for the platform is stored in a structured folder system within the GitHub repository.

### Problems

- **Location:** `models/problems/<problem_id>/`
- **Structure:**
    - `meta.json`: Contains metadata about the problem, such as title, difficulty, tags, and creator.
    - `problem.md`: The problem statement in Markdown format.
    - `testcases/`: A directory containing input and output files for testing solutions.

### Submissions

- **Location:** `models/submissions/<submission_id>/`
- **Structure:**
    - `meta.json`: Contains metadata about the submission, such as user ID, problem ID, language, status, and timestamp.
    - `solution.<language_extension>`: The source code of the submission.

### Users

- **Location:** `models/users/<user_id>/`
- **Structure:**
    - `meta.json`: Contains metadata about the user, such as username, join date, and a list of their submissions.