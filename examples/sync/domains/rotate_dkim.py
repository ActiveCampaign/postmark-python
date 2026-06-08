import postmark

domain_id = 0  # Replace with the ID of the domain to rotate DKIM keys for

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    domain = account.domain.rotate_dkim(domain_id)

    print(f"Domain: {domain.name}")
    print(f"  DKIM update status:       {domain.dkim_update_status}")
    print(f"  Current DKIM host:        {domain.dkim_host}")
    print(f"  Pending DKIM host:        {domain.dkim_pending_host}")
    print(f"  Pending DKIM text value:  {domain.dkim_pending_text_value}")
