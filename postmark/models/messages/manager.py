import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from pydantic import ValidationError

from postmark.exceptions import InvalidEmailException
from postmark.models.page import Page
from postmark.models.templates.schemas import TemplateEmail
from postmark.utils.types import HTTPClient

from .schemas import (
    BulkEmail,
    BulkSendResponse,
    BulkSendStatus,
    ClickEvent,
    Email,
    Message,
    MessageDetails,
    OpenEvent,
    OutboundMessageDump,
    SendResponse,
)

logger = logging.getLogger(__name__)


def _parse_email(message: Union[Email, Dict[str, Any]]) -> Email:
    """
    Coerce a dict to an Email model using snake_case field names,
    or raise InvalidEmailException
    """
    if isinstance(message, Email):
        return message
    try:
        return Email.model_validate(message)
    except ValidationError as e:
        raise InvalidEmailException(e.errors()) from e


def _parse_template_email(msg: Union[TemplateEmail, Dict[str, Any]]) -> TemplateEmail:
    if isinstance(msg, TemplateEmail):
        return msg
    try:
        return TemplateEmail.model_validate(msg)
    except ValidationError as e:
        raise InvalidEmailException(e.errors()) from e


def _parse_bulk_email(message: Union[BulkEmail, Dict[str, Any]]) -> BulkEmail:
    """
    Coerce a dict to a BulkEmail model, raising InvalidEmailException
    on validation failure. Passes through a BulkEmail instance unchanged.
    """
    if isinstance(message, BulkEmail):
        return message
    try:
        return BulkEmail.model_validate(message)
    except ValidationError as e:
        raise InvalidEmailException(e.errors()) from e


class OutboundManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    # -------------------------------------------------------------------------
    # Single send
    # -------------------------------------------------------------------------

    async def send(self, message: Union[Email, Dict[str, Any]]) -> SendResponse:
        """Send a single email."""
        email_payload = _parse_email(message)

        logger.debug(f"Sending email to {email_payload.to}")
        response = await self.client.post(
            "/email",
            json=email_payload.model_dump(by_alias=True, exclude_none=True),
        )
        return SendResponse(**response.json())

    # -------------------------------------------------------------------------
    # Batch send — different messages, one request (max 500)
    # -------------------------------------------------------------------------

    async def send_batch(
        self, messages: List[Union[Email, Dict[str, Any]]]
    ) -> List[SendResponse]:
        """
        Send up to 500 different emails in a single request.
        Use this when each recipient needs a **completely different** message.
        For sending the **same message** to many recipients, use send_bulk().
        """
        if len(messages) > 500:
            raise ValueError("Batch size cannot exceed 500 messages")

        payload = []
        for i, msg in enumerate(messages):
            try:
                email_obj = _parse_email(msg)
            except InvalidEmailException as e:
                raise InvalidEmailException(
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

    # -------------------------------------------------------------------------
    # Bulk send — same message, many recipients, one request
    # -------------------------------------------------------------------------

    async def send_bulk(
        self, message: Union[BulkEmail, Dict[str, Any]]
    ) -> BulkSendResponse:
        """
        Send the **same message** to multiple recipients in a single request.
        """
        bulk_payload = _parse_bulk_email(message)

        if not bulk_payload.messages:
            raise ValueError(
                "Bulk email must include at least one recipient in messages"
            )

        logger.debug(f"Sending bulk email to {len(bulk_payload.messages)} recipients")
        response = await self.client.post(
            "/email/bulk",
            json=bulk_payload.model_dump(by_alias=True, exclude_none=True),
        )
        return BulkSendResponse(**response.json())

    async def get_bulk_status(self, bulk_id: str) -> BulkSendStatus:
        """
        Poll the status of a bulk send request.
        """
        response = await self.client.get(f"/email/bulk/{bulk_id}")
        return BulkSendStatus(**response.json())

    # -------------------------------------------------------------------------
    # Template sends
    # -------------------------------------------------------------------------

    async def send_with_template(
        self, message: Union[TemplateEmail, Dict[str, Any]]
    ) -> SendResponse:
        """Send an email using a template."""
        email = _parse_template_email(message)
        logger.debug(f"Sending template email to {email.to}")
        response = await self.client.post(
            "/email/withTemplate",
            json=email.model_dump(by_alias=True, exclude_none=True),
        )
        return SendResponse(**response.json())

    async def send_batch_with_template(
        self, messages: List[Union[TemplateEmail, Dict[str, Any]]]
    ) -> List[SendResponse]:
        """Send up to 500 template emails in a single batch request."""
        if len(messages) > 500:
            raise ValueError("Batch size cannot exceed 500 messages")

        payload = []
        for i, msg in enumerate(messages):
            try:
                email = _parse_template_email(msg)
            except InvalidEmailException as e:
                raise InvalidEmailException(
                    [
                        {
                            "loc": (f"messages[{i}]", *err["loc"]),
                            **{k: v for k, v in err.items() if k != "loc"},
                        }
                        for err in e.errors
                    ]
                ) from e
            payload.append(email.model_dump(by_alias=True, exclude_none=True))

        response = await self.client.post(
            "/email/batchWithTemplates", json={"Messages": payload}
        )
        return [SendResponse(**item) for item in response.json()]

    # -------------------------------------------------------------------------
    # List / stream / get
    # -------------------------------------------------------------------------

    async def list(
        self,
        count: int = 100,
        offset: int = 0,
        metadata: Optional[Dict[str, str]] = None,
        **filters,
    ) -> Page[Message]:
        """List sent messages."""
        if count > 500:
            raise ValueError("Count cannot exceed 500 messages per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000 messages")

        if metadata:
            if len(metadata) > 1:
                raise ValueError("Can only filter by one metadata field at a time")
            for key, value in metadata.items():
                filters[f"metadata_{key}"] = value

        params: Dict[str, Any] = {"count": count, "offset": offset}
        for key, value in filters.items():
            if value is not None:
                if isinstance(value, datetime):
                    params[key] = value.strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    params[key] = value

        response = await self.client.get("/messages/outbound", params=params)
        response.raise_for_status()
        data = response.json()

        return Page(
            items=[Message(**msg) for msg in data.get("Messages", [])],
            total=data.get("TotalCount", 0),
        )

    async def stream(
        self, batch_size: int = 500, max_messages: int = 1000, **filters
    ) -> AsyncGenerator[Message, None]:
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

            page = await self.list(count=current_limit, offset=offset, **filters)
            if not page.items:
                break

            for msg in page.items:
                yield msg
                yielded += 1
                if yielded >= max_messages:
                    return

            offset += len(page.items)
            if offset >= page.total:
                break

    async def get(self, message_id: str) -> MessageDetails:
        """Get detailed information for a specific message."""
        response = await self.client.get(f"/messages/outbound/{message_id}/details")
        return MessageDetails(**response.json())

    async def get_dump(self, message_id: str) -> OutboundMessageDump:
        """Get the raw SMTP source for a specific message."""
        response = await self.client.get(f"/messages/outbound/{message_id}/dump")
        return OutboundMessageDump(**response.json())

    # -------------------------------------------------------------------------
    # Opens
    # -------------------------------------------------------------------------

    async def list_opens(
        self, count: int = 100, offset: int = 0, **filters
    ) -> Page[OpenEvent]:
        """
        List open tracking events across all messages.

        Args:
            count: Number of events to return (max 500).
            offset: Number of records to skip.
            **filters: recipient, tag, client_name, client_company, client_family,
                os_name, os_family, os_company, platform, country, region, city,
                messagestream, fromdate, todate.

        Returns:
            A ``(opens, total_count)`` tuple.
        """
        if count > 500:
            raise ValueError("Count cannot exceed 500 per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000")

        params: Dict[str, Any] = {"count": count, "offset": offset}
        for key, value in filters.items():
            if value is not None:
                params[key] = value

        response = await self.client.get("/messages/outbound/opens", params=params)
        data = response.json()
        return Page(
            items=[OpenEvent(**o) for o in data.get("Opens", [])],
            total=data.get("TotalCount", 0),
        )

    async def list_message_opens(
        self, message_id: str, count: int = 100, offset: int = 0
    ) -> Page[OpenEvent]:
        """
        List open tracking events for a specific message.

        Returns:
            A ``(opens, total_count)`` tuple.
        """
        if count > 500:
            raise ValueError("Count cannot exceed 500 per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000")

        params: Dict[str, Any] = {"count": count, "offset": offset}
        response = await self.client.get(
            f"/messages/outbound/opens/{message_id}", params=params
        )
        data = response.json()
        return Page(
            items=[OpenEvent(**o) for o in data.get("Opens", [])],
            total=data.get("TotalCount", 0),
        )

    # -------------------------------------------------------------------------
    # Clicks
    # -------------------------------------------------------------------------

    async def list_clicks(
        self, count: int = 100, offset: int = 0, **filters
    ) -> Page[ClickEvent]:
        """
        List click tracking events across all messages.

        Args:
            count: Number of events to return (max 500).
            offset: Number of records to skip.
            **filters: recipient, tag, client_name, client_company, client_family,
                os_name, os_family, os_company, platform, country, region, city,
                messagestream, fromdate, todate.

        Returns:
            A ``(clicks, total_count)`` tuple.
        """
        if count > 500:
            raise ValueError("Count cannot exceed 500 per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000")

        params: Dict[str, Any] = {"count": count, "offset": offset}
        for key, value in filters.items():
            if value is not None:
                params[key] = value

        response = await self.client.get("/messages/outbound/clicks", params=params)
        data = response.json()
        return Page(
            items=[ClickEvent(**c) for c in data.get("Clicks", [])],
            total=data.get("TotalCount", 0),
        )

    async def list_message_clicks(
        self, message_id: str, count: int = 100, offset: int = 0
    ) -> Page[ClickEvent]:
        """
        List click tracking events for a specific message.

        Returns:
            A ``(clicks, total_count)`` tuple.
        """
        if count > 500:
            raise ValueError("Count cannot exceed 500 per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000")

        params: Dict[str, Any] = {"count": count, "offset": offset}
        response = await self.client.get(
            f"/messages/outbound/clicks/{message_id}", params=params
        )
        data = response.json()
        return Page(
            items=[ClickEvent(**c) for c in data.get("Clicks", [])],
            total=data.get("TotalCount", 0),
        )
