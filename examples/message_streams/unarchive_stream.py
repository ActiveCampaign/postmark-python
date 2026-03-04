import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

STREAM_ID = "my-broadcasts"


async def main():
    stream = await client.stream.unarchive(STREAM_ID)

    print(f"Unarchived stream: {stream.id}")
    print(f"Name:        {stream.name}")
    print(f"Type:        {stream.message_stream_type.value}")
    print(f"Archived at: {stream.archived_at}")


asyncio.run(main())
