import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from postmark.models.bounces import BounceManager
from postmark.models.inbound import InboundManager
from postmark.models.inbound_rules import InboundRuleManager
from postmark.models.outbound import OutboundManager
from postmark.models.servers import ServerManager
from postmark.models.stats import StatsManager
from postmark.models.streams import StreamManager
from postmark.models.suppressions import SuppressionManager
from postmark.models.templates import TemplateManager
from postmark.models.webhooks import WebhookManager

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


class ServerClient:
    _base_url = "https://api.postmarkapp.com"

    def __init__(
        self,
        server_token: str,
        retries: int = 3,
        timeout: float = 30.0,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the Postmark Server Client.

        Args:
            server_token: The Postmark server token.
            retries: Number of times to retry on rate limit, server, or timeout errors.
            timeout: HTTP request timeout in seconds.
            base_url: Override the API base URL (e.g. a local mock server for testing).
        """
        if not server_token:
            logger.error("A Postmark server token is required")
            raise PostmarkException("A Postmark server token is required.")

        self.server_token = server_token
        self.retries = retries
        self.timeout = timeout

        # Allow SSL verification to be controlled via environment variable
        self.verify_ssl = os.getenv("POSTMARK_SSL_VERIFY", "true").lower() != "false"

        if not self.verify_ssl:
            logger.warning("SSL verification is disabled. Do not use in production!")

        self.outbound = OutboundManager(self)
        self.inbound = InboundManager(self)
        self.inbound_rules = InboundRuleManager(self)
        self.bounces = BounceManager(self)
        self.templates = TemplateManager(self)
        self.server = ServerManager(self)
        self.stream = StreamManager(self)
        self.stats = StatsManager(self)
        self.webhooks = WebhookManager(self)
        self.suppressions = SuppressionManager(self)

        self._http_client = httpx.AsyncClient(
            base_url=base_url or self._base_url,
            headers={
                "X-Postmark-Server-Token": self.server_token,
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
        Make a request to the Postmark API using the configured token.
        """
        logger.debug(f"Making {method} request to {endpoint}")

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
                    response = await self._http_client.request(
                        method, endpoint, **kwargs
                    )
                    response.raise_for_status()
                    logger.debug(f"Request successful: {response.status_code}")
                    return response

                except httpx.TimeoutException as e:
                    logger.error(f"Request timeout for {method} {endpoint}")
                    raise TimeoutException("Request timed out after 30 seconds") from e

                except httpx.HTTPStatusError as e:
                    # Parse Postmark error response
                    message, error_code = parse_error_response(e.response)
                    http_status = e.response.status_code

                    logger.error(f"API error {error_code or http_status}: {message}")

                    # Get exception class
                    exception_class = get_exception_class(error_code or 0, http_status)

                    # Raise exception
                    raise exception_class(
                        message=message,
                        error_code=error_code or 0,
                        http_status=http_status,
                    ) from e

                except httpx.RequestError as e:
                    logger.error(f"Request failed: {e}")
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
