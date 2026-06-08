import postmark

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.data_removals.get(42)

    print(f"ID:     {result.id}")
    print(f"Status: {result.status}")
