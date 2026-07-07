from datetime import datetime
from typing import Any

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
        recipient: str | None = None,
        from_email: str | None = None,
        tag: str | None = None,
        subject: str | None = None,
        mailbox_hash: str | None = None,
        status: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Page[InboundMessage]:
        """List inbound messages."""
        if count > 500:
            raise ValueError("Count cannot exceed 500 per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000")

        params: dict[str, Any] = {"count": count, "offset": offset}

        if recipient is not None:
            params["recipient"] = recipient
        if from_email is not None:
            params["fromemail"] = from_email
        if tag is not None:
            params["tag"] = tag
        if subject is not None:
            params["subject"] = subject
        if mailbox_hash is not None:
            params["mailboxhash"] = mailbox_hash
        if status is not None:
            params["status"] = status
        if from_date is not None:
            params["fromdate"] = from_date.strftime("%Y-%m-%dT%H:%M:%S")
        if to_date is not None:
            params["todate"] = to_date.strftime("%Y-%m-%dT%H:%M:%S")

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
