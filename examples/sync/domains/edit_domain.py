import postmark

domain_id = 0  # Replace with the ID of the domain to update

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    domain = account.domain.edit(
        domain_id,
        return_path_domain="pm-bounces.example.com",
    )

    print("Updated domain:")
    print(f"  ID:                   {domain.id}")
    print(f"  Name:                 {domain.name}")
    print(f"  Return-Path domain:   {domain.return_path_domain}")
    print(f"  Return-Path verified: {domain.return_path_domain_verified}")
