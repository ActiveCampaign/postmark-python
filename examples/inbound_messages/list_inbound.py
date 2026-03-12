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
        result = await client.inbound.list(count=10)

        print(f"Total inbound messages: {result.total}")
        print()

        for msg in result.items:
            print(f"  [{msg.message_id}] {msg.subject}")
            print(f"       From:   {msg.from_email}")
            print(f"       Status: {msg.status}")
            print(f"       Date:   {msg.date}")
            print("----------------------------------------")


asyncio.run(main())
