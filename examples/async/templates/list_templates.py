import asyncio
import os

import postmark
from postmark.models.templates import TemplateTypeFilter

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        # --- List all templates (default: count=100, offset=0) ---
        result = await client.templates.list()
        print(f"Total templates: {result.total}, showing {len(result.items)}")
        for t in result.items:
            print(
                f"  [{t.template_id:>6}]  {t.name:<30}"
                f"  type={t.template_type}  active={t.active}"
            )

        # --- List only Standard templates ---
        result = await client.templates.list(
            count=50,
            template_type=TemplateTypeFilter.STANDARD,
        )
        print(
            f"\nStandard templates: {result.total} total, showing {len(result.items)}"
        )

        # --- List only Layout templates ---
        result = await client.templates.list(
            template_type=TemplateTypeFilter.LAYOUT,
        )
        print(f"Layout templates:   {result.total} total, showing {len(result.items)}")

        # --- Paginate: second result of 10 ---
        result = await client.templates.list(count=10, offset=10)
        print(f"\nresult 2 (offset=10): {len(result.items)} template(s)")


asyncio.run(main())
