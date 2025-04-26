# weasyprint-mcp-server

## WeasyPrint Server Implementation

This repository contains an implementation of a WeasyPrint server built with FastAPI. The server accepts client data via API, injects branding dynamically into templates, renders PDFs using WeasyPrint, and returns PDF responses or stores them.

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/adammabrouk/weasyprint-mcp-server.git
   cd weasyprint-mcp-server
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Run the FastAPI server:
   ```bash
   poetry run uvicorn main:app --reload
   ```

### Usage Examples

#### Generate PDF

To generate a PDF, send a POST request to the `/generate-pdf` endpoint with the required client data.

Example request:
```bash
curl -X POST "http://localhost:8000/generate-pdf" -H "Content-Type: application/json" -d '{
  "client_name": "Example Client",
  "logo_url": "https://example.com/logo.png",
  "branding_color": "#FF5733"
}'
```

### FastAPI Server Endpoints

- `POST /generate-pdf`: Accepts client data and generates a PDF with dynamic branding.

### Configuring Branding Elements

Branding elements such as logos, colors, and fonts can be configured and stored in cloud storage. Ensure that the file paths or URLs of these assets are specified when generating the PDFs.

### Dockerizing the Web Service

1. Build the Docker image:
   ```bash
   docker build -t weasyprint-mcp-server .
   ```

2. Run the Docker container:
   ```bash
   docker run -p 8000:8000 weasyprint-mcp-server
   ```

### Using Poetry for Package Management

This project uses Poetry for package management. Ensure that you have Poetry installed on your system. You can install Poetry by following the instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

To add a new dependency, use the following command:
```bash
poetry add <package-name>
```

To update dependencies, use:
```bash
poetry update
```
