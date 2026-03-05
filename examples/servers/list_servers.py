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
        result = await account.server.list()

        print(f"Total servers: {result.total}")
        print()

        for server in result.items:
            print(f"  [{server.id}] {server.name}")
            print(f"       Color:         {server.color.value}")
            print(f"       Delivery type: {server.delivery_type.value}")
            print(f"       SMTP enabled:  {server.smtp_api_activated}")
            print("----------------------------------------")


asyncio.run(main())
