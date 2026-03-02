import asyncio
import os

import postmark
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

bounce_id = 692560173


async def main():
    bounce = await client.bounces.get(bounce_id)

    print(f"ID:           {bounce.id}")
    print(f"Type:         {bounce.type}")
    print(f"Email:        {bounce.email}")
    print(f"Subject:      {bounce.subject}")
    print(f"Bounced at:   {bounce.bounced_at:%Y-%m-%d %H:%M:%S}")
    print(f"Description:  {bounce.description}")
    print(f"Inactive:     {bounce.inactive}")
    print(f"Can activate: {bounce.can_activate}")
    print(f"Dump available: {bounce.dump_available}")


asyncio.run(main())
