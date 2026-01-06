import httpx
import os
import logging

# Get a logger for this module
logger = logging.getLogger(__name__)

_base_url = "https://api.postmarkapp.com"

async def request(method: str, endpoint: str, server_token: str, **kwargs) -> httpx.Response:
    """
    Make a request to the Postmark API using a specific token.
    """
    if not server_token:
        logger.error("A Postmark server token is required")
        raise ValueError("A Postmark server token is required.")

    # Allow SSL verification to be controlled via environment variable
    verify_ssl = os.getenv("POSTMARK_SSL_VERIFY", "true").lower() != "false"
    
    if not verify_ssl:
        logger.warning("SSL verification is disabled. Do not use in production!")

    headers = {
        "X-Postmark-Server-Token": server_token,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    logger.debug(f"Making {method} request to {endpoint}")

    # Create a client for this specific request context
    async with httpx.AsyncClient(
        base_url=_base_url,
        headers=headers,
        verify=verify_ssl,
        timeout=30.0
    ) as client:
        try:
            response = await client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            logger.debug(f"Request successful: {response.status_code}")
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {method} {endpoint}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

async def get(endpoint: str, server_token: str, params: dict = None) -> httpx.Response:
    return await request("GET", endpoint, server_token=server_token, params=params)

async def post(endpoint: str, server_token: str, json: dict = None) -> httpx.Response:
    return await request("POST", endpoint, server_token=server_token, json=json)

async def put(endpoint: str, server_token: str, json: dict = None) -> httpx.Response:
    return await request("PUT", endpoint, server_token=server_token, json=json)

async def delete(endpoint: str, server_token: str) -> httpx.Response:
    return await request("DELETE", endpoint, server_token=server_token)