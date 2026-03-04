import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # All clicks across messages
    clicks, total = await client.outbound.list_clicks(count=10)

    print(f"Total clicks: {total}")
    print()

    for event in clicks:
        print(f"  [{event.message_id}] {event.recipient}")
        print(f"       Link:     {event.original_link}")
        print(f"       Location: {event.click_location}")
        print(f"       At:       {event.received_at}")

    print()

    # Clicks for a specific message
    if clicks:
        msg_id = clicks[0].message_id
        msg_clicks, msg_total = await client.outbound.list_message_clicks(msg_id)
        print(f"Clicks for {msg_id}: {msg_total}")


asyncio.run(main())
