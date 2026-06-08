import postmark

signature_id = 0  # Replace with the ID of the sender signature

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.signature.resend_confirmation(signature_id)
    print(result.message)
