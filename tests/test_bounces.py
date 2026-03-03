"""Tests for the BounceManager."""

from datetime import datetime

import pytest

from postmark.models.bounces import BounceType

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

BOUNCE = {
    "ID": 123,
    "Type": "HardBounce",
    "TypeCode": 1,
    "Name": "Hard bounce",
    "Tag": "welcome",
    "MessageID": "msg-abc",
    "ServerID": 456,
    "MessageStream": "outbound",
    "Description": "The server was unable to deliver your message",
    "Details": "smtp;550 5.1.1 The email account does not exist",
    "Email": "user@example.com",
    "From": "sender@example.com",
    "BouncedAt": "2024-01-15T10:30:00Z",
    "DumpAvailable": True,
    "Inactive": True,
    "CanActivate": True,
    "Subject": "Hello",
    "Content": None,
}


def _make_bounce(**overrides) -> dict:
    return {**BOUNCE, **overrides}


# ---------------------------------------------------------------------------
# Delivery stats
# ---------------------------------------------------------------------------


class TestDeliveryStats:
    @pytest.fixture
    def stats_response(self):
        return {
            "InactiveMails": 5,
            "Bounces": [
                {
                    "Name": "Hard bounce",
                    "Type": "HardBounce",
                    "Count": 3,
                    "TypeCode": 1,
                },
                {
                    "Name": "Soft bounce",
                    "Type": "SoftBounce",
                    "Count": 2,
                    "TypeCode": 4096,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_get_delivery_stats_success(self, bounces, stats_response):
        manager, fake = bounces
        fake.mock_get_response(stats_response)

        stats = await manager.get_delivery_stats()

        assert stats.inactive_mails == 5
        assert len(stats.bounces) == 2
        assert stats.bounces[0].type == "HardBounce"
        assert stats.bounces[0].count == 3
        assert stats.bounces[1].type == "SoftBounce"
        fake.get.assert_called_once_with("/deliverystats")

    @pytest.mark.asyncio
    async def test_get_delivery_stats_empty_bounces(self, bounces):
        manager, fake = bounces
        fake.mock_get_response({"InactiveMails": 0, "Bounces": []})

        stats = await manager.get_delivery_stats()

        assert stats.inactive_mails == 0
        assert stats.bounces == []


# ---------------------------------------------------------------------------
# Bounce List
# ---------------------------------------------------------------------------


class TestListBounces:
    @pytest.fixture
    def list_response(self):
        return {
            "TotalCount": 2,
            "Bounces": [
                _make_bounce(ID=1, Email="a@example.com"),
                _make_bounce(ID=2, Email="b@example.com"),
            ],
        }

    @pytest.mark.asyncio
    async def test_list_success(self, bounces, list_response):
        manager, fake = bounces
        fake.mock_get_response(list_response)

        results, total = await manager.list(count=50)

        assert total == 2
        assert len(results) == 2
        assert results[0].id == 1
        assert results[1].email == "b@example.com"

    @pytest.mark.asyncio
    async def test_list_default_params(self, bounces):
        manager, fake = bounces
        fake.mock_get_response({"TotalCount": 0, "Bounces": []})

        await manager.list()

        fake.get.assert_called_once_with("/bounces", params={"count": 100, "offset": 0})

    @pytest.mark.asyncio
    async def test_list_with_bounce_type_filter(self, bounces):
        manager, fake = bounces
        fake.mock_get_response({"TotalCount": 0, "Bounces": []})

        await manager.list(type=BounceType.HARD_BOUNCE)

        params = fake.get.call_args[1]["params"]
        assert params["type"] == "HardBounce"

    @pytest.mark.asyncio
    async def test_list_with_all_optional_filters(self, bounces):
        manager, fake = bounces
        fake.mock_get_response({"TotalCount": 0, "Bounces": []})

        await manager.list(
            count=25,
            offset=10,
            type=BounceType.SPAM_COMPLAINT,
            inactive=True,
            email_filter="user@example.com",
            tag="welcome",
            message_id="msg-xyz",
            from_date=datetime(2024, 1, 1, 0, 0, 0),
            to_date=datetime(2024, 1, 31, 23, 59, 59),
            message_stream="outbound",
        )

        params = fake.get.call_args[1]["params"]
        assert params["count"] == 25
        assert params["offset"] == 10
        assert params["type"] == "SpamComplaint"
        assert params["inactive"] is True
        assert params["emailFilter"] == "user@example.com"
        assert params["tag"] == "welcome"
        assert params["messageID"] == "msg-xyz"
        assert params["fromdate"] == "2024-01-01T00:00:00"
        assert params["todate"] == "2024-01-31T23:59:59"
        assert params["messagestream"] == "outbound"

    @pytest.mark.asyncio
    async def test_list_count_too_large_raises(self, bounces):
        manager, fake = bounces

        with pytest.raises(ValueError, match="count cannot exceed 500"):
            await manager.list(count=501)

        fake.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_offset_too_large_raises(self, bounces):
        manager, fake = bounces

        with pytest.raises(ValueError, match="count \\+ offset cannot exceed 10,000"):
            await manager.list(count=500, offset=9_501)

        fake.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_bounce_type_parsed_correctly(self, bounces):
        manager, fake = bounces
        fake.mock_get_response({"TotalCount": 1, "Bounces": [BOUNCE]})

        results, _ = await manager.list()

        assert results[0].type == BounceType.HARD_BOUNCE


# ---------------------------------------------------------------------------
# Bounce Stream
# ---------------------------------------------------------------------------


class TestStreamBounces:
    def _page(self, total: int, ids: range) -> dict:
        return {
            "TotalCount": total,
            "Bounces": [_make_bounce(ID=i) for i in ids],
        }

    @pytest.mark.asyncio
    async def test_stream_paginates_across_pages(self, bounces):
        manager, fake = bounces
        fake.mock_get_responses(
            self._page(750, range(500)),
            self._page(750, range(500, 750)),
        )

        result = [b async for b in manager.stream(batch_size=500, max_bounces=750)]

        assert len(result) == 750
        assert result[0].id == 0
        assert result[499].id == 499
        assert result[500].id == 500
        assert fake.get.call_count == 2

    @pytest.mark.asyncio
    async def test_stream_stops_at_max_bounces(self, bounces):
        manager, fake = bounces
        # Server has 200 records but we only want 50
        fake.mock_get_response(self._page(200, range(200)))

        result = [b async for b in manager.stream(batch_size=500, max_bounces=50)]

        assert len(result) == 50
        assert fake.get.call_count == 1

    @pytest.mark.asyncio
    async def test_stream_stops_when_server_exhausted(self, bounces):
        manager, fake = bounces
        fake.mock_get_responses(
            self._page(3, range(3)),
            {"TotalCount": 3, "Bounces": []},
        )

        result = [b async for b in manager.stream(batch_size=500, max_bounces=1000)]

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_stream_max_bounces_over_limit_raises(self, bounces):
        manager, fake = bounces

        with pytest.raises(ValueError, match="max_bounces cannot exceed 10,000"):
            async for _ in manager.stream(max_bounces=10_001):
                pass


# ---------------------------------------------------------------------------
# Single bounce
# ---------------------------------------------------------------------------


class TestGetBounce:
    @pytest.mark.asyncio
    async def test_get_success(self, bounces):
        manager, fake = bounces
        fake.mock_get_response(BOUNCE)

        bounce = await manager.get(123)

        assert bounce.id == 123
        assert bounce.type == BounceType.HARD_BOUNCE
        assert bounce.email == "user@example.com"
        assert bounce.inactive is True
        assert bounce.can_activate is True
        assert bounce.dump_available is True

    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self, bounces):
        manager, fake = bounces
        fake.mock_get_response(BOUNCE)

        await manager.get(999)

        fake.get.assert_called_once_with("/bounces/999")

    @pytest.mark.asyncio
    async def test_get_optional_fields_are_none(self, bounces):
        manager, fake = bounces
        bounce_no_tag = _make_bounce(Tag=None, Content=None)
        fake.mock_get_response(bounce_no_tag)

        bounce = await manager.get(123)

        assert bounce.tag is None
        assert bounce.content is None


# ---------------------------------------------------------------------------
# Bounce dumps
# ---------------------------------------------------------------------------


class TestGetBounceDump:
    @pytest.mark.asyncio
    async def test_get_dump_success(self, bounces):
        manager, fake = bounces
        raw = (
            "Return-Path: <sender@example.com>\r\nDate: Mon, 15 Jan 2024 10:30:00 +0000"
        )
        fake.mock_get_response({"Body": raw})

        dump = await manager.get_dump(123)

        assert dump.body == raw

    @pytest.mark.asyncio
    async def test_get_dump_empty_body_when_unavailable(self, bounces):
        manager, fake = bounces
        fake.mock_get_response({"Body": ""})

        dump = await manager.get_dump(123)

        assert dump.body == ""

    @pytest.mark.asyncio
    async def test_get_dump_calls_correct_endpoint(self, bounces):
        manager, fake = bounces
        fake.mock_get_response({"Body": ""})

        await manager.get_dump(456)

        fake.get.assert_called_once_with("/bounces/456/dump")


# ---------------------------------------------------------------------------
# Activate bounce
# ---------------------------------------------------------------------------


class TestActivateBounce:
    @pytest.fixture
    def activate_response(self):
        return {
            "Message": "OK",
            "Bounce": _make_bounce(Inactive=False, CanActivate=False),
        }

    @pytest.mark.asyncio
    async def test_activate_success(self, bounces, activate_response):
        manager, fake = bounces
        fake.mock_put_response(activate_response)

        result = await manager.activate(123)

        assert result.message == "OK"
        assert result.bounce.inactive is False
        assert result.bounce.can_activate is False

    @pytest.mark.asyncio
    async def test_activate_calls_put_on_correct_endpoint(
        self, bounces, activate_response
    ):
        manager, fake = bounces
        fake.mock_put_response(activate_response)

        await manager.activate(789)

        fake.put.assert_called_once_with("/bounces/789/activate")
        fake.get.assert_not_called()
        fake.post.assert_not_called()
