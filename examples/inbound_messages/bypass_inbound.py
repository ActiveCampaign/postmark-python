import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

MESSAGE_ID = "your-blocked-message-id-here"


async def main():
    result = await client.inbound.bypass(MESSAGE_ID)

    print(f"Error code: {result.error_code}")
    print(f"Message:    {result.message}")


asyncio.run(main())
