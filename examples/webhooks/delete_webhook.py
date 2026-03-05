import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

webhook_id = 0  # Replace with the ID of the webhook to delete


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as server:
        result = await server.webhooks.delete(webhook_id)
        print(result.message)


asyncio.run(main())
