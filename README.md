# postmark-python

[![PyPI version](https://badge.fury.io/py/postmark.svg)](https://badge.fury.io/py/postmark)
[![Python Versions](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/ActiveCampaign/postmark-python/actions/workflows/tests.yml/badge.svg)](https://github.com/ActiveCampaign/postmark-python/actions/workflows/tests.yml)

The official Python SDK for [Postmark](https://postmarkapp.com) — the email delivery service that people actually like.

## Installation

```bash
pip install postmark
```

### Requirements
- Python 3.10+

## Quick Start

```python
import asyncio
import os
import postmark
from dotenv import load_dotenv

load_dotenv()
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

async def main():
    response = await client.email.send({
        "sender": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Hello from Postmark",
        "text_body": "Sent with the Postmark Python SDK.",
    })
    print(f"Sent: {response.message_id}")

asyncio.run(main())
```

## Setup (Development)

```bash
git clone https://github.com/ActiveCampaign/postmark-python.git
cd postmark-python
poetry install
```

Create a `.env` file:

```bash
POSTMARK_SERVER_TOKEN=your-server-token
POSTMARK_ACCOUNT_TOKEN=your-account-token
POSTMARK_SENDER_EMAIL=sender@example.com
```

[Find your tokens in the Postmark dashboard](https://account.postmarkapp.com/api_tokens).

## Authentication

The SDK has two clients for two different token types:

```python
import postmark

# Server token — for sending email and managing a single server's settings
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])

# Account token — for managing servers across your account
account = postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"])
```

## Usage

### Sending Email

```python
from postmark import Email

# Using a dict
await client.email.send({
    "sender": "sender@example.com",
    "to": "recipient@example.com",
    "subject": "Hello",
    "text_body": "Hello from Postmark.",
})

# Using the Email model (recommended — type-safe)
await client.email.send(
    Email(
        sender="sender@example.com",
        to="recipient@example.com",
        subject="Hello",
        text_body="Hello from Postmark.",
    )
)
```

### Batch Send

```python
from postmark.models.messages import BulkEmail, BulkRecipient

# Same message, many recipients
await client.email.send_bulk(
    BulkEmail(
        sender="sender@example.com",
        subject="Your order is ready, {{FirstName}}!",
        text_body="Hi {{FirstName}}, order {{OrderId}} is ready.",
        messages=[
            BulkRecipient(
                to="alice@example.com",
                template_model={"FirstName": "Alice", "OrderId": "001"},
            ),
            BulkRecipient(
                to="bob@example.com",
                template_model={"FirstName": "Bob", "OrderId": "002"},
            ),
        ],
    )
)

# Different messages, one request (up to 500)
await client.email.send_batch([email1, email2, email3])
```

### List & Stream Sent Messages

```python
# Paginated list
messages, total = await client.email.list(
    count=50,
    recipient="user@example.com",
    tag="onboarding",
)
print(f"Found {total} messages")

# Auto-paginating stream
async for message in client.email.stream(max_messages=5000, tag="onboarding"):
    print(message.subject)
```

### Bounces

```python
from postmark.models.bounces import BounceType

# Delivery stats
stats = await client.bounces.get_delivery_stats()
print(f"Inactive addresses: {stats.inactive_mails}")

# List bounces
bounces, total = await client.bounces.list(
    type=BounceType.HARD_BOUNCE,
    count=50,
)

# Stream all bounces
async for bounce in client.bounces.stream(max_bounces=1000):
    print(f"{bounce.email}: {bounce.type}")

# Single bounce
bounce = await client.bounces.get(bounce_id)

# Reactivate a deactivated address
result = await client.bounces.activate(bounce_id)
```

### Templates

```python
from postmark.models.templates import TemplateTypeFilter

# List templates
templates, total = await client.templates.list()

# Get / create / edit / delete
template = await client.templates.get(template_id)
created = await client.templates.create({"Name": "Welcome", "Subject": "Hi!"})
await client.templates.edit(template_id, {"Subject": "Updated subject"})
await client.templates.delete(template_id)

# Send with a template
await client.email.send_with_template({
    "template_id": template_id,
    "sender": "sender@example.com",
    "to": "recipient@example.com",
    "template_model": {"name": "Alice"},
})
```

### Server Settings (server token)

Read and update the settings of the server associated with your server token:

```python
from postmark.models.servers import ServerColor, TrackLinks

# Get current server config
server = await client.server.get()
print(f"{server.name}: {server.delivery_type.value}")

# Update settings
server = await client.server.edit(
    track_opens=True,
    track_links=TrackLinks.HTML_AND_TEXT,
    color=ServerColor.GREEN,
)
```

### Server Management (account token)

Create, list, and manage all servers on your account:

```python
from postmark.models.servers import DeliveryType, ServerColor

# List all servers
servers, total = await account.server.list()

# Get a specific server
server = await account.server.get(server_id)

# Create a server
server = await account.server.create(
    name="My New Server",
    color=ServerColor.BLUE,
    delivery_type=DeliveryType.SANDBOX,
)

# Edit a server
server = await account.server.edit(server_id, name="Renamed Server")

# Delete a server
result = await account.server.delete(server_id)
print(result.message)
```

## Error Handling

```python
from postmark import (
    InvalidAPIKeyException,
    ValidationException,
    RateLimitException,
    InactiveRecipientException,
    PostmarkException,
)

try:
    await client.email.send(...)

except InvalidAPIKeyException:
    print("Check your POSTMARK_SERVER_TOKEN")

except InactiveRecipientException as e:
    print(f"Bounced addresses: {e.inactive_recipients}")

except RateLimitException:
    print("Rate limited — back off and retry")

except ValidationException as e:
    print(f"Bad request: {e}")

except PostmarkException as e:
    print(f"Postmark error [{e.error_code}]: {e}")
```

### Exception Reference

| Exception | HTTP | Description |
|-----------|------|-------------|
| `InvalidAPIKeyException` | 401 | Missing or invalid API key |
| `InactiveRecipientException` | 406 | Recipient address is inactive |
| `ValidationException` | 422 | Invalid request parameters |
| `RateLimitException` | 429 | Rate limit exceeded |
| `ServerException` | 500/503 | Postmark server error |
| `TimeoutException` | — | Request timed out (30 s) |
| `PostmarkException` | — | Base class for all SDK errors |

## Advanced Configuration

### SSL Verification

For development/testing only:

```python
import os
os.environ["POSTMARK_SSL_VERIFY"] = "false"
```

### Debug Logging

```python
import logging
logging.getLogger("postmark").setLevel(logging.DEBUG)
```

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=postmark --cov-report=term-missing

# Specific file
poetry run pytest tests/test_bounces.py -v
```

### Code Quality

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, [mypy](https://mypy-lang.org/) for type checking, and [pre-commit](https://pre-commit.com/) to enforce all checks before every commit.

```bash
# Install hooks (one-time setup)
poetry run pre-commit install

# Run all hooks manually
poetry run pre-commit run --all-files

# Lint and format individually
poetry run ruff check --fix .
poetry run ruff format .
poetry run mypy postmark/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Install pre-commit hooks (`poetry run pre-commit install`)
4. Add tests for your changes
5. Ensure all checks pass (`poetry run pre-commit run --all-files`)
6. Open a Pull Request

### Guidelines

- Line length: 88 characters (enforced by Ruff)
- Add type hints to all new code
- Write unit tests for new functionality
- Keep examples up to date

## Support

- **Postmark Docs**: [postmarkapp.com/developer](https://postmarkapp.com/developer)
- **API Reference**: [postmarkapp.com/developer/api/overview](https://postmarkapp.com/developer/api/overview)
- **Issues**: [GitHub Issues](https://github.com/ActiveCampaign/postmark-python/issues)
- **Support**: [support@postmarkapp.com](mailto:support@postmarkapp.com)

## License

MIT — see [LICENSE](LICENSE).

---

Made with ❤️ by [ActiveCampaign](https://www.activecampaign.com/)
