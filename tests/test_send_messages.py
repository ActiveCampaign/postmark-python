"""Tests for Postmark messages module."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import Response

from postmark import ServerClient
from postmark.models.messages import Email


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
    async def test_find_messages_success(self, mock_response_data):
        """Test successful message search."""
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = Mock()

        # Instantiate Client
        client = ServerClient(server_token="test-token")
        # Mock the instance's get method
        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            # Call the method via the client instance
            messages_list, total = await client.messages.Outbound.find(
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
    async def test_find_messages_with_filters(self):
        """Test message search with multiple filters."""
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {"TotalCount": 0, "Messages": []}
        mock_response.raise_for_status = Mock()

        client = ServerClient(server_token="test-token")

        with patch.object(client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            # Test with date filters
            messages_list, total = await client.messages.Outbound.find(
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
    async def test_find_messages_validation_errors(self):
        """Test validation errors for invalid parameters."""
        client = ServerClient(server_token="test-token")

        # Test count > 500
        with pytest.raises(ValueError, match="Count cannot exceed 500"):
            await client.messages.Outbound.find(count=501)

        # Test count + offset > 10000
        with pytest.raises(ValueError, match="Count \\+ Offset cannot exceed 10,000"):
            await client.messages.Outbound.find(count=500, offset=9501)

        # Test multiple metadata fields
        with pytest.raises(ValueError, match="Can only filter by one metadata field"):
            await client.messages.Outbound.find(
                metadata={"field1": "value1", "field2": "value2"}
            )

    @pytest.mark.asyncio
    async def test_find_all_pagination(self):
        """Test find_all handles pagination correctly."""
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

            all_messages = await client.messages.Outbound.find_all(max_messages=750)

            assert len(all_messages) == 750
            assert all_messages[0].message_id == "msg-0"
            assert all_messages[499].message_id == "msg-499"
            assert all_messages[500].message_id == "msg-500"
            assert all_messages[749].message_id == "msg-749"

            # Verify pagination calls
            assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_find_by_id(self):
        """Test getting message details by ID."""
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

    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test sending a single email message with dictionary input."""
        send_response = {
            "To": "receiver@example.com",
            "SubmittedAt": "2014-02-17T07:25:01.4178645-05:00",
            "MessageID": "test-9876",
            "ErrorCode": 0,
            "Message": "OK",
        }

        mock_response = Mock(spec=Response)
        mock_response.json.return_value = send_response
        mock_response.raise_for_status = Mock()

        client = ServerClient(server_token="test-token")

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            response = await client.messages.Outbound.send(
                {
                    "From": "sender@example.com",
                    "To": "receiver@example.com",
                    "Cc": "copied@example.com",
                    "Bcc": "blind-copied@example.com",
                    "Subject": "Test",
                    "Tag": "Invitation",
                    "HtmlBody": '<b>Hello</b> <img src="cid:image.jpg"/>',
                    "TextBody": "Hello",
                    "ReplyTo": "reply@example.com",
                    "Headers": [{"Name": "CUSTOM-HEADER", "Value": "value"}],
                    "TrackOpens": True,
                    "TrackLinks": "None",
                    "Attachments": [
                        {
                            "Name": "readme.txt",
                            "Content": "dGVzdCBjb250ZW50",
                            "ContentType": "text/plain",
                        },
                        {
                            "Name": "report.pdf",
                            "Content": "dGVzdCBjb250ZW50",
                            "ContentType": "application/octet-stream",
                        },
                        {
                            "Name": "image.jpg",
                            "ContentID": "cid:image.jpg",
                            "Content": "dGVzdCBjb250ZW50",
                            "ContentType": "image/jpeg",
                        },
                    ],
                    "Metadata": {"color": "blue", "client-id": "12345"},
                    "MessageStream": "outbound",
                }
            )

            assert response.message_id == "test-9876"
            assert response.to == "receiver@example.com"
            assert response.error_code == 0

            # Verify the structure sent to the API
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0] == ("/email",)
            payload = call_args[1]["json"]
            assert payload["From"] == "sender@example.com"
            assert payload["To"] == "receiver@example.com"
            assert payload["Attachments"][0]["Name"] == "readme.txt"

    @pytest.mark.asyncio
    async def test_send_email_from_model(self):
        """Test sending a single email using the Email model."""
        send_response = {
            "To": "receiver@example.com",
            "SubmittedAt": "2024-01-01T00:00:00",
            "MessageID": "test-model-123",
            "ErrorCode": 0,
            "Message": "OK",
        }

        mock_response = Mock(spec=Response)
        mock_response.json.return_value = send_response
        mock_response.raise_for_status = Mock()

        client = ServerClient(server_token="test-token")

        email = Email(
            from_="sender@example.com",
            to="receiver@example.com",
            subject="Pythonic Way",
            text_body="Hello",
        )

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            response = await client.messages.Outbound.send(email)

            assert response.message_id == "test-model-123"

            # Verify alias conversion
            mock_post.assert_called_once()
            payload = mock_post.call_args[1]["json"]
            assert payload["From"] == "sender@example.com"
            assert payload["TextBody"] == "Hello"

    @pytest.mark.asyncio
    async def test_send_batch(self):
        """Test sending a batch of emails."""
        batch_response = [
            {
                "To": "user1@example.com",
                "SubmittedAt": "2024-01-01T00:00:00",
                "MessageID": "id-1",
                "ErrorCode": 0,
                "Message": "OK",
            },
            {
                "To": "user2@example.com",
                "SubmittedAt": "2024-01-01T00:00:00",
                "MessageID": "id-2",
                "ErrorCode": 0,
                "Message": "OK",
            },
        ]

        mock_response = Mock(spec=Response)
        mock_response.json.return_value = batch_response
        mock_response.raise_for_status = Mock()

        client = ServerClient(server_token="test-token")

        messages = [
            {"From": "sender@example.com", "To": "user1@example.com", "Subject": "1"},
            {"From": "sender@example.com", "To": "user2@example.com", "Subject": "2"},
        ]

        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            responses = await client.messages.Outbound.send_batch(messages)

            assert len(responses) == 2
            assert responses[0].message_id == "id-1"
            assert responses[1].to == "user2@example.com"

            mock_post.assert_called_once()
            assert mock_post.call_args[0] == ("/email/batch",)
            assert len(mock_post.call_args[1]["json"]) == 2

    @pytest.mark.asyncio
    async def test_send_batch_limit(self):
        """Test validation for batch size limit."""
        client = ServerClient(server_token="test-token")

        # Create 501 messages
        messages = [{"To": "user@example.com"}] * 501

        with pytest.raises(ValueError, match="Batch size cannot exceed 500"):
            await client.messages.Outbound.send_batch(messages)
