import asyncio
import os

import postmark
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # stream() paginates automatically; adjust max_bounces as needed (max 10,000).
    count = 0
    async for b in client.bounces.stream(max_bounces=200):
        print(f"  [{b.id}] {b.email}  type={b.type}")
        count += 1
    print(f"Streamed {count} bounce(s)")


asyncio.run(main())
