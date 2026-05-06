import base64
import pickle

from email.mime.text import MIMEText
from googleapiclient.discovery import build


def send_gmail_api(to_email, subject, body):
    with open("token.pkl", "rb") as token:
        creds = pickle.load(token)

    service = build("gmail", "v1", credentials=creds)

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