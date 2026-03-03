from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ..messages.enums import TrackLinksOption
from ..messages.schemas import Attachment, Header, SendResponse
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
    template_id: Optional[int] = Field(None, alias="TemplateId")
    template_alias: Optional[str] = Field(None, alias="TemplateAlias")
    template_model: Dict[str, Any] = Field(default_factory=dict, alias="TemplateModel")
    sender: str = Field(alias="From")
    to: str = Field(alias="To")
    cc: Optional[str] = Field(None, alias="Cc")
    bcc: Optional[str] = Field(None, alias="Bcc")
    reply_to: Optional[str] = Field(None, alias="ReplyTo")
    tag: Optional[str] = Field(None, alias="Tag")
    inline_css: Optional[bool] = Field(None, alias="InlineCss")
    headers: List[Header] = Field(default_factory=list, alias="Headers")
    track_opens: Optional[bool] = Field(None, alias="TrackOpens")
    track_links: Optional[TrackLinksOption] = Field(None, alias="TrackLinks")
    attachments: List[Attachment] = Field(default_factory=list, alias="Attachments")
    metadata: Dict[str, str] = Field(default_factory=dict, alias="Metadata")
    message_stream: Optional[str] = Field(None, alias="MessageStream")

    model_config = ConfigDict(populate_by_name=True)


class TemplateSummary(BaseModel):
    active: bool = Field(alias="Active")
    template_id: int = Field(alias="TemplateId")
    name: str = Field(alias="Name")
    alias: Optional[str] = Field(None, alias="Alias")
    template_type: TemplateType = Field(alias="TemplateType")
    layout_template: Optional[str] = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class Template(BaseModel):
    template_id: int = Field(alias="TemplateId")
    name: str = Field(alias="Name")
    subject: Optional[str] = Field(None, alias="Subject")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    text_body: Optional[str] = Field(None, alias="TextBody")
    associated_server_id: int = Field(alias="AssociatedServerId")
    active: bool = Field(alias="Active")
    alias: Optional[str] = Field(None, alias="Alias")
    template_type: TemplateType = Field(alias="TemplateType")
    layout_template: Optional[str] = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class TemplateListResponse(BaseModel):
    total_count: int = Field(alias="TotalCount")
    templates: List[TemplateSummary] = Field(alias="Templates")

    model_config = ConfigDict(populate_by_name=True)


class CreateTemplateRequest(BaseModel):
    name: str = Field(alias="Name")
    alias: Optional[str] = Field(None, alias="Alias")
    subject: Optional[str] = Field(None, alias="Subject")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    text_body: Optional[str] = Field(None, alias="TextBody")
    template_type: Optional[TemplateType] = Field(None, alias="TemplateType")
    layout_template: Optional[str] = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class EditTemplateRequest(BaseModel):
    name: Optional[str] = Field(None, alias="Name")
    alias: Optional[str] = Field(None, alias="Alias")
    subject: Optional[str] = Field(None, alias="Subject")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    text_body: Optional[str] = Field(None, alias="TextBody")
    layout_template: Optional[str] = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class UpsertTemplateResponse(BaseModel):
    template_id: int = Field(alias="TemplateId")
    name: str = Field(alias="Name")
    active: bool = Field(alias="Active")
    alias: Optional[str] = Field(None, alias="Alias")
    template_type: TemplateType = Field(alias="TemplateType")
    layout_template: Optional[str] = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class DeleteTemplateResponse(BaseModel):
    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)


class ValidationError(BaseModel):
    message: str = Field(alias="Message")
    line: Optional[int] = Field(None, alias="Line")
    character_position: Optional[int] = Field(None, alias="CharacterPosition")

    model_config = ConfigDict(populate_by_name=True)


class TemplateContentValidation(BaseModel):
    content_is_valid: bool = Field(alias="ContentIsValid")
    validation_errors: List[ValidationError] = Field(alias="ValidationErrors")
    rendered_content: Optional[str] = Field(None, alias="RenderedContent")

    model_config = ConfigDict(populate_by_name=True)


class ValidateTemplateRequest(BaseModel):
    subject: Optional[str] = Field(None, alias="Subject")
    html_body: Optional[str] = Field(None, alias="HtmlBody")
    text_body: Optional[str] = Field(None, alias="TextBody")
    test_render_model: Optional[Dict[str, Any]] = Field(None, alias="TestRenderModel")
    inline_css_for_html_test_render: Optional[bool] = Field(
        None, alias="InlineCssForHtmlTestRender"
    )
    template_type: Optional[TemplateType] = Field(None, alias="TemplateType")
    layout_template: Optional[str] = Field(None, alias="LayoutTemplate")

    model_config = ConfigDict(populate_by_name=True)


class ValidateTemplateResponse(BaseModel):
    all_content_is_valid: bool = Field(alias="AllContentIsValid")
    html_body: Optional[TemplateContentValidation] = Field(None, alias="HtmlBody")
    text_body: Optional[TemplateContentValidation] = Field(None, alias="TextBody")
    subject: Optional[TemplateContentValidation] = Field(None, alias="Subject")
    suggested_template_model: Optional[Dict[str, Any]] = Field(
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
    template_id: Optional[int] = Field(None, alias="TemplateId")
    alias: Optional[str] = Field(None, alias="Alias")
    name: str = Field(alias="Name")
    template_type: TemplateType = Field(alias="TemplateType")

    model_config = ConfigDict(populate_by_name=True)


class PushTemplatesResponse(BaseModel):
    total_count: int = Field(alias="TotalCount")
    templates: List[PushedTemplate] = Field(alias="Templates")

    model_config = ConfigDict(populate_by_name=True)
