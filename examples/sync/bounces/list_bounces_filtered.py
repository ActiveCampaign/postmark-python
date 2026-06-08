from datetime import datetime

import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # Narrow results to inactive addresses within a date range on a specific stream.
    result = client.bounces.list(
        count=25,
        inactive=True,
        from_date=datetime(2024, 1, 1),
        to_date=datetime(2024, 12, 31),
        message_stream="outbound",
    )
    print(f"{result.total} matching bounce(s), showing {len(result.items)}")
    for b in result.items:
        print(f"  [{b.id}] {b.email}  type={b.type}  bounced={b.bounced_at:%Y-%m-%d}")
