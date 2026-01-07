import logging
import re
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import (BaseModel, BeforeValidator, ConfigDict, EmailStr, Field,
                      TypeAdapter, ValidationError)

from . import client

# Initialize TypeAdapter
email_adapter = TypeAdapter(EmailStr)

# Logging Initialize
logger = logging.getLogger(__name__)


def validate_formatted_email(v: str) -> str:
    """
    Validate email fields that may contain formatted strings like "Name" <email@example.com>
    """
    if not v:
        return v

    # Extract email from formats like: "Name" <email@example.com> or just email@example.com
    email_pattern = r'<([^>]+)>|([^\s<>"]+@[^\s<>"]+)'
    match = re.search(email_pattern, v)
    if not match:
        raise ValueError(f"Invalid email field format: {v}")

    email = match.group(1) or match.group(2)
    try:
        # Correct way to validate in Pydantic v2
        email_adapter.validate_python(email)
    except ValidationError:
        raise ValueError(f"Invalid email address: {email}")

    return v


def validate_email_list(v: List[str]) -> List[str]:
    """Validate that all items in a list are valid email addresses"""
    for email in v:
        try:
            email_adapter.validate_python(email)
        except ValidationError:
            raise ValueError(f"Invalid email address in list: {email}")
    return v


# Type aliases for commonly used field patterns
FormattedEmailStr = Annotated[str, BeforeValidator(validate_formatted_email)]
EmailList = Annotated[List[str], BeforeValidator(validate_email_list)]


class MessageStatus(str, Enum):
    SENT = "Sent"
    PROCESSED = "Processed"
    QUEUED = "Queued"
    BLOCKED = "Blocked"
    FAILED = "Failed"
    SCHEDULED = "Scheduled"


class TrackLinksOption(str, Enum):
    NONE = "None"
    HTML_AND_TEXT = "HtmlAndText"
    HTML_ONLY = "HtmlOnly"
    TEXT_ONLY = "TextOnly"


class MessageEventType(str, Enum):
    DELIVERED = "Delivered"
    TRANSIENT = "Transient"
    OPENED = "Opened"
    BOUNCED = "Bounced"
    SUBSCRIPTION_CHANGED = "SubscriptionChanged"
    LINK_CLICKED = "LinkClicked"


class Platform(str, Enum):
    WEBMAIL = "WebMail"
    DESKTOP = "Desktop"
    MOBILE = "Mobile"
    UNKNOWN = "Unknown"


# Sub-models
class EmailAddress(BaseModel):
    email: EmailStr = Field(alias="Email")
    name: Optional[str] = Field(None, alias="Name")


class Attachment(BaseModel):
    name: str = Field(alias="Name")
    content: Optional[str] = Field(None, alias="Content")
    content_type: Optional[str] = Field(None, alias="ContentType")
    content_id: Optional[str] = Field(None, alias="ContentID")
    content_length: Optional[int] = Field(None, alias="ContentLength")


class Header(BaseModel):
    name: str = Field(alias="Name")
    value: str = Field(alias="Value")


class ClientInfo(BaseModel):
    name: Optional[str] = Field(None, alias="Name")
    company: Optional[str] = Field(None, alias="Company")
    family: Optional[str] = Field(None, alias="Family")


class OSInfo(BaseModel):
    name: Optional[str] = Field(None, alias="Name")
    company: Optional[str] = Field(None, alias="Company")
    family: Optional[str] = Field(None, alias="Family")


class GeoInfo(BaseModel):
    country_iso_code: Optional[str] = Field(None, alias="CountryISOCode")
    country: Optional[str] = Field(None, alias="Country")
    region_iso_code: Optional[str] = Field(None, alias="RegionISOCode")
    region: Optional[str] = Field(None, alias="Region")
    city: Optional[str] = Field(None, alias="City")
    zip: Optional[str] = Field(None, alias="Zip")
    coords: Optional[str] = Field(None, alias="Coords")
    ip: Optional[str] = Field(
        None, alias="IP"
    )  # Keep as str since PostMark returns it as string


class MessageEventDetails(BaseModel):
    # Delivered events
    delivery_message: Optional[str] = Field(None, alias="DeliveryMessage")
    destination_server: Optional[str] = Field(None, alias="DestinationServer")
    destination_ip: Optional[str] = Field(None, alias="DestinationIP")

    # Opened events
    summary: Optional[str] = Field(None, alias="Summary")

    # Bounced events
    bounce_id: Optional[str] = Field(None, alias="BounceID")

    # SubscriptionChanged events
    origin: Optional[str] = Field(None, alias="Origin")
    suppress_sending: Optional[str] = Field(None, alias="SuppressSending")

    # LinkClicked events
    link: Optional[str] = Field(None, alias="Link")
    click_location: Optional[str] = Field(None, alias="ClickLocation")


class MessageEvent(BaseModel):
    recipient: EmailStr = Field(alias="Recipient")  # Use EmailStr for recipient
    type: MessageEventType = Field(alias="Type")
    received_at: datetime = Field(alias="ReceivedAt")
    details: Optional[MessageEventDetails] = Field(None, alias="Details")


# Main Message models
class Outbound(BaseModel):
    """Outbound message summary returned from search/list endpoints"""

    tag: Optional[str] = Field(None, alias="Tag")
    message_id: str = Field(alias="MessageID")
    message_stream: str = Field(alias="MessageStream")
    to: List[EmailAddress] = Field(alias="To")
    cc: List[EmailAddress] = Field(default_factory=list, alias="Cc")
    bcc: List[EmailAddress] = Field(default_factory=list, alias="Bcc")
    recipients: EmailList = Field(alias="Recipients")
    received_at: datetime = Field(alias="ReceivedAt")
    from_: FormattedEmailStr = Field(alias="From")
    subject: str = Field(alias="Subject")
    attachments: List[Union[str, Attachment]] = Field(
        default_factory=list, alias="Attachments"
    )
    status: MessageStatus = Field(alias="Status")
    track_opens: bool = Field(alias="TrackOpens")
    track_links: TrackLinksOption = Field(alias="TrackLinks")
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="Metadata")
    sandboxed: bool = Field(alias="Sandboxed")

    @classmethod
    async def find(
        cls,
        server_token: str,
        count: int = 100,
        offset: int = 0,
        recipient: Optional[str] = None,
        fromemail: Optional[str] = None,
        tag: Optional[str] = None,
        status: Optional[str] = None,  # 'queued' or 'sent'/'processed'
        todate: Optional[Union[datetime, str]] = None,
        fromdate: Optional[Union[datetime, str]] = None,
        subject: Optional[str] = None,
        messagestream: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> tuple[List["Outbound"], int]:
        """
        Search for outbound messages.

        Args:
            server_token: Postmark server server_token.
            count: Number of messages to return (max 500). Count + Offset cannot exceed 10,000.
            offset: Number of messages to skip.
            recipient: Filter by recipient email address.
            fromemail: Filter by sender email address.
            tag: Filter by tag.
            status: Filter by status ('queued' or 'sent'/'processed').
            todate: Filter messages up to this date/time (inclusive).
                   Can be datetime or ISO string like '2021-01-01T12:00:00'.
            fromdate: Filter messages starting from this date/time (inclusive).
            subject: Filter by email subject.
            messagestream: Filter by message stream ID. Defaults to 'outbound' if not specified.
            metadata: Filter by metadata key-value pairs. Only one metadata field at a time.

        Returns:
            Tuple of (list of Outbound objects, total_count)

        Raises:
            ValueError: If count > 500 or count + offset > 10000
        """
        logger.info(f"Searching for outbound messages (count={count}, offset={offset})")

        # Validate constraints
        if count > 500:
            raise ValueError("Count cannot exceed 500 messages per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000 messages")

        # Build params
        params = {
            "count": count,
            "offset": offset,
        }

        # Add (optional) filters
        if recipient:
            params["recipient"] = recipient
        if fromemail:
            params["fromemail"] = fromemail
        if tag:
            params["tag"] = tag
        if status:
            params["status"] = status
        if subject:
            params["subject"] = subject
        if messagestream:
            params["messagestream"] = messagestream

        # Handle date formatting
        if todate:
            if isinstance(todate, datetime):
                params["todate"] = todate.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                params["todate"] = todate
        if fromdate:
            if isinstance(fromdate, datetime):
                params["fromdate"] = fromdate.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                params["fromdate"] = fromdate

        if metadata:
            if len(metadata) > 1:
                raise ValueError("Can only filter by one metadata field at a time")
            for key, value in metadata.items():
                params[f"metadata_{key}"] = value

        logger.debug(f"Search parameters: {params}")

        response = await client.get(
            "/messages/outbound", server_token=server_token, params=params
        )
        response.raise_for_status()
        data = response.json()

        total_count = data.get("TotalCount", 0)
        messages = [cls(**msg) for msg in data.get("Messages", [])]

        logger.info(f"Found {total_count} messages, retrieved {len(messages)}")

        return messages, total_count

    @classmethod
    async def find_all(
        cls, server_token: str, max_messages: int = 1000, **filters
    ) -> List["Outbound"]:
        """
        Find all messages matching the filters, handling pagination automatically.

        Args:
            server_token: Postmark server server token.
            max_messages: Maximum number of messages to retrieve (up to 10,000)
            **filters: Same filter parameters as find() method

        Returns:
            List of all matching Outbound objects
        """
        logger.debug(f"Finding all messages (max={max_messages})")

        if max_messages > 10000:
            raise ValueError("Cannot retrieve more than 10,000 messages")

        all_messages = []
        offset = 0
        count = min(500, max_messages)  # Use max batch size or remaining

        while offset < max_messages:
            messages, total_count = await cls.find(
                server_token=server_token, count=count, offset=offset, **filters
            )

            all_messages.extend(messages)

            # Check if all available messages have been retrieved
            if not messages or len(all_messages) >= total_count:
                break

            offset += count
            # Adjust count for the last batch if needed
            remaining = max_messages - offset
            count = min(500, remaining)

        logger.info(f"Retrieved {len(all_messages)} messages total")
        return all_messages[:max_messages]  # Ensure we don't exceed max_messages

    @classmethod
    async def get(cls, message_id: str, server_token: str) -> "OutboundMessageDetails":
        """
        Get detailed information about a specific message.

        Args:
            message_id: The MessageID to retrieve
            server_token: Postmark server server_token.

        Returns:
            OutboundMessageDetails object with full message content
        """
        logger.debug(f"Fetching message details for ID: {message_id}")
        response = await client.get(
            f"/messages/outbound/{message_id}/details", server_token=server_token
        )
        return OutboundMessageDetails(**response.json())

    model_config = ConfigDict(populate_by_name=True)


class OutboundMessageDetails(Outbound):
    """Detailed outbound message with full content"""

    text_body: Optional[str] = Field(None, alias="TextBody")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    body: Optional[str] = Field(None, alias="Body")  # Raw SMTP dump
    message_events: List[MessageEvent] = Field(
        default_factory=list, alias="MessageEvents"
    )


class InboundMessageSummary(BaseModel):
    """Inbound message summary returned from search/list endpoints"""

    from_: FormattedEmailStr = Field(alias="From")
    from_name: Optional[str] = Field(None, alias="FromName")
    from_full: Optional[EmailAddress] = Field(None, alias="FromFull")
    to: str = Field(alias="To")
    to_full: List[EmailAddress] = Field(default_factory=list, alias="ToFull")
    cc: str = Field("", alias="Cc")
    cc_full: List[EmailAddress] = Field(default_factory=list, alias="CcFull")
    reply_to: str = Field("", alias="ReplyTo")
    original_recipient: str = Field(
        alias="OriginalRecipient"
    )  # Keep as str - might contain hash
    subject: str = Field(alias="Subject")
    date: str = Field(alias="Date")
    mailbox_hash: str = Field("", alias="MailboxHash")
    tag: str = Field("", alias="Tag")
    attachments: List[Attachment] = Field(default_factory=list, alias="Attachments")
    message_id: str = Field(alias="MessageID")
    status: MessageStatus = Field(alias="Status")

    model_config = ConfigDict(populate_by_name=True)


class InboundMessageDetails(InboundMessageSummary):
    """Detailed inbound message with full content"""

    text_body: Optional[str] = Field(None, alias="TextBody")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    headers: List[Header] = Field(default_factory=list, alias="Headers")
    blocked_reason: Optional[str] = Field(None, alias="BlockedReason")


class MessageOpen(BaseModel):
    """Message open event"""

    record_type: str = Field("Open", alias="RecordType")
    client: Optional[ClientInfo] = Field(None, alias="Client")
    os: Optional[OSInfo] = Field(None, alias="OS")
    platform: Optional[Platform] = Field(None, alias="Platform")
    user_agent: str = Field(alias="UserAgent")
    geo: Optional[GeoInfo] = Field(None, alias="Geo")
    message_id: str = Field(alias="MessageID")
    message_stream: str = Field(alias="MessageStream")
    received_at: datetime = Field(alias="ReceivedAt")
    tag: Optional[str] = Field(None, alias="Tag")
    recipient: EmailStr = Field(alias="Recipient")  # Use EmailStr for recipient

    model_config = ConfigDict(populate_by_name=True)


class MessageClick(BaseModel):
    """Message click event"""

    record_type: str = Field("Click", alias="RecordType")
    click_location: str = Field(alias="ClickLocation")
    client: Optional[ClientInfo] = Field(None, alias="Client")
    os: Optional[OSInfo] = Field(None, alias="OS")
    platform: Optional[Platform] = Field(None, alias="Platform")
    user_agent: str = Field(alias="UserAgent")
    original_link: str = Field(
        alias="OriginalLink"
    )  # Keep as str - might be relative URL
    geo: Optional[GeoInfo] = Field(None, alias="Geo")
    message_id: str = Field(alias="MessageID")
    message_stream: str = Field(alias="MessageStream")
    received_at: datetime = Field(alias="ReceivedAt")
    tag: Optional[str] = Field(None, alias="Tag")
    recipient: EmailStr = Field(alias="Recipient")  # Use EmailStr for recipient

    model_config = ConfigDict(populate_by_name=True)
