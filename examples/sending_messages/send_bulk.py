import asyncio
import os

import postmark
from postmark.models.messages import BulkEmail, BulkRecipient
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])
SENDER = os.environ["POSTMARK_SENDER_EMAIL"]


async def main():
    # --- It's recommended sending using BulkRecipient class models, for improved type safety. ---
    response = await client.email.send_bulk(
        BulkEmail(
            sender=SENDER,
            subject="Hello {{FirstName}}, your order is ready",
            html_body="<p>Hi {{FirstName}}, your order <strong>{{OrderId}}</strong> is ready.</p>",
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
    response = await client.email.send_bulk(
        {
            "sender": SENDER,
            "subject": "Hello {{FirstName}}, your order is ready",
            "html_body": "<p>Hi {{FirstName}}, your order <strong>{{OrderId}}</strong> is ready.</p>",
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
    status = await client.email.get_bulk_status(response.id)
    print(
        f"Status: {status.status}  ({status.percentage_completed:.0f}% of {status.total_messages} messages sent)"
    )


asyncio.run(main())
