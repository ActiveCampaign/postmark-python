import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

webhook_id = 0  # Replace with the ID of the webhook to update


async def main():
    wh = await server.webhooks.edit(
        webhook_id,
        triggers={
            "Open": {"Enabled": False, "PostFirstOpenOnly": False},
            "Bounce": {"Enabled": True, "IncludeContent": True},
        },
    )

    print("Updated webhook:")
    print(f"  ID:      {wh.id}")
    print(f"  URL:     {wh.url}")
    print(f"  Opens:   {wh.triggers.open.enabled}")
    print(f"  Bounces: {wh.triggers.bounce.enabled}")


asyncio.run(main())
