"""Tests for Postmark messages module."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import Response

from postmark import ServerClient


class TestOutboundMessages:
    """Tests for Outbound message operations."""

    @pytest.fixture
    def mock_response_data(self):
        """Sample API response data."""
        return {
            "TotalCount": 2,
            "Messages": [
                {
                    "Tag": "welcome",
                    "MessageID": "msg-123",
                    "MessageStream": "outbound",
                    "To": [{"Email": "user@example.com", "Name": "User"}],
                    "Cc": [],
                    "Bcc": [],
                    "Recipients": ["user@example.com"],
                    "ReceivedAt": "2024-01-15T10:30:00Z",
                    "From": "sender@example.com",
                    "Subject": "Welcome!",
                    "Attachments": [],
                    "Status": "Sent",
                    "TrackOpens": True,
                    "TrackLinks": "None",
                    "Metadata": {},
                    "Sandboxed": False,
                },
                {
                    "Tag": "notification",
                    "MessageID": "msg-456",
                    "MessageStream": "outbound",
                    "To": [{"Email": "another@example.com", "Name": "Another"}],
                    "Cc": [],
                    "Bcc": [],
                    "Recipients": ["another@example.com"],
                    "ReceivedAt": "2024-01-15T11:00:00Z",
                    "From": "sender@example.com",
                    "Subject": "Notification",
                    "Attachments": [],
                    "Status": "Sent",
                    "TrackOpens": False,
                    "TrackLinks": "None",
                    "Metadata": {},
                    "Sandboxed": False,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_list_messages_success(self, mock_response_data):
        """Test successful message search using .list()."""
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()

        # Instantiate Client
        client = ServerClient(server_token="test-token")
        # Mock the instance's get method
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            # Call the method via the client instance
            # CHANGED: .find() -> .list()
            messages_list, total = await client.messages.Outbound.list(
                count=50, tag="welcome"
            )

            # Assertions
            assert total == 2
            assert len(messages_list) == 2
            assert messages_list[0].message_id == "msg-123"
            assert messages_list[0].subject == "Welcome!"
            # Verify the API was called correctly
            mock_get.assert_called_once_with(
                "/messages/outbound",
                params={"count": 50, "offset": 0, "tag": "welcome"},
            )

    @pytest.mark.asyncio
    async def test_list_messages_with_filters(self):
        """Test message search with multiple filters using .list()."""
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {"TotalCount": 0, "Messages": []}
        mock_response.raise_for_status = Mock()

        client = ServerClient(server_token="test-token")

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            # Test with date filters
            # CHANGED: .find() -> .list()
            messages_list, total = await client.messages.Outbound.list(
                recipient="user@example.com",
                fromdate=datetime(2024, 1, 1, 10, 0, 0),
                todate="2024-01-31T23:59:59",
                status="sent",
            )

            # Check the parameters were formatted correctly
            call_args = mock_get.call_args
            params = call_args[1]["params"]

            assert params["recipient"] == "user@example.com"
            assert params["fromdate"] == "2024-01-01T10:00:00"
            assert params["todate"] == "2024-01-31T23:59:59"
            assert params["status"] == "sent"

    @pytest.mark.asyncio
    async def test_list_messages_validation_errors(self):
        """Test validation errors for invalid parameters in .list()."""
        client = ServerClient(server_token="test-token")

        # Test count > 500
        with pytest.raises(ValueError, match="Count cannot exceed 500"):
            await client.messages.Outbound.list(count=501)

        # Test count + offset > 10000
        with pytest.raises(ValueError, match="Count \+ Offset cannot exceed 10,000"):
            await client.messages.Outbound.list(count=500, offset=9501)

    @pytest.mark.asyncio
    async def test_stream_pagination(self):
        """Test .stream() handles pagination via AsyncGenerator."""
        # First response
        response1_data = {
            "TotalCount": 750,
            "Messages": [
                {
                    "MessageID": f"msg-{i}",
                    "Subject": f"Subject {i}",
                    "From": "test@example.com",
                    "To": [{"Email": "user@example.com"}],
                    "Recipients": ["user@example.com"],
                    "ReceivedAt": "2024-01-15T10:00:00Z",
                    "Status": "Sent",
                    "TrackOpens": True,
                    "TrackLinks": "None",
                    "MessageStream": "outbound",
                    "Cc": [],
                    "Bcc": [],
                    "Attachments": [],
                    "Metadata": {},
                    "Sandboxed": False,
                }
                for i in range(500)
            ],
        }

        # Second response
        response2_data = {
            "TotalCount": 750,
            "Messages": [
                {
                    "MessageID": f"msg-{i}",
                    "Subject": f"Subject {i}",
                    "From": "test@example.com",
                    "To": [{"Email": "user@example.com"}],
                    "Recipients": ["user@example.com"],
                    "ReceivedAt": "2024-01-15T10:00:00Z",
                    "Status": "Sent",
                    "TrackOpens": True,
                    "TrackLinks": "None",
                    "MessageStream": "outbound",
                    "Cc": [],
                    "Bcc": [],
                    "Attachments": [],
                    "Metadata": {},
                    "Sandboxed": False,
                }
                for i in range(500, 750)
            ],
        }

        mock_response1 = Mock(spec=Response)
        mock_response1.json.return_value = response1_data
        mock_response1.raise_for_status = Mock()

        mock_response2 = Mock(spec=Response)
        mock_response2.json.return_value = response2_data
        mock_response2.raise_for_status = Mock()

        client = ServerClient(server_token="test-token")

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [mock_response1, mock_response2]

            # CHANGED: Iterate over the AsyncGenerator to collect results
            all_messages = [
                msg async for msg in client.messages.Outbound.stream(max_messages=750)
            ]

            assert len(all_messages) == 750
            assert all_messages[0].message_id == "msg-0"
            assert all_messages[499].message_id == "msg-499"
            assert all_messages[500].message_id == "msg-500"
            assert all_messages[749].message_id == "msg-749"

            # Verify pagination calls
            assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        """Test getting message details by ID using .get()."""
        detail_response = {
            "MessageID": "msg-123",
            "Subject": "Test Subject",
            "TextBody": "Plain text content",
            "HtmlBody": "<p>HTML content</p>",
            "Body": None,
            "From": "sender@example.com",
            "To": [{"Email": "user@example.com"}],
            "Recipients": ["user@example.com"],
            "ReceivedAt": "2024-01-15T10:00:00Z",
            "Status": "Sent",
            "MessageEvents": [],
            "MessageStream": "outbound",
            "TrackOpens": True,
            "TrackLinks": "None",
            "Cc": [],
            "Bcc": [],
            "Attachments": [],
            "Metadata": {},
            "Sandboxed": False,
        }

        mock_response = Mock(spec=Response)
        mock_response.json.return_value = detail_response
        mock_response.raise_for_status = Mock()

        client = ServerClient(server_token="test-token")

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            message = await client.messages.Outbound.get(message_id="msg-123")

            assert message.message_id == "msg-123"
            assert message.text_body == "Plain text content"
            assert message.html_body == "<p>HTML content</p>"

            mock_get.assert_called_once_with("/messages/outbound/msg-123/details")
