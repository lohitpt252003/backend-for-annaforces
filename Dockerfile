# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
# Add gunicorn to the requirements for a production server
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Define environment variables for default values (optional, can be overridden)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application using Gunicorn
# The command "gunicorn --bind 0.0.0.0:5000 app:app" tells Gunicorn to:
# --bind 0.0.0.0:5000 : Listen on all network interfaces on port 5000.
# app:app : Look for a Flask app instance named 'app' inside the 'app.py' module.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
