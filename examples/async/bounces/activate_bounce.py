import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Bounce ID's that can be activated show "can_activate" -> True.
bounce_id = 692560173


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        result = await client.bounces.activate(bounce_id)
        print(f"Response: {result.message}")
        print(f"Inactive after activation: {result.bounce.inactive}")


asyncio.run(main())
