# postmark/utils/types.py
from typing import Any, Dict, Optional, Protocol
import httpx


class HTTPClient(Protocol):
    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response: ...

    async def post(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> httpx.Response: ...

    async def put(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> httpx.Response: ...

    async def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response: ...
