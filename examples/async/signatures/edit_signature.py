import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

signature_id = 0  # Replace with the ID of the sender signature to update


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        sig = await account.signature.edit(
            signature_id,
            name="Updated Sender Name",
            reply_to="reply@example.com",
        )

        print("Updated sender signature:")
        print(f"  ID:                   {sig.id}")
        print(f"  Name:                 {sig.name}")
        print(f"  Email:                {sig.email_address}")
        print(f"  Return-Path domain:   {sig.return_path_domain}")


asyncio.run(main())
