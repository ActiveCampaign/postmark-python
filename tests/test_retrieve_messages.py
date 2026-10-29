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

        result = await manager.list(count=50, tag="welcome")

        assert result.total == 2
        assert len(result.items) == 2
        assert result.items[0].message_id == "msg-123"
        assert result.items[0].subject == "Welcome!"

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
            from_date=datetime(2024, 1, 1, 10, 0, 0),
            to_date=datetime(2024, 1, 31, 23, 59, 59),
            status="sent",
        )

        params = fake.get.call_args[1]["params"]
        assert params["recipient"] == "user@example.com"
        assert params["fromdate"] == "2024-01-01T10:00:00"
        assert params["todate"] == "2024-01-31T23:59:59"
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


@pytest.mark.parametrize(
    "list_method,msg_method,response_key,event_data,unique_field,unique_value",
    [
        (
            "list_opens",
            "list_message_opens",
            "Opens",
            OPEN_EVENT,
            "platform",
            "Desktop",
        ),
        (
            "list_clicks",
            "list_message_clicks",
            "Clicks",
            CLICK_EVENT,
            "click_location",
            "HTML",
        ),
    ],
)
class TestTrackingEvents:
    @pytest.mark.asyncio
    async def test_list_success(
        self,
        outbound,
        list_method,
        msg_method,
        response_key,
        event_data,
        unique_field,
        unique_value,
    ):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 1, response_key: [event_data]})

        result = await getattr(manager, list_method)()

        assert result.total == 1
        assert result.items[0].message_id == "msg-123"
        assert getattr(result.items[0], unique_field) == unique_value

    @pytest.mark.asyncio
    async def test_list_default_params(
        self,
        outbound,
        list_method,
        msg_method,
        response_key,
        event_data,
        unique_field,
        unique_value,
    ):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, response_key: []})

        await getattr(manager, list_method)()

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 100
        assert params["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_with_filters(
        self,
        outbound,
        list_method,
        msg_method,
        response_key,
        event_data,
        unique_field,
        unique_value,
    ):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, response_key: []})

        await getattr(manager, list_method)(tag="promo", recipient="user@example.com")

        params = fake.get.call_args[1]["params"]
        assert params["tag"] == "promo"
        assert params["recipient"] == "user@example.com"

    @pytest.mark.asyncio
    async def test_list_count_validation(
        self,
        outbound,
        list_method,
        msg_method,
        response_key,
        event_data,
        unique_field,
        unique_value,
    ):
        manager, fake = outbound

        with pytest.raises(ValueError, match="Count cannot exceed 500"):
            await getattr(manager, list_method)(count=501)

    @pytest.mark.asyncio
    async def test_list_message_endpoint(
        self,
        outbound,
        list_method,
        msg_method,
        response_key,
        event_data,
        unique_field,
        unique_value,
    ):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, response_key: []})

        await getattr(manager, msg_method)("msg-123")

        fake.get.assert_called_once_with(
            f"/messages/outbound/{response_key.lower()}/msg-123",
            params={"count": 100, "offset": 0},
        )

    @pytest.mark.asyncio
    async def test_list_message_success(
        self,
        outbound,
        list_method,
        msg_method,
        response_key,
        event_data,
        unique_field,
        unique_value,
    ):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 1, response_key: [event_data]})

        result = await getattr(manager, msg_method)("msg-123")

        assert result.total == 1
        assert result.items[0].message_id == "msg-123"


# ---------------------------------------------------------------------------
# Opens / clicks: wire names of the filters (verified against the live API)
# ---------------------------------------------------------------------------

TRACKING_FILTERS = [
    # (python argument, wire query parameter)
    ("recipient", "recipient"),
    ("tag", "tag"),
    ("client_name", "client_name"),
    ("client_company", "client_company"),
    ("client_family", "client_family"),
    ("os_name", "os_name"),
    ("os_family", "os_family"),
    ("os_company", "os_company"),
    ("platform", "platform"),
    ("country", "country"),
    ("region", "region"),
    ("city", "city"),
    ("message_stream", "messagestream"),
]


@pytest.mark.parametrize(
    "list_method,response_key",
    [("list_opens", "Opens"), ("list_clicks", "Clicks")],
)
class TestTrackingFilterWireNames:
    """The API silently ignores unknown query parameters, so the exact wire
    spelling matters: ``client_family`` filters, ``clientFamily`` does nothing."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("argument,wire", TRACKING_FILTERS)
    async def test_each_filter_uses_its_wire_name(
        self, outbound, list_method, response_key, argument, wire
    ):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, response_key: []})

        await getattr(manager, list_method)(**{argument: "value"})

        params = fake.get.call_args[1]["params"]
        assert params[wire] == "value"
        assert set(params) == {"count", "offset", wire}

    @pytest.mark.asyncio
    async def test_all_filters_together_send_only_snake_case_names(
        self, outbound, list_method, response_key
    ):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, response_key: []})

        await getattr(manager, list_method)(
            **{argument: f"v-{argument}" for argument, _ in TRACKING_FILTERS}
        )

        params = fake.get.call_args[1]["params"]
        assert {wire: params[wire] for _, wire in TRACKING_FILTERS} == {
            wire: f"v-{argument}" for argument, wire in TRACKING_FILTERS
        }
        camel = {
            "clientName",
            "clientCompany",
            "clientFamily",
            "osName",
            "osFamily",
            "osCompany",
        }
        assert camel.isdisjoint(params)

    @pytest.mark.asyncio
    async def test_count_plus_offset_validation(
        self, outbound, list_method, response_key
    ):
        manager, fake = outbound

        with pytest.raises(ValueError, match="Count \\+ Offset cannot exceed 10,000"):
            await getattr(manager, list_method)(count=500, offset=9501)

        fake.get.assert_not_called()


class TestListMessageFilters:
    """Remaining GET /messages/outbound filters and their wire names."""

    @pytest.mark.asyncio
    async def test_from_email_subject_and_stream_filters(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Messages": []})

        await manager.list(
            from_email="sender@example.com",
            subject="Welcome",
            message_stream="broadcast",
        )

        params = fake.get.call_args[1]["params"]
        assert params["fromemail"] == "sender@example.com"
        assert params["subject"] == "Welcome"
        assert params["messagestream"] == "broadcast"

    @pytest.mark.asyncio
    async def test_single_metadata_filter(self, outbound):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, "Messages": []})

        await manager.list(metadata={"customer": "42"})

        assert fake.get.call_args[1]["params"]["metadata_customer"] == "42"

    @pytest.mark.asyncio
    async def test_multiple_metadata_filters_rejected(self, outbound):
        manager, fake = outbound

        with pytest.raises(ValueError, match="one metadata field at a time"):
            await manager.list(metadata={"a": "1", "b": "2"})

        fake.get.assert_not_called()


@pytest.mark.parametrize("msg_method", ["list_message_opens", "list_message_clicks"])
class TestPerMessageTrackingValidation:
    @pytest.mark.asyncio
    async def test_count_and_offset_limits(self, outbound, msg_method):
        manager, fake = outbound

        with pytest.raises(ValueError, match="Count cannot exceed 500"):
            await getattr(manager, msg_method)("msg-1", count=501)
        with pytest.raises(ValueError, match="Count \\+ Offset cannot exceed 10,000"):
            await getattr(manager, msg_method)("msg-1", count=500, offset=9501)

        fake.get.assert_not_called()


@pytest.mark.parametrize(
    "list_method,response_key",
    [("list_opens", "Opens"), ("list_clicks", "Clicks")],
)
class TestTrackingDateFiltersUnsupported:
    """Postmark's opens/clicks endpoints ignore date filters, so the arguments warn
    and are not sent (the signature is kept so existing calls do not break)."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"from_date": datetime(2024, 1, 1)},
            {"to_date": datetime(2024, 1, 31)},
            {"from_date": datetime(2024, 1, 1), "to_date": datetime(2024, 1, 31)},
        ],
    )
    async def test_date_arguments_warn_and_are_not_sent(
        self, outbound, list_method, response_key, kwargs
    ):
        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, response_key: []})

        with pytest.warns(FutureWarning, match="have no effect") as record:
            result = await getattr(manager, list_method)(**kwargs)

        params = fake.get.call_args[1]["params"]
        assert "fromdate" not in params
        assert "todate" not in params
        assert result.total == 0
        # The warning points at the caller, not at the SDK internals
        assert record[0].filename == __file__
        assert list_method in str(record[0].message)

    @pytest.mark.asyncio
    async def test_no_warning_without_date_arguments(
        self, outbound, list_method, response_key
    ):
        import warnings

        manager, fake = outbound
        fake.mock_get_response({"TotalCount": 0, response_key: []})

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            await getattr(manager, list_method)(tag="promo")
