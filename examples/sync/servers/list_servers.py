import postmark

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.server.list()

    print(f"Total servers: {result.total}")
    print()

    for server in result.items:
        print(f"  [{server.id}] {server.name}")
        print(f"       Color:         {server.color.value}")
        print(f"       Delivery type: {server.delivery_type.value}")
        print(f"       SMTP enabled:  {server.smtp_api_activated}")
        print("----------------------------------------")
