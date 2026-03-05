import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]

# Each message can use a different template and model — up to 500 per batch.
RECIPIENTS = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Carol", "email": "carol@example.com"},
]


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        messages = [
            {
                "From": SENDER,
                "To": r["email"],
                "TemplateAlias": "welcome-email",
                "TemplateModel": {"name": r["name"]},
            }
            for r in RECIPIENTS
        ]

        responses = await client.outbound.send_batch_with_template(messages)

        print(f"Batch: {len(responses)} sent")
        for resp, r in zip(responses, RECIPIENTS):
            print(f"  {r['name']:10}  id={resp.message_id}  code={resp.error_code}")


asyncio.run(main())
