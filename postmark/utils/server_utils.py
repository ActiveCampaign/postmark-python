import json
from typing import Optional

import httpx


def parse_error_response(response: httpx.Response) -> tuple[str, Optional[int]]:
    """Parse error details from Postmark API response."""
    try:
        error_data = response.json()
        message = error_data.get("Message", "Unknown error")
        error_code = error_data.get("ErrorCode")
        return message, error_code
    except (json.JSONDecodeError, AttributeError):
        # If response isn't JSON, use status text
        return response.text or f"HTTP {response.status_code} error", None
