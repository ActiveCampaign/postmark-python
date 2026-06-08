import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

server_id = 1234567  # Replace with the ID of the server to retrieve


async def main():
    async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
        server = await account.server.get(server_id)

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
