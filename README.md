# Backend for Annaforces

This is the backend for the Annaforces project.

## Deployment

The backend is deployed at: `http://localhost:5000/`

## Services

### GitHub Service

The `services/github_services.py` file provides a set of functions to interact with a GitHub repository. This service is used to manage the data stored in the `DATA` repository.

### OTP and Email Service

The `services/email_service.py` module handles OTP generation and sending via email using Flask-Mail. This is primarily used for user email verification during registration, sending welcome emails, user ID reminders, and password reset OTPs.

#### Environment Variables

To use the services, you need to set the following environment variables in a `.env` file in the root of the `backend-for-annaforces` directory:

- `GITHUB_TOKEN`: A GitHub personal access token with `repo` scope.
- `GITHUB_REPO`: The name of the GitHub repository where the data is stored.
- `GITHUB_OWNER`: The owner of the GitHub repository.
- `JUDGE_API_SERVER_URL`: The URL of the code execution server.
- `MAIL_SERVER`: SMTP server address (e.g., `smtp.gmail.com`).
- `MAIL_PORT`: SMTP server port (e.g., `587`).
- `MAIL_USE_TLS`: Set to `True` for TLS encryption.
- `MAIL_USERNAME`: The email address used to send OTPs.
- `MAIL_PASSWORD`: The app password for the sending email address.
- `MAIL_DEFAULT_SENDER`: The default sender email address.

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

#### Problem Management

Problems are added and managed manually by directly modifying the `DATA` repository. The backend services will then read and serve these problems.

### Utils

The `utils` directory contains utility functions used throughout the backend application.

#### JWT Token

The `jwt_token.py` module provides functions for generating and verifying JSON Web Tokens (JWTs) for user authentication.

## Security Enhancements

Recent updates have focused on improving the security posture of the backend. Key enhancements include:

-   **Input Validation:** Stricter validation has been implemented for user-provided IDs (`user_id`, `submission_id`) to prevent path traversal vulnerabilities. Only IDs conforming to expected formats (e.g., `U123`, `S456`) are accepted.
-   **Language Whitelisting:** Code submission endpoints now enforce a whitelist for programming languages (`python`, `c`, `c++`) to ensure only supported and safe languages are processed by the judge service.

-   **Email Enumeration Prevention:** The `/api/auth/forgot-userid` endpoint now returns a generic success message, regardless of whether the email exists, to prevent attackers from enumerating valid user email addresses.
-   **Import Fixes:** Resolved import issues for email service functions (`send_password_reset_email`, `send_password_changed_confirmation_email`) ensuring proper functionality of password reset and confirmation emails.

-   **Authorization Policy Update:** The `/api/users/<user_id>` endpoint now allows any authenticated user to view the profile details of any other user, aligning with the updated requirement for public profile viewing.

These measures contribute to a more robust and secure application.

## Recent Bug Fixes

- **GitHub Service:**
  - Fixed an issue where files larger than 1MB could not be fetched from GitHub. The service now uses the `download_url` for large files.
- **Submission Service:**
  - Fixed an issue where the submission service was not returning detailed test results.
  - Fixed a bug that caused the service to crash if there was an error adding a submission to the database.
  - Corrected a syntax error that prevented the service from returning any value.
- **Judge Service:**
  - Fixed a bug related to tuple indexing when fetching test cases.
- **API:**
  - Standardized the language parameter for C++ submissions to "c++". Submissions with "cpp" are now automatically converted.

## Running Tests

To run the tests for the backend, navigate to the `backend-for-annaforces` directory and use the `pytest` command.

### Running All Tests (Utils Folder)

To run all `unittest` tests specifically for the `utils` folder, execute the `test_all.py` script:

```bash
python tests/utils/test_all.py
```

This script will automatically discover and run all `unittest` tests in `tests/utils`.

### Running Specific Tests

You can also run specific test files directly using Python. For example, to run the JWT token tests:

```bash
python tests/utils/test_jwt_token.py
```

To run the Email Service tests:

```bash
python tests/services/test_email_service.py
```

These test files use the `unittest` framework and include necessary `sys.path` adjustments for module imports.

The `-s` flag is recommended to see the output of any `print` statements within the tests.

For more details on the tests, see the `README.md` file in the `tests` directory.

## API Endpoints

### Auth API

The `/api/auth/login` endpoint handles user authentication. It expects a `user_id` and `password` in the request body. Upon successful authentication, it returns a JWT token. If the user is not found, a specific error message is returned.

**Example to get a token:**

```bash
curl -X POST -H "Content-Type: application/json" -d "{"user_id": "U1", "password": "1234"}" https://backend-for-annaforces.onrender.com/api/auth/login
```

### Problems API

**PDF Support**

The API now supports PDF versions of problem statements and solutions. 

- The `/api/problems/<problem_id>` endpoint will now include a `has_pdf_statement` boolean flag.
- The `/api/problems/<problem_id>/solution` endpoint will now include a `has_pdf_solution` boolean flag.

If these flags are true, you can use the following endpoints to retrieve the PDF data:

- `/api/problems/<problem_id>/statement.pdf`: Returns a JSON object with the base64 encoded PDF data for the problem statement.
- `/api/problems/<problem_id>/solution.pdf`: Returns a JSON object with the base64 encoded PDF data for the solution.


**Endpoint:** `/api/problems`

**Method:** `GET`

**Description:** Retrieves a list of all problems with filtering capabilities. Requires a valid JWT in the Authorization header.

**Query Parameters:**

- `search`: (Optional) A search term to filter problems by title or ID.
- `difficulty`: (Optional) Filter problems by difficulty (e.g., "Easy", "Medium", "Hard").
- `tag`: (Optional) Filter problems by a specific tag.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "problems": {
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
  },
  "total_problems": 5
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

**Endpoint:** `/api/problems/<problem_id>/submissions`

**Method:** `GET`

**Description:** Retrieves all submissions for a specific problem. Requires a valid JWT in the Authorization header. The `problem_id` must have the prefix 'P' (e.g., 'P1'). Submissions are sorted by timestamp in descending order (newest first).

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve submissions for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "submissions": [
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
  ],
  "total_submissions": 2
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

### Submissions API

**Endpoint:** `/api/submissions/<submission_id>`

**Method:** `GET`

**Description:** Retrieves detailed information about a specific submission, including code, status, and test case results. Requires a valid JWT in the Authorization header.

**URL Parameters:**

- `submission_id`: The ID of the submission to retrieve.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

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

- **Code:** 401 Unauthorized, 404 Not Found, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

### Contests API

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

**Description:** Retrieves detailed information about a specific contest, including its metadata, description, and theoretical background.

**URL Parameters:**

- `contest_id`: The ID of the contest to retrieve.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
    "id": "C1",
    "name": "Genesis Contest",
    "description": "The first-ever contest on AnnaForces.",
    "problems": ["P1", "P2", "P6"],
    "startTime": "2025-10-01T00:00:00Z",
    "endTime": "2025-10-07T23:59:59Z",
    "authors": ["Gemini"],
    "contest_description": "# Genesis Contest\n\nThis is the inaugural contest for AnnaForces. It features a selection of introductory problems designed to test fundamental programming skills.\n\n## Rules\n\n*   Participants must submit solutions in C, C++, or Python.\n*   Solutions will be judged based on correctness, time efficiency, and memory usage.\n*   Standard competitive programming rules apply.\n\nGood luck to all participants!",
    "contest_theory": "# Theory Behind the Genesis Contest\n\nThe problems in this contest are designed to cover basic algorithmic concepts such as:\n\n*   **Input/Output Handling:** Reading data from standard input and writing to standard output.\n*   **Conditional Statements:** Using `if-else` structures to make decisions.\n*   **Basic Arithmetic:** Performing addition, subtraction, multiplication, and division.\n*   **Finding Maximum/Minimum:** Identifying the largest or smallest among a set of numbers.\n\nThese fundamental concepts are crucial for building more complex algorithms and solving advanced problems in competitive programming."
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

**Endpoint:** `/api/users/<user_id>/submissions`

**Method:** `GET`

**Description:** Retrieves all submissions for a specific user. Requires a valid JWT in the Authorization header. The `user_id` must have the prefix 'U' (e.g., 'U1') and consist only of alphanumeric characters. Submissions are sorted by timestamp in descending order (newest first).

**URL Parameters:**

- `user_id`: The ID of the user to retrieve submissions for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "submissions": [
    {
      "submission_id": "S1",
      "user_id": "U1",
      "problem_id": "P1",
      "timestamp": "2023-10-27T10:00:00Z",
      "status": "Accepted",
      "language": "cpp"
    }
  ],
  "total_submissions": 1
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

### Google Sign-In

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


### Signup and OTP Verification

**Endpoint:** `/api/auth/signup`

**Method:** `POST`

**Description:** Initiates the user registration process. It sends an OTP to the provided email address. The user is only created in the system after successful OTP verification.

**Request Body:**

```json
{
  "username": "new_username",
  "password": "secure_password",
  "name": "New User",
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

- **Code:** 400 Bad Request, 409 Conflict, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

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

- **Code:** 400 Bad Request
- **Content:**

```json
{
  "error": "<error message>"
}
```

### Forgot User ID

**Endpoint:** `/api/auth/forgot-userid`

**Method:** `POST`

**Description:** Sends an email to the user containing their User ID and username if the provided email exists in the system. Returns a generic message to prevent email enumeration.

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

- **Code:** 400 Bad Request, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

### Password Reset

**Endpoint:** `/api/auth/request-password-reset`

**Method:** `POST`

**Description:** Initiates the password reset process by sending a One-Time Password (OTP) to the user's email if the provided email exists.

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
  "message": "If a user with that email exists, an OTP has been sent."
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

**Endpoint:** `/api/auth/verify-password-reset-otp`

**Method:** `POST`

**Description:** Verifies the OTP and allows the user to set a new password. The OTP is single-use and expires after 5 minutes.

**Request Body:**

```json
{
  "email": "user@example.com",
  "otp": "123456",
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