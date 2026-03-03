import asyncio
import os

import postmark
from postmark.models.templates import TemplateEmail
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])
SENDER = os.environ["POSTMARK_SENDER_EMAIL"]


async def main():
    # --- Send via model(using template ID) ---
    response = await client.email.send_with_template(
        TemplateEmail(
            sender=SENDER,
            to="recipient@example.com",
            template_id=12345,
            template_model={
                "name": "Alice",
                "action_url": "https://example.com/confirm",
            },
        )
    )
    print(f"Sent (dict, ID):    {response.message_id}")

    # --- Send via dict (using template alias) ---
    response = await client.email.send_with_template(
        {
            "From": SENDER,
            "To": "recipient@example.com",
            "TemplateAlias": "welcome-email",
            "TemplateModel": {
                "name": "Bob",
                "action_url": "https://example.com/confirm",
            },
        }
    )
    print(f"Sent (dict, alias): {response.message_id}")

    # --- Send via TemplateEmail model (recommended, offering better type safety) ---
    response = await client.email.send_with_template(
        TemplateEmail(
            sender=SENDER,
            to="recipient@example.com",
            template_alias="welcome-email",
            template_model={"name": "Carol"},
            message_stream="outbound",
        )
    )
    print(f"Sent (model):       {response.message_id}")


asyncio.run(main())
