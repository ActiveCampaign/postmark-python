import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])

signature_id = 0  # Replace with the ID of the sender signature to retrieve


async def main():
    sig = await account.signature.get(signature_id)

    print(f"Sender signature: {sig.name} <{sig.email_address}>")
    print(f"  ID:                      {sig.id}")
    print(f"  Confirmed:               {sig.confirmed}")
    print(f"  DKIM verified:           {sig.dkim_verified}")
    print(f"  DKIM host:               {sig.dkim_host}")
    print(f"  Return-Path domain:      {sig.return_path_domain}")
    print(f"  Return-Path verified:    {sig.return_path_domain_verified}")


asyncio.run(main())
