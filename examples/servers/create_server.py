import asyncio
import os

import postmark
from postmark.models.servers import DeliveryType, ServerColor

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        server = await account.server.create(
            name="My New Server",
            color=ServerColor.BLUE,
            delivery_type=DeliveryType.SANDBOX,
            track_opens=True,
        )

        print("Created server:")
        print(f"  ID:            {server.id}")
        print(f"  Name:          {server.name}")
        print(f"  Color:         {server.color.value}")
        print(f"  Delivery type: {server.delivery_type.value}")
        print(f"  Inbound address: {server.inbound_address}")


asyncio.run(main())
