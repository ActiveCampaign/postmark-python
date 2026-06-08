import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

domain_id = 0  # Replace with the ID of the domain to rotate DKIM keys for


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        domain = await account.domain.rotate_dkim(domain_id)

        print(f"Domain: {domain.name}")
        print(f"  DKIM update status:       {domain.dkim_update_status}")
        print(f"  Current DKIM host:        {domain.dkim_host}")
        print(f"  Pending DKIM host:        {domain.dkim_pending_host}")
        print(f"  Pending DKIM text value:  {domain.dkim_pending_text_value}")


asyncio.run(main())
