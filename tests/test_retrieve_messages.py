"""Tests for email message retrieval."""

from datetime import datetime

import pytest


class TestEmailMessages:
    """Tests for email message operations."""

    @pytest.fixture
    def mock_response_data(self):
        """Sample API response data for two messages."""
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

    @pytest.fixture
    def base_message(self):
        """Minimal valid message dict for building paginated responses."""
        return {
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

    @pytest.mark.asyncio
    async def test_list_messages_success(self, outbound, mock_response_data):
        """Test successful message listing with tag filter."""
        manager, fake = outbound
        fake.mock_get_response(mock_response_data)

        messages_list, total = await manager.list(count=50, tag="welcome")

        assert total == 2
        assert len(messages_list) == 2
        assert messages_list[0].message_id == "msg-123"
        assert messages_list[0].subject == "Welcome!"

        fake.get.assert_called_once_with(
            "/messages/outbound",
            params={"count": 50, "offset": 0, "tag": "welcome"},
        )

    @pytest.mark.asyncio
    async def test_list_messages_with_filters(self, outbound):
        """Test that filters and datetime values are formatted correctly."""
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Messages": []})

        await manager.list(
            recipient="user@example.com",
            fromdate=datetime(2024, 1, 1, 10, 0, 0),
            todate="2024-01-31T23:59:59",
            status="sent",
        )

        params = fake.get.call_args[1]["params"]
        assert params["recipient"] == "user@example.com"
        assert params["fromdate"] == "2024-01-01T10:00:00"  # datetime was formatted
        assert params["todate"] == "2024-01-31T23:59:59"  # string passed through
        assert params["status"] == "sent"

    @pytest.mark.asyncio
    async def test_list_messages_validation_errors(self, outbound):
        """Test that out-of-range count/offset values raise before any API call."""
        manager, fake = outbound

        with pytest.raises(ValueError, match="Count cannot exceed 500"):
            await manager.list(count=501)

        with pytest.raises(ValueError, match="Count \\+ Offset cannot exceed 10,000"):
            await manager.list(count=500, offset=9501)

        # No HTTP calls should have been made
        fake.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_stream_pagination(self, outbound, base_message):
        """Test that .stream() paginates correctly across multiple pages."""
        manager, fake = outbound

        page1 = {
            "TotalCount": 750,
            "Messages": [
                {**base_message, "MessageID": f"msg-{i}", "Subject": f"Subject {i}"}
                for i in range(500)
            ],
        }
        page2 = {
            "TotalCount": 750,
            "Messages": [
                {**base_message, "MessageID": f"msg-{i}", "Subject": f"Subject {i}"}
                for i in range(500, 750)
            ],
        }

        fake.mock_get_responses(page1, page2)

        all_messages = [msg async for msg in manager.stream(max_messages=750)]

        assert len(all_messages) == 750
        assert all_messages[0].message_id == "msg-0"
        assert all_messages[499].message_id == "msg-499"
        assert all_messages[500].message_id == "msg-500"
        assert all_messages[749].message_id == "msg-749"
        assert fake.get.call_count == 2

    @pytest.mark.asyncio
    async def test_get_by_id(self, outbound):
        """Test fetching full message details by ID."""
        manager, fake = outbound
        fake.mock_get_response(
            {
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
        )

        message = await manager.get(message_id="msg-123")

        assert message.message_id == "msg-123"
        assert message.text_body == "Plain text content"
        assert message.html_body == "<p>HTML content</p>"
        fake.get.assert_called_once_with("/messages/outbound/msg-123/details")


# ---------------------------------------------------------------------------
# Shared fixture data for tracking events
# ---------------------------------------------------------------------------

TRACKING_GEO = {
    "CountryISOCode": "US",
    "Country": "United States",
    "RegionISOCode": "CA",
    "Region": "California",
    "City": "San Francisco",
    "Zip": "94107",
    "Coords": "37.7,-122.4",
    "IP": "1.2.3.4",
}
TRACKING_CLIENT = {"Name": "Chrome", "Company": "Google", "Family": "Chrome"}
TRACKING_OS = {"Name": "macOS", "Company": "Apple", "Family": "OS X"}

OPEN_EVENT = {
    "RecordType": "Open",
    "UserAgent": "Mozilla/5.0",
    "MessageID": "msg-123",
    "MessageStream": "outbound",
    "ReceivedAt": "2024-01-15T10:30:00Z",
    "Tag": "welcome",
    "Recipient": "user@example.com",
    "Client": TRACKING_CLIENT,
    "OS": TRACKING_OS,
    "Platform": "Desktop",
    "Geo": TRACKING_GEO,
}

CLICK_EVENT = {
    **OPEN_EVENT,
    "RecordType": "Click",
    "ClickLocation": "HTML",
    "OriginalLink": "https://example.com",
}


class TestGetDump:
    @pytest.mark.asyncio
    async def test_get_dump_success(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"Body": "raw smtp source"})

        dump = await manager.get_dump("msg-123")

        assert dump.body == "raw smtp source"

    @pytest.mark.asyncio
    async def test_get_dump_calls_correct_endpoint(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"Body": ""})

        await manager.get_dump("msg-123")

        fake.get.assert_called_once_with("/messages/outbound/msg-123/dump")


class TestListOpens:
    @pytest.mark.asyncio
    async def test_list_opens_success(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 1, "Opens": [OPEN_EVENT]})

        opens, total = await manager.list_opens()

        assert total == 1
        assert opens[0].message_id == "msg-123"
        assert opens[0].recipient == "user@example.com"
        assert opens[0].platform == "Desktop"
        assert opens[0].geo.country == "United States"

    @pytest.mark.asyncio
    async def test_list_opens_default_params(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Opens": []})

        await manager.list_opens()

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 100
        assert params["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_opens_with_filters(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Opens": []})

        await manager.list_opens(tag="welcome", recipient="user@example.com")

        params = fake.get.call_args[1]["params"]
        assert params["tag"] == "welcome"
        assert params["recipient"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_list_opens_count_validation(self, outbound):
        manager, fake = outbound

        with pytest.raises(ValueError, match="Count cannot exceed 500"):
            await manager.list_opens(count=501)

    @pytest.mark.asyncio
    async def test_list_message_opens_calls_correct_endpoint(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Opens": []})

        await manager.list_message_opens("msg-123")

        fake.get.assert_called_once_with(
            "/messages/outbound/opens/msg-123",
            params={"count": 100, "offset": 0},
        )

    @pytest.mark.asyncio
    async def test_list_message_opens_success(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 1, "Opens": [OPEN_EVENT]})

        opens, total = await manager.list_message_opens("msg-123")

        assert total == 1
        assert opens[0].message_id == "msg-123"


class TestListClicks:
    @pytest.mark.asyncio
    async def test_list_clicks_success(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 1, "Clicks": [CLICK_EVENT]})

        clicks, total = await manager.list_clicks()

        assert total == 1
        assert clicks[0].message_id == "msg-123"
        assert clicks[0].original_link == "https://example.com"
        assert clicks[0].click_location == "HTML"

    @pytest.mark.asyncio
    async def test_list_clicks_default_params(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Clicks": []})

        await manager.list_clicks()

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 100
        assert params["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_clicks_with_filters(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Clicks": []})

        await manager.list_clicks(tag="promo", recipient="user@example.com")

        params = fake.get.call_args[1]["params"]
        assert params["tag"] == "promo"
        assert params["recipient"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_list_clicks_count_validation(self, outbound):
        manager, fake = outbound

        with pytest.raises(ValueError, match="Count cannot exceed 500"):
            await manager.list_clicks(count=501)

    @pytest.mark.asyncio
    async def test_list_message_clicks_calls_correct_endpoint(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Clicks": []})

        await manager.list_message_clicks("msg-123")

        fake.get.assert_called_once_with(
            "/messages/outbound/clicks/msg-123",
            params={"count": 100, "offset": 0},
        )

    @pytest.mark.asyncio
    async def test_list_message_clicks_success(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 1, "Clicks": [CLICK_EVENT]})

        clicks, total = await manager.list_message_clicks("msg-123")

        assert total == 1
        assert clicks[0].original_link == "https://example.com"
