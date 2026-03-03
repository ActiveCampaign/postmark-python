import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


# Bounce ID's that can be activated show "can_activate" -> True.
bounce_id = 692560173


async def main():
    result = await client.bounces.activate(bounce_id)
    print(f"Response: {result.message}")
    print(f"Inactive after activation: {result.bounce.inactive}")


asyncio.run(main())
