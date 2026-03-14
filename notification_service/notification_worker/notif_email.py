import os
import smtplib
from email.message import EmailMessage
from typing import Iterable, Tuple, List



SMTP_HOST = os.getenv("SMTP_HOST", "smtp")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@example.com")
FROM_NAME = os.getenv("FROM_NAME", "Online Cinema")


class SMTPClient:
    """
    Explicit SMTP client with controlled lifecycle.
    """

    def __init__(self):
        self.server: smtplib.SMTP | None = None

    def __enter__(self):
        self.server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        self.server.ehlo()

        if SMTP_USE_TLS:
            self.server.starttls()
            self.server.ehlo()

        if SMTP_USER and SMTP_PASSWORD:
            self.server.login(SMTP_USER, SMTP_PASSWORD)

        return self

    def __exit__(self, exc_type, exc, tb):
        if self.server:
            try:
                self.server.quit()
            except Exception:
                self.server.close()

    def send(self, message: EmailMessage) -> None:
        if not self.server:
            raise RuntimeError("SMTP connection not initialized")
        self.server.send_message(message)


def _build_message(
    to_email: str,
    subject: str,
    body: str,
    html_body: str | None = None,
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    if html_body:
        msg.set_content(body)
        msg.add_alternative(html_body, subtype="html")
    else:
        msg.set_content(body)

    return msg


# ===============================
# Public API
# ===============================

def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: str | None = None,
) -> None:
    """
    Send a single email.
    """
    msg = _build_message(to_email, subject, body, html_body)

    with SMTPClient() as client:
        client.send(msg)


def send_bulk_emails(
    emails: Iterable[Tuple[str, str, str, str | None]],
) -> None:
    """
    Send many emails in a single SMTP connection.

    Input format:
        [
          (to_email, subject, body, html_body),
          ...
        ]
    """
    messages: List[EmailMessage] = [
        _build_message(to, subject, body, html)
        for to, subject, body, html in emails
    ]

    with SMTPClient() as client:
        for msg in messages:
            client.send(msg)
