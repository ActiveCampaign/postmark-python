import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

MESSAGE_ID = "your-message-id-here"


async def main():
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
