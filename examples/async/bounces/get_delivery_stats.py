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
        stats = await client.bounces.get_delivery_stats()

        print(f"Inactive addresses: {stats.inactive_mails}")

        for entry in stats.bounces:
            print(f"  {entry.name}: {entry.count}")


asyncio.run(main())
