import os
from typing import List
from requests import Response, post


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class MailGun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    MAILGUN_EMAIL = os.environ.get("MAILGUN_EMAIL")

    @classmethod
    def send_email(cls, email: List["str"], subject: str, text: str, html: str) -> Response:

        if cls.MAILGUN_API_KEY is None:
            raise MailGunException("Mailgun failed load api key")

        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException("Mailgun failed load domain")

        if cls.MAILGUN_EMAIL is None:
            raise MailGunException("Mailgun failed load email")

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"FVA<{cls.MAILGUN_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            }
        )
        if response.status_code != 200:
            raise MailGunException("Mailgun error sending email")
        return response