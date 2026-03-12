"""Tests for ServerClient HTTP plumbing."""

import os
from unittest.mock import ANY, AsyncMock, Mock, patch

import httpx
import pytest
from httpx import AsyncClient, HTTPStatusError, Response

from postmark import ServerClient
from postmark.exceptions import (
    InvalidAPIKeyException,
    PostmarkException,
    ServerException,
    TimeoutException,
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
        return ServerClient(server_token="test-token", retries=0)

    @pytest.fixture
    def mock_ok_response(self):
        response = Mock(spec=Response)
        response.raise_for_status = Mock()
        response.status_code = 200
        response.headers = {}
        return response

    # -------------------------------------------------------------------------
    # Initialize
    # -------------------------------------------------------------------------

    def test_init_without_token_raises(self):
        with pytest.raises(
            PostmarkException, match="A Postmark server token is required"
        ):
            ServerClient(server_token="")

    def test_negative_retries_raises(self):
        with pytest.raises(PostmarkException, match="retries"):
            ServerClient(server_token="test-token", retries=-1)

    def test_zero_timeout_raises(self):
        with pytest.raises(PostmarkException, match="timeout"):
            ServerClient(server_token="test-token", timeout=0)

    def test_negative_timeout_raises(self):
        with pytest.raises(PostmarkException, match="timeout"):
            ServerClient(server_token="test-token", timeout=-1.0)

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
        mock_req.assert_called_once_with(
            "GET", "/test", headers={"X-Postmark-Correlation-Id": ANY}
        )

    def test_ssl_verify_passed_to_httpx(self):
        """Confirm verify_ssl reaches the underlying httpx.AsyncClient."""
        with patch.dict(os.environ, {"POSTMARK_SSL_VERIFY": "false"}):
            client = ServerClient(server_token="test-token")
        assert client.verify_ssl is False

    def test_server_token_header_on_persistent_client(self, client):
        assert client._http_client.headers["x-postmark-server-token"] == "test-token"

    @pytest.mark.asyncio
    async def test_close_calls_aclose(self, client):
        with patch.object(
            client._http_client, "aclose", new_callable=AsyncMock
        ) as mock_aclose:
            await client.close()
            mock_aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_twice_does_not_raise(self, client):
        await client.close()
        await client.close()

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        async with ServerClient(server_token="test-token") as client:
            assert isinstance(client, ServerClient)

    # -------------------------------------------------------------------------
    # Error mapping
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_401_raises_invalid_api_key(self, client):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 401
        mock_response.headers = {}
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
        mock_response.headers = {}
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

    @pytest.mark.asyncio
    async def test_timeout_raises_timeout_exception(self, client):
        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = httpx.TimeoutException("timed out")

            with pytest.raises(TimeoutException, match="timed out"):
                await client.request("GET", "/test")

    @pytest.mark.asyncio
    async def test_request_error_raises_postmark_exception(self, client):
        with patch.object(AsyncClient, "request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = httpx.RequestError("connection refused")

            with pytest.raises(PostmarkException, match="Request failed"):
                await client.request("GET", "/test")

    # -------------------------------------------------------------------------
    # Correlation ID uniqueness
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_correlation_ids_unique_across_requests(self, client):
        ok_resp = Mock(spec=Response)
        ok_resp.raise_for_status = Mock()
        ok_resp.status_code = 200
        ok_resp.headers = {}

        captured_ids = []

        async def capture(*args, **kwargs):
            captured_ids.append(kwargs["headers"]["X-Postmark-Correlation-Id"])
            return ok_resp

        with patch.object(AsyncClient, "request", side_effect=capture):
            await client.request("GET", "/test")
            await client.request("GET", "/test")

        assert len(captured_ids) == 2
        assert captured_ids[0] != captured_ids[1]

    # -------------------------------------------------------------------------
    # Retry behaviour
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_retries_on_rate_limit(self):
        client = ServerClient(server_token="test-token", retries=2)

        failing_resp = Mock(spec=Response)
        failing_resp.status_code = 429
        failing_resp.headers = {}
        failing_resp.json.return_value = {"ErrorCode": 429, "Message": "Rate limit"}
        failing_resp.raise_for_status.side_effect = HTTPStatusError(
            "429", request=Mock(), response=failing_resp
        )
        ok_resp = Mock(spec=Response)
        ok_resp.raise_for_status = Mock()
        ok_resp.status_code = 200
        ok_resp.headers = {}

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with patch.object(
                AsyncClient,
                "request",
                new_callable=AsyncMock,
                side_effect=[failing_resp, failing_resp, ok_resp],
            ) as mock_req:
                response = await client.request("GET", "/test")

        assert mock_req.call_count == 3
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_retries_on_server_error(self):
        client = ServerClient(server_token="test-token", retries=1)

        failing_resp = Mock(spec=Response)
        failing_resp.status_code = 500
        failing_resp.headers = {}
        failing_resp.json.return_value = {"ErrorCode": 500, "Message": "Server error"}
        failing_resp.raise_for_status.side_effect = HTTPStatusError(
            "500", request=Mock(), response=failing_resp
        )
        ok_resp = Mock(spec=Response)
        ok_resp.raise_for_status = Mock()
        ok_resp.status_code = 200
        ok_resp.headers = {}

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with patch.object(
                AsyncClient,
                "request",
                new_callable=AsyncMock,
                side_effect=[failing_resp, ok_resp],
            ) as mock_req:
                response = await client.request("GET", "/test")

        assert mock_req.call_count == 2
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_retries_exhausted_reraises(self):
        client = ServerClient(server_token="test-token", retries=2)

        mock_response = Mock(spec=Response)
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_response.json.return_value = {"ErrorCode": 500, "Message": "Server error"}
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            "500", request=Mock(), response=mock_response
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with patch.object(
                AsyncClient,
                "request",
                new_callable=AsyncMock,
                return_value=mock_response,
            ) as mock_req:
                with pytest.raises(ServerException):
                    await client.request("GET", "/test")

        assert mock_req.call_count == 3  # 1 initial + 2 retries

    @pytest.mark.asyncio
    async def test_no_retry_on_validation_error(self):
        client = ServerClient(server_token="test-token", retries=2)

        mock_response = Mock(spec=Response)
        mock_response.status_code = 422
        mock_response.headers = {}
        mock_response.json.return_value = {
            "ErrorCode": 300,
            "Message": "Validation error",
        }
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            "422", request=Mock(), response=mock_response
        )

        with patch.object(
            AsyncClient, "request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_req:
            with pytest.raises(ValidationException):
                await client.request("POST", "/test")

        assert mock_req.call_count == 1

    @pytest.mark.asyncio
    async def test_retries_disabled_with_zero(self):
        client = ServerClient(server_token="test-token", retries=0)

        mock_response = Mock(spec=Response)
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_response.json.return_value = {"ErrorCode": 500, "Message": "Server error"}
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            "500", request=Mock(), response=mock_response
        )

        with patch.object(
            AsyncClient, "request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_req:
            with pytest.raises(ServerException):
                await client.request("GET", "/test")

        assert mock_req.call_count == 1
