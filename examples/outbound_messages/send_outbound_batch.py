import asyncio
import os

import postmark

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

SENDER = os.environ["POSTMARK_SENDER_EMAIL"]


async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        # --- Send batch ---
        responses = await client.outbound.send_batch(
            [
                {
                    "sender": SENDER,
                    "to": "receiver1@example.com",
                    "subject": "Batch 1",
                    "text_body": "Hello Receiver 1",
                },
                {
                    "sender": SENDER,
                    "to": "receiver2@example.com",
                    "subject": "Batch 2",
                    "text_body": "Hello Receiver 2",
                },
            ]
        )
        print(f"Batch: {len(responses)} sent")
        for i, resp in enumerate(responses, start=1):
            print(f"  {i}: {resp.message_id}")


asyncio.run(main())
