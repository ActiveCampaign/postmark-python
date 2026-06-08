import postmark

trigger_id = 0  # Replace with the ID of the inbound rule to delete

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.inbound_rules.delete(trigger_id)
    print(result.message)
