"""
Examples for sending messages.

    python examples/sync/outbound_messages/send_outbound_simple.py
"""

import postmark
from postmark import Email

SENDER = "sender@example.com"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # --- Send via dict ---
    response = client.outbound.send(
        {
            "sender": SENDER,
            "to": "receiver@adjkshfjkadshfjkash.com",
            "subject": "Hello from Postmark Python SDK",
            "text_body": "This is a test email sent using the Python SDK.",
            "html_body": (
                "<html><body><strong>Hello</strong>"
                " from Postmark Python SDK.</body></html>"
            ),
            "message_stream": "outbound",
        }
    )
    # print(f"Sent (using dict):  {response.message_id}")
    print(f"\nFull Response: {response}")

    # --- Send via Email model (recommended, offering better type safety) ---
    response = client.outbound.send(
        Email(
            sender=SENDER,
            to="receiver@example.com",
            subject="Hello via Model",
            text_body="This email was built using the Pydantic model.",
            metadata={"user_id": "12345"},
        )
    )
    print(f"Sent (model): {response.message_id}")
