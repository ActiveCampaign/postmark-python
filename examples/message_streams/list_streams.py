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
