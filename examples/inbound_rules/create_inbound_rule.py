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
        rule = await server.inbound_rules.create("spam@example.com")

        print("Created inbound rule:")
        print(f"  ID:   {rule.id}")
        print(f"  Rule: {rule.rule}")


asyncio.run(main())
