import asyncio
import os
from datetime import date

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    result = await server.stats.bounce_counts(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print("Bounce totals:")
    print(f"  Hard bounces:    {result.hard_bounce}")
    print(f"  Soft bounces:    {result.soft_bounce}")
    print(f"  SMTP API errors: {result.smtp_api_error}")
    print(f"  Transient:       {result.transient}")
    print()

    for day in result.days:
        print(f"  {day.date}:  hard={day.hard_bounce}  soft={day.soft_bounce}")


asyncio.run(main())
