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
