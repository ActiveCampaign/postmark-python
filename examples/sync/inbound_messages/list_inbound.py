import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    result = client.inbound.list(count=10)

    print(f"Total inbound messages: {result.total}")
    print()

    for msg in result.items:
        print(f"  [{msg.message_id}] {msg.subject}")
        print(f"       From:   {msg.from_email}")
        print(f"       Status: {msg.status}")
        print(f"       Date:   {msg.date}")
        print("----------------------------------------")
