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
        result = await server.stats.browser_usage(
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
        )

        print("Browser totals:")
        for browser, count in result.model_extra.items():
            print(f"  {browser}: {count}")
        print()

        for day in result.days:
            date_str = day.pop("Date", "?")
            print(f"  {date_str}: {day}")


asyncio.run(main())
