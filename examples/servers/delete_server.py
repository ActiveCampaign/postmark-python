import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])

server_id = 0  # Replace with the ID of the server to delete


async def main():
    result = await account.server.delete(server_id)
    print(result.message)


asyncio.run(main())
