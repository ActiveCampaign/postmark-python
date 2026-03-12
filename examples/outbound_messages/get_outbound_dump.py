import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MESSAGE_ID = "your-message-id-here"


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        dump = await client.outbound.get_dump(MESSAGE_ID)
        print(dump.body)


asyncio.run(main())
