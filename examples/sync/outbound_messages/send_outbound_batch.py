import postmark

SENDER = "sender@example.com"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # --- Send batch ---
    responses = client.outbound.send_batch(
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
