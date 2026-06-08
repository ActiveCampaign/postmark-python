import postmark

webhook_id = 0  # Replace with the ID of the webhook to delete

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.webhooks.delete(webhook_id)
    print(result.message)
