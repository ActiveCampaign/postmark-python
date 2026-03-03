import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # Filter to a specific bounce type; omit `type` to list all.
    bounces, total = await client.bounces.list()
    print(f"{total} hard bounce(s) on server, showing {len(bounces)}")
    for b in bounces:
        print(
            f"  [{b.id}] {b.email}  bounced={b.bounced_at:%Y-%m-%d}"
            f"  inactive={b.inactive}"
        )


asyncio.run(main())
