import asyncio
import os
from datetime import date

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    result = await server.stats.click_counts(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print(f"Total clicks:  {result.clicks}")
    print(f"Unique clicks: {result.unique}")
    print()

    for day in result.days:
        print(f"  {day.date}:  clicks={day.clicks}  unique={day.unique}")


asyncio.run(main())
