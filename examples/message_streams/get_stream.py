import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

STREAM_ID = "outbound"


async def main():
    stream = await client.stream.get(STREAM_ID)

    print(f"ID:           {stream.id}")
    print(f"Name:         {stream.name}")
    print(f"Type:         {stream.message_stream_type.value}")
    print(f"Description:  {stream.description}")
    print(f"Created at:   {stream.created_at}")
    print(f"Updated at:   {stream.updated_at}")
    print(
        f"Unsubscribe:  {stream.subscription_management_configuration.unsubscribe_handling_type.value}"
    )


asyncio.run(main())
