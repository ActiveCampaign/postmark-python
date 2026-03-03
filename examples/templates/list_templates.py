import asyncio
import os

import postmark
from postmark.models.templates import TemplateTypeFilter
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # --- List all templates (default: count=100, offset=0) ---
    templates, total = await client.templates.list()
    print(f"Total templates: {total}, showing {len(templates)}")
    for t in templates:
        print(f"  [{t.template_id:>6}]  {t.name:<30}  type={t.template_type}  active={t.active}")

    # --- List only Standard templates ---
    templates, total = await client.templates.list(
        count=50,
        template_type=TemplateTypeFilter.STANDARD,
    )
    print(f"\nStandard templates: {total} total, showing {len(templates)}")

    # --- List only Layout templates ---
    templates, total = await client.templates.list(
        template_type=TemplateTypeFilter.LAYOUT,
    )
    print(f"Layout templates:   {total} total, showing {len(templates)}")

    # --- Paginate: second page of 10 ---
    templates, total = await client.templates.list(count=10, offset=10)
    print(f"\nPage 2 (offset=10): {len(templates)} template(s)")


asyncio.run(main())
