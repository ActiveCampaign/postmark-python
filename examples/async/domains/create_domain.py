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
        domain = await account.domain.create(
            name="example.com",
            return_path_domain="pm-bounces.example.com",
        )

        print("Created domain:")
        print(f"  ID:                   {domain.id}")
        print(f"  Name:                 {domain.name}")
        print(f"  DKIM host:            {domain.dkim_host}")
        print(f"  DKIM text value:      {domain.dkim_text_value}")
        print(f"  Return-Path domain:   {domain.return_path_domain}")
        print(f"  Return-Path CNAME:    {domain.return_path_domain_cname_value}")


asyncio.run(main())
