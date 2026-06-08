import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as server:
        result = await server.stats.read_times()

        print("Read-time distribution (totals):")
        for bucket, count in result.model_extra.items():
            print(f"  {bucket}: {count}")

        print(f"\nDaily breakdown ({len(result.days)} day(s)):")
        for day in result.days:
            print(f"  {day}")


asyncio.run(main())
