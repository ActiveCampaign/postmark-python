from datetime import date
from typing import Optional

from postmark.utils.types import HTTPClient

from .schemas import (
    BounceCounts,
    BrowserPlatformUsage,
    BrowserUsage,
    ClickCounts,
    ClickLocation,
    EmailClientUsage,
    OpenCounts,
    OutboundOverview,
    PlatformUsage,
    ReadTimes,
    SentCounts,
    SpamComplaints,
    TrackedCounts,
)


class StatsManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    def _params(
        self,
        tag: Optional[str],
        from_date: Optional[date],
        to_date: Optional[date],
        message_stream: Optional[str],
    ) -> dict:
        params: dict = {}
        if tag is not None:
            params["tag"] = tag
        if from_date is not None:
            params["fromdate"] = from_date.strftime("%Y-%m-%d")
        if to_date is not None:
            params["todate"] = to_date.strftime("%Y-%m-%d")
        if message_stream is not None:
            params["messagestream"] = message_stream
        return params

    async def overview(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> OutboundOverview:
        """Return aggregate outbound statistics."""
        response = await self.client.get(
            "/stats/outbound",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return OutboundOverview(**response.json())

    async def sent_counts(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> SentCounts:
        """Return daily sent counts."""
        response = await self.client.get(
            "/stats/outbound/sends",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return SentCounts(**response.json())

    async def bounce_counts(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> BounceCounts:
        """Return daily bounce counts broken down by type."""
        response = await self.client.get(
            "/stats/outbound/bounces",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return BounceCounts(**response.json())

    async def spam_counts(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> SpamComplaints:
        """Return daily spam complaint counts."""
        response = await self.client.get(
            "/stats/outbound/spam",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return SpamComplaints(**response.json())

    async def tracked_counts(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> TrackedCounts:
        """Return daily tracked email counts."""
        response = await self.client.get(
            "/stats/outbound/tracked",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return TrackedCounts(**response.json())

    async def open_counts(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> OpenCounts:
        """Return daily email open counts."""
        response = await self.client.get(
            "/stats/outbound/opens",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return OpenCounts(**response.json())

    async def platform_usage(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> PlatformUsage:
        """Return daily email open counts broken down by platform."""
        response = await self.client.get(
            "/stats/outbound/opens/platforms",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return PlatformUsage(**response.json())

    async def email_client_usage(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> EmailClientUsage:
        """Return email open counts broken down by email client."""
        response = await self.client.get(
            "/stats/outbound/opens/emailclients",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return EmailClientUsage(**response.json())

    async def click_counts(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> ClickCounts:
        """Return daily click counts."""
        response = await self.client.get(
            "/stats/outbound/clicks",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return ClickCounts(**response.json())

    async def browser_usage(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> BrowserUsage:
        """Return click counts broken down by browser family."""
        response = await self.client.get(
            "/stats/outbound/clicks/browserfamilies",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return BrowserUsage(**response.json())

    async def browser_platform_usage(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> BrowserPlatformUsage:
        """Return click counts broken down by browser platform."""
        response = await self.client.get(
            "/stats/outbound/clicks/platforms",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return BrowserPlatformUsage(**response.json())

    async def click_location(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> ClickLocation:
        """Return click counts broken down by link location (HTML vs text)."""
        response = await self.client.get(
            "/stats/outbound/clicks/location",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return ClickLocation(**response.json())

    async def read_times(
        self,
        tag: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        message_stream: Optional[str] = None,
    ) -> ReadTimes:
        """Return email open read-time distribution."""
        response = await self.client.get(
            "/stats/outbound/opens/readTimes",
            params=self._params(tag, from_date, to_date, message_stream),
        )
        return ReadTimes(**response.json())
