"""
Send an email with an attachment through Postmark's Django backend.

Attachment content is base64-encoded automatically — pass the raw
bytes/str you'd normally give EmailMessage.attach(), same as any other
Django email backend.

Run:
    poetry run python examples/django/send_simple_with_attachment.py
    python examples/django/send_simple_with_attachment.py  # with venv active
"""

import os

import django
from django.conf import settings

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

if not settings.configured:
    settings.configure(
        EMAIL_BACKEND="postmark.django.EmailBackend",
        POSTMARK_SERVER_TOKEN=os.environ["POSTMARK_SERVER_TOKEN"],
    )
    django.setup()

from django.core.mail import EmailMessage  # noqa: E402

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]

message = EmailMessage(
    subject="Your report and resources",
    body="Please find your report attached.",
    from_email=SENDER,
    to=["receiver@example.com"],
)
message.attach("report.txt", "Q3 sales are up 12%.", "text/plain")

with open("/path/to/book.pdf", "rb") as f:
    message.attach("book.pdf", f.read(), "application/pdf")

message.send()

print("Sent.")
