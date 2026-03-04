from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from postmark.models.messages.schemas import EmailAddress, Header


class InboundAttachment(BaseModel):
    name: str = Field(alias="Name")
    content_id: Optional[str] = Field(None, alias="ContentID")
    content_type: str = Field(alias="ContentType")
    content_length: int = Field(alias="ContentLength")

    model_config = ConfigDict(populate_by_name=True)


class InboundMessage(BaseModel):
    """Response item from ``GET /messages/inbound``."""

    message_id: str = Field(alias="MessageID")
    from_email: str = Field(alias="From")
    from_name: str = Field(alias="FromName")
    from_full: EmailAddress = Field(alias="FromFull")
    to: str = Field(alias="To")
    to_full: List[EmailAddress] = Field(alias="ToFull")
    cc: Optional[str] = Field(None, alias="Cc")
    cc_full: List[EmailAddress] = Field(default_factory=list, alias="CcFull")
    reply_to: Optional[str] = Field(None, alias="ReplyTo")
    original_recipient: str = Field(alias="OriginalRecipient")
    subject: str = Field(alias="Subject")
    date: str = Field(alias="Date")
    mailbox_hash: Optional[str] = Field(None, alias="MailboxHash")
    tag: Optional[str] = Field(None, alias="Tag")
    status: str = Field(alias="Status")
    attachments: List[InboundAttachment] = Field(
        default_factory=list, alias="Attachments"
    )

    model_config = ConfigDict(populate_by_name=True)


class InboundMessageDetails(InboundMessage):
    """Response from ``GET /messages/inbound/{messageid}/details``."""

    text_body: Optional[str] = Field(None, alias="TextBody")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    blocked_reason: Optional[str] = Field(None, alias="BlockedReason")
    headers: List[Header] = Field(default_factory=list, alias="Headers")


class InboundActionResponse(BaseModel):
    """Response from bypass and retry endpoints."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)
