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
        # stream() paginates automatically; adjust max_bounces as needed (max 10,000).
        count = 0
        async for b in client.bounces.stream(max_bounces=200):
            print(f"[{b.id}] {b.email}  type={b.type}")
            count += 1
        print(f"Streamed {count} bounce(s)")


asyncio.run(main())
