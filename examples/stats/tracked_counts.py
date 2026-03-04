import asyncio
import os
from datetime import date

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    result = await server.stats.tracked_counts(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print(f"Total tracked emails: {result.tracked}")
    print()

    for day in result.days:
        print(f"  {day.date}:  tracked={day.tracked}")


asyncio.run(main())
