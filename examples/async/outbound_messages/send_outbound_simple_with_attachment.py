"""
Example for sending emails with attachments.

Attachment content must be Base64-encoded before sending.
The standard library's base64 module handles this for both
in-memory content and files read from disk.

"""

import asyncio
import base64
import os

import postmark
from postmark.models.outbound import Attachment, Email

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        # Building an attachment from a string (in-memory content)
        report_txt = Attachment(
            name="report.txt",
            content=base64.b64encode(b"Q3 sales are up 12%.").decode("utf-8"),
            content_type="text/plain",
        )

        # Building an attachments from a file, on disk
        with open("/path/to/book.pdf", "rb") as f:
            book_pdf = Attachment(
                name="book.pdf",
                content=base64.b64encode(f.read()).decode("utf-8"),
                content_type="application/pdf",
            )

        # Building an attachment from an inline image
        with open("/path/to/logo.png", "rb") as f:
            inline_logo = Attachment(
                name="logo.png",
                content=base64.b64encode(f.read()).decode("utf-8"),
                content_type="image/png",
                content_id="cid:logo",  # reference in html_body as <img src="cid:logo">
            )

        # --- Send ---
        response = await client.outbound.send(
            Email(
                sender=SENDER,
                to="receiver@example.com",
                subject="Your report and resources",
                text_body="Please find your report and resources attached.",
                html_body='<p>Please find your report attached.</p><img src="cid:logo">',
                attachments=[report_txt, book_pdf, inline_logo],
            )
        )

        print(f"Sent: {response.message_id}")


asyncio.run(main())
