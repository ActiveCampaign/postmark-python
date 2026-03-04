import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])

signature_id = 0  # Replace with the ID of the sender signature to delete


async def main():
    result = await account.signature.delete(signature_id)
    print(result.message)


asyncio.run(main())
