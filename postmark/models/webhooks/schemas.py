from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HttpAuth(BaseModel):
    username: str = Field(alias="Username")
    password: str = Field(alias="Password")

    model_config = ConfigDict(populate_by_name=True)


class HttpHeader(BaseModel):
    name: str = Field(alias="Name")
    value: str = Field(alias="Value")

    model_config = ConfigDict(populate_by_name=True)


class OpenTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")
    post_first_open_only: bool = Field(alias="PostFirstOpenOnly")

    model_config = ConfigDict(populate_by_name=True)


class ClickTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")

    model_config = ConfigDict(populate_by_name=True)


class DeliveryTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")

    model_config = ConfigDict(populate_by_name=True)


class BounceTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")
    include_content: bool = Field(alias="IncludeContent")

    model_config = ConfigDict(populate_by_name=True)


class SpamComplaintTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")
    include_content: bool = Field(alias="IncludeContent")

    model_config = ConfigDict(populate_by_name=True)


class SubscriptionChangeTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")

    model_config = ConfigDict(populate_by_name=True)


class WebhookTriggers(BaseModel):
    open: OpenTrigger = Field(alias="Open")
    click: ClickTrigger = Field(alias="Click")
    delivery: DeliveryTrigger = Field(alias="Delivery")
    bounce: BounceTrigger = Field(alias="Bounce")
    spam_complaint: SpamComplaintTrigger = Field(alias="SpamComplaint")
    subscription_change: SubscriptionChangeTrigger = Field(alias="SubscriptionChange")

    model_config = ConfigDict(populate_by_name=True)


class Webhook(BaseModel):
    """A webhook configuration returned by create, get, edit, and list endpoints."""

    id: int = Field(alias="ID")
    url: str = Field(alias="Url")
    message_stream: str = Field(alias="MessageStream")
    http_auth: Optional[HttpAuth] = Field(None, alias="HttpAuth")
    http_headers: Optional[List[HttpHeader]] = Field(None, alias="HttpHeaders")
    triggers: WebhookTriggers = Field(alias="Triggers")

    model_config = ConfigDict(populate_by_name=True)


class WebhooksListResponse(BaseModel):
    """Response from ``GET /webhooks``."""

    webhooks: List[Webhook] = Field(alias="Webhooks")

    model_config = ConfigDict(populate_by_name=True)


class DeleteWebhookResponse(BaseModel):
    """Response from ``DELETE /webhooks/{Id}``."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)
