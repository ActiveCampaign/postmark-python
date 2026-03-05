import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

domain_id = 0  # Replace with the ID of the domain to update


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        domain = await account.domain.edit(
            domain_id,
            return_path_domain="pm-bounces.example.com",
        )

        print("Updated domain:")
        print(f"  ID:                   {domain.id}")
        print(f"  Name:                 {domain.name}")
        print(f"  Return-Path domain:   {domain.return_path_domain}")
        print(f"  Return-Path verified: {domain.return_path_domain_verified}")


asyncio.run(main())
