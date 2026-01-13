# postmark-python

[![PyPI version](https://badge.fury.io/py/postmark.svg)](https://badge.fury.io/py/postmark)
[![Python Versions](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/ActiveCampaign/postmark-python/actions/workflows/tests.yml/badge.svg)](https://github.com/ActiveCampaign/postmark-python/actions/workflows/tests.yml)

The official Python SDK for [Postmark](https://postmarkapp.com) - The email delivery service that people actually like.

## Installation

```bash
pip install postmark
```

**Requirements:** Python 3.9 or higher

## Quick Start

```python
import asyncio
import postmark

async def get_messages():
    # Initialize the client
    server = postmark.ServerClient(server_token="your-server-token")
    
    # Search for messages
    messages, total = await server.messages.Outbound.find(
        recipient="user@example.com",
        fromdate="2024-01-01"
    )
    
    print(f"Found {total} messages")
    for msg in messages[:5]:
        print(f"  - {msg.subject} (from: {msg.from_})")

asyncio.run(get_messages())
```

## Authentication

The SDK requires a Postmark Server Token for API authentication. You can find your token in the [Postmark dashboard](https://account.postmarkapp.com/servers).

```python
server_token = "your-postmark-server-token"
```

For security, we recommend storing your token in environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("POSTMARK_SERVER_TOKEN")
server = postmark.ServerClient(server_token=token)
```

## Usage Examples

### Search Outbound Messages

```python
import asyncio
import postmark

async def search_messages():
    server = postmark.ServerClient(server_token="your-server-token")
    
    # Search with filters
    messages, total = await server.messages.Outbound.find(
        count=50,
        recipient="user@example.com",
        tag="onboarding",
        status="sent",
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
    server = postmark.ServerClient(server_token="your-server-token")
    message_id = "your-message-id"
    
    message = await server.messages.Outbound.get(message_id=message_id)
    
    print(f"Subject: {message.subject}")
    print(f"From: {message.from_}")
    print(f"HTML Body: {message.html_body}")

asyncio.run(get_message_details())
```

### Pagination (Auto-handling)

```python
async def get_all_messages():
    server = postmark.ServerClient(server_token="your-server-token")
    
    # Automatically handles pagination to retrieve up to 1000 messages
    all_messages = await server.messages.Outbound.find_all(
        max_messages=1000,
        tag="onboarding"
    )
    
    print(f"Retrieved {len(all_messages)} messages with 'onboarding' tag")

asyncio.run(get_all_messages())
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
import postmark
from postmark.exceptions import (
    InvalidAPIKeyException,
    ValidationException,
    RateLimitException,
    InactiveRecipientException,
    PostmarkException
)

async def safe_message_search():
    server = postmark.ServerClient(server_token="your-server-token")

    try:
        messages, total = await server.messages.Outbound.find(
            recipient="user@example.com"
        )
        print(f"Found {total} messages")
        
    except InvalidAPIKeyException as e:
        print(f"Invalid API key: {e}")
        
    except ValidationException as e:
        print(f"Invalid parameters: {e}")
        
    except RateLimitException as e:
        print(f"Rate limit hit: {e}")
        # Implement retry logic here
        
    except InactiveRecipientException as e:
        print(f"Recipient has bounced: {e}")
        
    except PostmarkException as e:
        print(f"General Postmark error: {e}")

asyncio.run(safe_message_search())

```

### Exception Types

- **`InvalidAPIKeyException`**: Invalid or missing API key (401)
- **`ValidationException`**: Invalid request parameters (422)
- **`RateLimitException`**: Rate limit exceeded (429)
- **`InactiveRecipientException`**: Inactive recipient (406)
- **`ServerException`**: Server errors (500/503)
- **`TimeoutException`**: Request timeout
- **`PostmarkException`**: Base exception for all Postmark errors

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

### Outbound Messages API
Access via `Access via server.messages.Outbound`

#### `Outbound.find()`
Search for outbound messages with various filters.

**Parameters:**
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

#### `Outbound.get()`
Get detailed information about a specific message.

**Parameters:**
- `message_id` (str): The message ID to retrieve

**Returns:** `OutboundMessageDetails` object with full message content

#### `Outbound.find_all()`
Retrieve all messages matching filters with automatic pagination.

**Parameters:**
- `max_messages` (int): Maximum messages to retrieve (up to 10,000, default 1000)
- `**filters`: Same filter parameters as `find()` method

**Returns:** List of all matching `Outbound` objects

## Development

### Prerequisites
- Python 3.9+
- Poetry (for dependency management)

### Setup

```bash
# Clone the repository
git clone [https://github.com/ActiveCampaign/postmark-python.git](https://github.com/ActiveCampaign/postmark-python.git)
cd postmark-python

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=postmark --cov-report=term-missing

# Run examples
poetry run python examples/get_messages.py
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=postmark --cov-report=term-missing

# Run specific test file
poetry run pytest postmark/tests/test_messages.py

# Run with verbose output
poetry run pytest -v

# See HTML coverage report
poetry run pytest --cov=postmark --cov-report=html
open htmlcov/index.html
```

### Code Formatting

This project uses [Black](https://github.com/psf/black) for code formatting:

```bash
# Format code
poetry run black postmark/

# Check formatting without making changes
poetry run black --check postmark/
```

### Type Checking

Run type checking with mypy:

```bash
poetry run mypy postmark/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Format your code with Black (`poetry run black postmark/`)
4. Add tests for your changes
5. Run tests to ensure everything passes (`poetry run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- All code must be formatted with Black (line length: 100)
- Add type hints where possible
- Write tests for new functionality
- Update documentation as needed
- Follow existing code style and conventions

## Support

- **Documentation**: [https://postmarkapp.com/developer](https://postmarkapp.com/developer)
- **API Reference**: [https://postmarkapp.com/developer/api/overview](https://postmarkapp.com/developer/api/overview)
- **Issues**: [GitHub Issues](https://github.com/ActiveCampaign/postmark-python/issues)
- **Support**: [support@postmarkapp.com](mailto:support@postmarkapp.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## About Postmark

Postmark is a fast and reliable transactional email service... that people actually like. Learn more at [postmarkapp.com](https://postmarkapp.com).

---

Made with ❤️ by [ActiveCampaign](https://www.activecampaign.com/)