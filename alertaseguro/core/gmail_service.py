import os
import json
import base64
import pickle
import tempfile

from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


def get_google_credentials():
    token_base64 = os.environ.get("GOOGLE_TOKEN_BASE64")
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

    if not token_base64:
        raise Exception("GOOGLE_TOKEN_BASE64 não encontrada")

    if not credentials_json:
        raise Exception("GOOGLE_CREDENTIALS_JSON não encontrada")

    token_bytes = base64.b64decode(token_base64)
    creds = pickle.loads(token_bytes)

    return creds


def send_gmail_api(to_email, subject, body):
    creds = get_google_credentials()

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()