import asyncio
import os
from datetime import date

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    result = await server.stats.spam_counts(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print(f"Total spam complaints: {result.spam_complaint}")
    print()

    for day in result.days:
        print(f"  {day.date}:  complaints={day.spam_complaint}")


asyncio.run(main())
