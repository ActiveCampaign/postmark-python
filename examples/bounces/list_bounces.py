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
        # Filter to a specific bounce type; omit `type` to list all.
        result = await client.bounces.list()
        print(f"{result.total} hard bounce(s) on server, showing {len(result.items)}")
        for b in result.items:
            print(
                f"  [{b.id}] {b.email}  bounced={b.bounced_at:%Y-%m-%d}"
                f"  inactive={b.inactive}"
            )


asyncio.run(main())
