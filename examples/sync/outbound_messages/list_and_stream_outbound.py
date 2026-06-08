"""
Examples for retrieving sent messages.

    python examples/sync/outbound_messages/list_and_stream_outbound.py
"""

import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # --- List ---
    result = client.outbound.list(count=10)
    print(f"List: {result.total} total on server, showing {len(result.items)}")
    for msg in result.items:
        print(f"  {msg.received_at:%Y-%m-%d}  {msg.subject}  → {msg.recipients}")

    # --- Stream (auto-paginated) ---
    print("\nStream: first 50 messages")
    for msg in client.outbound.stream(max_messages=50):
        print(f"  {msg.message_id}  {msg.subject}")

    # --- Get full detail for the first message from the list ---
    if result.items:
        print(f"\nDetail for message: {result.items[0].message_id}")
        detail = client.outbound.get(result.items[0].message_id)
        print(f"  Status: {detail.status}")
        print(f"  Events: {[e.type for e in detail.message_events]}")
    else:
        print("No messages found to fetch details for.")
