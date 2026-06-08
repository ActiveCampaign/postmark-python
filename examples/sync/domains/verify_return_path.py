import postmark

domain_id = 0  # Replace with the ID of the domain to verify

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    domain = account.domain.verify_return_path(domain_id)

    print(f"Domain: {domain.name}")
    print(f"  Return-Path domain:   {domain.return_path_domain}")
    print(f"  Return-Path verified: {domain.return_path_domain_verified}")
    print(f"  Return-Path CNAME:    {domain.return_path_domain_cname_value}")
