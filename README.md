# postmark-python

[![PyPI version](https://badge.fury.io/py/postmark.svg)](https://badge.fury.io/py/postmark)
[![Python Versions](https://img.shields.io/pypi/pyversions/postmark.svg)](https://pypi.org/project/postmark/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for [Postmark](https://postmarkapp.com) - a fast and reliable email delivery service.

## Installation

```bash
pip install postmark
```

## Quick Start

```python
import asyncio
import postmark

async def send_email():
    server_token = "your-server-token"
    
    # Send a simple email
    response = await postmark.emails.send(
        server_token=server_token,
        from_="sender@example.com",
        to="recipient@example.com",
        subject="Hello from Postmark!",
        html_body="<h1>Welcome</h1><p>This email was sent using Postmark Python SDK.</p>"
    )
    print(f"Message sent! ID: {response.message_id}")

asyncio.run(send_email())
```

## Authentication

The SDK requires a Postmark Server Token for API authentication. You can find your token in the [Postmark dashboard](https://account.postmarkapp.com/servers).

For security, we recommend storing your token in environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()
server_token = os.getenv("POSTMARK_SERVER_TOKEN")
```

## Usage Examples

### Search Outbound Messages

```python
import asyncio
import postmark

async def search_messages():
    server_token = "your-server-token"
    
    # Find messages sent in the last 7 days
    messages, total = await postmark.messages.Outbound.find(
        server_token=server_token,
        count=50,
        recipient="user@example.com",
        fromdate="2024-01-01"
    )
    
    print(f"Found {total} messages, retrieved {len(messages)}")
    for msg in messages:
        print(f"  - {msg.subject} (sent: {msg.received_at})")

asyncio.run(search_messages())
```

### Get Message Details

```python
async def get_message_details():
    server_token = "your-server-token"
    message_id = "your-message-id"
    
    message = await postmark.messages.Outbound.find_by_id(
        message_id=message_id,
        server_token=server_token
    )
    
    print(f"Subject: {message.subject}")
    print(f"From: {message.from_}")
    print(f"HTML Body: {message.html_body}")

asyncio.run(get_message_details())
```

### Pagination

```python
async def get_all_messages():
    server_token = "your-server-token"
    
    # Automatically handles pagination to retrieve up to 1000 messages
    all_messages = await postmark.messages.Outbound.find_all(
        server_token=server_token,
        max_messages=1000,
        tag="onboarding"
    )
    
    print(f"Retrieved {len(all_messages)} messages with 'onboarding' tag")

asyncio.run(get_all_messages())
```

## Advanced Configuration

### SSL Verification

For development/testing only (not recommended for production):

```python
import os
os.environ["POSTMARK_SSL_VERIFY"] = "false"
```

### Debugging

Enable debug logging to see detailed API calls and responses:

```python
import logging

# Enable all debug output
logging.basicConfig(level=logging.DEBUG)

# Or just for Postmark SDK
logging.getLogger('postmark').setLevel(logging.DEBUG)
```

## API Reference

### Messages API

#### `Outbound.find()`
Search for outbound messages with various filters.

**Parameters:**
- `server_token` (str): Your Postmark server token
- `count` (int): Number of messages to return (max 500, default 100)
- `offset` (int): Number of messages to skip (default 0)
- `recipient` (str): Filter by recipient email
- `fromemail` (str): Filter by sender email
- `tag` (str): Filter by message tag
- `status` (str): Filter by status ('sent', 'processed', 'queued')
- `fromdate` (datetime|str): Start date filter
- `todate` (datetime|str): End date filter
- `subject` (str): Filter by subject
- `messagestream` (str): Filter by message stream

**Returns:** Tuple of (list of messages, total count)

#### `Outbound.find_by_id()`
Get detailed information about a specific message.

**Parameters:**
- `message_id` (str): The message ID to retrieve
- `server_token` (str): Your Postmark server token

**Returns:** `OutboundMessageDetails` object with full message content

#### `Outbound.find_all()`
Retrieve all messages matching filters with automatic pagination.

**Parameters:**
- `server_token` (str): Your Postmark server token
- `max_messages` (int): Maximum messages to retrieve (up to 10,000, default 1000)
- `**filters`: Same filter parameters as `find()` method

**Returns:** List of all matching `Outbound` objects

## Error Handling

```python
import asyncio
import postmark
from httpx import HTTPStatusError

async def safe_message_search():
    try:
        messages, total = await postmark.messages.Outbound.find(
            server_token="your-token",
            recipient="user@example.com"
        )
        print(f"Found {total} messages")
    except HTTPStatusError as e:
        print(f"API error: {e.response.status_code}")
    except ValueError as e:
        print(f"Invalid parameters: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(safe_message_search())
```

## Development

### Prerequisites
- Python 3.8+
- Poetry (for dependency management)

### Setup

```bash
# Clone the repository
git clone https://github.com/ActiveCampaign/postmark-python.git
cd postmark-python

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run examples
poetry run python examples/get_messages.py
```

### Project Structure

```
postmark-python/
├── postmark/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py      # HTTP client logic
│   │   └── messages.py    # Message models and API methods
│   └── logging.py          # Logging utilities
├── examples/
│   └── get_messages.py     # Usage examples
├── tests/
│   └── test_messages.py    # Test suite
├── README.md
├── LICENSE
└── pyproject.toml          # Project dependencies
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=postmark

# Run specific test file
poetry run pytest tests/test_messages.py

# Run specific test
poetry run pytest tests/test_messages.py::TestOutboundMessages::test_find_messages_success

# Run with verbose output
poetry run pytest -v

# Run only failed tests
poetry run pytest --lf
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

This project uses:
- [Black](https://github.com/psf/black) for code formatting
- [isort](https://github.com/PyCQA/isort) for import sorting
- [mypy](https://github.com/python/mypy) for type checking

```bash
# Format code
poetry run black postmark/
poetry run isort postmark/

# Type checking
poetry run mypy postmark/
```

## Support

- **Documentation**: [https://postmarkapp.com/developer](https://postmarkapp.com/developer)
- **API Reference**: [https://postmarkapp.com/developer/api/overview](https://postmarkapp.com/developer/api/overview)
- **Issues**: [GitHub Issues](https://github.com/ActiveCampaign/postmark-python/issues)
- **Support**: [support@postmarkapp.com](mailto:support@postmarkapp.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

### Version History

- **0.0.1** - Alpha release with very limited functionality

## About Postmark

Postmark is a fast and reliable transactional email service designed for developers. Learn more at [postmarkapp.com](https://postmarkapp.com).

---

Made with ❤️ by [ActiveCampaign](https://www.activecampaign.com/)