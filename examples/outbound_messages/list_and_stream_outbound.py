"""
Examples for retrieving sent messages.

    python examples/get_messages.py
"""

import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # --- List ---
    result = await client.outbound.list(count=10)
    print(f"List: {result.total} total on server, showing {len(result.items)}")
    for msg in result.items:
        print(f"  {msg.received_at:%Y-%m-%d}  {msg.subject}  → {msg.recipients}")

    # --- Stream (auto-paginated) ---
    print("\nStream: first 50 messages")
    async for msg in client.outbound.stream(max_messages=50):
        print(f"  {msg.message_id}  {msg.subject}")

    # --- Get full detail for the first message from the list ---
    if result.items:
        print(f"\nDetail for message: {result.items[0].message_id}")
        detail = await client.outbound.get(result.items[0].message_id)
        print(f"  Status: {detail.status}")
        print(f"  Events: {[e.type for e in detail.message_events]}")
    else:
        print("No messages found to fetch details for.")


asyncio.run(main())
