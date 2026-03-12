import asyncio
import os

import postmark
from postmark.models.streams import UnsubscribeHandlingType

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

STREAM_ID = "my-broadcasts"


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        stream = await client.stream.edit(
            STREAM_ID,
            name="Updated Broadcast Stream",
            description="Newsletters and product updates",
            unsubscribe_handling_type=UnsubscribeHandlingType.POSTMARK,
        )

        print("Updated stream:")
        print(f"  ID:          {stream.id}")
        print(f"  Name:        {stream.name}")
        print(f"  Description: {stream.description}")
        print(
            f"  Unsubscribe: {stream.subscription_management_configuration.unsubscribe_handling_type.value}"
        )


asyncio.run(main())
