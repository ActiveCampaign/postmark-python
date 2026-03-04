import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])


async def main():
    result = await account.signature.list()

    print(f"Total sender signatures: {result.total}")
    print()

    for sig in result.items:
        print(f"  [{sig.id}] {sig.name} <{sig.email_address}>")
        print(f"       Domain:    {sig.domain}")
        print(f"       Confirmed: {sig.confirmed}")
        print("----------------------------------------")


asyncio.run(main())
