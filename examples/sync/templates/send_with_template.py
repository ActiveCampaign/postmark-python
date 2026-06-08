import postmark
from postmark.models.templates import TemplateEmail

SENDER = "sender@example.com"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # --- Send via model(using template ID) ---
    response = client.outbound.send_with_template(
        TemplateEmail(
            sender=SENDER,
            to="recipient@example.com",
            template_id=12345,
            template_model={
                "name": "Alice",
                "action_url": "https://example.com/confirm",
            },
        )
    )
    print(f"Sent (dict, ID):    {response.message_id}")

    # --- Send via dict (using template alias) ---
    response = client.outbound.send_with_template(
        {
            "From": SENDER,
            "To": "recipient@example.com",
            "TemplateAlias": "welcome-email",
            "TemplateModel": {
                "name": "Bob",
                "action_url": "https://example.com/confirm",
            },
        }
    )
    print(f"Sent (dict, alias): {response.message_id}")

    # --- Send via TemplateEmail model (recommended, offering better type safety) ---
    response = client.outbound.send_with_template(
        TemplateEmail(
            sender=SENDER,
            to="recipient@example.com",
            template_alias="welcome-email",
            template_model={"name": "Carol"},
            message_stream="outbound",
        )
    )
    print(f"Sent (model):       {response.message_id}")
