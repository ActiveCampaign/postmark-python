from datetime import datetime

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
    # "verified" or "unverified"; only present on enabled triggers.
    status: str | None = Field(None, alias="Status")

    model_config = ConfigDict(populate_by_name=True)


class ClickTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")
    # "verified" or "unverified"; only present on enabled triggers.
    status: str | None = Field(None, alias="Status")

    model_config = ConfigDict(populate_by_name=True)


class DeliveryTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")
    # "verified" or "unverified"; only present on enabled triggers.
    status: str | None = Field(None, alias="Status")

    model_config = ConfigDict(populate_by_name=True)


class BounceTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")
    include_content: bool = Field(alias="IncludeContent")
    # "verified" or "unverified"; only present on enabled triggers.
    status: str | None = Field(None, alias="Status")

    model_config = ConfigDict(populate_by_name=True)


class SpamComplaintTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")
    include_content: bool = Field(alias="IncludeContent")
    # "verified" or "unverified"; only present on enabled triggers.
    status: str | None = Field(None, alias="Status")

    model_config = ConfigDict(populate_by_name=True)


class SubscriptionChangeTrigger(BaseModel):
    enabled: bool = Field(alias="Enabled")
    # "verified" or "unverified"; only present on enabled triggers.
    status: str | None = Field(None, alias="Status")

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
    http_auth: HttpAuth | None = Field(None, alias="HttpAuth")
    http_headers: list[HttpHeader] | None = Field(None, alias="HttpHeaders")
    triggers: WebhookTriggers = Field(alias="Triggers")

    model_config = ConfigDict(populate_by_name=True)


class WebhooksListResponse(BaseModel):
    """Response from ``GET /webhooks``."""

    webhooks: list[Webhook] = Field(alias="Webhooks")

    model_config = ConfigDict(populate_by_name=True)


class DeleteWebhookResponse(BaseModel):
    """Response from ``DELETE /webhooks/{Id}``."""

    error_code: int = Field(alias="ErrorCode")
    message: str = Field(alias="Message")

    model_config = ConfigDict(populate_by_name=True)


class WebhookMetrics(BaseModel):
    """Delivery metrics for a webhook (or for one of its triggers) over the window."""

    total_requests: int = Field(0, alias="TotalRequests")
    success_count: int = Field(0, alias="SuccessCount")
    failure_count: int = Field(0, alias="FailureCount")
    retry_count: int = Field(0, alias="RetryCount")
    success_rate: float = Field(0.0, alias="SuccessRate")
    slow_count: int = Field(0, alias="SlowCount")
    very_slow_count: int = Field(0, alias="VerySlowCount")
    # Absent when there was no traffic / no retries in the window.
    average_terminal_response_time_ms: float | None = Field(
        None, alias="AverageTerminalResponseTimeMs"
    )
    average_retry_response_time_ms: float | None = Field(
        None, alias="AverageRetryResponseTimeMs"
    )

    model_config = ConfigDict(populate_by_name=True)


class WebhookTimeRange(BaseModel):
    """The window the statistics cover (currently the last 24 hours)."""

    start_time: datetime = Field(alias="StartTime")
    end_time: datetime = Field(alias="EndTime")
    hours: int = Field(alias="Hours")

    model_config = ConfigDict(populate_by_name=True)


class WebhookStatistics(BaseModel):
    """Response from ``GET /webhooks/{id}/statistics``."""

    webhook_id: int = Field(alias="WebhookId")
    server_id: int | None = Field(None, alias="ServerId")
    message_stream_id: str | None = Field(None, alias="MessageStreamId")
    url: str | None = Field(None, alias="Url")
    # Enabled triggers only, e.g. {"Delivery": "verified"}.
    statuses: dict[str, str] = Field(default_factory=dict, alias="Statuses")
    time_range: WebhookTimeRange | None = Field(None, alias="TimeRange")
    metrics: WebhookMetrics = Field(
        default_factory=lambda: WebhookMetrics.model_validate({}), alias="Metrics"
    )
    # Keyed by trigger name (Open, Click, Delivery, Bounce, ...).
    metrics_by_trigger: dict[str, WebhookMetrics] = Field(
        default_factory=dict, alias="MetricsByTrigger"
    )

    model_config = ConfigDict(populate_by_name=True)


class WebhookTriggerVerification(BaseModel):
    """Outcome of the test event sent for one trigger."""

    # "Open", "Click", "Delivery", "Bounce", "SpamComplaint" or "SubscriptionChange".
    trigger_type: str = Field(alias="TriggerType")
    success: bool = Field(alias="Success")
    # HTTP status your endpoint returned; 0 when it could not be reached at all.
    status_code: int | None = Field(None, alias="StatusCode")
    message: str | None = Field(None, alias="Message")

    model_config = ConfigDict(populate_by_name=True)


class WebhookVerificationResult(BaseModel):
    """Response from ``POST /webhooks/{id}/verify``."""

    id: int = Field(alias="Id")
    url: str | None = Field(None, alias="Url")
    # True only if every enabled trigger's test event got HTTP 200.
    success: bool = Field(alias="Success")
    results: list[WebhookTriggerVerification] = Field(
        default_factory=list, alias="Results"
    )
    message: str | None = Field(None, alias="Message")

    model_config = ConfigDict(populate_by_name=True)
