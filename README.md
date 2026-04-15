<table>
<tr>
<td>
<h1>postmark-python</h1>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue" alt="Python Versions"></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
<a href="https://github.com/ActiveCampaign/postmark-python/actions/workflows/tests.yml"><img src="https://github.com/ActiveCampaign/postmark-python/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
</td>
<td align="right" valign="top">
<img src="https://raw.githubusercontent.com/ActiveCampaign/postmark-python/main/postmark_python_sdk.png" width="200" alt="Postmark Python SDK">
</td>
</tr>
</table>

The official (Beta) Python SDK for [Postmark](https://postmarkapp.com) — send emails, manage bounces, templates, webhooks, and more.

For tutorials and detailed usage, check out the **[wiki](https://github.com/ActiveCampaign/postmark-python/wiki)**.

For details about the Postmark API in general, see the **[Postmark developer docs](https://postmarkapp.com/developer)**.

## Requirements

- Python 3.10+

## Installation

Install from PyPI as **`postmark-python`** (the Python package you import is still **`postmark`**):

```bash
pip install postmark-python
```

## Quick Start

The SDK is fully async. All API calls must be awaited.

```python
import asyncio
import os

import postmark

# Tokens are read from the environment here. Optionally: pip install python-dotenv,
# then use load_dotenv() to populate os.environ from a .env file.

async def main():
    async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
        response = await client.outbound.send({
            "sender": "sender@example.com",
            "to": "recipient@example.com",
            "subject": "Hello from Postmark",
            "text_body": "Sent with the Postmark Python SDK.",
        })
        print(f"Sent: {response.message_id}")

asyncio.run(main())
```

## Two Client Types

| Client | Token | Use for |
|---|---|---|
| `ServerClient` | Server API token | Sending email, bounces, templates, stats, webhooks, streams |
| `AccountClient` | Account API token | Domains, sender signatures, managing servers, data removals |

```python
import postmark

# Use as async context managers to ensure connections are closed
async with postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
    ...

async with postmark.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as account:
    ...

# Or call close() explicitly when done
client = postmark.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"])
await client.close()
```

## Development

```bash
git clone https://github.com/ActiveCampaign/postmark-python.git
cd postmark-python
poetry install
poetry run pre-commit install
```

```bash
# Run tests
poetry run pytest

# Lint and type-check
poetry run pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all checks pass (`poetry run pre-commit run --all-files`)
5. Open a Pull Request

## Support

- **Issues**: [GitHub Issues](https://github.com/ActiveCampaign/postmark-python/issues)
- **Postmark Support**: [support@postmarkapp.com](mailto:support@postmarkapp.com)

## License

MIT — see [LICENSE](LICENSE).
