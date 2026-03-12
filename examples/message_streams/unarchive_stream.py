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
        stream = await client.stream.unarchive(STREAM_ID)

        print(f"Unarchived stream: {stream.id}")
        print(f"Name:        {stream.name}")
        print(f"Type:        {stream.message_stream_type.value}")
        print(f"Archived at: {stream.archived_at}")


asyncio.run(main())
