from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl, Field
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
import requests
from celery import Celery
from celery.result import AsyncResult
from typing import List, Dict
import base64
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

app = FastAPI()

# Celery configuration
celery = Celery(
    __name__,
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)


# Define the data model for the client data
class ClientData(BaseModel):
    client_name: str
    logo_url: HttpUrl
    branding_color: str


class HTMLPage(BaseModel):
    page_id: int
    encoded_page_html: str


class GeneratePDFRequest(BaseModel):
    drive_token: str
    destination_folder_id: str
    html_pages: List[HTMLPage]


# Load Jinja2 templates
template_loader = FileSystemLoader(searchpath="./templates")
template_env = Environment(loader=template_loader)


@app.post("/generate-pdf")
async def generate_pdf(request: GeneratePDFRequest, background_tasks: BackgroundTasks):
    # Decode base64 encoded HTML
    decoded_htmls = []
    for page in request.html_pages:
        decoded_html = base64.b64decode(page.encoded_page_html).decode('utf-8')
        decoded_htmls.append(decoded_html)

    # Generate PDF asynchronously
    task = generate_pdf_task.delay(decoded_htmls, request.drive_token, request.destination_folder_id)
    return {"task_id": task.id}


@app.get("/pdf-status/{task_id}")
async def pdf_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    if task_result.state == "PENDING":
        return {"status": "Pending"}
    elif task_result.state == "SUCCESS":
        return {"status": "Success", "file_id": task_result.result}
    else:
        return {"status": "Failed"}


@celery.task
def generate_pdf_task(decoded_htmls: List[str], drive_token: str, destination_folder_id: str):
    pdf_path = "./temp/generated_pdf.pdf"
    combined_html = "".join(decoded_htmls)
    HTML(string=combined_html).write_pdf(pdf_path)

    # Upload the PDF to Google Drive
    credentials = Credentials(token=drive_token)
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {
        'name': 'generated_pdf.pdf',
        'parents': [destination_folder_id]
    }
    media = MediaFileUpload(pdf_path, mimetype='application/pdf')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return file.get('id')


@app.get("/mcp-endpoint")
async def mcp_endpoint():
    return {"message": "MCP endpoint is working"}
