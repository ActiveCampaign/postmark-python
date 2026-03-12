import asyncio
import os

import postmark
from postmark.models.servers import ServerColor, TrackLinks

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        server = await client.server.edit(
            name="My Updated Server",
            color=ServerColor.GREEN,
            track_opens=True,
            track_links=TrackLinks.HTML_AND_TEXT,
            inbound_spam_threshold=5,
        )

        print(f"ID:            {server.id}")
        print(f"Name:          {server.name}")
        print(f"Color:         {server.color}")
        print(f"Track opens:   {server.track_opens}")
        print(f"Track links:   {server.track_links}")
        print(f"Spam threshold: {server.inbound_spam_threshold}")


asyncio.run(main())
