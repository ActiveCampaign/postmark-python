"""
Examples for sending outbound messages.

    python examples/send_messages.py
"""

import asyncio
import os

import postmark
from postmark import Email
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])
SENDER = os.environ["POSTMARK_SENDER_EMAIL"]


async def main():
    # --- Send via dict ---
    response = await client.outbound.send(
        {
            "sender": SENDER,
            "to": "receiver@example.com",
            "subject": "Hello from Postmark Python SDK",
            "text_body": "This is a test email sent using the Python SDK.",
            "html_body": "<html><body><strong>Hello</strong> from Postmark Python SDK.</body></html>",
            "message_stream": "outbound",
        }
    )
    print(f"Sent (dict):  {response.message_id}")

    # --- Send via Email model (recommended, offering better type safety) ---
    response = await client.outbound.send(
        Email(
            sender=SENDER,
            to="receiver@example.com",
            subject="Hello via Model",
            text_body="This email was built using the Pydantic model.",
            metadata={"user_id": "12345"},
        )
    )
    print(f"Sent (model): {response.message_id}")

    # --- Send batch ---
    responses = await client.outbound.send_batch(
        [
            {
                "sender": SENDER,
                "to": "receiver1@example.com",
                "subject": "Batch 1",
                "text_body": "Hello Receiver 1",
            },
            {
                "sender": SENDER,
                "to": "receiver2@example.com",
                "subject": "Batch 2",
                "text_body": "Hello Receiver 2",
            },
        ]
    )
    print(f"Batch: {len(responses)} sent")
    for i, resp in enumerate(responses, start=1):
        print(f"  {i}: {resp.message_id}")


asyncio.run(main())
