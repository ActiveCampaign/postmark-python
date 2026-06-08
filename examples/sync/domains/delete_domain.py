import postmark

domain_id = 0  # Replace with the ID of the domain to delete

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.domain.delete(domain_id)
    print(result.message)
