"""Tests for Postmark messages module (Sending)."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import Response

from postmark import ServerClient
from postmark.models.messages import Email


class TestOutboundSending:
    """Tests for Outbound message sending operations."""

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
            sender="sender@example.com",
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
