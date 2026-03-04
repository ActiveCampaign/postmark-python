import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])

domain_id = 0  # Replace with the ID of the domain to verify


async def main():
    domain = await account.domain.verify_dkim(domain_id)

    print(f"Domain: {domain.name}")
    print(f"  DKIM verified:      {domain.dkim_verified}")
    print(f"  DKIM update status: {domain.dkim_update_status}")
    print(f"  Weak DKIM:          {domain.weak_dkim}")


asyncio.run(main())
