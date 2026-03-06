import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Union

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from postmark.models.data_removals import DataRemovalManager
from postmark.models.domains import DomainManager
from postmark.models.servers import AccountServerManager
from postmark.models.signatures import SenderSignatureManager
from postmark.models.templates import AccountTemplateManager

from .. import __version__
from ..exceptions import (
    PostmarkException,
    RateLimitException,
    ServerException,
    TimeoutException,
    get_exception_class,
)
from ..utils.server_utils import parse_error_response

logger = logging.getLogger(__name__)


class AccountClient:
    _base_url = "https://api.postmarkapp.com"

    def __init__(
        self,
        account_token: str,
        retries: int = 3,
        timeout: float = 30.0,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the Postmark Account Client.

        Args:
            account_token: The Postmark account token.
            retries: Number of times to retry on rate limit, server, or timeout errors.
            timeout: HTTP request timeout in seconds.
            base_url: Override the API base URL (e.g. a local mock server for testing).
        """
        if not account_token:
            logger.error("A Postmark account token is required")
            raise PostmarkException("A Postmark account token is required.")

        self.account_token = account_token
        self.retries = retries
        self.timeout = timeout

        self.verify_ssl = os.getenv("POSTMARK_SSL_VERIFY", "true").lower() != "false"

        if not self.verify_ssl:
            logger.warning("SSL verification is disabled. Do not use in production!")

        self.server = AccountServerManager(self)
        self.domain = DomainManager(self)
        self.signature = SenderSignatureManager(self)
        self.data_removals = DataRemovalManager(self)
        self.templates = AccountTemplateManager(self)

        self._http_client = httpx.AsyncClient(
            base_url=base_url or self._base_url,
            headers={
                "X-Postmark-Account-Token": self.account_token,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": f"Postmark.PY - {__version__} (Python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})",
            },
            verify=self.verify_ssl,
            timeout=self.timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()

    async def close(self):
        await self._http_client.aclose()

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        Make a request to the Postmark API using the configured account token.
        """
        logger.debug("Making request", extra={"method": method, "endpoint": endpoint})

        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type(
                (RateLimitException, ServerException, TimeoutException)
            ),
            wait=wait_exponential_jitter(initial=1, max=60),
            stop=stop_after_attempt(self.retries + 1),
            reraise=True,
        ):
            with attempt:
                try:
                    start = time.monotonic()
                    response = await self._http_client.request(
                        method, endpoint, **kwargs
                    )
                    response.raise_for_status()
                    duration_ms = round((time.monotonic() - start) * 1000)
                    request_id = response.headers.get("X-Request-Id")
                    logger.debug(
                        "Request successful",
                        extra={
                            "method": method,
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "duration_ms": duration_ms,
                            "request_id": request_id,
                        },
                    )
                    return response

                except httpx.TimeoutException as e:
                    duration_ms = round((time.monotonic() - start) * 1000)
                    logger.error(
                        "Request timed out",
                        extra={
                            "method": method,
                            "endpoint": endpoint,
                            "duration_ms": duration_ms,
                        },
                    )
                    raise TimeoutException("Request timed out after 30 seconds") from e

                except httpx.HTTPStatusError as e:
                    duration_ms = round((time.monotonic() - start) * 1000)
                    request_id = e.response.headers.get("X-Request-Id")
                    message, error_code = parse_error_response(e.response)
                    http_status = e.response.status_code

                    logger.error(
                        "API error",
                        extra={
                            "method": method,
                            "endpoint": endpoint,
                            "status_code": http_status,
                            "error_code": error_code or http_status,
                            "postmark_message": message,
                            "duration_ms": duration_ms,
                            "request_id": request_id,
                        },
                    )

                    exception_class = get_exception_class(error_code or 0, http_status)
                    raise exception_class(
                        message=message,
                        error_code=error_code or 0,
                        http_status=http_status,
                        request_id=request_id,
                    ) from e

                except httpx.RequestError as e:
                    logger.error(
                        "Request failed",
                        extra={"method": method, "endpoint": endpoint, "error": str(e)},
                    )
                    raise PostmarkException(f"Request failed: {str(e)}") from e

        raise AssertionError("The Postmark API is unreachable.")

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        return await self.request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json: Union[Dict[str, Any], List[Dict[str, Any]], None] = None,
    ) -> httpx.Response:
        return await self.request("POST", endpoint, json=json)

    async def put(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        return await self.request("PUT", endpoint, json=json)

    async def patch(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        return await self.request("PATCH", endpoint, json=json)

    async def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        return await self.request("DELETE", endpoint, params=params)
