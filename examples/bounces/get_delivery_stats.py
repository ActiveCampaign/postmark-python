import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    stats = await client.bounces.get_delivery_stats()

    print(f"Inactive addresses: {stats.inactive_mails}")

    for entry in stats.bounces:
        print(f"  {entry.name}: {entry.count}")


asyncio.run(main())
