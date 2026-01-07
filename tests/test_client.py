"""Tests for the HTTP client module."""
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import AsyncClient, HTTPStatusError, Response, Request

from postmark.models import client

from postmark.exceptions import (
    PostmarkException,
    PostmarkAPIException,
    InvalidAPIKeyException,
    TimeoutException,
    ValidationException
)


class TestClientModule:
    """Tests for client HTTP functions."""
    
    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful API request."""
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200  # Add this line
        
        with patch.object(AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            response = await client.request(
                method="GET",
                endpoint="/test",
                server_token="test-token"
            )
            
            assert response == mock_response
            mock_request.assert_called_once_with("GET", "/test")
    
    @pytest.mark.asyncio
    async def test_request_without_token(self):
        """Test request fails without server token."""
        with pytest.raises(PostmarkException, match="A Postmark server token is required"):
            await client.request("GET", "/test", server_token="")
    
    @pytest.mark.asyncio
    async def test_request_with_ssl_disabled(self):
        """Test request with SSL verification disabled."""
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200  # Add this line
        
        with patch.dict(os.environ, {"POSTMARK_SSL_VERIFY": "false"}):
            with patch.object(AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # Should not raise an error
                await client.request(
                    method="GET",
                    endpoint="/test",
                    server_token="test-token"
                )
    
    @pytest.mark.asyncio
    async def test_get_post_put_delete(self):
        """Test convenience methods."""
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200  # Add this line
        
        with patch('postmark.models.client.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            # Test GET
            await client.get("/test", "token", params={"key": "value"})
            mock_request.assert_called_with("GET", "/test", server_token="token", params={"key": "value"})
            
            # Test POST
            await client.post("/test", "token", json={"data": "value"})
            mock_request.assert_called_with("POST", "/test", server_token="token", json={"data": "value"})
            
            # Test PUT
            await client.put("/test", "token", json={"data": "value"})
            mock_request.assert_called_with("PUT", "/test", server_token="token", json={"data": "value"})
            
            # Test DELETE
            await client.delete("/test", "token")
            mock_request.assert_called_with("DELETE", "/test", server_token="token")

    @pytest.mark.asyncio
    async def test_handle_401_invalid_api_key(self):
        """Test handling of 401 invalid API key error."""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "ErrorCode": 10,
            "Message": "Invalid API key"
        }
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            message="401 error",
            request=Mock(),
            response=mock_response
        )
        
        with patch.object(AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(InvalidAPIKeyException) as exc_info:
                await client.request("GET", "/test", server_token="bad-token")
            
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
            "Message": "Invalid 'From' address"
        }
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            message="422 error",
            request=Mock(),
            response=mock_response
        )
        
        with patch.object(AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(ValidationException) as exc_info:
                await client.request("POST", "/email", server_token="token")
            
            assert exc_info.value.error_code == 300
            assert "Invalid 'From' address" in str(exc_info.value)