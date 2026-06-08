import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Note that this call is on the ServerClient, which returns information about itself.
# To retrieve information about other servers, use AccountClient and POSTMARK_ACCOUNT_TOKEN.


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        server = await client.server.get()

        print(f"ID:                   {server.id}")
        print(f"Name:                 {server.name}")
        print(f"Color:                {server.color.value}")
        print(f"Delivery type:        {server.delivery_type.value}")
        print(f"SMTP enabled:         {server.smtp_api_activated}")
        print(f"Track opens:          {server.track_opens}")
        print(f"Track links:          {server.track_links.value}")
        print(f"Inbound address:      {server.inbound_address}")
        print(f"Inbound spam threshold: {server.inbound_spam_threshold}")
        print(f"Server link:          {server.server_link}")


asyncio.run(main())
