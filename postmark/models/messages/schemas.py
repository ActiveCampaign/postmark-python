import logging
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
)

from ...utils.message_utils import validate_email_list, validate_formatted_email
from .enums import MessageEventType, MessageStatus, TrackLinksOption

logger = logging.getLogger(__name__)

FormattedEmailStr = Annotated[str, BeforeValidator(validate_formatted_email)]
EmailList = Annotated[List[str], BeforeValidator(validate_email_list)]


# ---------------------------------------------------------------------------
# Shared primitives
# ---------------------------------------------------------------------------


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
    ip: Optional[str] = Field(None, alias="IP")


# ---------------------------------------------------------------------------
# Single / batch send
# ---------------------------------------------------------------------------


class MessageEventDetails(BaseModel):
    delivery_message: Optional[str] = Field(None, alias="DeliveryMessage")
    destination_server: Optional[str] = Field(None, alias="DestinationServer")
    destination_ip: Optional[str] = Field(None, alias="DestinationIP")
    summary: Optional[str] = Field(None, alias="Summary")
    bounce_id: Optional[str] = Field(None, alias="BounceID")
    origin: Optional[str] = Field(None, alias="Origin")
    suppress_sending: Optional[str] = Field(None, alias="SuppressSending")
    link: Optional[str] = Field(None, alias="Link")
    click_location: Optional[str] = Field(None, alias="ClickLocation")


class MessageEvent(BaseModel):
    recipient: EmailStr = Field(alias="Recipient")
    type: MessageEventType = Field(alias="Type")
    received_at: datetime = Field(alias="ReceivedAt")
    details: Optional[MessageEventDetails] = Field(None, alias="Details")


class SendResponse(BaseModel):
    to: str = Field(alias="To")
    submitted_at: datetime = Field(alias="SubmittedAt")
    message_id: str = Field(alias="MessageID")
    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)


class Email(BaseModel):
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


class Message(BaseModel):
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


class MessageDetails(Message):
    text_body: Optional[str] = Field(None, alias="TextBody")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    body: Optional[str] = Field(None, alias="Body")
    message_events: List[MessageEvent] = Field(
        default_factory=list, alias="MessageEvents"
    )


# ---------------------------------------------------------------------------
# Bulk send
# ---------------------------------------------------------------------------


class BulkRecipient(BaseModel):
    """
    Per-recipient entry in a bulk send request.
    """

    to: str = Field(alias="To")
    cc: Optional[str] = Field(None, alias="Cc")
    bcc: Optional[str] = Field(None, alias="Bcc")
    template_model: Optional[Dict[str, Any]] = Field(None, alias="TemplateModel")
    metadata: Optional[Dict[str, str]] = Field(None, alias="Metadata")
    headers: List[Header] = Field(default_factory=list, alias="Headers")

    model_config = ConfigDict(populate_by_name=True)


class BulkEmail(BaseModel):
    """
    Request body for POST /email/bulk.
    """

    sender: str = Field(alias="From")
    messages: List[BulkRecipient] = Field(alias="Messages")
    reply_to: Optional[str] = Field(None, alias="ReplyTo")
    subject: Optional[str] = Field(None, alias="Subject")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    text_body: Optional[str] = Field(None, alias="TextBody")
    template_id: Optional[int] = Field(None, alias="TemplateId")
    template_alias: Optional[str] = Field(None, alias="TemplateAlias")
    inline_css: Optional[bool] = Field(None, alias="InlineCss")
    tag: Optional[str] = Field(None, alias="Tag")
    metadata: Optional[Dict[str, str]] = Field(None, alias="Metadata")
    message_stream: Optional[str] = Field(None, alias="MessageStream")
    track_opens: Optional[bool] = Field(None, alias="TrackOpens")
    track_links: Optional[TrackLinksOption] = Field(None, alias="TrackLinks")
    attachments: List[Attachment] = Field(default_factory=list, alias="Attachments")
    headers: List[Header] = Field(default_factory=list, alias="Headers")

    model_config = ConfigDict(populate_by_name=True)


class BulkSendResponse(BaseModel):
    """
    Response from POST /email/bulk.
    """

    id: str = Field(alias="ID")
    status: str = Field(alias="Status")  # "Accepted" | "Failed"
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
    status: str = Field(alias="Status")  # "Accepted" | "Processing" | "Completed"
    subject: Optional[str] = Field(None, alias="Subject")

    model_config = ConfigDict(populate_by_name=True)
