from celery import Celery
from weasyprint import HTML
import os

celery = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery.task
def generate_pdf_task(html_content: str):
    pdf_path = "./temp/generated_pdf.pdf"
    HTML(string=html_content).write_pdf(pdf_path)
    # Here you can add code to upload the PDF to cloud storage and return the URL
    return pdf_path
