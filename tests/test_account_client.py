"""Tests for AccountClient HTTP plumbing."""

import os
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from httpx import AsyncClient, HTTPStatusError, Response

from postmark import AccountClient
from postmark.exceptions import (
    InvalidAPIKeyException,
    PostmarkException,
    TimeoutException,
    ValidationException,
)


class TestAccountClient:
    """
    Covers AccountClient's HTTP layer: auth headers, error mapping,
    SSL config, and method delegation.
    """

    @pytest.fixture
    def client(self):
        return AccountClient(account_token="test-account-token")

    @pytest.fixture
    def mock_ok_response(self):
        response = Mock(spec=Response)
        response.raise_for_status = Mock()
        response.status_code = 200
        return response

    # -------------------------------------------------------------------------
    # Initialize
    # -------------------------------------------------------------------------

    def test_init_without_token_raises(self):
        with pytest.raises(
            PostmarkException, match="A Postmark account token is required"
        ):
            AccountClient(account_token="")

    def test_ssl_disabled_via_env(self):
        with patch.dict(os.environ, {"POSTMARK_SSL_VERIFY": "false"}):
            client = AccountClient(account_token="test-account-token")
        assert client.verify_ssl is False

    def test_server_manager_attached(self, client):
        from postmark.models.servers import AccountServerManager

        assert isinstance(client.server, AccountServerManager)

    # -------------------------------------------------------------------------
    # Request delegation (GET / POST / PUT / DELETE → request())
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_delegates_to_request(self, client):
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = Mock(spec=Response)
            await client.get("/servers", params={"count": 10})
            mock_req.assert_called_once_with("GET", "/servers", params={"count": 10})

    @pytest.mark.asyncio
    async def test_post_delegates_to_request(self, client):
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = Mock(spec=Response)
            await client.post("/servers", json={"Name": "My Server"})
            mock_req.assert_called_once_with(
                "POST", "/servers", json={"Name": "My Server"}
            )

    @pytest.mark.asyncio
    async def test_put_delegates_to_request(self, client):
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = Mock(spec=Response)
            await client.put("/servers/42", json={"Name": "Renamed"})
            mock_req.assert_called_once_with(
                "PUT", "/servers/42", json={"Name": "Renamed"}
            )

    @pytest.mark.asyncio
    async def test_delete_delegates_to_request(self, client):
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = Mock(spec=Response)
            await client.delete("/servers/42")
            mock_req.assert_called_once_with("DELETE", "/servers/42", params=None)

    # -------------------------------------------------------------------------
    # Successful request
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_request_success(self, client, mock_ok_response):
        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_ok_response
            response = await client.request(method="GET", endpoint="/servers")

        assert response == mock_ok_response
        mock_req.assert_called_once_with("GET", "/servers")

    def test_ssl_verify_passed_to_httpx(self):
        with patch.dict(os.environ, {"POSTMARK_SSL_VERIFY": "false"}):
            client = AccountClient(account_token="test-account-token")
        assert client.verify_ssl is False

    def test_account_token_header_on_persistent_client(self, client):
        assert (
            client._http_client.headers["x-postmark-account-token"]
            == "test-account-token"
        )

    @pytest.mark.asyncio
    async def test_close_calls_aclose(self, client):
        with patch.object(
            client._http_client, "aclose", new_callable=AsyncMock
        ) as mock_aclose:
            await client.close()
            mock_aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        async with AccountClient(account_token="test-account-token") as client:
            assert isinstance(client, AccountClient)

    # -------------------------------------------------------------------------
    # Error mapping
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_401_raises_invalid_api_key(self, client):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "ErrorCode": 10,
            "Message": "Invalid API key",
        }
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            message="401", request=Mock(), response=mock_response
        )

        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_response

            with pytest.raises(InvalidAPIKeyException) as exc_info:
                await client.request("GET", "/servers")

        assert exc_info.value.error_code == 10
        assert exc_info.value.http_status == 401
        assert "Invalid API key" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_422_raises_validation_exception(self, client):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "ErrorCode": 300,
            "Message": "Invalid request body",
        }
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            message="422", request=Mock(), response=mock_response
        )

        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_response

            with pytest.raises(ValidationException) as exc_info:
                await client.request("POST", "/servers")

        assert exc_info.value.error_code == 300
        assert "Invalid request body" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_raises_timeout_exception(self, client):
        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = httpx.TimeoutException("timed out")

            with pytest.raises(TimeoutException, match="timed out"):
                await client.request("GET", "/servers")

    @pytest.mark.asyncio
    async def test_request_error_raises_postmark_exception(self, client):
        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = httpx.RequestError("connection refused")

            with pytest.raises(PostmarkException, match="Request failed"):
                await client.request("GET", "/servers")
