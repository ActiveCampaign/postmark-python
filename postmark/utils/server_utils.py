import json
from typing import Any, Optional

import httpx


def _coerce_postmark_error_code(raw: Any) -> Optional[int]:
    """Normalize Postmark ``ErrorCode`` from JSON (int or numeric string) to ``int`` or ``None``."""
    if raw is None:
        return None
    if isinstance(
        raw, bool
    ):  # must be before ``int`` (``bool`` is a subclass of ``int``)
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str):
        stripped = raw.strip()
        if not stripped:
            return None
        try:
            return int(stripped, 10)
        except ValueError:
            return None
    return None


def parse_error_response(response: httpx.Response) -> tuple[str, Optional[int]]:
    """Parse error details from Postmark API response."""
    try:
        error_data = response.json()
        message = error_data.get("Message", "Unknown error")
        error_code = _coerce_postmark_error_code(error_data.get("ErrorCode"))
        return message, error_code
    except (json.JSONDecodeError, AttributeError):
        # If response isn't JSON, use status text
        return response.text or f"HTTP {response.status_code} error", None
