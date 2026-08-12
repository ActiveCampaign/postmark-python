"""
Send HTML email referencing an external image URL (e.g. a tracking pixel or a
logo hosted on your own server) — loaded by the recipient's email client at
open time, no attachment needed.

Note: inline (Content-ID / cid:) images are NOT supported through this Django
backend, since Django only exposes that via passing a raw email.mime.base.MIMEBase
object to EmailMessage.attach() — a legacy path this backend intentionally
doesn't support (see the Django-Backend wiki page). For inline images, either
host the image externally as shown here, or send directly with
postmark.ServerClient / postmark.sync.ServerClient using an Attachment with
content_id set (see examples/async/outbound_messages/send_with_inline_and_external_images.py).

Run:
    poetry run python examples/django/send_with_external_image.py
    python examples/django/send_with_external_image.py  # with venv active
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

from django.core.mail import EmailMultiAlternatives  # noqa: E402

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]

# Fetched by the recipient's email client at open time, so the server can
# record the open event.
TRACKING_PIXEL_URL = "https://track.example.com/pixel.png"

html_body = f"""
<html><body>
  <p>Hello! Thanks for reading.</p>
  <img src="{TRACKING_PIXEL_URL}" width="1" height="1" alt="" />
</body></html>
"""

message = EmailMultiAlternatives(
    subject="Hello — with tracking image",
    body="Hello! Thanks for reading. (Open the HTML version to see the image.)",
    from_email=SENDER,
    to=["receiver@example.com"],
)
message.attach_alternative(html_body, "text/html")
message.send()

print("Sent.")
