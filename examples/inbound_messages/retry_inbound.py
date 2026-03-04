import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

MESSAGE_ID = "id-of-a-failed-message"


async def main():
    result = await client.inbound.retry(MESSAGE_ID)

    print(f"Error code: {result.error_code}")
    print(f"Message:    {result.message}")


asyncio.run(main())
