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
        result = await server.stats.overview(
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
        )

        print("Outbound overview:")
        print(f"  Sent:              {result.sent}")
        print(f"  Bounced:           {result.bounced}")
        print(f"  Bounce rate:       {result.bounce_rate:.2%}")
        print(f"  Spam complaints:   {result.spam_complaints}")
        print(f"  Opens:             {result.opens}")
        print(f"  Unique opens:      {result.unique_opens}")
        print(f"  Total clicks:      {result.total_clicks}")


asyncio.run(main())
