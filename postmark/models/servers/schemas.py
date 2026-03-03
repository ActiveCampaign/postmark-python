from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import DeliveryType, ServerColor, TrackLinks


class Server(BaseModel):
    """Response from ``GET /server`` and ``PUT /server``."""

    id: int = Field(alias="ID")
    name: str = Field(alias="Name")
    api_tokens: List[str] = Field(alias="ApiTokens")
    color: ServerColor = Field(alias="Color")
    smtp_api_activated: bool = Field(alias="SmtpApiActivated")
    raw_email_enabled: bool = Field(alias="RawEmailEnabled")
    delivery_type: DeliveryType = Field(alias="DeliveryType")
    server_link: str = Field(alias="ServerLink")
    inbound_address: str = Field(alias="InboundAddress")
    inbound_hook_url: Optional[str] = Field(None, alias="InboundHookUrl")
    bounce_hook_url: Optional[str] = Field(None, alias="BounceHookUrl")
    open_hook_url: Optional[str] = Field(None, alias="OpenHookUrl")
    delivery_hook_url: Optional[str] = Field(None, alias="DeliveryHookUrl")
    post_first_open_only: bool = Field(alias="PostFirstOpenOnly")
    inbound_domain: Optional[str] = Field(None, alias="InboundDomain")
    inbound_hash: str = Field(alias="InboundHash")
    inbound_spam_threshold: int = Field(alias="InboundSpamThreshold")
    track_opens: bool = Field(alias="TrackOpens")
    track_links: TrackLinks = Field(alias="TrackLinks")
    include_bounce_content_in_hook: bool = Field(alias="IncludeBounceContentInHook")
    click_hook_url: Optional[str] = Field(None, alias="ClickHookUrl")
    enable_smtp_api_error_hooks: bool = Field(alias="EnableSmtpApiErrorHooks")

    model_config = ConfigDict(populate_by_name=True)


class ServersListResponse(BaseModel):
    """Response from ``GET /servers``."""

    total_count: int = Field(alias="TotalCount")
    servers: List[Server] = Field(alias="Servers")

    model_config = ConfigDict(populate_by_name=True)


class DeleteServerResponse(BaseModel):
    """Response from ``DELETE /servers/{serverid}``."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)
