import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

template_id = 12345


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        # --- Delete by numeric ID ---
        result = await client.templates.delete(template_id)
        print(f"Deleted (ID):    code={result.error_code}  message={result.message}")

        # --- Delete by alias ---
        result = await client.templates.delete("old-promo-email")
        print(f"Deleted (alias): code={result.error_code}  message={result.message}")


asyncio.run(main())
