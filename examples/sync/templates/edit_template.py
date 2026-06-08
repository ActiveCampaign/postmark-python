import postmark
from postmark.models.templates import EditTemplateRequest

template_id = 12345

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    # --- Edit by numeric ID via dict ---
    result = client.templates.edit(
        template_id,
        {
            "Subject": "Welcome back, {{name}}!",
            "HtmlBody": (
                "<p>Hi {{name}}, we updated our terms."
                " <a href='{{url}}'>Read more</a>.</p>"
            ),
        },
    )
    print(f"Edited (ID):    {result.name}  active={result.active}")

    # --- Edit by alias via EditTemplateRequest model ---
    result = client.templates.edit(
        "welcome-email",
        EditTemplateRequest(name="Welcome Email v2"),
    )
    print(f"Edited (alias): {result.name}  id={result.template_id}")
