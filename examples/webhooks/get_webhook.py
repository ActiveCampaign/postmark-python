import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

WEBHOOK_ID = int(os.environ.get("POSTMARK_WEBHOOK_ID", "1"))


async def main():
    wh = await server.webhooks.get(WEBHOOK_ID)

    print(f"ID:     {wh.id}")
    print(f"URL:    {wh.url}")
    print(f"Stream: {wh.message_stream}")
    print()
    print("Triggers:")
    print(f"  Opens:   {wh.triggers.open.enabled}")
    print(f"  Clicks:  {wh.triggers.click.enabled}")
    print(f"  Bounces: {wh.triggers.bounce.enabled}")


asyncio.run(main())
