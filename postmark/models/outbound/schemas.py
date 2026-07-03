import logging
from datetime import datetime
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
)

from ...utils.message_utils import validate_email_list, validate_formatted_email
from .enums import BulkJobStatus, MessageEventType, MessageStatus, TrackLinksOption

logger = logging.getLogger(__name__)

FormattedEmailStr = Annotated[str, BeforeValidator(validate_formatted_email)]
EmailList = Annotated[list[str], BeforeValidator(validate_email_list)]


# ---------------------------------------------------------------------------
# Shared primitives
# ---------------------------------------------------------------------------


class EmailAddress(BaseModel):
    email: EmailStr = Field(alias="Email")
    name: str | None = Field(None, alias="Name")


class Attachment(BaseModel):
    name: str = Field(alias="Name")
    content: str = Field(alias="Content")
    content_type: str = Field(alias="ContentType")
    content_id: str | None = Field(None, alias="ContentID")
    content_length: int | None = Field(None, alias="ContentLength")

    model_config = ConfigDict(populate_by_name=True)


class Header(BaseModel):
    name: str = Field(alias="Name")
    value: str = Field(alias="Value")

    model_config = ConfigDict(populate_by_name=True)


class ClientInfo(BaseModel):
    name: str | None = Field(None, alias="Name")
    company: str | None = Field(None, alias="Company")
    family: str | None = Field(None, alias="Family")


class OSInfo(BaseModel):
    name: str | None = Field(None, alias="Name")
    company: str | None = Field(None, alias="Company")
    family: str | None = Field(None, alias="Family")


class GeoInfo(BaseModel):
    country_iso_code: str | None = Field(None, alias="CountryISOCode")
    country: str | None = Field(None, alias="Country")
    region_iso_code: str | None = Field(None, alias="RegionISOCode")
    region: str | None = Field(None, alias="Region")
    city: str | None = Field(None, alias="City")
    zip: str | None = Field(None, alias="Zip")
    coords: str | None = Field(None, alias="Coords")
    ip: str | None = Field(None, alias="IP")


# ---------------------------------------------------------------------------
# Single / batch send
# ---------------------------------------------------------------------------


class MessageEventDetails(BaseModel):
    delivery_message: str | None = Field(None, alias="DeliveryMessage")
    destination_server: str | None = Field(None, alias="DestinationServer")
    destination_ip: str | None = Field(None, alias="DestinationIP")
    summary: str | None = Field(None, alias="Summary")
    bounce_id: str | None = Field(None, alias="BounceID")
    origin: str | None = Field(None, alias="Origin")
    suppress_sending: bool | None = Field(None, alias="SuppressSending")
    link: str | None = Field(None, alias="Link")
    click_location: str | None = Field(None, alias="ClickLocation")


class MessageEvent(BaseModel):
    recipient: EmailStr = Field(alias="Recipient")
    type: MessageEventType = Field(alias="Type")
    received_at: datetime = Field(alias="ReceivedAt")
    details: MessageEventDetails | None = Field(None, alias="Details")


class SendResponse(BaseModel):
    to: str = Field(alias="To")
    submitted_at: datetime = Field(alias="SubmittedAt")
    message_id: str = Field(alias="MessageID")
    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)

    @property
    def success(self) -> bool:
        """Return True if the message was accepted (error_code == 0)."""
        return self.error_code == 0


class Email(BaseModel):
    sender: str = Field(alias="From")
    to: str = Field(alias="To")
    cc: str | None = Field(None, alias="Cc")
    bcc: str | None = Field(None, alias="Bcc")
    subject: str | None = Field(None, alias="Subject")
    tag: str | None = Field(None, alias="Tag")
    html_body: str | None = Field(None, alias="HtmlBody")
    text_body: str | None = Field(None, alias="TextBody")
    reply_to: str | None = Field(None, alias="ReplyTo")
    headers: list[Header] = Field(default_factory=list, alias="Headers")
    track_opens: bool | None = Field(None, alias="TrackOpens")
    track_links: TrackLinksOption | None = Field(None, alias="TrackLinks")
    attachments: list[Attachment] = Field(default_factory=list, alias="Attachments")
    metadata: dict[str, str] = Field(default_factory=dict, alias="Metadata")
    message_stream: str | None = Field(None, alias="MessageStream")

    model_config = ConfigDict(populate_by_name=True)


class Message(BaseModel):
    tag: str | None = Field(None, alias="Tag")
    message_id: str = Field(alias="MessageID")
    message_stream: str = Field(alias="MessageStream")
    to: list[EmailAddress] = Field(alias="To")
    cc: list[EmailAddress] = Field(default_factory=list, alias="Cc")
    bcc: list[EmailAddress] = Field(default_factory=list, alias="Bcc")
    recipients: EmailList = Field(alias="Recipients")
    received_at: datetime = Field(alias="ReceivedAt")
    sender: FormattedEmailStr = Field(alias="From")
    subject: str = Field(alias="Subject")
    attachments: list[str | Attachment] = Field(
        default_factory=list, alias="Attachments"
    )
    status: MessageStatus = Field(alias="Status")
    track_opens: bool = Field(alias="TrackOpens")
    track_links: TrackLinksOption = Field(alias="TrackLinks")
    metadata: dict[str, Any] = Field(default_factory=dict, alias="Metadata")
    sandboxed: bool = Field(alias="Sandboxed")

    model_config = ConfigDict(populate_by_name=True)


class MessageDetails(Message):
    text_body: str | None = Field(None, alias="TextBody")
    html_body: str | None = Field(None, alias="HtmlBody")
    body: str | None = Field(None, alias="Body")
    message_events: list[MessageEvent] = Field(
        default_factory=list, alias="MessageEvents"
    )


# ---------------------------------------------------------------------------
# Outbound retrieval — dump / opens / clicks
# ---------------------------------------------------------------------------


class OutboundMessageDump(BaseModel):
    """Response from ``GET /messages/outbound/{messageid}/dump``."""

    body: str = Field(alias="Body")

    model_config = ConfigDict(populate_by_name=True)


class OpenEvent(BaseModel):
    """Single record from ``GET /messages/outbound/opens`` endpoints."""

    record_type: str = Field(alias="RecordType")
    user_agent: str | None = Field(None, alias="UserAgent")
    message_id: str = Field(alias="MessageID")
    message_stream: str = Field(alias="MessageStream")
    received_at: datetime = Field(alias="ReceivedAt")
    tag: str | None = Field(None, alias="Tag")
    recipient: str = Field(alias="Recipient")
    client: ClientInfo = Field(alias="Client")
    os: OSInfo = Field(alias="OS")
    platform: str = Field(alias="Platform")
    geo: GeoInfo = Field(alias="Geo")

    model_config = ConfigDict(populate_by_name=True)


class ClickEvent(BaseModel):
    """Single record from ``GET /messages/outbound/clicks`` endpoints."""

    record_type: str = Field(alias="RecordType")
    user_agent: str | None = Field(None, alias="UserAgent")
    message_id: str = Field(alias="MessageID")
    message_stream: str = Field(alias="MessageStream")
    received_at: datetime = Field(alias="ReceivedAt")
    tag: str | None = Field(None, alias="Tag")
    recipient: str = Field(alias="Recipient")
    click_location: str | None = Field(None, alias="ClickLocation")
    original_link: str = Field(alias="OriginalLink")
    client: ClientInfo = Field(alias="Client")
    os: OSInfo = Field(alias="OS")
    platform: str = Field(alias="Platform")
    geo: GeoInfo = Field(alias="Geo")

    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Bulk send
# ---------------------------------------------------------------------------


class BulkRecipient(BaseModel):
    """
    Per-recipient entry in a bulk send request.
    """

    to: str = Field(alias="To")
    cc: str | None = Field(None, alias="Cc")
    bcc: str | None = Field(None, alias="Bcc")
    template_model: dict[str, Any] | None = Field(None, alias="TemplateModel")
    metadata: dict[str, str] | None = Field(None, alias="Metadata")
    headers: list[Header] = Field(default_factory=list, alias="Headers")

    model_config = ConfigDict(populate_by_name=True)


class BulkEmail(BaseModel):
    """
    Request body for POST /email/bulk.
    """

    sender: str = Field(alias="From")
    messages: list[BulkRecipient] = Field(alias="Messages")
    reply_to: str | None = Field(None, alias="ReplyTo")
    subject: str | None = Field(None, alias="Subject")
    html_body: str | None = Field(None, alias="HtmlBody")
    text_body: str | None = Field(None, alias="TextBody")
    template_id: int | None = Field(None, alias="TemplateId")
    template_alias: str | None = Field(None, alias="TemplateAlias")
    inline_css: bool | None = Field(None, alias="InlineCss")
    tag: str | None = Field(None, alias="Tag")
    metadata: dict[str, str] | None = Field(None, alias="Metadata")
    message_stream: str | None = Field(None, alias="MessageStream")
    track_opens: bool | None = Field(None, alias="TrackOpens")
    track_links: TrackLinksOption | None = Field(None, alias="TrackLinks")
    attachments: list[Attachment] = Field(default_factory=list, alias="Attachments")
    headers: list[Header] = Field(default_factory=list, alias="Headers")

    model_config = ConfigDict(populate_by_name=True)


class BulkSendResponse(BaseModel):
    """
    Response from POST /email/bulk.
    """

    id: str = Field(alias="ID")
    status: BulkJobStatus = Field(alias="Status")
    submitted_at: datetime = Field(alias="SubmittedAt")

    model_config = ConfigDict(populate_by_name=True)


class BulkSendStatus(BaseModel):
    """
    Response from GET /email/bulk/{bulk-request-id}.
    """

    id: str = Field(alias="Id")  # Note: Postmark uses "Id" here, not "ID"
    submitted_at: datetime = Field(alias="SubmittedAt")
    total_messages: int = Field(alias="TotalMessages")
    percentage_completed: float = Field(alias="PercentageCompleted")
    status: BulkJobStatus = Field(alias="Status")
    subject: str | None = Field(None, alias="Subject")

    model_config = ConfigDict(populate_by_name=True)
