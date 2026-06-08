import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as server:
        result = await server.inbound_rules.list()

        print(f"Total inbound rules: {result.total}\n")

        for rule in result.items:
            print(f"  [{rule.id}] {rule.rule}")


asyncio.run(main())
