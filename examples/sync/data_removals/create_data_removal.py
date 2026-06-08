import postmark

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.data_removals.create(
        requested_by="admin@example.com",
        requested_for="user@example.com",
        notify_when_completed=True,
    )

    print(f"ID:     {result.id}")
    print(f"Status: {result.status}")
