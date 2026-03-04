import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
server = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    result = await server.inbound_rules.list()

    print(f"Total inbound rules: {result.total}\n")

    for rule in result.items:
        print(f"  [{rule.id}] {rule.rule}")


asyncio.run(main())
