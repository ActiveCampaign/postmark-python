import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MESSAGE_ID = "id-of-a-failed-message"


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        result = await client.inbound.retry(MESSAGE_ID)

        print(f"Error code: {result.error_code}")
        print(f"Message:    {result.message}")


asyncio.run(main())
