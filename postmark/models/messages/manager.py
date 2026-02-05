import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING, AsyncGenerator

from .schemas import Email, SendResponse, Outbound, OutboundMessageDetails

if TYPE_CHECKING:
    from ..server_client import ServerClient

logger = logging.getLogger(__name__)


class OutboundManager:
    def __init__(self, client: "ServerClient"):
        self.client = client

    async def send(self, message: Union[Email, Dict[str, Any]]) -> SendResponse:
        """Send a single email."""
        if isinstance(message, dict):
            email_payload = Email(**message)
        else:
            email_payload = message

        logger.debug(f"Sending email to {email_payload.to}")
        response = await self.client.post(
            "/email", json=email_payload.model_dump(by_alias=True, exclude_none=True)
        )
        return SendResponse(**response.json())

    async def send_batch(
        self, messages: List[Union[Email, Dict[str, Any]]]
    ) -> List[SendResponse]:
        """Send multiple emails in a single batch (max 500)."""
        if len(messages) > 500:
            raise ValueError("Batch size cannot exceed 500 messages")

        payload = []
        for msg in messages:
            email_obj = Email(**msg) if isinstance(msg, dict) else msg
            payload.append(email_obj.model_dump(by_alias=True, exclude_none=True))

        response = await self.client.post("/email/batch", json=payload)
        return [SendResponse(**item) for item in response.json()]

    async def list(
        self,
        count: int = 100,
        offset: int = 0,
        metadata: Optional[Dict[str, str]] = None,
        **filters,
    ) -> tuple[List[Outbound], int]:
        """List outbound messages with specific validation for tests."""

        # 1. Validate count and offset with descriptive messages for tests
        if count > 500:
            raise ValueError("Count cannot exceed 500 messages per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000 messages")

        # 2. Metadata validation (Fixes the 3rd assertion failure)
        if metadata:
            if len(metadata) > 1:
                raise ValueError("Can only filter by one metadata field at a time")

            # Map metadata dictionary to the format expected by Postmark API (metadata_key=value)
            for key, value in metadata.items():
                filters[f"metadata_{key}"] = value

        params = {"count": count, "offset": offset}

        # Process other filters (dates, tags, etc.)
        for key, value in filters.items():
            if value is not None:
                if isinstance(value, datetime):
                    params[key] = value.strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    params[key] = value

        response = await self.client.get("/messages/outbound", params=params)
        response.raise_for_status()
        data = response.json()

        total_count = data.get("TotalCount", 0)
        messages = [Outbound(**msg) for msg in data.get("Messages", [])]

        return messages, total_count

    async def stream(
        self, batch_size: int = 500, max_messages: int = 1000, **filters
    ) -> AsyncGenerator[Outbound, None]:
        """Stream messages with automatic pagination."""
        if max_messages > 10000:
            raise ValueError("Cannot retrieve more than 10,000 messages")

        offset = 0
        yielded = 0
        batch_size = min(batch_size, 500)

        while yielded < max_messages:
            remaining = max_messages - yielded
            current_limit = min(batch_size, remaining)

            if offset + current_limit > 10000:
                current_limit = 10000 - offset
                if current_limit <= 0:
                    break

            messages, total = await self.list(
                count=current_limit, offset=offset, **filters
            )
            if not messages:
                break

            for msg in messages:
                yield msg
                yielded += 1
                if yielded >= max_messages:
                    return

            offset += len(messages)
            if offset >= total:
                break

    async def get(self, message_id: str) -> OutboundMessageDetails:
        """Get detailed information for a specific message."""
        response = await self.client.get(f"/messages/outbound/{message_id}/details")
        return OutboundMessageDetails(**response.json())


class MessageService:
    def __init__(self, client: "ServerClient"):
        self.Outbound = OutboundManager(client)
