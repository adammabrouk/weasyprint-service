from celery import Celery
from weasyprint import HTML
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

celery = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery.task
def generate_pdf_task(decoded_htmls: list, drive_token: str, destination_folder_id: str):
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
