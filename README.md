# Backend for Annaforces

This is the backend for the Annaforces project.

## Deployment

The backend is deployed at: `https://backend-for-annaforces.onrender.com/`

## Services

### GitHub Service

The `services/github_services.py` file provides a set of functions to interact with a GitHub repository. This service is used to manage the data stored in the `DATA` repository.

#### Environment Variables

To use the services, you need to set the following environment variables in a `.env` file in the root of the `backend-for-annaforces` directory:

- `GITHUB_TOKEN`: A GitHub personal access token with `repo` scope.
- `GITHUB_REPO`: The name of the GitHub repository where the data is stored.
- `GITHUB_OWNER`: The owner of the GitHub repository.
- `JUDGE_API_SERVER_URL`: The URL of the code execution server.

### Firebase Service

The `services/firebase_service.py` handles user authentication and management using Google Firebase Firestore. It provides functionalities for adding, retrieving, and verifying user credentials.

#### Environment Variables

To use the Firebase service, you need to set the following environment variable in a `.env` file in the root of the `backend-for-annaforces` directory:

- `FIREBASE_DB_CREDENTIALS`: The JSON content of your Firebase service account key. This should be a single, unquoted JSON string.

### Submission Service

The `services/submission_service.py` handles the submission of solutions by users. It orchestrates the process of receiving a submission, saving it, judging it, and updating the relevant data.

#### Submission Flow

When a user submits a solution, the following steps are performed:

1.  A new submission ID is generated.
2.  The submission metadata and code are saved to the `DATA` repository.
3.  The submission is graded by the Judge Service.
4.  The submission status is updated with the judging result.
5.  The `number_of_submissions` is incremented in the corresponding user's and problem's `meta.json` files.
6.  All file operations are committed with a commit message prefixed with `[AUTO]`.

### Judge Service

The `services/judge_service.py` is responsible for evaluating submitted code. It uses a Docker container to create a sandboxed environment for code execution. It retrieves test cases from the `DATA` repository and runs the user's code against them, checking for correctness and resource limits (time and memory).

### Problem Service

The `services/problem_service.py` is responsible for managing problems. It handles the creation of new problems, including validation of the problem data.

## API Endpoints

### Auth API

The `/api/auth/login` endpoint handles user authentication. It expects a `user_id` and `password` in the request body. Upon successful authentication, it returns a JWT token. If the user is not registered, a specific error message is returned.

**Example to get a token:**

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"user_id\": \"U1\", \"password\": \"1234\"}" https://backend-for-annaforces.onrender.com/api/auth/login
```

"Content-Type: application/json" -d "{\"user_id\": \"U1\", \"password\": \"1234\"}" https://backend-for-annaforces.onrender.com/api/auth/login
```

