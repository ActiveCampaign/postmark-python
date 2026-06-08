"""
Example for sending emails with custom headers.

Custom headers are useful for:
- Threading replies (Reply-To, References, In-Reply-To)
- Passing internal tracking or correlation IDs
- Setting message priority
- Integrating with third-party systems that inspect headers
"""

import asyncio
import os

import postmark
from postmark.models.outbound import Email, Header

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        response = await client.outbound.send(
            Email(
                sender=SENDER,
                to="receiver@example.com",
                subject="Invoice #1042",
                text_body="Please find your invoice details below.",
                headers=[
                    Header(name="X-Correlation-ID", value="order-1042-usr-9981"),
                    Header(name="X-Priority", value="1"),
                    Header(
                        name="References", value="<original-message-id@example.com>"
                    ),
                    Header(
                        name="In-Reply-To", value="<original-message-id@example.com>"
                    ),
                ],
            )
        )

        print(f"Sent: {response.message_id}")


asyncio.run(main())
