"""
Example: combining inline (base64) images and external image URLs in one email.

Use case:
  - Inline images (content_id / cid:) are embedded in the email itself.
    The recipient's email client displays them without making any external HTTP
    request, which is ideal for logos or brand assets you always want visible.
  - External image URLs are loaded from a remote server at open time.
    This is the standard technique for tracking pixels and analytics because
    the server can record who fetched the image and when.

Both techniques can appear in the same html_body.
"""

import base64

import postmark
from postmark.models.outbound import Attachment, Email

SENDER = "sender@example.com"

# External tracking pixel URL — loaded by the recipient's email client at open
# time, so the server can record the open event.
TRACKING_PIXEL_URL = "https://track.example.com/pixel.png"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # Inline logo — embedded in the email as base64, no external request.
    with open("/path/to/logo.png", "rb") as f:
        inline_logo = Attachment(
            name="logo.png",
            content=base64.b64encode(f.read()).decode("utf-8"),
            content_type="image/png",
            content_id="cid:logo",  # referenced below as <img src="cid:logo">
        )

    html_body = f"""
    <html><body>
      <!-- Inline image: served from the email itself, always visible offline -->
      <img src="cid:logo" alt="Logo" />

      <p>Hello! Thanks for reading.</p>

      <!-- External image: fetched at open time for analytics -->
      <img src="{TRACKING_PIXEL_URL}" width="1" height="1" alt="" />
    </body></html>
    """

    response = client.outbound.send(
        Email(
            sender=SENDER,
            to="receiver@example.com",
            subject="Hello — with inline logo and tracking",
            text_body="Hello! Thanks for reading. (Open the HTML version to see the logo.)",
            html_body=html_body,
            attachments=[inline_logo],
        )
    )

    print(f"Sent: {response.message_id}")
