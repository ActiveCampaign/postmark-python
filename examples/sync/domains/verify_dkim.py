import postmark

domain_id = 0  # Replace with the ID of the domain to verify

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    domain = account.domain.verify_dkim(domain_id)

    print(f"Domain: {domain.name}")
    print(f"  DKIM verified:      {domain.dkim_verified}")
    print(f"  DKIM update status: {domain.dkim_update_status}")
    print(f"  Weak DKIM:          {domain.weak_dkim}")
