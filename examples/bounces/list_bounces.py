import asyncio
import os

import postmark
from postmark.models.bounces import BounceType
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # Filter to a specific bounce type; omit `type` to list all.
    bounces, total = await client.bounces.list(
        count=10,
        type=BounceType.HARD_BOUNCE,
    )
    print(f"{total} hard bounce(s) on server, showing {len(bounces)}")
    for b in bounces:
        print(f"  [{b.id}] {b.email}  bounced={b.bounced_at:%Y-%m-%d}  inactive={b.inactive}")


asyncio.run(main())
