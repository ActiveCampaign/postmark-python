import postmark
from postmark.models.templates import CreateTemplateRequest

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # --- Create via dict ---
    result = client.templates.create(
        {
            "Name": "Welcome Email",
            "Alias": "welcome-email",
            "Subject": "Welcome, {{name}}!",
            "HtmlBody": "<p>Hi {{name}}, thanks for joining!</p>",
            "TextBody": "Hi {{name}}, thanks for joining!",
        }
    )
    print(f"Created (via dict):  id={result.template_id}  alias={result.alias}")

    # --- Create via CreateTemplateRequest model ---
    result = client.templates.create(
        CreateTemplateRequest(
            name="Password Reset",
            alias="password-reset",
            subject="Reset your password",
            html_body=(
                "<p>Click <a href='{{reset_url}}'>here</a> to reset your password.</p>"
            ),
            text_body="Reset your password: {{reset_url}}",
        )
    )

    print(f"Created (model): id={result.template_id}  alias={result.alias}")
