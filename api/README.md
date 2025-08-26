# APIs

This document provides an overview of the available APIs.

## Problems API

**Endpoint:** `/api/problems`

**Method:** `GET`

**Description:** Retrieves a list of all problems.

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

- **Code:** 500 Internal Server Error
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

**Description:** Submits a solution for a specific problem.

**Request Body:**

```json
{
  "user_id": "U1",
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

**Description:** Retrieves all submissions for a specific problem. The `problem_id` must have the prefix 'P' (e.g., 'P1').

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

