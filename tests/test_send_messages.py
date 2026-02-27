"""Tests for outbound message sending."""

import pytest
from postmark.models.messages import Email


class TestOutboundSending:
    """Tests for Outbound message sending operations."""

    @pytest.fixture
    def send_response(self):
        """Minimal valid send response from Postmark."""
        return {
            "To": "receiver@example.com",
            "SubmittedAt": "2024-01-01T00:00:00",
            "MessageID": "test-9876",
            "ErrorCode": 0,
            "Message": "OK",
        }

    @pytest.mark.asyncio
    async def test_send_email_from_dict(self, outbound, send_response):
        """Test sending a single email using a raw dictionary."""
        manager, fake = outbound
        fake.mock_post_response(send_response)

        response = await manager.send(
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

        # Verify the payload sent to the API
        payload = fake.post.call_args[1]["json"]
        assert fake.post.call_args[0] == ("/email",)
        assert payload["From"] == "sender@example.com"
        assert payload["To"] == "receiver@example.com"
        assert payload["Attachments"][0]["Name"] == "readme.txt"

    @pytest.mark.asyncio
    async def test_send_email_from_model(self, outbound, send_response):
        """Test that Email model fields are correctly serialised to API aliases."""
        manager, fake = outbound
        fake.mock_post_response({**send_response, "MessageID": "test-model-123"})

        email = Email(
            sender="sender@example.com",
            to="receiver@example.com",
            subject="Pythonic Way",
            text_body="Hello",
        )

        response = await manager.send(email)

        assert response.message_id == "test-model-123"

        # Snake_case model fields should be serialised back to PascalCase aliases
        payload = fake.post.call_args[1]["json"]
        assert payload["From"] == "sender@example.com"
        assert payload["TextBody"] == "Hello"

    @pytest.mark.asyncio
    async def test_send_batch(self, outbound):
        """Test sending a batch of emails."""
        manager, fake = outbound
        fake.mock_post_response(
            [
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
        )

        responses = await manager.send_batch(
            [
                {
                    "From": "sender@example.com",
                    "To": "user1@example.com",
                    "Subject": "1",
                },
                {
                    "From": "sender@example.com",
                    "To": "user2@example.com",
                    "Subject": "2",
                },
            ]
        )

        assert len(responses) == 2
        assert responses[0].message_id == "id-1"
        assert responses[1].to == "user2@example.com"

        assert fake.post.call_args[0] == ("/email/batch",)
        assert len(fake.post.call_args[1]["json"]) == 2

    @pytest.mark.asyncio
    async def test_send_batch_limit(self, outbound):
        """Test that batches over 500 are rejected before any API call."""
        manager, fake = outbound

        with pytest.raises(ValueError, match="Batch size cannot exceed 500"):
            await manager.send_batch([{"To": "user@example.com"}] * 501)

        fake.post.assert_not_called()
