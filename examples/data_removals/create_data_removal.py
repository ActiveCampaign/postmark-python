import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])


async def main():
    result = await account.data_removals.create(
        requested_by="admin@example.com",
        requested_for="user@example.com",
        notify_when_completed=True,
    )

    print(f"ID:     {result.id}")
    print(f"Status: {result.status}")


asyncio.run(main())
