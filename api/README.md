# APIs

This document provides an overview of the available APIs.

**Note:** The data structure for problems has been updated. Problems are now located inside their respective contest's directory, and the `problem_id` is in the format `C<contest_id><problem_letter>` (e.g., `C0A`, `C1C`, `C1000F`). If there are more than 26 problems in a contest, the problem letters will continue as `AA`, `AB`, etc. (e.g., `C1AA`, `C1AB`). The API implementation needs to be updated to reflect these changes.

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
  "C0A": {
    "title": "Binary Divisibility",
    "difficulty": "Easy",
    "tags": ["easy", "math", "binary"],
    "authors": ["Admin"]
  },
  "C0B": {
    "title": "A recursive Algorithm",
    "difficulty": "Easy",
    "tags": ["math", "recursion"],
    "authors": ["Lohit", "Sriramchandher"]
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

**Description:** Retrieves a specific problem by its ID. The `problem_id` must be in the format `C<contest_id><problem_letter>` (e.g., `C0A`, `C1C`, `C1000F`).

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve.

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "meta": {
    "id": "C0A",
    "memoryLimit": 256,
    "number_of_submissions": 2,
    "timeLimit": 2000,
    "title": "Binary Divisibility",
    "tags": ["easy", "math", "binary"],
    "authors": ["Admin"],
    "difficulty": "Easy",
    "contest_id": "C0"
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

**Endpoint:** `/api/problems/<problem_id>/submit`

**Method:** `POST`

**Description:** Submits code for a specific problem. Requires a valid JWT in the Authorization header.

**URL Parameters:**

- `problem_id`: The ID of the problem to submit code for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Request Body:**

```json
{
  "language": "python",
  "code": "print('Hello World')"
}
```

**Success Response:**

- **Code:** 201 Created
- **Content:**

```json
{
  "message": "Submission received and is being processed.",
  "submission_id": "S1"
}
```

**Error Response:**

- **Code:** 400 Bad Request (if code or language is missing), 401 Unauthorized, 500 Internal Server Error
- **Content:**

```json
{
  "error": "<error message>"
}
```

**Endpoint:** `/api/problems/<problem_id>/testcases`

**Method:** `GET`

**Description:** Retrieves all test cases for a specific problem. Requires a valid JWT in the Authorization header.

**URL Parameters:**

- `problem_id`: The ID of the problem to retrieve test cases for.

**Authorization Header:**

`Authorization: Bearer <your_jwt_token>`

**Success Response:**

- **Code:** 200 OK
- **Content:**

```json
{
  "testcases": [
    {
      "stdin": "input for test case 1",
      "path": "path/to/testcase1.in"
    },
    {
      "stdin": "input for test case 2",
      "path": "path/to/testcase2.in"
    }
  ]
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

## Submissions API

(No changes needed for this API at the moment)

## Contests API

(No changes needed for this API at the moment)

## Users API

(No changes needed for this API at the moment)
