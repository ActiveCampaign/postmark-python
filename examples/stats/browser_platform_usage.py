import asyncio
import os
from datetime import date

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as server:
        result = await server.stats.browser_platform_usage(
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
        )

        print("Browser platform totals:")
        print(f"  Desktop: {result.desktop}")
        print(f"  Mobile:  {result.mobile}")
        print(f"  Unknown: {result.unknown}")
        print()

        for day in result.days:
            print(f"  {day.date}:  desktop={day.desktop}  mobile={day.mobile}")


asyncio.run(main())
