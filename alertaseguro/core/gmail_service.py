import os
import base64
import pickle

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build


def get_google_credentials():
    with open("token.pkl", "rb") as token:
        creds = pickle.load(token)

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