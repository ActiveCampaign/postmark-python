import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        result = await account.data_removals.create(
            requested_by="admin@example.com",
            requested_for="user@example.com",
            notify_when_completed=True,
        )

        print(f"ID:     {result.id}")
        print(f"Status: {result.status}")


asyncio.run(main())
