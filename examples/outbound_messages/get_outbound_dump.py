import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

MESSAGE_ID = "your-message-id-here"


async def main():
    dump = await client.outbound.get_dump(MESSAGE_ID)
    print(dump.body)


asyncio.run(main())
