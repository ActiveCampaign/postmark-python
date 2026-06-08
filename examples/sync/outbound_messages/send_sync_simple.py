"""
Send a single email synchronously — no async/await required.

Run:
    poetry run python examples/sync/outbound_messages/send_sync_simple.py
    python examples/sync/outbound_messages/send_sync_simple.py  # with venv active
"""

import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    response = client.outbound.send(
        {
            "sender": "sender@example.com",
            "to": "you@example.com",  # change to your address
            "subject": "Hello from Postmark (sync)",
            "text_body": "Sent with postmark.sync — no async required.",
            "html_body": "<p>Sent with <strong>postmark.sync</strong> — no async required.</p>",
        }
    )
    print(f"Message ID: {response.message_id}")
    print(f"Accepted:   {response.success}")
