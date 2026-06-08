import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # stream() paginates automatically; adjust max_bounces as needed (max 10,000).
    count = 0
    for b in client.bounces.stream(max_bounces=200):
        print(f"[{b.id}] {b.email}  type={b.type}")
        count += 1
    print(f"Streamed {count} bounce(s)")
