import postmark

# Bounce ID's that can be activated show "can_activate" -> True.
bounce_id = 692560173

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    result = client.bounces.activate(bounce_id)
    print(f"Response: {result.message}")
    print(f"Inactive after activation: {result.bounce.inactive}")
