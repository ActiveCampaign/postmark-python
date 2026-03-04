import asyncio
import os
from datetime import date

from dotenv import load_dotenv

import postmark
from postmark.models.suppressions import SuppressionReason

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    suppressions = await server.suppressions.dump(
        "outbound",
        suppression_reason=SuppressionReason.HARD_BOUNCE,
        from_date=date(2024, 1, 1),
    )

    print(f"Total suppressions: {len(suppressions)}")
    print()

    for s in suppressions:
        print(f"  {s.email_address}")
        print(f"       Reason:  {s.suppression_reason.value}")
        print(f"       Origin:  {s.origin.value}")
        print(f"       Created: {s.created_at}")
        print("----------------------------------------")


asyncio.run(main())
