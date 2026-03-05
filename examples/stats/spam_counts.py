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
        result = await server.stats.spam_counts(
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
        )

        print(f"Total spam complaints: {result.spam_complaint}")
        print()

        for day in result.days:
            print(f"  {day.date}:  complaints={day.spam_complaint}")


asyncio.run(main())
