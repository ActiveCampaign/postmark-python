import postmark

WEBHOOK_ID = 1

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    wh = server.webhooks.get(WEBHOOK_ID)

    print(f"ID:     {wh.id}")
    print(f"URL:    {wh.url}")
    print(f"Stream: {wh.message_stream}")
    print()
    print("Triggers:")
    print(f"  Opens:   {wh.triggers.open.enabled}")
    print(f"  Clicks:  {wh.triggers.click.enabled}")
    print(f"  Bounces: {wh.triggers.bounce.enabled}")
