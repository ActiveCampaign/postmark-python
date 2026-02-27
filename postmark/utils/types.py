# postmark/utils/types.py
from typing import Any, Dict, Optional, Protocol
import httpx


class HTTPClient(Protocol):
    """
    Describes the minimum interface that managers need from a client.
    Any object with these two methods satisfies this protocol — no inheritance needed.
    """

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response: ...

    async def post(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> httpx.Response: ...
