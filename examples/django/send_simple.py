"""
Send a single email through Postmark's Django backend.

Standalone script, not a full Django project — real projects configure
settings.py once (see settings_snippet.py) and just call
django.core.mail.send_mail(...) anywhere.

Run:
    poetry run python examples/django/send_simple.py
    python examples/django/send_simple.py  # with venv active
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

from django.core.mail import send_mail  # noqa: E402

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]

send_mail(
    subject="Hello from Postmark",
    message="Sent with postmark.django.EmailBackend.",
    from_email=SENDER,
    recipient_list=["receiver@example.com"],
    html_message="<p>Sent with <b>postmark.django.EmailBackend</b>.</p>",
)

print("Sent.")
