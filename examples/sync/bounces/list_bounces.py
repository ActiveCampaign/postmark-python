import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # Filter to a specific bounce type; omit `type` to list all.
    result = client.bounces.list()
    print(f"{result.total} hard bounce(s) on server, showing {len(result.items)}")
    for b in result.items:
        print(
            f"  [{b.id}] {b.email}  bounced={b.bounced_at:%Y-%m-%d}"
            f"  inactive={b.inactive}"
        )
