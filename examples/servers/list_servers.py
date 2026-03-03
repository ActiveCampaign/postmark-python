import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])


async def main():
    servers, total = await account.server.list()

    print(f"Total servers: {total}")
    print()

    for server in servers:
        print(f"  [{server.id}] {server.name}")
        print(f"       Color:         {server.color.value}")
        print(f"       Delivery type: {server.delivery_type.value}")
        print(f"       SMTP enabled:  {server.smtp_api_activated}")
        print("----------------------------------------")


asyncio.run(main())
