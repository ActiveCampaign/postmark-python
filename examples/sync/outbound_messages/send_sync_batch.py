"""
Send a batch of emails synchronously — no async/await required.

Up to 500 messages can be submitted in a single batch call.

Run:
    poetry run python examples/sync/outbound_messages/send_sync_batch.py
    python examples/sync/outbound_messages/send_sync_batch.py  # with venv active
"""

import postmark
from postmark import Email

SENDER = "sender@example.com"

messages = [
    Email(
        sender=SENDER,
        to="alice@example.com",  # change to real addresses
        subject="Hello Alice",
        text_body="Hi Alice, sent via postmark.sync.",
    ),
    Email(
        sender=SENDER,
        to="bob@example.com",
        subject="Hello Bob",
        text_body="Hi Bob, sent via postmark.sync.",
    ),
]

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    results = client.outbound.send_batch(messages)
    for r in results:
        print(f"Message ID: {r.message_id}  Accepted: {r.success}")
