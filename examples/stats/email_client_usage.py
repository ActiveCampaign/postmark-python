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
        result = await server.stats.email_client_usage(
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
        )

        print("Email client totals:")
        for client, count in result.model_extra.items():
            print(f"  {client}: {count}")


asyncio.run(main())
