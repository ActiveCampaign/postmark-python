import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

domain_id = 0  # Replace with the ID of the domain to retrieve


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        domain = await account.domain.get(domain_id)

        print(f"Domain: {domain.name}")
        print(f"  ID:                      {domain.id}")
        print(f"  DKIM verified:           {domain.dkim_verified}")
        print(f"  DKIM host:               {domain.dkim_host}")
        print(f"  Return-Path domain:      {domain.return_path_domain}")
        print(f"  Return-Path verified:    {domain.return_path_domain_verified}")
        print(f"  DKIM update status:      {domain.dkim_update_status}")


asyncio.run(main())
