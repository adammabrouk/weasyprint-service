# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI server
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
