import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

server_id = 0  # Replace with the ID of the server to delete


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        result = await account.server.delete(server_id)
        print(result.message)


asyncio.run(main())
