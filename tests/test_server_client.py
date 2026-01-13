"""Tests for the HTTP client module."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import AsyncClient, HTTPStatusError, Response

from postmark import ServerClient

from postmark.exceptions import (
    PostmarkException,
    InvalidAPIKeyException,
    ValidationException,
)


class TestClientModule:
    """Tests for client HTTP functions."""

    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful API request."""
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200

        # Instantiate the client with the token
        client = ServerClient(server_token="test-token")

        with patch.object(
            AsyncClient, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # Call request on the instance (no server_token arg needed here)
            response = await client.request(method="GET", endpoint="/test")

            assert response == mock_response
            mock_request.assert_called_once_with("GET", "/test")

    def test_init_without_token(self):
        """Test initialization fails without server token."""
        # Validation now happens in __init__, so this is no longer async
        with pytest.raises(
            PostmarkException, match="A Postmark server token is required"
        ):
            ServerClient(server_token="")

    @pytest.mark.asyncio
    async def test_request_with_ssl_disabled(self):
        """Test request with SSL verification disabled."""
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200

        # Patch environment before instantiating the client
        with patch.dict(os.environ, {"POSTMARK_SSL_VERIFY": "false"}):
            client = ServerClient(server_token="test-token")

            # verify_ssl property is set during init
            assert client.verify_ssl is False

            with patch.object(
                AsyncClient, "request", new_callable=AsyncMock
            ) as mock_request:
                mock_request.return_value = mock_response

                await client.request(method="GET", endpoint="/test")

    @pytest.mark.asyncio
    async def test_get_post_put_delegation(self):
        """Test that convenience methods delegate to self.request correctly."""
        client = ServerClient(server_token="test-token")

        # We patch the 'request' method on the instance of the client
        with patch.object(client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = Mock(spec=Response)

            # Test GET
            await client.get("/test", params={"key": "value"})
            mock_request.assert_called_with("GET", "/test", params={"key": "value"})

            # Test POST
            await client.post("/test", json={"data": "value"})
            mock_request.assert_called_with("POST", "/test", json={"data": "value"})

            # Test PUT
            await client.put("/test", json={"data": "value"})
            mock_request.assert_called_with("PUT", "/test", json={"data": "value"})

    @pytest.mark.asyncio
    async def test_handle_401_invalid_api_key(self):
        """Test handling of 401 invalid API key error."""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "ErrorCode": 10,
            "Message": "Invalid API key",
        }
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            message="401 error", request=Mock(), response=mock_response
        )

        client = ServerClient(server_token="bad-token")

        with patch.object(
            AsyncClient, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(InvalidAPIKeyException) as exc_info:
                await client.request("GET", "/test")

            assert exc_info.value.error_code == 10
            assert exc_info.value.http_status == 401
            assert "Invalid API key" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_422_validation_error(self):
        """Test handling of 422 validation error."""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "ErrorCode": 300,
            "Message": "Invalid 'From' address",
        }
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            message="422 error", request=Mock(), response=mock_response
        )

        client = ServerClient(server_token="token")

        with patch.object(
            AsyncClient, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(ValidationException) as exc_info:
                await client.request("POST", "/email")

            assert exc_info.value.error_code == 300
            assert "Invalid 'From' address" in str(exc_info.value)
