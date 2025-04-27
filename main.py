from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl, Field
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
import requests
from celery import Celery
from celery.result import AsyncResult
from typing import List, Dict

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


class GeneratePDFRequest(BaseModel):
    html_urls: List[HttpUrl]
    drive_link: HttpUrl
    auth_token: str
    static_assets: Dict[str, HttpUrl]


# Load Jinja2 templates
template_loader = FileSystemLoader(searchpath="./templates")
template_env = Environment(loader=template_loader)


@app.post("/generate-pdf")
async def generate_pdf(request: GeneratePDFRequest, background_tasks: BackgroundTasks):
    # Fetch HTML files
    html_contents = []
    headers = {"Authorization": f"Bearer {request.auth_token}"}
    for url in request.html_urls:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Invalid HTML URL: {url}")
        html_contents.append(response.text)

    # Fetch static assets
    static_assets = {}
    for asset_name, asset_url in request.static_assets.items():
        response = requests.get(asset_url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail=f"Invalid asset URL: {asset_url}"
            )
        asset_path = f"./temp/{asset_name}"
        with open(asset_path, "wb") as asset_file:
            asset_file.write(response.content)
        static_assets[asset_name] = asset_path

    # Render the HTML templates with client data
    rendered_htmls = []
    for html_content in html_contents:
        template = template_env.from_string(html_content)
        rendered_html = template.render(static_assets=static_assets)
        rendered_htmls.append(rendered_html)

    # Generate PDF asynchronously
    task = generate_pdf_task.delay(rendered_htmls)
    return {"task_id": task.id}


@app.get("/pdf-status/{task_id}")
async def pdf_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    if task_result.state == "PENDING":
        return {"status": "Pending"}
    elif task_result.state == "SUCCESS":
        return {"status": "Success", "pdf_url": task_result.result}
    else:
        return {"status": "Failed"}


@celery.task
def generate_pdf_task(rendered_htmls: List[str]):
    pdf_path = "./temp/generated_pdf.pdf"
    combined_html = "".join(rendered_htmls)
    HTML(string=combined_html).write_pdf(pdf_path)
    # Here you can add code to upload the PDF to cloud storage and return the URL
    return pdf_path


@app.get("/mcp-endpoint")
async def mcp_endpoint():
    return {"message": "MCP endpoint is working"}
