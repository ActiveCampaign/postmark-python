import postmark

signature_id = 0  # Replace with the ID of the sender signature to update

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    sig = account.signature.edit(
        signature_id,
        name="Updated Sender Name",
        reply_to="reply@example.com",
    )

    print("Updated sender signature:")
    print(f"  ID:                   {sig.id}")
    print(f"  Name:                 {sig.name}")
    print(f"  Email:                {sig.email_address}")
    print(f"  Return-Path domain:   {sig.return_path_domain}")
