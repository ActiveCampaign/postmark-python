import postmark

webhook_id = 0  # Replace with the ID of the webhook to update

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    wh = server.webhooks.edit(
        webhook_id,
        triggers={
            "Open": {"Enabled": False, "PostFirstOpenOnly": False},
            "Bounce": {"Enabled": True, "IncludeContent": True},
        },
    )

    print("Updated webhook:")
    print(f"  ID:      {wh.id}")
    print(f"  URL:     {wh.url}")
    print(f"  Opens:   {wh.triggers.open.enabled}")
    print(f"  Bounces: {wh.triggers.bounce.enabled}")
