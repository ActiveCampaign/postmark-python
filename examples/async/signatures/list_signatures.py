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
        result = await account.signature.list()

        print(f"Total sender signatures: {result.total}")
        print()

        for sig in result.items:
            print(f"  [{sig.id}] {sig.name} <{sig.email_address}>")
            print(f"       Domain:    {sig.domain}")
            print(f"       Confirmed: {sig.confirmed}")
            print("----------------------------------------")


asyncio.run(main())
