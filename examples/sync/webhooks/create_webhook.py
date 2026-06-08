import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    wh = server.webhooks.create(
        url="https://example.com/webhook",
        message_stream="outbound",
        triggers={
            "Open": {"Enabled": True, "PostFirstOpenOnly": False},
            "Bounce": {"Enabled": True, "IncludeContent": False},
        },
    )

    print("Created webhook:")
    print(f"  ID:      {wh.id}")
    print(f"  URL:     {wh.url}")
    print(f"  Stream:  {wh.message_stream}")
    print(f"  Opens:   {wh.triggers.open.enabled}")
    print(f"  Bounces: {wh.triggers.bounce.enabled}")
