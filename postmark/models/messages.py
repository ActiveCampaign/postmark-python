import logging
import re
from datetime import datetime
from enum import Enum
from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Optional,
    Union,
    TYPE_CHECKING,
    AsyncGenerator,
)

from ..utils.message_utils import validate_formatted_email, validate_email_list

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    TypeAdapter,
    ValidationError,
)

if TYPE_CHECKING:
    # Prevent circular import at runtime
    from .server_client import ServerClient

# Initialize TypeAdapter
email_adapter = TypeAdapter(EmailStr)

# Logging Initialize
logger = logging.getLogger(__name__)

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
    content: str = Field(alias="Content")
    content_type: str = Field(alias="ContentType")
    content_id: Optional[str] = Field(None, alias="ContentID")
    content_length: Optional[int] = Field(None, alias="ContentLength")

    model_config = ConfigDict(populate_by_name=True)


class Header(BaseModel):
    name: str = Field(alias="Name")
    value: str = Field(alias="Value")

    model_config = ConfigDict(populate_by_name=True)


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


# --- Response Models ---


class SendResponse(BaseModel):
    """Response returned when an email is sent."""

    to: str = Field(alias="To")
    submitted_at: datetime = Field(alias="SubmittedAt")
    message_id: str = Field(alias="MessageID")
    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)


# --- Request Models ---


class Email(BaseModel):
    """Model for sending an email."""

    sender: str = Field(alias="From")
    to: str = Field(alias="To")
    cc: Optional[str] = Field(None, alias="Cc")
    bcc: Optional[str] = Field(None, alias="Bcc")
    subject: Optional[str] = Field(None, alias="Subject")
    tag: Optional[str] = Field(None, alias="Tag")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    text_body: Optional[str] = Field(None, alias="TextBody")
    reply_to: Optional[str] = Field(None, alias="ReplyTo")
    headers: List[Header] = Field(default_factory=list, alias="Headers")
    track_opens: Optional[bool] = Field(None, alias="TrackOpens")
    track_links: Optional[TrackLinksOption] = Field(None, alias="TrackLinks")
    attachments: List[Attachment] = Field(default_factory=list, alias="Attachments")
    metadata: Dict[str, str] = Field(default_factory=dict, alias="Metadata")
    message_stream: Optional[str] = Field(None, alias="MessageStream")

    model_config = ConfigDict(populate_by_name=True)


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
    sender: FormattedEmailStr = Field(alias="From")
    subject: str = Field(alias="Subject")
    attachments: List[Union[str, Attachment]] = Field(
        default_factory=list, alias="Attachments"
    )
    status: MessageStatus = Field(alias="Status")
    track_opens: bool = Field(alias="TrackOpens")
    track_links: TrackLinksOption = Field(alias="TrackLinks")
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="Metadata")
    sandboxed: bool = Field(alias="Sandboxed")

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

    sender: FormattedEmailStr = Field(alias="From")
    sendername: Optional[str] = Field(None, alias="FromName")
    senderfull: Optional[EmailAddress] = Field(None, alias="FromFull")
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


# --- Service Managers ---


class OutboundManager:
    """Manager for outbound message operations."""

    def __init__(self, client: "ServerClient"):
        self.client = client

    async def send(self, message: Union[Email, Dict[str, Any]]) -> SendResponse:
        """
        Send a single email.

        Args:
            message: An Email object or a dictionary containing the email details.
        """
        if isinstance(message, dict):
            # Validate and convert dict to Email model
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
        """
        Send multiple emails in a single batch (max 500).

        Args:
            messages: A list of Email objects or dictionaries.
        """
        if len(messages) > 500:
            raise ValueError("Batch size cannot exceed 500 messages")

        logger.debug(f"Sending batch of {len(messages)} emails")

        payload = []
        for msg in messages:
            if isinstance(msg, dict):
                email_obj = Email(**msg)
            else:
                email_obj = msg
            payload.append(email_obj.model_dump(by_alias=True, exclude_none=True))

        response = await self.client.post("/email/batch", json=payload)

        # Batch response is a list of SendResponse objects
        return [SendResponse(**item) for item in response.json()]

    async def list(
        self,
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
    ) -> tuple[List[Outbound], int]:
        """
        List outbound messages.

        Returns:
            A tuple containing (list of Outbound messages, total count matching filter).
        """
        logger.info(f"Listing outbound messages (count={count}, offset={offset})")

        # Validate constraints
        if count > 500:
            raise ValueError("Count cannot exceed 500 messages per request")
        if count + offset > 10000:
            raise ValueError("Count + Offset cannot exceed 10,000 messages")

        # Build params
        params: Dict[str, Any] = {
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

        # Use the instance's get method
        response = await self.client.get("/messages/outbound", params=params)
        response.raise_for_status()
        data = response.json()

        total_count = data.get("TotalCount", 0)
        messages = [Outbound(**msg) for msg in data.get("Messages", [])]

        logger.info(f"Found {total_count} messages, retrieved {len(messages)}")

        return messages, total_count

    async def stream(
        self, batch_size: int = 500, max_messages: int = 1000, **filters
    ) -> AsyncGenerator[Outbound, None]:
        """
        Stream messages matching the filters, handling pagination automatically.
        Yields messages one by one.

        Args:
            batch_size: Number of messages to fetch per API call (max 500).
            max_messages: Maximum number of messages to yield (max 10,000 via API).
            **filters: Arguments passed to list() (e.g. tag, status, recipient).
        """
        logger.debug(f"Streaming messages (max={max_messages})")

        if max_messages > 10000:
            raise ValueError("Cannot retrieve more than 10,000 messages")

        offset = 0
        yielded_count = 0

        # Cap batch_size at 500 (API limit)
        batch_size = min(batch_size, 500)

        while yielded_count < max_messages:
            # Determine how many to fetch in this batch
            remaining = max_messages - yielded_count
            current_limit = min(batch_size, remaining)

            # Ensure we don't breach the 10k hard limit of offset + count
            if offset + current_limit > 10000:
                current_limit = 10000 - offset
                if current_limit <= 0:
                    break

            messages, total_count = await self.list(
                count=current_limit, offset=offset, **filters
            )

            if not messages:
                break

            for msg in messages:
                yield msg
                yielded_count += 1
                if yielded_count >= max_messages:
                    return

            offset += len(messages)

            # If we've reached the end of results on the server
            if offset >= total_count:
                break

    async def get(self, message_id: str) -> OutboundMessageDetails:
        """
        Get detailed information about a specific message.
        """
        logger.debug(f"Fetching message details for ID: {message_id}")
        response = await self.client.get(f"/messages/outbound/{message_id}/details")
        return OutboundMessageDetails(**response.json())


class MessageService:
    """Service to access message-related functionality."""

    def __init__(self, client: "ServerClient"):
        self.client = client
        # Map the manager to the .Outbound property
        self.Outbound = OutboundManager(client)
