import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MESSAGE_ID = "your-message-id-here"


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        msg = await client.inbound.get(MESSAGE_ID)

        print(f"ID:       {msg.message_id}")
        print(f"From:     {msg.from_email} ({msg.from_name})")
        print(f"To:       {msg.to}")
        print(f"Subject:  {msg.subject}")
        print(f"Status:   {msg.status}")
        print(f"Date:     {msg.date}")
        if msg.text_body:
            print(f"Body:     {msg.text_body[:100]}")
        if msg.blocked_reason:
            print(f"Blocked:  {msg.blocked_reason}")
        print(f"Headers:  {len(msg.headers)}")


asyncio.run(main())
