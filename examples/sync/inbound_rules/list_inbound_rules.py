import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.inbound_rules.list()

    print(f"Total inbound rules: {result.total}\n")

    for rule in result.items:
        print(f"  [{rule.id}] {rule.rule}")
