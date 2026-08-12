"""
Tag, metadata, and message stream require PostmarkEmailMessage /
PostmarkEmailMultiAlternatives instead of Django's plain EmailMessage, since
those are Postmark-specific fields with no Django equivalent.

Run:
    poetry run python examples/django/send_with_tags_and_metadata.py
    python examples/django/send_with_tags_and_metadata.py  # with venv active
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

from postmark.django import PostmarkEmailMessage  # noqa: E402

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]

message = PostmarkEmailMessage(
    subject="Your invitation",
    body="You're invited!",
    from_email=SENDER,
    to=["receiver@example.com"],
    tag="invitation",
    metadata={"user_id": "12345"},
    message_stream="outbound",
)
message.send()

print("Sent.")
