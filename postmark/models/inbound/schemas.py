from pydantic import BaseModel, ConfigDict, Field

from postmark.models.outbound.schemas import EmailAddress, Header


class InboundAttachment(BaseModel):
    name: str = Field(alias="Name")
    content_id: str | None = Field(None, alias="ContentID")
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
    to_full: list[EmailAddress] = Field(alias="ToFull")
    cc: str | None = Field(None, alias="Cc")
    cc_full: list[EmailAddress] = Field(default_factory=list, alias="CcFull")
    reply_to: str | None = Field(None, alias="ReplyTo")
    original_recipient: str = Field(alias="OriginalRecipient")
    subject: str = Field(alias="Subject")
    date: str = Field(alias="Date")
    mailbox_hash: str | None = Field(None, alias="MailboxHash")
    tag: str | None = Field(None, alias="Tag")
    status: str = Field(alias="Status")
    attachments: list[InboundAttachment] = Field(
        default_factory=list, alias="Attachments"
    )

    model_config = ConfigDict(populate_by_name=True)


class InboundMessageDetails(InboundMessage):
    """Response from ``GET /messages/inbound/{messageid}/details``."""

    text_body: str | None = Field(None, alias="TextBody")
    html_body: str | None = Field(None, alias="HtmlBody")
    blocked_reason: str | None = Field(None, alias="BlockedReason")
    headers: list[Header] = Field(default_factory=list, alias="Headers")


class InboundActionResponse(BaseModel):
    """Response from bypass and retry endpoints."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)
