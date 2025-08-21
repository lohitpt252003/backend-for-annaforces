# Backend for AnnaForces

This is the backend for the AnnaForces application.

## API Documentation

### Authentication API

This API is responsible for user authentication.

#### Get User Information

*   **Endpoint:** `/user/<user_id>`
*   **Method:** `GET`
*   **Description:** Fetches user information from the GitHub repository and returns it along with a JWT token for authentication.
*   **URL Parameters:**
    *   `user_id` (string, required): The ID of the user.
*   **Success Response (200):**
    *   **Content:**
        ```json
        {
            "user": {
                "name": "John Doe",
                "username": "johndoe",
                "user_id": "12345"
            },
            "token": "your.jwt.token"
        }
        ```
*   **Error Responses:**
    *   **404 Not Found:** If the user's data file is not found in the repository.
        ```json
        {
            "error": "File not found"
        }
        ```
    *   **500 Internal Server Error:** If the user's data file is not a valid JSON.
        ```json
        {
            "error": "Failed to decode user data."
        }
        ```

### Problems API

This API is responsible for fetching problem information.

#### Get All Problems

*   **Endpoint:** `/api/problems`
*   **Method:** `GET`
*   **Description:** Fetches a list of all available problems.
*   **Success Response (200):**
    *   **Content:**
        ```json
        [
            {
                "id": "problem1",
                "title": "Problem 1 Title"
            },
            {
                "id": "problem2",
                "title": "Problem 2 Title"
            }
        ]
        ```
*   **Error Responses:**
    *   **404 Not Found:** If `data/problem_list.json` is not found.
        ```json
        {
            "error": "file data/problem_list.json not found"
        }
        ```
    *   **500 Internal Server Error:** If the problem list data is not a valid JSON.
        ```json
        {
            "error": "Failed to decode problem list data."
        }
        ```

#### Get Problem by ID

*   **Endpoint:** `/api/problems/<problem_id>`
*   **Method:** `GET`
*   **Description:** Fetches the details of a specific problem.
*   **URL Parameters:**
    *   `problem_id` (string, required): The ID of the problem.
*   **Success Response (200):**
    *   **Content:**
        ```json
        {
          "authors": [
            1
          ],
          "constraints": {
            "-100 <= a <= 100": true,
            "-100 <= b <= 100": true
          },
          "description": "There is nothing to describe the problem\nAuthor has covered everything in the statment itself.",
          "id": 1,
          "input_format": "Two integers a and b",
          "language_supported": "c, cpp, py",
          "output_format": "Print a + b in single line",
          "sample_testcases": [
            {
              "explanation": "1 + 2 = 3",
              "input": "1 2",
              "output": "3"
            },
            {
              "explanation": "2 + 3 = 5",
              "input": "2 3",
              "output": "5"
            }
          ],
          "space_limit": "1MB",
          "statement": "Add the given two numbers",
          "tags": [
            "input",
            "output",
            "basic"
          ],
          "testers": [
            1
          ],
          "time_limit": "1s",
          "title": "Add"
        }
        ```
*   **Error Responses:**
    *   **404 Not Found:** If the problem with the given ID is not found.
        ```json
        {
            "error": "Problem with id <problem_id> not found"
        }
        ```
    *   **500 Internal Server Error:** If the problem data is not a valid JSON.
        ```json
        {
            "error": "Failed to decode problem data for problem id <problem_id>."
        }
        ```
