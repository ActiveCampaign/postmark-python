import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as server:
        wh = await server.webhooks.create(
            url="https://example.com/webhook",
            message_stream="outbound",
            triggers={
                "Open": {"Enabled": True, "PostFirstOpenOnly": False},
                "Bounce": {"Enabled": True, "IncludeContent": False},
            },
        )

        print("Created webhook:")
        print(f"  ID:      {wh.id}")
        print(f"  URL:     {wh.url}")
        print(f"  Stream:  {wh.message_stream}")
        print(f"  Opens:   {wh.triggers.open.enabled}")
        print(f"  Bounces: {wh.triggers.bounce.enabled}")


asyncio.run(main())
