import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])


async def main():
    sig = await account.signature.create(
        sender="sender@example.com",
        name="Sender Name",
        reply_to="reply@example.com",
        return_path_domain="pm-bounces.example.com",
    )

    print("Created sender signature:")
    print(f"  ID:                   {sig.id}")
    print(f"  Name:                 {sig.name}")
    print(f"  Email:                {sig.email_address}")
    print(f"  DKIM host:            {sig.dkim_host}")
    print(f"  Return-Path domain:   {sig.return_path_domain}")
    print(f"  Confirmed:            {sig.confirmed}")


asyncio.run(main())
