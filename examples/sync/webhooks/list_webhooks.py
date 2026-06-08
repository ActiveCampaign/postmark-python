import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    webhooks = server.webhooks.list()

    print(f"Total webhooks: {len(webhooks)}")
    print()

    for wh in webhooks:
        print(f"  [{wh.id}] {wh.url}")
        print(f"       Stream:  {wh.message_stream}")
        print(f"       Opens:   {wh.triggers.open.enabled}")
        print(f"       Bounces: {wh.triggers.bounce.enabled}")
        print("----------------------------------------")
