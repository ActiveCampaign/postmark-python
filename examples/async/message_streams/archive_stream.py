import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

STREAM_ID = "my-broadcasts"


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        result = await client.stream.archive(STREAM_ID)

        print(f"Archived stream: {result.id}")
        print(f"Expected purge date: {result.expected_purge_date}")


asyncio.run(main())
