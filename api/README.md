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
