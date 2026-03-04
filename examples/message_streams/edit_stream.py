import asyncio
import os

from dotenv import load_dotenv

import postmark
from postmark.models.streams import UnsubscribeHandlingType

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

STREAM_ID = "my-broadcasts"


async def main():
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
