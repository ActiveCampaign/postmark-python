import postmark

template_id = 12345

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # --- Delete by numeric ID ---
    result = client.templates.delete(template_id)
    print(f"Deleted (ID):    code={result.error_code}  message={result.message}")

    # --- Delete by alias ---
    result = client.templates.delete("old-promo-email")
    print(f"Deleted (alias): code={result.error_code}  message={result.message}")
