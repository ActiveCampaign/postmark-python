import asyncio
import os

import postmark
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

template_id = 12345


async def main():
    # --- Get by numeric ID ---
    template = await client.templates.get(template_id)

    print(f"ID:      {template.template_id}")
    print(f"Name:    {template.name}")
    print(f"Alias:   {template.alias}")
    print(f"Type:    {template.template_type}")
    print(f"Active:  {template.active}")
    print(f"Subject: {template.subject}")

    # --- Get by alias ---
    template = await client.templates.get("welcome-email")

    print(f"\nFetched by alias: {template.name} (id={template.template_id})")


asyncio.run(main())
