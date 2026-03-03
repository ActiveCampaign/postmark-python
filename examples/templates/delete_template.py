import asyncio
import os

from dotenv import load_dotenv

import postmark

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

template_id = 12345


async def main():
    # --- Delete by numeric ID ---
    result = await client.templates.delete(template_id)
    print(f"Deleted (ID):    code={result.error_code}  message={result.message}")

    # --- Delete by alias ---
    result = await client.templates.delete("old-promo-email")
    print(f"Deleted (alias): code={result.error_code}  message={result.message}")


asyncio.run(main())
