import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from pydantic import ValidationError

from postmark.exceptions import InvalidEmailPayloadException
from postmark.utils.types import HTTPClient

from .schemas import Email, Outbound, OutboundMessageDetails, SendResponse

logger = logging.getLogger(__name__)


def _parse_email(message: Union[Email, Dict[str, Any]]) -> Email:
    """
    Coerce a dict to an Email model, raising InvalidEmailPayloadException
    on validation failure. Passes through an Email instance unchanged.
    """
    if isinstance(message, Email):
        return message
    try:
        return Email(**message)
    except ValidationError as e:
        raise InvalidEmailPayloadException(e.errors()) from e


class OutboundManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def send(self, message: Union[Email, Dict[str, Any]]) -> SendResponse:
        """Send a single email."""
        email_payload = _parse_email(message)

        logger.debug(f"Sending email to {email_payload.to}")
        response = await self.client.post(
            "/email",
            json=email_payload.model_dump(by_alias=True, exclude_none=True),
        )
        return SendResponse(**response.json())

    async def send_batch(
        self, messages: List[Union[Email, Dict[str, Any]]]
    ) -> List[SendResponse]:
        """Send different emails in a single batch (max 500)."""
        if len(messages) > 500:
            raise ValueError("Batch size cannot exceed 500 messages")

        # Validate all messages up front so we fail before making any HTTP call
        payload = []
        for i, msg in enumerate(messages):
            try:
                email_obj = _parse_email(msg)
            except InvalidEmailPayloadException as e:
                raise InvalidEmailPayloadException(
                    [
                        {
                            "loc": (f"messages[{i}]", *err["loc"]),
                            **{k: v for k, v in err.items() if k != "loc"},
                        }
                        for err in e.errors
                    ]
                ) from e
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
        """List outbound messages."""
        if count > 500:
            raise ValueError("Count cannot exceed 500 messages per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000 messages")

        if metadata:
            if len(metadata) > 1:
                raise ValueError("Can only filter by one metadata field at a time")
            for key, value in metadata.items():
                filters[f"metadata_{key}"] = value

        params = {"count": count, "offset": offset}
        for key, value in filters.items():
            if value is not None:
                params[key] = (
                    value.strftime("%Y-%m-%dT%H:%M:%S")
                    if isinstance(value, datetime)
                    else value
                )

        response = await self.client.get("/messages/outbound", params=params)
        response.raise_for_status()
        data = response.json()

        return [Outbound(**msg) for msg in data.get("Messages", [])], data.get(
            "TotalCount", 0
        )

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
