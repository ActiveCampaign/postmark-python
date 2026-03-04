"""Tests for the InboundManager."""

import pytest

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

INBOUND_MSG = {
    "MessageID": "msg-in-123",
    "From": "sender@example.com",
    "FromName": "Sender Name",
    "FromFull": {"Email": "sender@example.com", "Name": "Sender Name"},
    "To": "inbox@example.com",
    "ToFull": [{"Email": "inbox@example.com", "Name": "Inbox"}],
    "Cc": None,
    "CcFull": [],
    "ReplyTo": None,
    "OriginalRecipient": "inbox@example.com",
    "Subject": "Hello inbound",
    "Date": "Thu, 16 Jan 2025 10:00:00 +0000",
    "MailboxHash": "abc123",
    "Tag": None,
    "Status": "Processed",
    "Attachments": [],
}

INBOUND_DETAILS = {
    **INBOUND_MSG,
    "TextBody": "Hello there",
    "HtmlBody": "<p>Hello there</p>",
    "BlockedReason": None,
    "Headers": [{"Name": "X-Custom", "Value": "test"}],
}

ACTION_RESPONSE = {"ErrorCode": 0, "Message": "OK"}


def _make_msg(**overrides) -> dict:
    return {**INBOUND_MSG, **overrides}


# ---------------------------------------------------------------------------
# List inbound messages
# ---------------------------------------------------------------------------


class TestListInbound:
    @pytest.fixture
    def list_response(self):
        return {
            "TotalCount": 2,
            "InboundMessages": [
                _make_msg(MessageID="msg-1", Subject="First"),
                _make_msg(MessageID="msg-2", Subject="Second"),
            ],
        }

    @pytest.mark.asyncio
    async def test_list_success(self, inbound, list_response):
        manager, fake = inbound
        fake.mock_get_response(list_response)

        result = await manager.list()

        assert result.total == 2
        assert len(result.items) == 2
        assert result.items[0].message_id == "msg-1"
        assert result.items[1].message_id == "msg-2"

    @pytest.mark.asyncio
    async def test_list_default_params(self, inbound):
        manager, fake = inbound
        fake.mock_get_response({"TotalCount": 0, "InboundMessages": []})

        await manager.list()

        fake.get.assert_called_once_with(
            "/messages/inbound", params={"count": 100, "offset": 0}
        )

    @pytest.mark.asyncio
    async def test_list_with_filters(self, inbound):
        manager, fake = inbound
        fake.mock_get_response({"TotalCount": 0, "InboundMessages": []})

        await manager.list(tag="newsletter", status="processed")

        params = fake.get.call_args[1]["params"]
        assert params["tag"] == "newsletter"
        assert params["status"] == "processed"

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, inbound):
        manager, fake = inbound
        fake.mock_get_response({"TotalCount": 0, "InboundMessages": []})

        await manager.list(count=10, offset=50)

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 10
        assert params["offset"] == 50

    @pytest.mark.asyncio
    async def test_list_count_validation(self, inbound):
        manager, fake = inbound

        with pytest.raises(ValueError, match="Count cannot exceed 500"):
            await manager.list(count=501)

    @pytest.mark.asyncio
    async def test_list_offset_validation(self, inbound):
        manager, fake = inbound

        with pytest.raises(ValueError, match="Count \\+ Offset cannot exceed 10,000"):
            await manager.list(count=500, offset=9501)

    @pytest.mark.asyncio
    async def test_list_message_fields(self, inbound):
        manager, fake = inbound
        fake.mock_get_response({"TotalCount": 1, "InboundMessages": [INBOUND_MSG]})

        result = await manager.list()
        msg = result.items[0]

        assert msg.message_id == "msg-in-123"
        assert msg.from_email == "sender@example.com"
        assert msg.from_name == "Sender Name"
        assert msg.from_full.email == "sender@example.com"
        assert msg.subject == "Hello inbound"
        assert msg.status == "Processed"
        assert msg.mailbox_hash == "abc123"

    @pytest.mark.asyncio
    async def test_list_empty(self, inbound):
        manager, fake = inbound
        fake.mock_get_response({"TotalCount": 0, "InboundMessages": []})

        result = await manager.list()

        assert result.total == 0
        assert result.items == []


# ---------------------------------------------------------------------------
# Get inbound message details
# ---------------------------------------------------------------------------


class TestGetInbound:
    @pytest.mark.asyncio
    async def test_get_success(self, inbound):
        manager, fake = inbound
        fake.mock_get_response(INBOUND_DETAILS)

        msg = await manager.get("msg-in-123")

        assert msg.message_id == "msg-in-123"
        assert msg.text_body == "Hello there"
        assert msg.html_body == "<p>Hello there</p>"
        assert msg.blocked_reason is None

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, inbound):
        manager, fake = inbound
        fake.mock_get_response(INBOUND_DETAILS)

        await manager.get("msg-in-123")

        fake.get.assert_called_once_with("/messages/inbound/msg-in-123/details")

    @pytest.mark.asyncio
    async def test_get_headers(self, inbound):
        manager, fake = inbound
        fake.mock_get_response(INBOUND_DETAILS)

        msg = await manager.get("msg-in-123")

        assert len(msg.headers) == 1
        assert msg.headers[0].name == "X-Custom"
        assert msg.headers[0].value == "test"

    @pytest.mark.asyncio
    async def test_get_with_blocked_reason(self, inbound):
        manager, fake = inbound
        fake.mock_get_response(
            {**INBOUND_DETAILS, "BlockedReason": "spam", "Status": "Blocked"}
        )

        msg = await manager.get("msg-in-123")

        assert msg.blocked_reason == "spam"


# ---------------------------------------------------------------------------
# Bypass inbound message
# ---------------------------------------------------------------------------


class TestBypassInbound:
    @pytest.mark.asyncio
    async def test_bypass_success(self, inbound):
        manager, fake = inbound
        fake.mock_put_response(ACTION_RESPONSE)

        result = await manager.bypass("msg-in-123")

        assert result.error_code == 0
        assert result.message == "OK"

    @pytest.mark.asyncio
    async def test_bypass_calls_correct_endpoint(self, inbound):
        manager, fake = inbound
        fake.mock_put_response(ACTION_RESPONSE)

        await manager.bypass("msg-in-123")

        fake.put.assert_called_once_with("/messages/inbound/msg-in-123/bypass")

    @pytest.mark.asyncio
    async def test_bypass_does_not_call_other_methods(self, inbound):
        manager, fake = inbound
        fake.mock_put_response(ACTION_RESPONSE)

        await manager.bypass("msg-in-123")

        fake.get.assert_not_called()
        fake.post.assert_not_called()


# ---------------------------------------------------------------------------
# Retry inbound message
# ---------------------------------------------------------------------------


class TestRetryInbound:
    @pytest.mark.asyncio
    async def test_retry_success(self, inbound):
        manager, fake = inbound
        fake.mock_put_response(ACTION_RESPONSE)

        result = await manager.retry("msg-in-123")

        assert result.error_code == 0
        assert result.message == "OK"

    @pytest.mark.asyncio
    async def test_retry_calls_correct_endpoint(self, inbound):
        manager, fake = inbound
        fake.mock_put_response(ACTION_RESPONSE)

        await manager.retry("msg-in-123")

        fake.put.assert_called_once_with("/messages/inbound/msg-in-123/retry")

    @pytest.mark.asyncio
    async def test_retry_does_not_call_other_methods(self, inbound):
        manager, fake = inbound
        fake.mock_put_response(ACTION_RESPONSE)

        await manager.retry("msg-in-123")

        fake.get.assert_not_called()
        fake.post.assert_not_called()
