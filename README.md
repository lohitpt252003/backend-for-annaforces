# Backend for Annaforces

This is the backend for the Annaforces project.

## Services

### GitHub Service

The `services/github_services.py` file provides a set of functions to interact with a GitHub repository. This service is used to manage the data stored in the `DATA` repository.

#### Environment Variables

To use the GitHub service, you need to set the following environment variables in a `.env` file in the root of the `backend-for-annaforces` directory:

- `GITHUB_TOKEN`: A GitHub personal access token with `repo` scope.
- `GITHUB_REPO`: The name of the GitHub repository where the data is stored.
- `GITHUB_OWNER`: The owner of the GitHub repository.

### Submission Service

The `services/submission_service.py` handles the submission of solutions by users. It orchestrates the process of receiving a submission, saving it, judging it, and updating the relevant data.

### Judge Service

The `services/judge_service.py` is responsible for evaluating submitted code. It uses a Docker container to create a sandboxed environment for code execution. It retrieves test cases from the `DATA` repository and runs the user's code against them, checking for correctness and resource limits (time and memory).

### Problem Service

The `services/problem_service.py` is responsible for managing problems. It handles the creation of new problems, including validation of the problem data.
