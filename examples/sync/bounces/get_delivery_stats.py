import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    stats = client.bounces.get_delivery_stats()

    print(f"Inactive addresses: {stats.inactive_mails}")

    for entry in stats.bounces:
        print(f"  {entry.name}: {entry.count}")
