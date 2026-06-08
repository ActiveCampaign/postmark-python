import postmark

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    result = account.signature.list()

    print(f"Total sender signatures: {result.total}")
    print()

    for sig in result.items:
        print(f"  [{sig.id}] {sig.name} <{sig.email_address}>")
        print(f"       Domain:    {sig.domain}")
        print(f"       Confirmed: {sig.confirmed}")
        print("----------------------------------------")
