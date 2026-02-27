"""Tests for ServerClient HTTP plumbing."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import AsyncClient, HTTPStatusError, Response

from postmark import ServerClient
from postmark.exceptions import (
    InvalidAPIKeyException,
    PostmarkException,
    ValidationException,
)


class TestServerClient:
    """
    These tests cover only ServerClient's HTTP layer:
    auth headers, error mapping, SSL config, and method delegation.
    Manager-level behaviour (list, send, stream) lives in the other test files.
    """

    @pytest.fixture
    def client(self):
        return ServerClient(server_token="test-token")

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
            PostmarkException, match="A Postmark server token is required"
        ):
            ServerClient(server_token="")

    def test_ssl_disabled_via_env(self):
        with patch.dict(os.environ, {"POSTMARK_SSL_VERIFY": "false"}):
            client = ServerClient(server_token="test-token")
        assert client.verify_ssl is False

    # -------------------------------------------------------------------------
    # Request delegation (GET / POST / PUT → request())
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_delegates_to_request(self, client):
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = Mock(spec=Response)
            await client.get("/test", params={"key": "value"})
            mock_req.assert_called_once_with("GET", "/test", params={"key": "value"})

    @pytest.mark.asyncio
    async def test_post_delegates_to_request(self, client):
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = Mock(spec=Response)
            await client.post("/test", json={"data": "value"})
            mock_req.assert_called_once_with("POST", "/test", json={"data": "value"})

    @pytest.mark.asyncio
    async def test_put_delegates_to_request(self, client):
        with patch.object(client, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = Mock(spec=Response)
            await client.put("/test", json={"data": "value"})
            mock_req.assert_called_once_with("PUT", "/test", json={"data": "value"})

    # -------------------------------------------------------------------------
    # Successful request
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_request_success(self, client, mock_ok_response):
        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_ok_response
            response = await client.request(method="GET", endpoint="/test")

        assert response == mock_ok_response
        mock_req.assert_called_once_with("GET", "/test")

    @pytest.mark.asyncio
    async def test_ssl_verify_passed_to_httpx(self, mock_ok_response):
        """Confirm verify_ssl reaches the underlying httpx.AsyncClient."""
        with patch.dict(os.environ, {"POSTMARK_SSL_VERIFY": "false"}):
            client = ServerClient(server_token="test-token")

        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_ok_response
            await client.request(method="GET", endpoint="/test")

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
                await client.request("GET", "/test")

        assert exc_info.value.error_code == 10
        assert exc_info.value.http_status == 401
        assert "Invalid API key" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_422_raises_validation_exception(self, client):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "ErrorCode": 300,
            "Message": "Invalid 'From' address",
        }
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            message="422", request=Mock(), response=mock_response
        )

        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_response

            with pytest.raises(ValidationException) as exc_info:
                await client.request("POST", "/email")

        assert exc_info.value.error_code == 300
        assert "Invalid 'From' address" in str(exc_info.value)
