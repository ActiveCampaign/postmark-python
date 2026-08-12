"""
Send several distinct messages in one call. django.core.mail.send_mass_mail
takes tuples of (subject, message, from_email, recipient_list) and sends them
through a single connection — the Django backend batches them into Postmark's
send_batch API (up to 500 per request) rather than one request per message.

Run:
    poetry run python examples/django/send_batch.py
    python examples/django/send_batch.py  # with venv active
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

from django.core.mail import send_mass_mail  # noqa: E402

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]

sent_count = send_mass_mail(
    (
        ("Batch 1", "Hello Receiver 1", SENDER, ["receiver1@example.com"]),
        ("Batch 2", "Hello Receiver 2", SENDER, ["receiver2@example.com"]),
    )
)

print(f"Sent: {sent_count}")
