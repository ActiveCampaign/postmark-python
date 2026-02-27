"""
Examples for retrieving outbound messages.

    python examples/get_messages.py
"""

import asyncio
import os

import postmark
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # --- List (one page) ---
    messages, total = await client.outbound.list(count=10)
    print(f"List: {total} total on server, showing {len(messages)}")
    for msg in messages:
        print(f"  {msg.received_at:%Y-%m-%d}  {msg.subject}  → {msg.recipients}")

    # --- Stream (auto-paginated) ---
    print("\nStream: first 50 messages")
    async for msg in client.outbound.stream(max_messages=50):
        print(f"  {msg.message_id}  {msg.subject}")

    # --- Get full detail for the first message from the list ---
    if messages:
        print(f"\nDetail for message: {messages[0].message_id}")
        detail = await client.outbound.get(messages[0].message_id)
        print(f"  Status: {detail.status}")
        print(f"  Events: {[e.type for e in detail.message_events]}")
    else:
        print("No messages found to fetch details for.")


asyncio.run(main())
