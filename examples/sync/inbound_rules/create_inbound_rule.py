import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    rule = server.inbound_rules.create("spam@example.com")

    print("Created inbound rule:")
    print(f"  ID:   {rule.id}")
    print(f"  Rule: {rule.rule}")
