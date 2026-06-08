import postmark

template_id = 12345

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # --- Get by numeric ID ---
    template = client.templates.get(template_id)

    print(f"ID:      {template.template_id}")
    print(f"Name:    {template.name}")
    print(f"Alias:   {template.alias}")
    print(f"Type:    {template.template_type}")
    print(f"Active:  {template.active}")
    print(f"Subject: {template.subject}")

    # --- Get by alias ---
    template = client.templates.get("welcome-email")

    print(f"\nFetched by alias: {template.name} (id={template.template_id})")
