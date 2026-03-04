import asyncio
import os

from dotenv import load_dotenv

import postmark
from postmark.models.templates import PushTemplatesRequest

load_dotenv()
client = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])

"""
This is an example of pushing all templates with changes to another server.
If the template already exists on the destination server, the template will
be updated. If the template does not exist on the destination server, it will be
created and assigned the alias of the template on the source server.
"""


SOURCE_SERVER_ID = os.environ.get("POSTMARK_SOURCE_SERVER_ID", "src-server-id")
DESTINATION_SERVER_ID = os.environ.get(
    "POSTMARK_DESTINATION_SERVER_ID", "dst-server-id"
)


async def main():
    # --- Dry run: preview what would change without applying ---
    result = await client.templates.push(
        {
            "SourceServerID": SOURCE_SERVER_ID,
            "DestinationServerID": DESTINATION_SERVER_ID,
            "PerformChanges": False,
        }
    )
    print(f"Dry run — {result.total_count} template(s) would be affected:")
    for t in result.templates:
        print(f"  action={t.action:<6}  [{t.template_id}]  {t.name}  alias={t.alias}")

    # --- Apply: push templates for real ---
    result = await client.templates.push(
        PushTemplatesRequest(
            SourceServerID=SOURCE_SERVER_ID,
            DestinationServerID=DESTINATION_SERVER_ID,
            PerformChanges=True,
        )
    )
    print(f"\nPushed — {result.total_count} template(s) updated.")


asyncio.run(main())
