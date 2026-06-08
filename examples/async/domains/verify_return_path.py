import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

domain_id = 0  # Replace with the ID of the domain to verify


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        domain = await account.domain.verify_return_path(domain_id)

        print(f"Domain: {domain.name}")
        print(f"  Return-Path domain:   {domain.return_path_domain}")
        print(f"  Return-Path verified: {domain.return_path_domain_verified}")
        print(f"  Return-Path CNAME:    {domain.return_path_domain_cname_value}")


asyncio.run(main())
