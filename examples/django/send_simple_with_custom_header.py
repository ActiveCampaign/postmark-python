"""
Send an email with custom headers through Postmark's Django backend.

Custom headers are useful for:
- Threading replies (References, In-Reply-To)
- Passing internal tracking or correlation IDs
- Setting message priority
- Integrating with third-party systems that inspect headers

Django's extra_headers dict maps directly onto Postmark's Headers field.

Run:
    poetry run python examples/django/send_simple_with_custom_header.py
    python examples/django/send_simple_with_custom_header.py  # with venv active
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
    subject="Invoice #1042",
    body="Please find your invoice details below.",
    from_email=SENDER,
    to=["receiver@example.com"],
    headers={
        "X-Correlation-ID": "order-1042-usr-9981",
        "X-Priority": "1",
        "References": "<original-message-id@example.com>",
        "In-Reply-To": "<original-message-id@example.com>",
    },
)
message.send()

print("Sent.")
