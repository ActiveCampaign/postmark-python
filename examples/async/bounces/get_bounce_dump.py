import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Bounce ID must have "dump_available" -> True.
bounce_id = 692560173
# Postmark retains raw SMTP dumps for ~30 days after the bounce.


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        dump = await client.bounces.get_dump(bounce_id)
        if dump.body:
            print(dump.body)
        else:
            print("Dump not available (may have expired after 30 days).")


asyncio.run(main())
