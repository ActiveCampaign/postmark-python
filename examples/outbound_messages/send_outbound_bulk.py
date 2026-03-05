import asyncio
import os

from dotenv import load_dotenv

import postmark
from postmark.models.outbound import BulkEmail, BulkRecipient

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])
SENDER = os.environ["POSTMARK_SENDER_EMAIL"]


async def main():
    # --- Recommended: use BulkRecipient models for improved type safety. ---
    response = await client.outbound.send_bulk(
        BulkEmail(
            sender=SENDER,
            subject="Hello {{FirstName}}, your order is ready",
            html_body=(
                "<p>Hi {{FirstName}}, your order"
                " <strong>{{OrderId}}</strong> is ready.</p>"
            ),
            text_body="Hi {{FirstName}}, your order {{OrderId}} is ready.",
            message_stream="broadcast",
            messages=[
                BulkRecipient(
                    to="bob@example.com",
                    template_model={"FirstName": "Bob", "OrderId": "ORD-001"},
                ),
                BulkRecipient(
                    to="frieda@example.com",
                    template_model={"FirstName": "Frieda", "OrderId": "ORD-002"},
                ),
                BulkRecipient(
                    to="elijah@example.com",
                    template_model={"FirstName": "Elijah", "OrderId": "ORD-003"},
                ),
            ],
        )
    )
    print(f"Bulk request accepted — ID: {response.id}  Status: {response.status}")

    # --- ...or send bulk using dict(s) ---
    response = await client.outbound.send_bulk(
        {
            "sender": SENDER,
            "subject": "Hello {{FirstName}}, your order is ready",
            "html_body": (
                "<p>Hi {{FirstName}}, your order"
                " <strong>{{OrderId}}</strong> is ready.</p>"
            ),
            "text_body": "Hi {{FirstName}}, your order {{OrderId}} is ready.",
            "message_stream": "broadcast",
            "track_opens": True,
            "messages": [
                {
                    "to": "bob@example.com",
                    "template_model": {"FirstName": "Bob", "OrderId": "ORD-001"},
                },
                {
                    "to": "frieda@example.com",
                    "template_model": {"FirstName": "Frieda", "OrderId": "ORD-002"},
                },
                {
                    "to": "elijah@example.com",
                    "template_model": {"FirstName": "Elijah", "OrderId": "ORD-003"},
                    "cc": "manager@example.com",
                },
            ],
        }
    )
    print(f"Bulk request accepted — ID: {response.id}  Status: {response.status}")

    # --- Poll for completion ---
    status = await client.outbound.get_bulk_status(response.id)
    print(
        f"Status: {status.status}  ("
        f"{status.percentage_completed:.0f}% of"
        f" {status.total_messages} messages sent)"
    )


asyncio.run(main())
