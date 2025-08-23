# Backend for Annaforces

This is the backend for the Annaforces project.

## GitHub Service

The `services/github_services.py` file provides a set of functions to interact with a GitHub repository. This service is used to manage the data stored in the `DATA` repository.

### Environment Variables

To use the GitHub service, you need to set the following environment variables in a `.env` file in the root of the `backend-for-annaforces` directory:

- `GITHUB_TOKEN`: A GitHub personal access token with `repo` scope.
- `GITHUB_REPO`: The name of the GitHub repository where the data is stored.
- `GITHUB_OWNER`: The owner of the GitHub repository.

### Functions

- `get_github_config()`: Reads the GitHub configuration from the environment variables.
- `get_file(filename_path)`: Retrieves the content and SHA of a file from the GitHub repository.
- `add_file(filename_path, data, commit_message=None, retries=3)`: Adds a new file to the GitHub repository.
- `update_file(filename_path, data, commit_message=None, retries=3)`: Updates an existing file in the GitHub repository.
- `create_or_update_file(filename_path, data, commit_message=None)`: Creates a new file or updates an existing one.
- `get_folder_contents(path)`: Retrieves the contents of all files in a folder from the GitHub repository.
