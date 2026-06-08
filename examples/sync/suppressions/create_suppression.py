import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    results = server.suppressions.create(
        "outbound",
        ["user@example.com", "other@example.com"],
    )

    for r in results:
        print(f"  {r.email_address}: {r.status}")
        if r.message:
            print(f"       {r.message}")
