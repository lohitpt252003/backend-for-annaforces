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
    "title": "Add",
    "difficulty": "Easy",
    "tags": ["easy", "input", "output"],
    "authors": ["boss", "baz"]
  },
  "problem_statement": "<problem statement in markdown>"
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

**Endpoint:** `/api/problems/<problem_id>/submit`

**Method:** `POST`

**Description:** Submits a solution for a specific problem. Requires a valid JWT in the Authorization header. When a solution is submitted, the `number_of_submissions` is automatically incremented for both the user and the problem. All related file changes in the `DATA` repository are committed with a message prefixed with `[AUTO]`.

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

**Endpoint:** `/api/problems/add`

**Method:** `POST`

**Description:** Adds a new problem.

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

- `user_id` (string, required): The ID of the user submitting the solution.
- `language` (string, required): The programming language of the solution. Supported languages are `c`, `c++`, and `python`.
- `code` (string, required): The source code of the solution. Can be plain text or base64 encoded.
- `is_base64_encoded` (boolean, optional): Set to `true` if the `code` is base64 encoded. Defaults to `false`.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "message": "Submission successful",
  "status": "accepted",
  "submission_id": "S12"
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


## Users API

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

**Description:** Retrieves a specific user by their ID. The `user_id` must have the prefix 'U' (e.g., 'U1').

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

- **Code:** 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/users/<user_id>/submissions`

**Method:** `GET`

**Description:** Retrieves all submissions for a specific user. Requires a valid JWT in the Authorization header.

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

- **Code:** 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```


## Auth API

**Endpoint:** `/api/auth/login`

**Method:** `POST`

**Description:** Authenticates a user by checking for the existence of their `meta.json` file.

**Request Body:**

```json
{
  "user_id": "U1"
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

- **Code:** 400 Bad Request (if `user_id` is missing), 401 Unauthorized (if `meta.json` not found), 500 Internal Server Error (if `meta.json` is invalid)
- **Content:**

```json
{
  "error": "<error message>"
}
```

## Submissions API

**Endpoint:** `/api/submissions/<submission_id>`

**Method:** `GET`

**Description:** Retrieves a specific submission by its ID, including the submitted code and language. Requires a valid JWT in the Authorization header.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**URL Parameters:**

- `submission_id`: The ID of the submission to retrieve.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "code": "#include <stdio.h>\nint main() { int a, b; scanf(\" %d %d \", &a, &b); printf(\" %d \", a + b); return 0; }",
  "language": "c",
  "problem_id": "P1",
  "status": "accepted",
  "submission_id": "S1",
  "test_results": [
    {
      "actual_output": " 2 ",
      "execution_time": 0.0,
      "expected_output": "2",
      "memory_usage": 1.47265625,
      "message": "Test case passed",
      "status": "passed",
      "test_case_number": 1
    },
    {
      "actual_output": " 4 ",
      "execution_time": 0.0,
      "expected_output": "4",
      "memory_usage": 1.58984375,
      "message": "Test case passed",
      "status": "passed",
      "test_case_number": 2
    }
  ],
  "timestamp": "2025-08-29T06:36:40Z",
  "user_id": "U1"
}
```

**Error Response:**

- **Code:** 401 Unauthorized (if token is missing or invalid), 500 Internal Server Error (if submission not found or metadata is invalid)
- **Content:**

```json
{
  "error": "<error message>"
}
```