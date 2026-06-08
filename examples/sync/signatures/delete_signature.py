import postmark

signature_id = 0  # Replace with the ID of the sender signature to delete

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.signature.delete(signature_id)
    print(result.message)
