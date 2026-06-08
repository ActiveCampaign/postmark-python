import postmark

SENDER = "sender@example.com"

# Each message can use a different template and model — up to 500 per batch.
RECIPIENTS = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Carol", "email": "carol@example.com"},
]

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    messages = [
        {
            "From": SENDER,
            "To": r["email"],
            "TemplateAlias": "welcome-email",
            "TemplateModel": {"name": r["name"]},
        }
        for r in RECIPIENTS
    ]

    responses = client.outbound.send_batch_with_template(messages)

    print(f"Batch: {len(responses)} sent")
    for resp, r in zip(responses, RECIPIENTS):
        print(f"  {r['name']:10}  id={resp.message_id}  code={resp.error_code}")
