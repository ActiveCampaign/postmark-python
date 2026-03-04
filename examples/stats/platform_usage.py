import asyncio
import os
from datetime import date

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    result = await server.stats.platform_usage(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print("Platform totals:")
    print(f"  Desktop: {result.desktop}")
    print(f"  Mobile:  {result.mobile}")
    print(f"  WebMail: {result.web_mail}")
    print(f"  Unknown: {result.unknown}")
    print()

    for day in result.days:
        print(
            f"  {day.date}:  desktop={day.desktop}  mobile={day.mobile}  webmail={day.web_mail}"
        )


asyncio.run(main())
