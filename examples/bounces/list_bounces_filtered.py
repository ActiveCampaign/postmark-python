import asyncio
import os
from datetime import datetime

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        # Narrow results to inactive addresses within a date range on a specific stream.
        result = await client.bounces.list(
            count=25,
            inactive=True,
            from_date=datetime(2024, 1, 1),
            to_date=datetime(2024, 12, 31),
            message_stream="outbound",
        )
        print(f"{result.total} matching bounce(s), showing {len(result.items)}")
        for b in result.items:
            print(
                f"  [{b.id}] {b.email}  type={b.type}  bounced={b.bounced_at:%Y-%m-%d}"
            )


asyncio.run(main())
