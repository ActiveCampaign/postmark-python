"""Tests for email message sending."""

import pytest

from postmark.exceptions import InvalidEmailException
from postmark.models.messages import Email
from postmark.models.templates import TemplateEmail


class TestEmailSending:
    """Tests for email message sending operations."""

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
    async def test_send_email_from_dict(self, email, send_response):
        """Test sending a single email using a snake_case dict."""
        manager, fake = email
        fake.mock_post_response(send_response)

        response = await manager.send(
            {
                "sender": "sender@example.com",
                "to": "receiver@example.com",
                "cc": "copied@example.com",
                "bcc": "blind-copied@example.com",
                "subject": "Test",
                "tag": "Invitation",
                "html_body": '<b>Hello</b> <img src="cid:image.jpg"/>',
                "text_body": "Hello",
                "reply_to": "reply@example.com",
                "headers": [{"Name": "CUSTOM-HEADER", "Value": "value"}],
                "track_opens": True,
                "track_links": "None",
                "attachments": [
                    {
                        "Name": "readme.txt",
                        "Content": "dGVzdCBjb250ZW50",
                        "ContentType": "text/plain",
                    },
                ],
                "metadata": {"color": "blue", "client-id": "12345"},
                "message_stream": "outbound",
            }
        )

        assert response.message_id == "test-9876"
        assert response.to == "receiver@example.com"
        assert response.error_code == 0

        # Dict keys are snake_case but the API payload should use PascalCase aliases
        payload = fake.post.call_args[1]["json"]
        assert fake.post.call_args[0] == ("/email",)
        assert payload["From"] == "sender@example.com"
        assert payload["To"] == "receiver@example.com"
        assert payload["Attachments"][0]["Name"] == "readme.txt"

    @pytest.mark.asyncio
    async def test_send_email_from_model(self, email, send_response):
        """Test that Email model fields are correctly serialised to API aliases."""
        manager, fake = email
        fake.mock_post_response({**send_response, "MessageID": "test-model-123"})

        response = await manager.send(
            Email(
                sender="sender@example.com",
                to="receiver@example.com",
                subject="Pythonic Way",
                text_body="Hello",
            )
        )

        assert response.message_id == "test-model-123"

        # Snake_case model fields should be serialised back to PascalCase aliases
        payload = fake.post.call_args[1]["json"]
        assert payload["From"] == "sender@example.com"
        assert payload["TextBody"] == "Hello"

    @pytest.mark.asyncio
    async def test_send_dict_and_model_produce_identical_payloads(
        self, email, send_response
    ):
        """Dict and model paths should produce the exact same API payload."""
        manager, fake = email
        fake.mock_post_response(send_response)

        await manager.send(
            {
                "sender": "sender@example.com",
                "to": "receiver@example.com",
                "subject": "Hello",
                "text_body": "Hi",
            }
        )
        dict_payload = fake.post.call_args[1]["json"]

        fake.post.reset_mock()
        fake.mock_post_response(send_response)

        await manager.send(
            Email(
                sender="sender@example.com",
                to="receiver@example.com",
                subject="Hello",
                text_body="Hi",
            )
        )
        model_payload = fake.post.call_args[1]["json"]

        assert dict_payload == model_payload

    @pytest.mark.asyncio
    async def test_send_dict_invalid_payload_raises(self, email):
        """Invalid dict raises InvalidEmailException before any API call."""
        manager, fake = email

        with pytest.raises(InvalidEmailException) as exc_info:
            await manager.send({"to": "receiver@example.com"})  # missing sender

        assert "From" in str(exc_info.value)
        fake.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_batch(self, email):
        """Test sending a batch of emails."""
        manager, fake = email
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
                    "sender": "sender@example.com",
                    "to": "user1@example.com",
                    "subject": "1",
                },
                {
                    "sender": "sender@example.com",
                    "to": "user2@example.com",
                    "subject": "2",
                },
            ]
        )

        assert len(responses) == 2
        assert responses[0].message_id == "id-1"
        assert responses[1].to == "user2@example.com"
        assert fake.post.call_args[0] == ("/email/batch",)
        assert len(fake.post.call_args[1]["json"]) == 2

    @pytest.mark.asyncio
    async def test_send_batch_limit(self, email):
        """Test that batches over 500 are rejected before any API call."""
        manager, fake = email

        with pytest.raises(ValueError, match="Batch size cannot exceed 500"):
            await manager.send_batch([{"to": "user@example.com"}] * 501)

        fake.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_batch_invalid_message_includes_index(self, email):
        """Validation error in a batch message should identify which index failed."""
        manager, fake = email

        with pytest.raises(InvalidEmailException) as exc_info:
            await manager.send_batch(
                [
                    {
                        "sender": "sender@example.com",
                        "to": "user1@example.com",
                        "subject": "OK",
                    },
                    {"to": "user2@example.com"},  # index 1 — missing sender
                ]
            )

        assert "messages[1]" in str(exc_info.value)
        fake.post.assert_not_called()


SEND_RESPONSE = {
    "To": "recipient@example.com",
    "SubmittedAt": "2024-01-15T10:30:00Z",
    "MessageID": "msg-abc",
    "ErrorCode": 0,
    "Message": "OK",
}


class TestSendWithTemplate:
    @pytest.fixture
    def msg_dict(self):
        return {
            "From": "sender@example.com",
            "To": "recipient@example.com",
            "TemplateId": 1,
            "TemplateModel": {"name": "World"},
        }

    @pytest.mark.asyncio
    async def test_dict_input(self, email, msg_dict):
        manager, fake = email
        fake.mock_post_response(SEND_RESPONSE)

        result = await manager.send_with_template(msg_dict)

        assert result.message_id == "msg-abc"
        fake.post.assert_called_once()
        endpoint = fake.post.call_args[0][0]
        assert endpoint == "/email/withTemplate"

    @pytest.mark.asyncio
    async def test_model_input(self, email):
        manager, fake = email
        fake.mock_post_response(SEND_RESPONSE)

        tmpl_email = TemplateEmail(
            **{
                "From": "sender@example.com",
                "To": "recipient@example.com",
                "TemplateId": 1,
                "TemplateModel": {},
            }
        )
        result = await manager.send_with_template(tmpl_email)

        assert result.error_code == 0

    @pytest.mark.asyncio
    async def test_missing_sender_raises(self, email):
        manager, fake = email

        with pytest.raises(InvalidEmailException):
            await manager.send_with_template(
                {"To": "recipient@example.com", "TemplateId": 1, "TemplateModel": {}}
            )

        fake.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_alias_used_instead_of_id(self, email):
        manager, fake = email
        fake.mock_post_response(SEND_RESPONSE)

        await manager.send_with_template(
            {
                "From": "sender@example.com",
                "To": "recipient@example.com",
                "TemplateAlias": "welcome",
                "TemplateModel": {},
            }
        )

        payload = fake.post.call_args[1]["json"]
        assert payload.get("TemplateAlias") == "welcome"


class TestSendBatchWithTemplates:
    @pytest.fixture
    def two_messages(self):
        return [
            {
                "From": "sender@example.com",
                "To": "a@example.com",
                "TemplateId": 1,
                "TemplateModel": {},
            },
            {
                "From": "sender@example.com",
                "To": "b@example.com",
                "TemplateId": 1,
                "TemplateModel": {},
            },
        ]

    @pytest.mark.asyncio
    async def test_multiple_messages(self, email, two_messages):
        manager, fake = email
        fake.mock_post_response([SEND_RESPONSE, SEND_RESPONSE])

        results = await manager.send_batch_with_template(two_messages)

        assert len(results) == 2
        endpoint = fake.post.call_args[0][0]
        assert endpoint == "/email/batchWithTemplates"

    @pytest.mark.asyncio
    async def test_wraps_in_messages_key(self, email, two_messages):
        manager, fake = email
        fake.mock_post_response([SEND_RESPONSE, SEND_RESPONSE])

        await manager.send_batch_with_template(two_messages)

        payload = fake.post.call_args[1]["json"]
        assert "Messages" in payload
        assert len(payload["Messages"]) == 2

    @pytest.mark.asyncio
    async def test_batch_over_500_raises(self, email):
        manager, fake = email
        messages = [
            {
                "From": "sender@example.com",
                "To": f"user{i}@example.com",
                "TemplateId": 1,
                "TemplateModel": {},
            }
            for i in range(501)
        ]

        with pytest.raises(ValueError, match="500"):
            await manager.send_batch_with_template(messages)

        fake.post.assert_not_called()
