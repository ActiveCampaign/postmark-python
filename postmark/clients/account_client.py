import logging
import os
from typing import Any, Dict, List, Optional, Union

import httpx

from postmark.models.servers import AccountServerManager

from ..exceptions import (
    PostmarkException,
    TimeoutException,
    get_exception_class,
)
from ..utils.server_utils import parse_error_response

logger = logging.getLogger(__name__)


class AccountClient:
    _base_url = "https://api.postmarkapp.com"

    def __init__(self, account_token: str):
        """
        Initialize the Postmark Account Client.

        Args:
            account_token: The Postmark account token.
        """
        if not account_token:
            logger.error("A Postmark account token is required")
            raise PostmarkException("A Postmark account token is required.")

        self.account_token = account_token

        self.verify_ssl = os.getenv("POSTMARK_SSL_VERIFY", "true").lower() != "false"

        if not self.verify_ssl:
            logger.warning("SSL verification is disabled. Do not use in production!")

        self.server = AccountServerManager(self)

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        Make a request to the Postmark API using the configured account token.
        """
        headers = {
            "X-Postmark-Account-Token": self.account_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        logger.debug(f"Making {method} request to {endpoint}")

        async with httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            verify=self.verify_ssl,
            timeout=30.0,
        ) as client:
            try:
                response = await client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                logger.debug(f"Request successful: {response.status_code}")
                return response

            except httpx.TimeoutException as e:
                logger.error(f"Request timeout for {method} {endpoint}")
                raise TimeoutException("Request timed out after 30 seconds") from e

            except httpx.HTTPStatusError as e:
                message, error_code = parse_error_response(e.response)
                http_status = e.response.status_code

                logger.error(f"API error {error_code or http_status}: {message}")

                exception_class = get_exception_class(error_code or 0, http_status)
                raise exception_class(
                    message=message, error_code=error_code or 0, http_status=http_status
                ) from e

            except httpx.RequestError as e:
                logger.error(f"Request failed: {e}")
                raise PostmarkException(f"Request failed: {str(e)}") from e

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
