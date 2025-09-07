# Tests

This directory contains the tests for the backend application.

## Structure

The tests are organized into subdirectories based on the part of the application they are testing:

- `api/`: Tests for the API endpoints.
- `services/`: Tests for the service layer.
- `utils/`: Tests for the utility functions.

## Running Tests

To run all the tests, navigate to the `backend-for-annaforces` directory and run the following command:

```bash
pytest -s
```

To run tests for a specific part of the application, you can specify the directory:

```bash
pytest -s tests/utils/
```

To run a specific test file, provide the path to the file:

```bash
pytest -s tests/utils/test_jwt_token.py
```

The `-s` flag is used to display the output of print statements in the terminal.
