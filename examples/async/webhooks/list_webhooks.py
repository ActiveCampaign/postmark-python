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
        webhooks = await server.webhooks.list()

        print(f"Total webhooks: {len(webhooks)}")
        print()

        for wh in webhooks:
            print(f"  [{wh.id}] {wh.url}")
            print(f"       Stream:  {wh.message_stream}")
            print(f"       Opens:   {wh.triggers.open.enabled}")
            print(f"       Bounces: {wh.triggers.bounce.enabled}")
            print("----------------------------------------")


asyncio.run(main())
