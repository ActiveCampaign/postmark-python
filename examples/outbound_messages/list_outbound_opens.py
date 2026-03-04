import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # All opens across messages
    opens, total = await client.outbound.list_opens(count=10)

    print(f"Total opens: {total}")
    print()

    for event in opens:
        print(f"  [{event.message_id}] {event.recipient}")
        print(f"       Platform: {event.platform}")
        print(f"       Client:   {event.client.name}")
        print(f"       At:       {event.received_at}")

    print()

    # Opens for a specific message
    if opens:
        msg_id = opens[0].message_id
        msg_opens, msg_total = await client.outbound.list_message_opens(msg_id)
        print(f"Opens for {msg_id}: {msg_total}")


asyncio.run(main())
