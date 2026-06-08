import postmark

domain_id = 0  # Replace with the ID of the domain to retrieve

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    domain = account.domain.get(domain_id)

    print(f"Domain: {domain.name}")
    print(f"  ID:                      {domain.id}")
    print(f"  DKIM verified:           {domain.dkim_verified}")
    print(f"  DKIM host:               {domain.dkim_host}")
    print(f"  Return-Path domain:      {domain.return_path_domain}")
    print(f"  Return-Path verified:    {domain.return_path_domain_verified}")
    print(f"  DKIM update status:      {domain.dkim_update_status}")
