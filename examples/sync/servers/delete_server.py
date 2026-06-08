import postmark

server_id = 0  # Replace with the ID of the server to delete

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.server.delete(server_id)
    print(result.message)
