# postmark/utils/types.py
from typing import Any, Protocol

import httpx


class HTTPClient(Protocol):
    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> httpx.Response: ...

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> httpx.Response: ...

    async def put(
        self, endpoint: str, json: dict[str, Any] | None = None
    ) -> httpx.Response: ...

    async def patch(
        self, endpoint: str, json: dict[str, Any] | None = None
    ) -> httpx.Response: ...

    async def delete(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> httpx.Response: ...
