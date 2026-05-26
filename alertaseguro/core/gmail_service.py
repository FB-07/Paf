import os
import base64
import pickle

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def get_google_credentials():
    token_base64 = os.environ.get("GOOGLE_TOKEN_BASE64")

    if not token_base64:
        raise Exception("GOOGLE_TOKEN_BASE64 não encontrada")

    token_bytes = base64.b64decode(token_base64)
    creds = pickle.loads(token_bytes)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds


def send_gmail_api(to_email, subject, text_body, html_body):
    creds = get_google_credentials()

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    message = MIMEMultipart("alternative")
    message["to"] = to_email
    message["subject"] = subject

    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()