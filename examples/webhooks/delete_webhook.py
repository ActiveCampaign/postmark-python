import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

webhook_id = 0  # Replace with the ID of the webhook to delete


async def main():
    result = await server.webhooks.delete(webhook_id)
    print(result.message)


asyncio.run(main())
