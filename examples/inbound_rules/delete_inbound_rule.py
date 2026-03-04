import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

trigger_id = 0  # Replace with the ID of the inbound rule to delete


async def main():
    result = await server.inbound_rules.delete(trigger_id)
    print(result.message)


asyncio.run(main())
