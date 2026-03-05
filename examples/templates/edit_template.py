import asyncio
import os

import postmark
from postmark.models.templates import EditTemplateRequest

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

template_id = 12345


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        # --- Edit by numeric ID via dict ---
        result = await client.templates.edit(
            template_id,
            {
                "Subject": "Welcome back, {{name}}!",
                "HtmlBody": (
                    "<p>Hi {{name}}, we updated our terms."
                    " <a href='{{url}}'>Read more</a>.</p>"
                ),
            },
        )
        print(f"Edited (ID):    {result.name}  active={result.active}")

        # --- Edit by alias via EditTemplateRequest model ---
        result = await client.templates.edit(
            "welcome-email",
            EditTemplateRequest(name="Welcome Email v2"),
        )
        print(f"Edited (alias): {result.name}  id={result.template_id}")


asyncio.run(main())
