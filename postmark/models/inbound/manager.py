from typing import Any, Dict

from postmark.models.page import Page
from postmark.utils.types import HTTPClient

from .schemas import InboundActionResponse, InboundMessage, InboundMessageDetails


class InboundManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def list(
        self,
        count: int = 100,
        offset: int = 0,
        **filters,
    ) -> Page[InboundMessage]:
        """
        List inbound messages.

        Args:
            count: Number of messages to return (max 500).
            offset: Number of records to skip.
            **filters: recipient, fromemail, tag, subject, mailboxhash, status,
                todate, fromdate.
        """
        if count > 500:
            raise ValueError("Count cannot exceed 500 per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000")

        params: Dict[str, Any] = {"count": count, "offset": offset}
        for key, value in filters.items():
            if value is not None:
                params[key] = value

        response = await self.client.get("/messages/inbound", params=params)
        data = response.json()
        return Page(
            items=[InboundMessage(**m) for m in data.get("InboundMessages", [])],
            total=data.get("TotalCount", 0),
        )

    async def get(self, message_id: str) -> InboundMessageDetails:
        """
        Return full details for a single inbound message.
        """
        response = await self.client.get(f"/messages/inbound/{message_id}/details")
        return InboundMessageDetails(**response.json())

    async def bypass(self, message_id: str) -> InboundActionResponse:
        """
        Bypass inbound rules for a blocked message and force processing.
        """
        response = await self.client.put(f"/messages/inbound/{message_id}/bypass")
        return InboundActionResponse(**response.json())

    async def retry(self, message_id: str) -> InboundActionResponse:
        """
        Retry a failed inbound message for processing.
        """
        response = await self.client.put(f"/messages/inbound/{message_id}/retry")
        return InboundActionResponse(**response.json())
