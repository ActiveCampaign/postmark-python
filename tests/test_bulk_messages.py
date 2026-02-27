"""Tests for bulk email sending."""

import pytest
from postmark.exceptions import InvalidEmailPayloadException
from postmark.models.messages import BulkEmail, BulkRecipient


class TestBulkSend:
    """Tests for OutboundManager.send_bulk() and get_bulk_status()."""

    @pytest.fixture
    def bulk_accepted_response(self):
        return {
            "ID": "f24af63c-533d-4b7a-ad65-4a7b3202d3a7",
            "Status": "Accepted",
            "SubmittedAt": "2024-03-17T07:25:01.4178645-05:00",
        }

    @pytest.fixture
    def bulk_status_response(self):
        return {
            "Id": "f24af63c-533d-4b7a-ad65-4a7b3202d3a7",
            "SubmittedAt": "2024-03-17T07:25:01.4178645-05:00",
            "TotalMessages": 3,
            "PercentageCompleted": 100.0,
            "Status": "Completed",
            "Subject": "Hello {{FirstName}}",
        }

    @pytest.fixture
    def minimal_bulk_dict(self):
        """Minimal valid bulk payload as a snake_case dict."""
        return {
            "sender": "sender@example.com",
            "subject": "Hello {{FirstName}}",
            "text_body": "Hi, {{FirstName}}",
            "message_stream": "broadcast",
            "messages": [
                {"to": "bob@example.com", "template_model": {"FirstName": "Bob"}},
                {"to": "frieda@example.com", "template_model": {"FirstName": "Frieda"}},
            ],
        }

    # -------------------------------------------------------------------------
    # send_bulk — dict input
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_send_bulk_from_dict(
        self, outbound, bulk_accepted_response, minimal_bulk_dict
    ):
        """Test sending a bulk email using a snake_case dict."""
        manager, fake = outbound
        fake.mock_post_response(bulk_accepted_response)

        response = await manager.send_bulk(minimal_bulk_dict)

        assert response.id == "f24af63c-533d-4b7a-ad65-4a7b3202d3a7"
        assert response.status == "Accepted"
        assert response.submitted_at is not None

        # Verify endpoint and PascalCase serialisation
        assert fake.post.call_args[0] == ("/email/bulk",)
        payload = fake.post.call_args[1]["json"]
        assert payload["From"] == "sender@example.com"
        assert payload["Subject"] == "Hello {{FirstName}}"
        assert len(payload["Messages"]) == 2
        assert payload["Messages"][0]["To"] == "bob@example.com"
        assert payload["Messages"][0]["TemplateModel"] == {"FirstName": "Bob"}

    # -------------------------------------------------------------------------
    # send_bulk — model input
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_send_bulk_from_model(self, outbound, bulk_accepted_response):
        """Test sending a bulk email using the BulkEmail model."""
        manager, fake = outbound
        fake.mock_post_response(bulk_accepted_response)

        bulk = BulkEmail(
            sender="sender@example.com",
            subject="Hello {{FirstName}}",
            html_body="<p>Hi, {{FirstName}}</p>",
            text_body="Hi, {{FirstName}}",
            message_stream="broadcast",
            messages=[
                BulkRecipient(
                    to="bob@example.com", template_model={"FirstName": "Bob"}
                ),
                BulkRecipient(
                    to="frieda@example.com",
                    cc="cc@example.com",
                    template_model={"FirstName": "Frieda"},
                ),
                BulkRecipient(
                    to="elijah@example.com",
                    bcc="bcc@example.com",
                    template_model={"FirstName": "Elijah"},
                ),
            ],
        )

        response = await manager.send_bulk(bulk)

        assert response.id == "f24af63c-533d-4b7a-ad65-4a7b3202d3a7"
        assert response.status == "Accepted"

        payload = fake.post.call_args[1]["json"]
        assert len(payload["Messages"]) == 3
        assert payload["Messages"][1]["Cc"] == "cc@example.com"
        assert payload["Messages"][2]["Bcc"] == "bcc@example.com"

    # -------------------------------------------------------------------------
    # send_bulk — dict and model produce identical payloads
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_send_bulk_dict_and_model_identical_payloads(
        self, outbound, bulk_accepted_response
    ):
        """Dict and model paths should produce the exact same API payload."""
        manager, fake = outbound

        fake.mock_post_response(bulk_accepted_response)
        await manager.send_bulk(
            {
                "sender": "sender@example.com",
                "subject": "Hello",
                "text_body": "Hi",
                "messages": [{"to": "bob@example.com"}],
            }
        )
        dict_payload = fake.post.call_args[1]["json"]

        fake.post.reset_mock()
        fake.mock_post_response(bulk_accepted_response)
        await manager.send_bulk(
            BulkEmail(
                sender="sender@example.com",
                subject="Hello",
                text_body="Hi",
                messages=[BulkRecipient(to="bob@example.com")],
            )
        )
        model_payload = fake.post.call_args[1]["json"]

        assert dict_payload == model_payload

    # -------------------------------------------------------------------------
    # send_bulk — validation
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_send_bulk_empty_messages_raises(
        self, outbound, bulk_accepted_response
    ):
        """A bulk request with no recipients should raise before any API call."""
        manager, fake = outbound

        with pytest.raises(ValueError, match="at least one recipient"):
            await manager.send_bulk(
                {
                    "sender": "sender@example.com",
                    "subject": "Hello",
                    "messages": [],
                }
            )

        fake.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_bulk_missing_sender_raises(self, outbound):
        """Missing required sender field raises InvalidEmailPayloadException."""
        manager, fake = outbound

        with pytest.raises(InvalidEmailPayloadException) as exc_info:
            await manager.send_bulk(
                {
                    "subject": "Hello",
                    "messages": [{"to": "bob@example.com"}],
                }
            )

        assert "From" in str(exc_info.value)
        fake.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_bulk_with_attachments(self, outbound, bulk_accepted_response):
        """Shared attachments should appear in the serialised payload."""
        manager, fake = outbound
        fake.mock_post_response(bulk_accepted_response)

        await manager.send_bulk(
            {
                "sender": "sender@example.com",
                "subject": "Report",
                "text_body": "See attached.",
                "message_stream": "broadcast",
                "attachments": [
                    {
                        "Name": "report.pdf",
                        "Content": "dGVzdA==",
                        "ContentType": "application/pdf",
                    }
                ],
                "messages": [{"to": "bob@example.com"}],
            }
        )

        payload = fake.post.call_args[1]["json"]
        assert len(payload["Attachments"]) == 1
        assert payload["Attachments"][0]["Name"] == "report.pdf"

    @pytest.mark.asyncio
    async def test_send_bulk_with_per_recipient_metadata(
        self, outbound, bulk_accepted_response
    ):
        """Per-recipient metadata should be serialised independently of shared metadata."""
        manager, fake = outbound
        fake.mock_post_response(bulk_accepted_response)

        await manager.send_bulk(
            {
                "sender": "sender@example.com",
                "subject": "Hello",
                "text_body": "Hi",
                "metadata": {"campaign": "newsletter"},
                "messages": [
                    {"to": "bob@example.com", "metadata": {"user_id": "001"}},
                    {"to": "frieda@example.com", "metadata": {"user_id": "002"}},
                ],
            }
        )

        payload = fake.post.call_args[1]["json"]
        assert payload["Metadata"] == {"campaign": "newsletter"}
        assert payload["Messages"][0]["Metadata"] == {"user_id": "001"}
        assert payload["Messages"][1]["Metadata"] == {"user_id": "002"}

    # -------------------------------------------------------------------------
    # get_bulk_status
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_bulk_status(self, outbound, bulk_status_response):
        """Test polling the status of a submitted bulk request."""
        manager, fake = outbound
        fake.mock_get_response(bulk_status_response)

        status = await manager.get_bulk_status("f24af63c-533d-4b7a-ad65-4a7b3202d3a7")

        assert status.id == "f24af63c-533d-4b7a-ad65-4a7b3202d3a7"
        assert status.status == "Completed"
        assert status.total_messages == 3
        assert status.percentage_completed == 100.0
        assert status.subject == "Hello {{FirstName}}"

        fake.get.assert_called_once_with(
            "/email/bulk/f24af63c-533d-4b7a-ad65-4a7b3202d3a7"
        )

    @pytest.mark.asyncio
    async def test_get_bulk_status_processing(self, outbound):
        """Test an in-progress bulk request returns partial completion."""
        manager, fake = outbound
        fake.mock_get_response(
            {
                "Id": "abc-123",
                "SubmittedAt": "2024-03-17T07:25:01Z",
                "TotalMessages": 1000,
                "PercentageCompleted": 45.5,
                "Status": "Processing",
                "Subject": "Weekly digest",
            }
        )

        status = await manager.get_bulk_status("abc-123")

        assert status.status == "Processing"
        assert status.percentage_completed == 45.5
        assert status.total_messages == 1000
