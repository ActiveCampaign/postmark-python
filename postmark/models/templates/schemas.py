from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..outbound.enums import TrackLinksOption
from ..outbound.schemas import Attachment, Header, SendResponse
from .enums import TemplateAction, TemplateType

__all__ = [
    "Attachment",
    "Header",
    "SendResponse",
    "TrackLinksOption",
    "TemplateEmail",
    "TemplateSummary",
    "Template",
    "TemplateListResponse",
    "CreateTemplateRequest",
    "EditTemplateRequest",
    "UpsertTemplateResponse",
    "DeleteTemplateResponse",
    "ValidateTemplateRequest",
    "ValidationError",
    "TemplateContentValidation",
    "ValidateTemplateResponse",
    "PushTemplatesRequest",
    "PushedTemplate",
    "PushTemplatesResponse",
]


class TemplateEmail(BaseModel):
    template_id: int | None = Field(None, alias="TemplateId")
    template_alias: str | None = Field(None, alias="TemplateAlias")
    template_model: dict[str, Any] = Field(default_factory=dict, alias="TemplateModel")
    sender: str = Field(alias="From")
    to: str = Field(alias="To")
    cc: str | None = Field(None, alias="Cc")
    bcc: str | None = Field(None, alias="Bcc")
    reply_to: str | None = Field(None, alias="ReplyTo")
    tag: str | None = Field(None, alias="Tag")
    inline_css: bool | None = Field(None, alias="InlineCss")
    headers: list[Header] = Field(default_factory=list, alias="Headers")
    track_opens: bool | None = Field(None, alias="TrackOpens")
    track_links: TrackLinksOption | None = Field(None, alias="TrackLinks")
    attachments: list[Attachment] = Field(default_factory=list, alias="Attachments")
    metadata: dict[str, str] = Field(default_factory=dict, alias="Metadata")
    message_stream: str | None = Field(None, alias="MessageStream")

    model_config = ConfigDict(populate_by_name=True)


class TemplateSummary(BaseModel):
    active: bool = Field(alias="Active")
    template_id: int = Field(alias="TemplateId")
    name: str = Field(alias="Name")
    alias: str | None = Field(None, alias="Alias")
    template_type: TemplateType = Field(alias="TemplateType")
    layout_template: str | None = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class Template(BaseModel):
    template_id: int = Field(alias="TemplateId")
    name: str = Field(alias="Name")
    subject: str | None = Field(None, alias="Subject")
    html_body: str | None = Field(None, alias="HtmlBody")
    text_body: str | None = Field(None, alias="TextBody")
    associated_server_id: int = Field(alias="AssociatedServerId")
    active: bool = Field(alias="Active")
    alias: str | None = Field(None, alias="Alias")
    template_type: TemplateType = Field(alias="TemplateType")
    layout_template: str | None = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class TemplateListResponse(BaseModel):
    total_count: int = Field(alias="TotalCount")
    templates: list[TemplateSummary] = Field(alias="Templates")

    model_config = ConfigDict(populate_by_name=True)


class CreateTemplateRequest(BaseModel):
    name: str = Field(alias="Name")
    alias: str | None = Field(None, alias="Alias")
    subject: str | None = Field(None, alias="Subject")
    html_body: str | None = Field(None, alias="HtmlBody")
    text_body: str | None = Field(None, alias="TextBody")
    template_type: TemplateType | None = Field(None, alias="TemplateType")
    layout_template: str | None = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class EditTemplateRequest(BaseModel):
    name: str | None = Field(None, alias="Name")
    alias: str | None = Field(None, alias="Alias")
    subject: str | None = Field(None, alias="Subject")
    html_body: str | None = Field(None, alias="HtmlBody")
    text_body: str | None = Field(None, alias="TextBody")
    layout_template: str | None = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class UpsertTemplateResponse(BaseModel):
    template_id: int = Field(alias="TemplateId")
    name: str = Field(alias="Name")
    active: bool = Field(alias="Active")
    alias: str | None = Field(None, alias="Alias")
    template_type: TemplateType = Field(alias="TemplateType")
    layout_template: str | None = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class DeleteTemplateResponse(BaseModel):
    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)


class ValidationError(BaseModel):
    message: str = Field(alias="Message")
    line: int | None = Field(None, alias="Line")
    character_position: int | None = Field(None, alias="CharacterPosition")

    model_config = ConfigDict(populate_by_name=True)


class TemplateContentValidation(BaseModel):
    content_is_valid: bool = Field(alias="ContentIsValid")
    validation_errors: list[ValidationError] = Field(alias="ValidationErrors")
    rendered_content: str | None = Field(None, alias="RenderedContent")

    model_config = ConfigDict(populate_by_name=True)


class ValidateTemplateRequest(BaseModel):
    subject: str | None = Field(None, alias="Subject")
    html_body: str | None = Field(None, alias="HtmlBody")
    text_body: str | None = Field(None, alias="TextBody")
    test_render_model: dict[str, Any] | None = Field(None, alias="TestRenderModel")
    inline_css_for_html_test_render: bool | None = Field(
        None, alias="InlineCssForHtmlTestRender"
    )
    template_type: TemplateType | None = Field(None, alias="TemplateType")
    layout_template: str | None = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class ValidateTemplateResponse(BaseModel):
    all_content_is_valid: bool = Field(alias="AllContentIsValid")
    html_body: TemplateContentValidation | None = Field(None, alias="HtmlBody")
    text_body: TemplateContentValidation | None = Field(None, alias="TextBody")
    subject: TemplateContentValidation | None = Field(None, alias="Subject")
    suggested_template_model: dict[str, Any] | None = Field(
        None, alias="SuggestedTemplateModel"
    )

    model_config = ConfigDict(populate_by_name=True)


class PushTemplatesRequest(BaseModel):
    source_server_id: str = Field(alias="SourceServerID")
    destination_server_id: str = Field(alias="DestinationServerID")
    perform_changes: bool = Field(alias="PerformChanges")

    model_config = ConfigDict(populate_by_name=True)


class PushedTemplate(BaseModel):
    action: TemplateAction = Field(alias="Action")
    template_id: int | None = Field(None, alias="TemplateId")
    alias: str | None = Field(None, alias="Alias")
    name: str = Field(alias="Name")
    template_type: TemplateType = Field(alias="TemplateType")

    model_config = ConfigDict(populate_by_name=True)


class PushTemplatesResponse(BaseModel):
    total_count: int = Field(alias="TotalCount")
    templates: list[PushedTemplate] = Field(alias="Templates")

    model_config = ConfigDict(populate_by_name=True)
