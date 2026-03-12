import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as server:
        results = await server.suppressions.delete(
            "outbound",
            ["user@example.com"],
        )

        for r in results:
            print(f"  {r.email_address}: {r.status}")
            if r.message:
                print(f"       {r.message}")


asyncio.run(main())
