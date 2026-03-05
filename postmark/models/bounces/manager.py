import logging
from datetime import datetime
from typing import AsyncGenerator, Optional

from postmark.models.page import Page
from postmark.utils.pagination import paginate
from postmark.utils.types import HTTPClient

from .enums import BounceType
from .schemas import (
    ActivateBounceResponse,
    Bounce,
    BounceDump,
    BouncesListResponse,
    DeliveryStats,
)

logger = logging.getLogger(__name__)


class BounceManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def get_delivery_stats(self) -> DeliveryStats:
        """
        Returns aggregate delivery statistics from client server.
        """
        response = await self.client.get("/deliverystats")
        return DeliveryStats(**response.json())

    async def list(
        self,
        count: int = 100,
        offset: int = 0,
        type: Optional[BounceType] = None,
        inactive: Optional[bool] = None,
        email_filter: Optional[str] = None,
        tag: Optional[str] = None,
        message_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        message_stream: Optional[str] = None,
    ) -> Page[Bounce]:
        """
        List bounces for the server.

        Args:
            count: Number of bounces to return per request (max 500).
            offset: Number of records to skip (count + offset ≤ 10,000).
            type: Filter by bounce type (see :class:`BounceType`).
            inactive: ``True`` to return only deactivated addresses, ``False``
                for active ones, ``None`` to return all.
            email_filter: Partial email address to filter by.
            tag: Filter by message tag.
            message_id: Filter by Postmark message ID.
            from_date: Return bounces on or after this date (Eastern Time).
            to_date: Return bounces on or before this date (Eastern Time).
            message_stream: Filter by message stream ID.
        """
        if count > 500:
            raise ValueError("count cannot exceed 500")
        if count + offset > 10_000:
            raise ValueError("count + offset cannot exceed 10,000")

        params: dict = {"count": count, "offset": offset}

        if type is not None:
            params["type"] = type.value
        if inactive is not None:
            params["inactive"] = inactive
        if email_filter is not None:
            params["emailFilter"] = email_filter
        if tag is not None:
            params["tag"] = tag
        if message_id is not None:
            params["messageID"] = message_id
        if from_date is not None:
            params["fromdate"] = from_date.strftime("%Y-%m-%dT%H:%M:%S")
        if to_date is not None:
            params["todate"] = to_date.strftime("%Y-%m-%dT%H:%M:%S")
        if message_stream is not None:
            params["messagestream"] = message_stream

        response = await self.client.get("/bounces", params=params)
        data = BouncesListResponse(**response.json())
        return Page(items=data.bounces, total=data.total_count)

    async def stream(
        self,
        batch_size: int = 500,
        max_bounces: int = 1000,
        **filters,
    ) -> AsyncGenerator[Bounce, None]:
        """Yield bounces with automatic pagination."""
        async for bounce in paginate(self.list, max_bounces, batch_size, **filters):
            yield bounce

    async def get(self, bounce_id: int) -> Bounce:
        """
        Return a single bounce record by its ID.
        """
        response = await self.client.get(f"/bounces/{bounce_id}")
        return Bounce(**response.json())

    async def get_dump(self, bounce_id: int) -> BounceDump:
        """
        Return the raw SMTP source for a bounce.

        Postmark retains dumps for 30 days; after that ``body`` will be an
        empty string.
        """
        response = await self.client.get(f"/bounces/{bounce_id}/dump")
        return BounceDump(**response.json())

    async def activate(self, bounce_id: int) -> ActivateBounceResponse:
        """
        Reactivate a deactivated email address.

        Only bounces where ``can_activate`` is ``True`` can be reactivated.
        """
        response = await self.client.put(f"/bounces/{bounce_id}/activate")
        return ActivateBounceResponse(**response.json())
