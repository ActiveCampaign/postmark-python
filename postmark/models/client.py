import json
import logging
import os
from typing import Optional, Dict, Any

import httpx

from ..exceptions import (
    InvalidAPIKeyException,
    PostmarkAPIException,
    PostmarkException,
    TimeoutException,
    get_exception_class,
)

# Get a logger for this module
logger = logging.getLogger(__name__)

_base_url = "https://api.postmarkapp.com"


async def request(
    method: str, endpoint: str, server_token: str, **kwargs
) -> httpx.Response:
    """
    Make a request to the Postmark API using a specific token.

    Raises:
        InvalidAPIKeyException: Invalid or missing API key
        ValidationException: Invalid request parameters
        RateLimitException: Rate limit exceeded
        ServerException: Server errors
        TimeoutException: Request timeout
        PostmarkAPIException: Other API errors
    """
    if not server_token:
        logger.error("A Postmark server token is required")
        raise PostmarkException("A Postmark server token is required.")

    # Allow SSL verification to be controlled via environment variable
    verify_ssl = os.getenv("POSTMARK_SSL_VERIFY", "true").lower() != "false"

    if not verify_ssl:
        logger.warning("SSL verification is disabled. Do not use in production!")

    headers = {
        "X-Postmark-Server-Token": server_token,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    logger.debug(f"Making {method} request to {endpoint}")

    # Create a client for this specific request context
    async with httpx.AsyncClient(
        base_url=_base_url, headers=headers, verify=verify_ssl, timeout=30.0
    ) as client:
        try:
            response = await client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            logger.debug(f"Request successful: {response.status_code}")
            return response

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout for {method} {endpoint}")
            raise TimeoutException(f"Request timed out after 30 seconds") from e

        except httpx.HTTPStatusError as e:
            # Parse Postmark error response
            message, error_code = parse_error_response(e.response)
            http_status = e.response.status_code

            logger.error(f"API error {error_code or http_status}: {message}")

            # Get appropriate exception class
            exception_class = get_exception_class(error_code or 0, http_status)

            # Raise the specific exception
            raise exception_class(
                message=message, error_code=error_code or 0, http_status=http_status
            ) from e

        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise PostmarkException(f"Request failed: {str(e)}") from e


async def get(
    endpoint: str, server_token: str, params: Optional[Dict[str, Any]] = None
) -> httpx.Response:
    return await request("GET", endpoint, server_token=server_token, params=params)


async def post(
    endpoint: str, server_token: str, json: Optional[Dict[str, Any]] = None
) -> httpx.Response:
    return await request("POST", endpoint, server_token=server_token, json=json)


async def put(
    endpoint: str, server_token: str, json: Optional[Dict[str, Any]] = None
) -> httpx.Response:
    return await request("PUT", endpoint, server_token=server_token, json=json)


# async def delete(
#     endpoint: str, server_token: str, json: Optional[Dict[str, Any]] = None
# ) -> httpx.Response:
#     return await request("DELETE", endpoint, server_token=server_token, json=json)


def parse_error_response(response: httpx.Response) -> tuple[str, Optional[int]]:
    """Parse error details from Postmark API respons`e."""
    try:
        error_data = response.json()
        message = error_data.get("Message", "Unknown error")
        error_code = error_data.get("ErrorCode")
        return message, error_code
    except (json.JSONDecodeError, AttributeError):
        # If response isn't JSON, use status text
        return response.text or f"HTTP {response.status_code} error", None
