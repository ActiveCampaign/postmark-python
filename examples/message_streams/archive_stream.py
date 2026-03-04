import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

STREAM_ID = "my-broadcasts"


async def main():
    result = await client.stream.archive(STREAM_ID)

    print(f"Archived stream: {result.id}")
    print(f"Expected purge date: {result.expected_purge_date}")


asyncio.run(main())
