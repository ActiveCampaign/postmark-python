import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])


async def main():
    result = await account.domain.list()

    print(f"Total domains: {result.total}")
    print()

    for domain in result.items:
        print(f"  [{domain.id}] {domain.name}")
        print(f"       DKIM verified:         {domain.dkim_verified}")
        print(f"       Return-Path verified:  {domain.return_path_domain_verified}")
        print("----------------------------------------")


asyncio.run(main())
