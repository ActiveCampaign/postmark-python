import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    results = await server.suppressions.create(
        "outbound",
        ["user@example.com", "other@example.com"],
    )

    for r in results:
        print(f"  {r.email_address}: {r.status}")
        if r.message:
            print(f"       {r.message}")


asyncio.run(main())
