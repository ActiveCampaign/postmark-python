import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    rule = await server.inbound_rules.create("spam@example.com")

    print("Created inbound rule:")
    print(f"  ID:   {rule.id}")
    print(f"  Rule: {rule.rule}")


asyncio.run(main())
