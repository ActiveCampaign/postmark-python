import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    result = await server.stats.read_times()

    print("Read-time distribution (totals):")
    for bucket, count in result.model_extra.items():
        print(f"  {bucket}: {count}")

    print(f"\nDaily breakdown ({len(result.days)} day(s)):")
    for day in result.days:
        print(f"  {day}")


asyncio.run(main())
