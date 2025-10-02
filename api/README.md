# APIs

This document provides an overview of the available APIs.

## Problems API

**Endpoint:** `/api/problems`

**Method:** `GET`

**Description:** Retrieves a list of all problems. Requires a valid JWT in the Authorization header.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "P1": {
    "title": "Add",
    "difficulty": "Easy",
    "tags": ["easy", "input", "output"],
    "authors": ["boss", "baz"]
  },
  "P2": {
    "title": "Subtract",
    "difficulty": "Easy",
    "tags": ["easy", "input", "output"],
    "authors": ["baz", "boss"]
  }
}
```

**Error Response:**

- **Code:** 401 Unauthorized (if token is missing or invalid), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/problems/<problem_id>`

**Method:** `GET`

**Description:** Retrieves a specific problem by its ID. The `problem_id` must have the prefix 'P' (e.g., 'P1').

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "meta": {
    "id": "P1",
    "memoryLimit": 256,
    "number_of_submissions": 2,
    "timeLimit": 1000,
    "title": "Add",
    "tags": ["easy", "input", "output"],
    "authors": ["boss", "baz"],
    "difficulty": "Easy"
  },
  "problem_statement": "<problem statement in markdown>",
  "constraints_content": "<problem constraints in markdown>",
  "has_pdf_statement": true
}
```

**Error Response:**

- **Code:** 404 Not Found (if problem not found), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `Problem not found`

**Endpoint:** `/api/problems/<problem_id>/meta`

**Method:** `GET`

**Description:** Retrieves only the metadata for a specific problem by its ID. This is a more efficient endpoint for fetching problem information when full problem details are not required. The `problem_id` must have the prefix 'P' (e.g., 'P1').

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve metadata for.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "id": "P1",
  "title": "Add",
  "difficulty": "Easy",
  "tags": ["easy", "input", "output"],
  "authors": ["boss", "baz"],
  "memoryLimit": 256,
  "timeLimit": 1000,
  "contest_id": "C1"
}
```

**Error Response:**

- **Code:** 401 Unauthorized (if token is missing or invalid), 404 Not Found (if problem meta not found), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `Problem meta not found`

**Endpoint:** `/api/problems/<problem_id>/solution`

**Method:** `GET`

**Description:** Retrieves the solution for a specific problem. The response format depends on whether the problem belongs to a running or scheduled contest.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve solutions for.

**Success Response:**

- **Code:** 200 OK

- **If the solution is available:**
  - **Content:**
    ```json
    {
        "status": "available",
        "data": {
            "python": "<python solution code>",
            "cpp": "<cpp solution code>",
            "c": "<c solution code>",
            "markdown": "<solution explanation in markdown>",
            "has_pdf_solution": true
        }
    }
    ```

- **If the solution is not available (due to an ongoing or scheduled contest):**
  - **Content:**
    ```json
    {
        "status": "not_available",
        "message": "Solutions are not available for problems in a running or scheduled contest."
    }
    ```

**Error Response:**

- **Code:** 401 Unauthorized (if token is missing or invalid), 404 Not Found (if solution files are not found for the problem_id), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `Solution files not found for this problem_id`

**Endpoint:** `/api/problems/<problem_id>/statement.pdf`

**Method:** `GET`

**Description:** Retrieves the problem statement in PDF format. Requires a valid JWT in the Authorization header.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve the statement for.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "pdf_data": "<base64 encoded pdf data>"
}
```

**Error Response:**

- **Code:** 401 Unauthorized, 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/problems/<problem_id>/solution.pdf`

**Method:** `GET`

**Description:** Retrieves the solution in PDF format. Requires a valid JWT in the Authorization header.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve the solution for.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "pdf_data": "<base64 encoded pdf data>"
}
```

**Error Response:**

- **Code:** 401 Unauthorized, 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/problems/<problem_id>/submit`

**Method:** `POST`

**Description:** Submits a solution for a specific problem. Requires a valid JWT in the Authorization header. The supported languages are `c`, `c++`, and `python`. The language `cpp` is also accepted as an alias for `c++`. When a solution is submitted, the `number_of_submissions` is automatically incremented for both the user and the problem. All related file changes in the `DATA` repository are committed with a message prefixed with `[AUTO]`.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Request Body:**

```json
{
  "language": "python",
  "code": "print(\"hello world\")",
  "is_base64_encoded": false
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "Submission successful",
  "status": "accepted",
  "submission_id": "S12",
  "test_results": [
    {
      "actual_output": "0",
      "execution_time": 0.09,
      "expected_output": "0",
      "memory_usage": 7.8203125,
      "message": "Test case passed",
      "status": "passed",
      "test_case_number": 1
    }
  ]
}
```

**Error Response:**

- **Code:** 400 Bad Request, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `Code execution service is not running. Please contact the admin.`
- `Unsupported language: <language>. Supported languages are c, c++, python.`


**Endpoint:** `/api/problems/add`

**Method:** `POST`

**Description:** This API endpoint allows for programmatic addition of new problems. However, problems are primarily added and managed manually by directly modifying the `DATA` repository.

**Request Body:**

```json
{
  "title": "New Problem",
  "time_limit": 1,
  "memory_limit": 256,
  "difficulty": "Medium",
  "tags": ["new", "problem"],
  "authors": ["Gemini"],
  "description": "# Problem 5: New Problem\n\n## Description\nThis is a new problem.\n\n## Input\n...\n\n## Output\n...\n\n## Constraints\n...\n\n## Example1\n### Input\n...\n### Output\n...\n\n## Explanation\n...",
  "testcases": [
    {
      "input": "...",
      "output": "..."
    }
  ]
}
```

**Success Response:**

- **Code:** 201 Created
- **Content:**

```json
{
  "message": "Problem added successfully",
  "problem_id": "P5"
}
```

**Error Response:**

- **Code:** 400 Bad Request, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/problems/<problem_id>/submissions`

**Method:** `GET`

**Description:** Retrieves all submissions for a specific problem. Requires a valid JWT in the Authorization header. The `problem_id` must have the prefix 'P' (e.g., 'P1'). This endpoint efficiently retrieves all submissions for a problem by listing the contents of the submissions directory.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve submissions for.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
[
  {
    "submission_id": "S1",
    "user_id": "U1",
    "problem_id": "P1",
    "timestamp": "2023-10-27T10:00:00Z",
    "status": "Accepted",
    "language": "cpp"
  },
  {
    "submission_id": "S2",
    "user_id": "U2",
    "problem_id": "P1",
    "timestamp": "2023-10-27T10:05:00Z",
    "status": "Wrong Answer",
    "language": "python"
  }
]
```

**Error Response:**

- **Code:** 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```


## Submissions API

**Endpoint:** `/api/submissions/<submission_id>`

**Method:** `GET`

**Description:** Retrieves detailed information about a specific submission. Access to submissions for problems in running contests is restricted.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `submission_id`: The ID of the submission to retrieve.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "submission_id": "S1",
  "problem_id": "P1",
  "user_id": "U1",
  "language": "python",
  "code": "print(1+2)",
  "status": "Accepted",
  "timestamp": "2023-10-27T10:00:00Z",
  "test_cases": [
    {
      "test_case_id": 1,
      "status": "Accepted",
      "time_taken": 0.01,
      "memory_used": 1024
    }
  ]
}
```

**Error Response:**

- **Code:** 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```
- **If the submission belongs to a running contest and the user is not the owner:**
  - **Code:** 403 Forbidden
  - **Content:**
    ```json
    {
      "error": "You are not allowed to see the submission of the other user during the contest."
    }
    ```

### Contests API

**Endpoint:** `/api/contests/<contest_id>/is-registered`

**Method:** `GET`

**Description:** Checks if the authenticated user is registered for a specific contest. Requires a valid JWT in the Authorization header.

**URL Parameters:**

- `contest_id`: The ID of the contest to check registration for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "is_registered": true
}
```

**Error Response:**

- **Code:** 401 Unauthorized, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/contests/<contest_id>/register`

**Method:** `POST`

**Description:** Registers the authenticated user for a specific contest. Requires a valid JWT in the Authorization header.

**URL Parameters:**

- `contest_id`: The ID of the contest to register for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "Successfully registered for the contest."
}
```

**Error Response:**

- **Code:** 401 Unauthorized, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/contests/<contest_id>/leaderboard`

**Method:** `GET`

**Description:** Retrieves the leaderboard for a specific contest, now including usernames.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `contest_id`: The ID of the contest to retrieve the leaderboard for.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "last_updated": "2025-10-01T12:30:00Z",
  "standings": [
    {
      "user_id": "U1",
      "username": "boss",
      "total_score": 200,
      "total_penalty": 10,
      "problems": {
        "P1": {
          "status": "solved",
          "score": 100,
          "attempts": 1,
          "time_taken": "00:15:00"
        },
        "P2": {
          "status": "not_solved",
          "score": 0,
          "attempts": 2,
          "time_taken": "00:30:00"
        }
      }
    }
  ]
}
```

**Error Response:**

- **Code:** 401 Unauthorized, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/contests`

**Method:** `GET`

**Description:** Retrieves a list of all contests with filtering capabilities. Requires a valid JWT in the Authorization header.

**Query Parameters:**

- `search`: (Optional) A search term to filter contests by name or ID.
- `author`: (Optional) Filter contests by a specific author.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
[
    {
        "id": "C1",
        "name": "Genesis Contest",
        "description": "The first-ever contest on AnnaForces.",
        "problems": ["P1", "P2", "P6"],
        "startTime": "2025-10-01T00:00:00Z",
        "endTime": "2025-10-07T23:59:59Z",
        "authors": ["Gemini"]
    }
]
```

**Error Response:**

- **Code:** 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/contests/<contest_id>`

**Method:** `GET`

**Description:** Retrieves detailed information about a specific contest. The response format depends on the contest's status.

**URL Parameters:**

- `contest_id`: The ID of the contest to retrieve.

**Success Response:**

- **Code:** 200 OK

- **If the contest has started:**
  - **Content:**
    ```json
    {
        "status": "started",
        "data": {
            "id": "C1",
            "name": "Genesis Contest",
            "description": "The first-ever contest on AnnaForces.",
            "problems": ["P1", "P2", "P6"],
            "startTime": "2025-10-01T00:00:00Z",
            "endTime": "2025-10-07T23:59:59Z",
            "authors": ["Gemini"],
            "contest_description": "# Genesis Contest\n\nThis is the inaugural contest for AnnaForces...",
            "contest_theory": "# Theory Behind the Genesis Contest\n\nThe problems in this contest are..."
        }
    }
    ```

- **If the contest has not started:**
  - **Content:**
    ```json
    {
        "status": "not_started",
        "message": "The contest has not begun yet"
    }
    ```

**Error Response:**

- **Code:** 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/users/`

**Method:** `GET`

**Description:** Retrieves a list of all users.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "U1": {
    "Name": "Chris Gayle",
    "username": "boss"
  },
  "U2": {
    "email": "Brendon McCullum",
    "username": "baz"
  }
}
```

**Error Response:**

- **Code:** 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/users/<user_id>`

**Method:** `GET`

**Description:** Retrieves a specific user by their ID. Requires a valid JWT in the Authorization header. Any authenticated user can view any other user's profile details. The `user_id` must have the prefix 'U' (e.g., 'U1') and consist only of alphanumeric characters.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `user_id`: The ID of the user to retrieve.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "Name": "Test User",
  "username": "testuser"
}
```

**Error Response:**

- **Code:** 401 Unauthorized (if token is missing or invalid), 400 Bad Request (if user_id format is invalid), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/users/<user_id>/submissions`

**Method:** `GET`

**Description:** Retrieves all submissions for a specific user. Requires a valid JWT in the Authorization header. Any authenticated user can view any other user's submissions. The `user_id` must have the prefix 'U' (e.g., 'U1') and consist only of alphanumeric characters.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `user_id`: The ID of the user to retrieve submissions for.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
[
  {
    "submission_id": "S1",
    "user_id": "U1",
    "problem_id": "P1",
    "timestamp": "2023-10-27T10:00:00Z",
    "status": "Accepted",
    "language": "cpp"
  }
]
```

**Error Response:**

- **Code:** 401 Unauthorized (if token is missing or invalid), 400 Bad Request (if user_id format is invalid), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```


**Endpoint:** `/api/users/<user_id>/solved`

**Method:** `GET`

**Description:** Retrieves a list of unique problems solved by a specific user (submissions with 'Accepted' status). Requires a valid JWT in the Authorization header. Any authenticated user can view any other user's solved problems. The `user_id` must have the prefix 'U' (e.g., 'U1') and consist only of alphanumeric characters.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `user_id`: The ID of the user to retrieve solved problems for.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
[
  "P1",
  "P3",
  "P5"
]
```

**Error Response:**

- **Code:** 401 Unauthorized (if token is missing or invalid), 400 Bad Request (if user_id format is invalid), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```


## Users API

**Endpoint:** `/api/users/<user_id>/username`

**Method:** `GET`

**Description:** Retrieves the username for a specific user ID. Requires a valid JWT in the Authorization header.

**URL Parameters:**

- `user_id`: The ID of the user to retrieve the username for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "username": "testuser"
}
```

**Error Response:**

- **Code:** 401 Unauthorized, 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

## Users API

**Endpoint:** `/api/users/<user_id>/problem-status`

**Method:** `GET`

**Description:** Retrieves the status of problems (solved, not_solved, not_attempted) for a specific user. Requires a valid JWT in the Authorization header.

**URL Parameters:**

- `user_id`: The ID of the user to retrieve problem statuses for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "P1": "solved",
  "P2": "not_solved",
  "P3": "not_attempted"
}
```

**Error Response:**

- **Code:** 401 Unauthorized, 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

## Users API

**Endpoint:** `/api/users/<user_id>/contests`

**Method:** `GET`

**Description:** Retrieves a list of contest IDs that the specified user has registered for. Requires a valid JWT in the Authorization header.

**URL Parameters:**

- `user_id`: The ID of the user to retrieve contest participation for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
[
  "C1",
  "C2"
]
```

**Error Response:**

- **Code:** 401 Unauthorized, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/auth/login`

**Method:** `POST`

**Description:** Authenticates a user with provided `user_id` and `password`. If the user is not found, a specific error message is returned.

**Request Body:**

```json
{
  "user_id": "U1",
  "password": "your_password"
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "Login successful",
  "user_id": "U1",
  "username": "boss",
  "name": "Chris Gayle",
  "token": "<token>"
}
```

**Error Response:**

- **Code:** 400 Bad Request (if `user_id` or `password` is missing), 401 Unauthorized (if credentials are invalid), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `User ID and password are required`
- `Invalid credentials`
- `User not found. Please sign up or contact the admin.`

**Endpoint:** `/api/auth/google-signin`

**Method:** `POST`

**Description:** Handles Google Sign-In by verifying the Google ID token received from the frontend. It uses Firebase Authentication to validate the token and either retrieves an existing user or creates a new user entry in Firestore based on the Google profile information. Upon successful verification and user handling, it generates and returns a JWT for the user.

**Request Body:**

```json
{
  "id_token": "<Google ID Token>"
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "Google sign-in successful",
  "user_id": "<Firebase UID>",
  "username": "<Google Email>",
  "name": "<Google Display Name>",
  "token": "<JWT>"
}
```

**Error Response:**

- **Code:** 400 Bad Request (if `id_token` is missing), 401 Unauthorized (if `id_token` is invalid or verification fails), 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/auth/signup`

**Method:** `POST`

**Description:** Initiates the user registration process. It sends an OTP to the provided email address. The user is only created in the system after successful OTP verification.

**Request Body:**

```json
{
  "username": "new_username",
  "password": "new_password",
  "name": "New User Name",
  "email": "user@example.com"
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "OTP has been sent to your email. Please verify to complete registration."
}
```

**Error Response:**

- **Code:** 400 Bad Request (missing fields), 409 Conflict (username already exists), 500 Internal Server Error (email sending failure)
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `All fields (username, password, name, email) are required`
- `Username already exists`
- `Failed to send OTP email: <error_details>`

**Endpoint:** `/api/auth/verify-otp`

**Method:** `POST`

**Description:** Verifies the OTP sent during signup. Upon successful verification, the user account is created, and a welcome email is sent.

**Request Body:**

```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Success Response:**

- **Code:** 201 Created
- **Content:**

```json
{
  "message": "Email verified and user registered successfully!",
  "user_id": "U3"
}
```

**Error Response:**

- **Code:** 400 Bad Request (missing fields, invalid OTP, OTP expired, too many attempts, email not found)
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `Email and OTP are required`
- `Invalid email or registration session expired.`
- `OTP expired.`
- `Too many incorrect OTP attempts. Please try signing up again.`
- `Invalid OTP.`

**Endpoint:** `/api/auth/forgot-userid`

**Method:** `POST`

**Description:** Sends an email to the user containing their User ID and username if the provided email exists in the system.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "If a user with that email exists, a reminder has been sent."
}
```

**Error Response:**

- **Code:** 400 Bad Request, 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `Email is required`
- `Email not found in our records.`

**Endpoint:** `/api/auth/request-password-reset`

**Method:** `POST`

**Description:** Initiates the password reset process. Sends a password reset link to the user's email if the provided email exists.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "If a user with that email exists, a password reset link has been sent."
}
```

**Error Response:**

- **Code:** 400 Bad Request, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `Email is required`

**Endpoint:** `/api/auth/reset-password/<token>`

**Method:** `POST`

**Description:** Resets the user's password using a valid reset token. The token is single-use and expires after 15 minutes.

**URL Parameters:**

- `token`: The password reset token received via email.

**Request Body:**

```json
{
  "new_password": "new_secure_password"
}
```

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "Password has been reset successfully."
}
```

**Error Response:**

- **Code:** 400 Bad Request, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

Possible error messages:
- `New password is required`
- `Invalid or expired reset token.`