from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class OutboundOverview(BaseModel):
    """Response from ``GET /stats/outbound``."""

    sent: int = Field(0, alias="Sent")
    bounced: int = Field(0, alias="Bounced")
    smtp_api_errors: int = Field(0, alias="SMTPApiErrors")
    bounce_rate: float = Field(0.0, alias="BounceRate")
    spam_complaints: int = Field(0, alias="SpamComplaints")
    spam_complaints_rate: float = Field(0.0, alias="SpamComplaintsRate")
    opens: int = Field(0, alias="Opens")
    unique_opens: int = Field(0, alias="UniqueOpens")
    total_clicks: int = Field(0, alias="TotalClicks")
    unique_links_clicked: int = Field(0, alias="UniqueLinksClicked")
    total_tracked_links_sent: int = Field(0, alias="TotalTrackedLinksSent")
    tracked: int = Field(0, alias="Tracked")
    with_link_tracking: int = Field(0, alias="WithLinkTracking")
    with_open_tracking: int = Field(0, alias="WithOpenTracking")
    with_client_recorded: int = Field(0, alias="WithClientRecorded")
    with_platform_recorded: int = Field(0, alias="WithPlatformRecorded")

    model_config = ConfigDict(populate_by_name=True)


class SentDay(BaseModel):
    date: str = Field(alias="Date")
    sent: int = Field(alias="Sent")

    model_config = ConfigDict(populate_by_name=True)


class SentCounts(BaseModel):
    """Response from ``GET /stats/outbound/sends``."""

    days: List[SentDay] = Field(alias="Days")
    sent: int = Field(0, alias="Sent")

    model_config = ConfigDict(populate_by_name=True)


class BounceDay(BaseModel):
    date: str = Field(alias="Date")
    hard_bounce: int = Field(alias="HardBounce")
    smtp_api_error: int = Field(alias="SMTPApiError")
    soft_bounce: int = Field(alias="SoftBounce")
    transient: int = Field(alias="Transient")

    model_config = ConfigDict(populate_by_name=True)


class BounceCounts(BaseModel):
    """Response from ``GET /stats/outbound/bounces``."""

    days: List[BounceDay] = Field(alias="Days")
    hard_bounce: int = Field(0, alias="HardBounce")
    smtp_api_error: int = Field(0, alias="SMTPApiError")
    soft_bounce: int = Field(0, alias="SoftBounce")
    transient: int = Field(0, alias="Transient")

    model_config = ConfigDict(populate_by_name=True)


class SpamComplaintDay(BaseModel):
    date: str = Field(alias="Date")
    spam_complaint: int = Field(alias="SpamComplaint")

    model_config = ConfigDict(populate_by_name=True)


class SpamComplaints(BaseModel):
    """Response from ``GET /stats/outbound/spam``."""

    days: List[SpamComplaintDay] = Field(alias="Days")
    spam_complaint: int = Field(0, alias="SpamComplaint")

    model_config = ConfigDict(populate_by_name=True)


class TrackedDay(BaseModel):
    date: str = Field(alias="Date")
    tracked: int = Field(alias="Tracked")

    model_config = ConfigDict(populate_by_name=True)


class TrackedCounts(BaseModel):
    """Response from ``GET /stats/outbound/tracked``."""

    days: List[TrackedDay] = Field(alias="Days")
    tracked: int = Field(0, alias="Tracked")

    model_config = ConfigDict(populate_by_name=True)


class OpenDay(BaseModel):
    date: str = Field(alias="Date")
    opens: int = Field(alias="Opens")
    unique: int = Field(alias="Unique")

    model_config = ConfigDict(populate_by_name=True)


class OpenCounts(BaseModel):
    """Response from ``GET /stats/outbound/opens``."""

    days: List[OpenDay] = Field(alias="Days")
    opens: int = Field(0, alias="Opens")
    unique: int = Field(0, alias="Unique")

    model_config = ConfigDict(populate_by_name=True)


class PlatformDay(BaseModel):
    date: str = Field(alias="Date")
    desktop: int = Field(alias="Desktop")
    mobile: int = Field(alias="Mobile")
    unknown: int = Field(alias="Unknown")
    web_mail: int = Field(alias="WebMail")

    model_config = ConfigDict(populate_by_name=True)


class PlatformUsage(BaseModel):
    """Response from ``GET /stats/outbound/opens/platforms``."""

    days: List[PlatformDay] = Field(alias="Days")
    desktop: int = Field(0, alias="Desktop")
    mobile: int = Field(0, alias="Mobile")
    unknown: int = Field(0, alias="Unknown")
    web_mail: int = Field(0, alias="WebMail")

    model_config = ConfigDict(populate_by_name=True)


class EmailClientUsage(BaseModel):
    """Response from ``GET /stats/outbound/opens/emailclients``.

    Client names (e.g. ``"Apple Mail"``) appear as dynamic top-level keys and
    within each day object alongside ``Date``.  Access totals via
    ``model_extra`` and individual day dicts via ``days``.
    """

    days: List[Dict[str, Any]] = Field(alias="Days")

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class ClickDay(BaseModel):
    date: str = Field(alias="Date")
    clicks: int = Field(alias="Clicks")
    unique: int = Field(alias="Unique")

    model_config = ConfigDict(populate_by_name=True)


class ClickCounts(BaseModel):
    """Response from ``GET /stats/outbound/clicks``."""

    days: List[ClickDay] = Field(alias="Days")
    clicks: int = Field(0, alias="Clicks")
    unique: int = Field(0, alias="Unique")

    model_config = ConfigDict(populate_by_name=True)


class BrowserUsage(BaseModel):
    """Response from ``GET /stats/outbound/clicks/browserfamilies``.

    Browser names (e.g. ``"Google Chrome"``) appear as dynamic top-level keys
    and within each day object.  Access totals via ``model_extra``.
    """

    days: List[Dict[str, Any]] = Field(alias="Days")

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class BrowserPlatformDay(BaseModel):
    date: str = Field(alias="Date")
    desktop: int = Field(alias="Desktop")
    mobile: int = Field(alias="Mobile")
    unknown: int = Field(alias="Unknown")

    model_config = ConfigDict(populate_by_name=True)


class BrowserPlatformUsage(BaseModel):
    """Response from ``GET /stats/outbound/clicks/platforms``."""

    days: List[BrowserPlatformDay] = Field(alias="Days")
    desktop: int = Field(0, alias="Desktop")
    mobile: int = Field(0, alias="Mobile")
    unknown: int = Field(0, alias="Unknown")

    model_config = ConfigDict(populate_by_name=True)


class ClickLocationDay(BaseModel):
    date: str = Field(alias="Date")
    html: int = Field(alias="HTML")
    text: int = Field(alias="Text")

    model_config = ConfigDict(populate_by_name=True)


class ClickLocation(BaseModel):
    """Response from ``GET /stats/outbound/clicks/location``."""

    days: List[ClickLocationDay] = Field(alias="Days")
    html: int = Field(0, alias="HTML")
    text: int = Field(0, alias="Text")

    model_config = ConfigDict(populate_by_name=True)
