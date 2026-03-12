import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

STREAM_ID = "outbound"


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
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
