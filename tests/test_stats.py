"""Tests for StatsManager."""

from datetime import date

import pytest

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

OVERVIEW = {
    "Sent": 100,
    "Bounced": 2,
    "SMTPApiErrors": 1,
    "BounceRate": 0.02,
    "SpamComplaints": 0,
    "SpamComplaintsRate": 0.0,
    "Opens": 50,
    "UniqueOpens": 40,
    "TotalClicks": 20,
    "UniqueLinksClicked": 15,
    "TotalTrackedLinksSent": 80,
    "Tracked": 90,
    "WithLinkTracking": 70,
    "WithOpenTracking": 85,
    "WithClientRecorded": 45,
    "WithPlatformRecorded": 43,
}

SENT_COUNTS = {
    "Days": [{"Date": "2024-01-01", "Sent": 50}, {"Date": "2024-01-02", "Sent": 50}],
    "Sent": 100,
}

BOUNCE_COUNTS = {
    "Days": [
        {
            "Date": "2024-01-01",
            "HardBounce": 1,
            "SMTPApiError": 0,
            "SoftBounce": 1,
            "Transient": 0,
        }
    ],
    "HardBounce": 1,
    "SMTPApiError": 0,
    "SoftBounce": 1,
    "Transient": 0,
}

SPAM_COMPLAINTS = {
    "Days": [{"Date": "2024-01-01", "SpamComplaint": 1}],
    "SpamComplaint": 1,
}

TRACKED_COUNTS = {
    "Days": [{"Date": "2024-01-01", "Tracked": 90}],
    "Tracked": 90,
}

OPEN_COUNTS = {
    "Days": [{"Date": "2024-01-01", "Opens": 50, "Unique": 40}],
    "Opens": 50,
    "Unique": 40,
}

PLATFORM_USAGE = {
    "Days": [
        {
            "Date": "2024-01-01",
            "Desktop": 20,
            "Mobile": 15,
            "Unknown": 5,
            "WebMail": 0,
        }
    ],
    "Desktop": 20,
    "Mobile": 15,
    "Unknown": 5,
    "WebMail": 0,
}

EMAIL_CLIENT_USAGE = {
    "Days": [{"Date": "2024-01-01", "Apple Mail": 20, "Gmail": 15}],
    "Apple Mail": 20,
    "Gmail": 15,
}

CLICK_COUNTS = {
    "Days": [{"Date": "2024-01-01", "Clicks": 20, "Unique": 15}],
    "Clicks": 20,
    "Unique": 15,
}

BROWSER_USAGE = {
    "Days": [{"Date": "2024-01-01", "Google Chrome": 10, "Safari": 5}],
    "Google Chrome": 10,
    "Safari": 5,
}

BROWSER_PLATFORM_USAGE = {
    "Days": [{"Date": "2024-01-01", "Desktop": 12, "Mobile": 6, "Unknown": 2}],
    "Desktop": 12,
    "Mobile": 6,
    "Unknown": 2,
}

CLICK_LOCATION = {
    "Days": [{"Date": "2024-01-01", "HTML": 14, "Text": 6}],
    "HTML": 14,
    "Text": 6,
}


# ---------------------------------------------------------------------------
# Shared param-building behaviour
# ---------------------------------------------------------------------------


class TestParamBuilding:
    """The same filter params apply to every endpoint; test them once via overview."""

    @pytest.mark.asyncio
    async def test_no_params(self, stats):
        manager, fake = stats
        fake.mock_get_response(OVERVIEW)

        await manager.overview()

        fake.get.assert_called_once_with("/stats/outbound", params={})

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "kwargs,expected_key,expected_val",
        [
            ({"tag": "welcome"}, "tag", "welcome"),
            ({"from_date": date(2024, 1, 1)}, "fromdate", "2024-01-01"),
            ({"to_date": date(2024, 1, 31)}, "todate", "2024-01-31"),
            ({"message_stream": "outbound"}, "messagestream", "outbound"),
        ],
    )
    async def test_single_param(self, stats, kwargs, expected_key, expected_val):
        manager, fake = stats
        fake.mock_get_response(OVERVIEW)

        await manager.overview(**kwargs)

        params = fake.get.call_args[1]["params"]
        assert params[expected_key] == expected_val

    @pytest.mark.asyncio
    async def test_all_params(self, stats):
        manager, fake = stats
        fake.mock_get_response(OVERVIEW)

        await manager.overview(
            tag="promo",
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 31),
            message_stream="outbound",
        )

        params = fake.get.call_args[1]["params"]
        assert params == {
            "tag": "promo",
            "fromdate": "2024-01-01",
            "todate": "2024-01-31",
            "messagestream": "outbound",
        }


# ---------------------------------------------------------------------------
# Endpoint routing
# ---------------------------------------------------------------------------


class TestEndpoints:
    """Each method hits the correct URL."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method,endpoint,data",
        [
            ("overview", "/stats/outbound", OVERVIEW),
            ("sent_counts", "/stats/outbound/sends", SENT_COUNTS),
            ("bounce_counts", "/stats/outbound/bounces", BOUNCE_COUNTS),
            ("spam_counts", "/stats/outbound/spam", SPAM_COMPLAINTS),
            ("tracked_counts", "/stats/outbound/tracked", TRACKED_COUNTS),
            ("open_counts", "/stats/outbound/opens", OPEN_COUNTS),
            ("platform_usage", "/stats/outbound/opens/platforms", PLATFORM_USAGE),
            (
                "email_client_usage",
                "/stats/outbound/opens/emailclients",
                EMAIL_CLIENT_USAGE,
            ),
            ("click_counts", "/stats/outbound/clicks", CLICK_COUNTS),
            ("browser_usage", "/stats/outbound/clicks/browserfamilies", BROWSER_USAGE),
            (
                "browser_platform_usage",
                "/stats/outbound/clicks/platforms",
                BROWSER_PLATFORM_USAGE,
            ),
            ("click_location", "/stats/outbound/clicks/location", CLICK_LOCATION),
            (
                "read_times",
                "/stats/outbound/opens/readTimes",
                {"Days": [], "read_2s": 0},
            ),
        ],
    )
    async def test_endpoint_routing(self, stats, method, endpoint, data):
        manager, fake = stats
        fake.mock_get_response(data)
        await getattr(manager, method)()
        fake.get.assert_called_once_with(endpoint, params={})


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


class TestResponseParsing:
    @pytest.mark.asyncio
    async def test_overview_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(OVERVIEW)

        result = await manager.overview()

        assert result.sent == 100
        assert result.bounced == 2
        assert result.bounce_rate == 0.02
        assert result.unique_opens == 40
        assert result.total_clicks == 20

    @pytest.mark.asyncio
    async def test_sent_counts_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(SENT_COUNTS)

        result = await manager.sent_counts()

        assert result.sent == 100
        assert len(result.days) == 2
        assert result.days[0].date == "2024-01-01"
        assert result.days[0].sent == 50

    @pytest.mark.asyncio
    async def test_bounce_counts_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(BOUNCE_COUNTS)

        result = await manager.bounce_counts()

        assert result.hard_bounce == 1
        assert result.soft_bounce == 1
        assert result.days[0].hard_bounce == 1

    @pytest.mark.asyncio
    async def test_spam_counts_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(SPAM_COMPLAINTS)

        result = await manager.spam_counts()

        assert result.spam_complaint == 1
        assert result.days[0].spam_complaint == 1

    @pytest.mark.asyncio
    async def test_open_counts_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(OPEN_COUNTS)

        result = await manager.open_counts()

        assert result.opens == 50
        assert result.unique == 40

    @pytest.mark.asyncio
    async def test_platform_usage_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(PLATFORM_USAGE)

        result = await manager.platform_usage()

        assert result.desktop == 20
        assert result.mobile == 15
        assert result.web_mail == 0

    @pytest.mark.asyncio
    async def test_email_client_usage_dynamic_keys(self, stats):
        manager, fake = stats
        fake.mock_get_response(EMAIL_CLIENT_USAGE)

        result = await manager.email_client_usage()

        assert len(result.days) == 1
        assert result.days[0]["Apple Mail"] == 20
        assert result.model_extra["Apple Mail"] == 20
        assert result.model_extra["Gmail"] == 15

    @pytest.mark.asyncio
    async def test_click_counts_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(CLICK_COUNTS)

        result = await manager.click_counts()

        assert result.clicks == 20
        assert result.unique == 15

    @pytest.mark.asyncio
    async def test_browser_usage_dynamic_keys(self, stats):
        manager, fake = stats
        fake.mock_get_response(BROWSER_USAGE)

        result = await manager.browser_usage()

        assert result.days[0]["Google Chrome"] == 10
        assert result.model_extra["Google Chrome"] == 10
        assert result.model_extra["Safari"] == 5

    @pytest.mark.asyncio
    async def test_browser_platform_usage_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(BROWSER_PLATFORM_USAGE)

        result = await manager.browser_platform_usage()

        assert result.desktop == 12
        assert result.mobile == 6
        assert result.unknown == 2

    @pytest.mark.asyncio
    async def test_click_location_fields(self, stats):
        manager, fake = stats
        fake.mock_get_response(CLICK_LOCATION)

        result = await manager.click_location()

        assert result.html == 14
        assert result.text == 6
        assert result.days[0].html == 14
