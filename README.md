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

## API Endpoints

### Auth API

The `/api/auth/login` endpoint handles user authentication. It expects a `user_id` and `password` in the request body. Upon successful authentication, it returns a JWT token. If the user is not found, a specific error message is returned.

**Example to get a token:**

```bash
curl -X POST -H "Content-Type: application/json" -d "{"user_id": "U1", "password": "1234"}" https://backend-for-annaforces.onrender.com/api/auth/login
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