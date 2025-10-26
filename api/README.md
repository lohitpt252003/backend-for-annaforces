# APIs

This document provides an overview of the available APIs.

## Authentication API (`auth_bp`)

**Base URL Prefix:** `/api/auth`

### `POST /api/auth/login`

**Description:** Handles user authentication. Expects `username` and `password` in the request body. Returns a JWT token on success.
**Request Body:**
```json
{
  "username": "testuser",
  "password": "password123"
}
```
**Success Response (200 OK):**
```json
{
  "message": "Login successful",
  "username": "testuser",
  "name": "Test User",
  "token": "<JWT>"
}
```
**Error Response (400, 401, 500):**
```json
{
  "error": "<error message>"
}
```

### `POST /api/auth/google-signin`

**Description:** Handles Google Sign-In by verifying the Google ID token.
**Request Body:**
```json
{
  "id_token": "<Google ID Token>"
}
```
**Success Response (200 OK):**
```json
{
  "message": "Google sign-in successful",
  "username": "<Google Email>",
  "name": "<Google Display Name>",
  "token": "<JWT>"
}
```
**Error Response (400, 401, 500):**
```json
{
  "error": "<error message>"
}
```

### `POST /api/auth/signup`

**Description:** Initiates user registration by sending an OTP to the provided email.
**Request Body:**
```json
{
  "username": "new_username",
  "password": "secure_password",
  "name": "New User",
  "email": "user@example.com"
}
```
**Success Response (200 OK):**
```json
{
  "message": "OTP has been sent to your email. Please verify to complete registration."
}
```
**Error Response (400, 409, 500):**
```json
{
  "error": "<error message>"
}
```

### `POST /api/auth/verify-otp`

**Description:** Verifies the OTP sent during signup.
**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```
**Success Response (201 Created):**
```json
{
  "message": "Email verified and user registered successfully!",
  "username": "new_username"
}
```
**Error Response (400):**
```json
{
  "error": "<error message>"
}
```

### `POST /api/auth/forgot-userid`

**Description:** Sends an email with the username if the email exists. Returns a generic message to prevent enumeration.
**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Success Response (200 OK):**
```json
{
  "message": "If a user with that email exists, a reminder has been sent."
}
```
**Error Response (400, 500):**
```json
{
  "error": "<error message>"
}
```

### `POST /api/auth/request-password-reset`

**Description:** Initiates password reset by sending an OTP.
**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Success Response (200 OK):**
```json
{
  "message": "If a user with that email exists, an OTP has been sent."
}
```
**Error Response (400, 500):**
```json
{
  "error": "<error message>"
}
```

### `POST /api/auth/verify-password-reset-otp`

**Description:** Verifies OTP and allows setting a new password.
**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "new_secure_password"
}
```
**Success Response (200 OK):**
```json
{
  "message": "Password has been reset successfully."
}
```
**Error Response (400, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/auth/<username>/submissions`

**Description:** Retrieves all submissions for a specific user directly from MongoDB.
**URL Parameters:**
- `username`: The username of the user.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
[
  {
    "submission_id": "S1",
    "problem_id": "P1",
    "username": "testuser",
    "language": "python",
    "status": "Accepted",
    "timestamp": 1678886400,
    "test_results": [...]
  }
]
```
**Error Response (401, 500):**
```json
{
  "error": "<error message>"
}
```

## Problems API (`problems_bp`)

**Base URL Prefix:** `/api/problems`

### `GET /api/problems`

**Description:** Retrieves a list of all problems with filtering capabilities.
**Authentication:** Required (JWT token).
**Query Parameters:** `search`, `difficulty`, `tag`.
**Success Response (200 OK):**
```json
{
  "problems": {
    "C0A": { ... },
    "C0B": { ... }
  },
  "total_problems": 2
}
```
**Error Response (401, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/problems/<problem_id>`

**Description:** Retrieves a specific problem by its ID. Includes problem statement, samples, and PDF availability.
**URL Parameters:**
- `problem_id`: The ID of the problem (e.g., `C1A`).
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "meta": { ... },
  "problem_statement": "<problem statement in markdown>",
  "samples_data": [...],
  "has_pdf_statement": true
}
```
**Special Response (200 OK):** If the associated contest has not started.
```json
{
  "message": "Contest has not started yet"
}
```
**Error Response (404, 500):**
```json
{
  "error": "<error message>"
}
```

### `POST /api/problems/<problem_id>/submit`

**Description:** Submits code for a specific problem.
**URL Parameters:**
- `problem_id`: The ID of the problem.
**Authentication:** Required (JWT token).
**Request Body:**
```json
{
  "language": "python",
  "code": "print('Hello World')"
}
```
**Success Response (200 OK):**
```json
{
  "message": "Submission received and is being processed.",
  "submission_id": "S1"
}
```
**Error Response (400, 401, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/problems/<problem_id>/submissions`

**Description:** Retrieves all submissions for a specific problem directly from MongoDB.
**URL Parameters:**
- `problem_id`: The ID of the problem.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
[
  {
    "submission_id": "S1",
    "problem_id": "P1",
    "username": "testuser",
    "language": "python",
    "status": "Accepted",
    "timestamp": 1678886400,
    "test_results": [...]
  }
]
```
**Error Response (401, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/problems/<problem_id>/meta`

**Description:** Retrieves only the metadata for a specific problem.
**URL Parameters:**
- `problem_id`: The ID of the problem.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "id": "C1A",
  "memoryLimit": 256,
  "timeLimit": 2000,
  "title": "Binary Divisibility",
  "tags": ["easy", "math", "binary"],
  "authors": ["Admin"],
  "difficulty": "Easy",
  "contest_id": "C0"
}
```
**Error Response (404, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/problems/<problem_id>/statement.pdf`

**Description:** Returns the base64 encoded PDF data for the problem statement.
**URL Parameters:**
- `problem_id`: The ID of the problem.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "pdf_data": "<base64 encoded PDF>"
}
```
**Error Response (404, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/problems/<problem_id>/solution.pdf`

**Description:** Returns the base64 encoded PDF data for the problem solution.
**URL Parameters:**
- `problem_id`: The ID of the problem.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "pdf_data": "<base64 encoded PDF>"
}
```
**Error Response (404, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/problems/<problem_id>/testcases`

**Description:** Retrieves all test cases for a specific problem.
**URL Parameters:**
- `problem_id`: The ID of the problem.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "testcases": [
    {
      "stdin": "input for test case 1",
      "path": "path/to/testcase1.in"
    }
  ]
}
```
**Error Response (404, 500):**
```json
{
  "error": "<error message>"
}
```

## Submissions API (`submissions_bp`)

**Base URL Prefix:** `/api/submissions`

### `GET /api/submissions/queue`

**Description:** Retrieves all submissions currently in the processing queue.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
[
  {
    "problem_id": "C1A",
    "username": "testuser",
    "language": "python",
    "code": "print('hello')",
    "status": "running test case 1",
    "created_at": 1678886400
  }
]
```
**Error Response (401, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/submissions/<submission_id>`

**Description:** Retrieves detailed information about a specific submission from MongoDB.
**URL Parameters:**
- `submission_id`: The ID of the submission.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "submission_id": "S1",
  "problem_id": "P1",
  "username": "testuser",
  "language": "python",
  "status": "Accepted",
  "timestamp": 1678886400,
  "test_results": [...]
}
```
**Error Response (401, 404, 500):**
```json
{
  "error": "<error message>"
}
```

## Contests API (`contests_bp`)

**Base URL Prefix:** `/api/contests`

### `GET /api/contests/`

**Description:** Retrieves a list of all contests from MongoDB with filtering capabilities.
**Authentication:** Required (JWT token).
**Query Parameters:** `search`, `author`.
**Success Response (200 OK):**
```json
[
  {
    "id": "C1",
    "name": "Genesis Contest",
    "description": "...",
    "startTime": "...",
    "endTime": "...",
    "authors": ["..."],
    "problems": ["..."],
    "participants": ["..."],
    "status_info": {
      "status": "Upcoming",
      "timeInfo": "Starts in: 5d 10h 30m 15s",
      "progress": 0
    }
  }
]
```
**Error Response (401, 404, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/contests/<contest_id>`

**Description:** Retrieves detailed information about a specific contest from MongoDB, including its status.
**URL Parameters:**
- `contest_id`: The ID of the contest.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "id": "C1",
  "name": "Genesis Contest",
  "description": "...",
  "startTime": "...",
  "endTime": "...",
  "authors": ["..."],
  "problems": ["..."],
  "participants": ["..."],
  "contest_description": "<markdown content>",
  "contest_theory": "<markdown content>",
  "status_info": {
    "status": "Running",
    "timeInfo": "Ends in: 1d 5h 20m 30s",
    "progress": 50
  }
}
```
**Error Response (401, 404, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/contests/<contest_id>/meta`

**Description:** Retrieves only the metadata for a specific contest from MongoDB.
**URL Parameters:**
- `contest_id`: The ID of the contest.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "id": "C1",
  "name": "Genesis Contest",
  "startTime": "...",
  "endTime": "...",
  "authors": ["..."],
  "problems": ["..."]
}
```
**Error Response (401, 404, 500):**
```json
{
  "error": "<error message>"
}
```

### `GET /api/contests/<contest_id>/is-registered`

**Description:** Checks if the current user is registered for a specific contest.
**URL Parameters:**
- `contest_id`: The ID of the contest.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "is_registered": true
}
```
**Error Response (401, 500):**
```json
{
  "error": "<error message>"
}
```

### `POST /api/contests/<contest_id>/register`

**Description:** Registers the current user for a specific contest.
**URL Parameters:**
- `contest_id`: The ID of the contest.
**Authentication:** Required (JWT token).
**Success Response (200 OK):**
```json
{
  "message": "Successfully registered for the contest."
}
```
**Error Response (401, 500):**
```json
{
  "error": "<error message>"
}
```