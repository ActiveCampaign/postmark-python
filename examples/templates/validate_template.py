import asyncio
import os

from dotenv import load_dotenv

import postmark
from postmark.models.templates import ValidateTemplateRequest

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])


async def main():
    # --- Validate via dict with a test render model ---
    print("-----------VALID TEMPLATE EXAMPLE-----------")
    result = await client.templates.validate(
        {
            "Subject": "Hello, {{name}}!",
            "HtmlBody": "<p>Hi {{name}}, your code is <strong>{{code}}</strong>.</p>",
            "TextBody": "Hi {{name}}, your code is {{code}}.",
            "TestRenderModel": {"name": "Alice", "code": "ABC-123"},
        }
    )
    print(f"All valid: {result.all_content_is_valid}")
    print("Subject ", result.subject)
    print("HtmlBody", result.html_body)
    print("TextBody", result.text_body)
    if result.suggested_template_model:
        print(f"  Suggested model: {result.suggested_template_model}")

    # --- Validate a layout template missing the required {{{@content}}} placeholder ---
    print("-----------INVALID TEMPLATE EXAMPLE-----------")
    result = await client.templates.validate(
        ValidateTemplateRequest(
            **{
                "TemplateType": "Layout",
                "HtmlBody": "<html><body>No content placeholder here</body></html>",
                "TextBody": "No content placeholder here",
            }
        )
    )
    print(f"\nAll valid: {result.all_content_is_valid}")
    for field_name, field in [
        ("HtmlBody", result.html_body),
        ("TextBody", result.text_body),
    ]:
        if field and not field.content_is_valid:
            for err in field.validation_errors:
                location = (
                    f" (line {err.line}, col {err.character_position})"
                    if err.line
                    else ""
                )
                print(f"  {field_name} error: {err.message}{location}")


asyncio.run(main())
