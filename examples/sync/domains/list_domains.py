import postmark

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.domain.list()

    print(f"Total domains: {result.total}")
    print()

    for domain in result.items:
        print(f"  [{domain.id}] {domain.name}")
        print(f"       DKIM verified:         {domain.dkim_verified}")
        print(f"       Return-Path verified:  {domain.return_path_domain_verified}")
        print("----------------------------------------")
