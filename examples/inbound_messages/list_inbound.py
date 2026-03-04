import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    messages, total = await client.inbound.list(count=10)

    print(f"Total inbound messages: {total}")
    print()

    for msg in messages:
        print(f"  [{msg.message_id}] {msg.subject}")
        print(f"       From:   {msg.from_email}")
        print(f"       Status: {msg.status}")
        print(f"       Date:   {msg.date}")
        print("----------------------------------------")


asyncio.run(main())
