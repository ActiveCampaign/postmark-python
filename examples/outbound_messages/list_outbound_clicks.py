import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        # All clicks across messages
        result = await client.outbound.list_clicks(count=10)

        print(f"Total clicks: {result.total}")
        print()

        for event in result.items:
            print(f"  [{event.message_id}] {event.recipient}")
            print(f"       Link:     {event.original_link}")
            print(f"       Location: {event.click_location}")
            print(f"       At:       {event.received_at}")

        print()

        # Clicks for a specific message
        if result.items:
            msg_id = result.items[0].message_id
            msg_result = await client.outbound.list_message_clicks(msg_id)
            print(f"Clicks for {msg_id}: {msg_result.total}")


asyncio.run(main())
