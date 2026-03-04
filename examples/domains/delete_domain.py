import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])

domain_id = 0  # Replace with the ID of the domain to delete


async def main():
    result = await account.domain.delete(domain_id)
    print(result.message)


asyncio.run(main())
