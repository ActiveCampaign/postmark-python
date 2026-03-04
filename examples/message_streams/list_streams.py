import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    result = await client.stream.list()

    print(f"Total streams: {result.total}")
    print()

    for stream in result.items:
        print(f"  [{stream.id}] {stream.name}")
        print(f"       Type:        {stream.message_stream_type.value}")
        print(f"       Created at:  {stream.created_at}")
        print(f"       Archived:    {stream.archived_at is not None}")
        print("----------------------------------------")


asyncio.run(main())
